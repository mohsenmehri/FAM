"""Central FAM service. Run behind HTTPS IIS; SQLite must be on a local disk.
All authorisation is server-side. Browser snapshots use optimistic revisions and
idempotent receipts; no last-writer-wins or automatic conflict overwrite.
"""
import copy
import hashlib
import hmac
import json
import logging
import math
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time
import uuid
from contextlib import contextmanager, closing
from datetime import datetime
from flask import Flask, request, jsonify, g, redirect, send_file, has_app_context, current_app

try:
    from .account_policy import is_custom_user, may_manage_users
except ImportError:
    from account_policy import is_custom_user, may_manage_users

try:
    from .manage import backup as verified_backup
except ImportError:  # Running directly from C:\FAM\server\app.py.
    from manage import backup as verified_backup

# Equipment Management runs bounded, one-shot SSH jobs directly from the FAM
# server (Windows OpenSSH ssh.exe). It has no browser Worker API, bearer
# token, pairing process, Windows service, or persistent equipment credentials.
try:
    from .equipment_ops import register_equipment_ops
except ImportError:
    try:
        from equipment_ops import register_equipment_ops
    except ImportError:
        register_equipment_ops=None

try:
    from . import equipment_inventory as eq_inventory
except ImportError:
    import equipment_inventory as eq_inventory

ROOT = Path(__file__).resolve().parent
SYSTEM = {'CONTROL_PANEL','SYSTEM_SEARCH_INDEX','SYSTEM_SHEET_CONFIG','SYSTEM_DATA_DICTIONARY','CHANGE_LOG','SEARCH_RESULTS','SYSTEM_KEYS','SYSTEM_UNDO_BUFFER','SYSTEM_NAVIGATOR'}
EPHEMERAL = SYSTEM - {'SYSTEM_SHEET_CONFIG', 'SYSTEM_KEYS'}
META = {'SYSTEM_SHEET_CONFIG', 'SYSTEM_KEYS'}
# `/api/state` may append this display-only log for authorised history users.
# It is accepted then discarded by validate_state, never persisted from a client.
CLIENT_TRANSIENT = {'CHANGE_LOG'}
ARCHIVES = {'لیست جمع آوری سرویس','جمع آوری مبین نت','جمع آوری آسیاتک'}
FORBIDDEN = {'__proto__','constructor','prototype'}
REGIONS = [
 ['خراسان رضوی','خراسان شمالی','خراسان جنوبی','سیستان و بلوچستان','گلستان'],
 ['تهران'],
 ['اردبیل','آذربایجان غربی','آذربایجان شرقی','خوزستان','قم','کردستان','لرستان','همدان','مرکزی','کرمانشاه','قزوین','زنجان','البرز','کهگیلویه و بویراحمد'],
 ['فارس','ایلام','اصفهان','بوشهر','چهارمحال و بختیاری','سمنان','یزد','گیلان','مازندران','هرمزگان','کرمان']]
ALIASES={'آذربایجان غربی':['آذرغربی','آذربایجانغربی'],'آذربایجان شرقی':['آذرشرقی','آذربایجانشرقی'],'کهگیلویه و بویراحمد':['کهکلویه','کهکیلویه','کهگیلویه','کهکیلویه و بویر احمد']}
EMPTY={'v':2,'order':[],'sheets':{},'lockedSheets':{},'categoryConfig':None,'regionConfig':None,'panelProtected':True}
# Central accounts use the same explicit product capabilities as the local
# client. `role` remains only for legacy rows during the safe, gradual migration.
PERMISSIONS={
    'view-sheets','search','view-history','edit-cells','save-results','add-record','remove-record','undo-remove',
    'refresh-panel','refresh-index','import-data','export-xlsx','backup-server','restore-data','empty-data','reset-data',
    'manage-regions','manage-categories','manage-users','equipment-operations'
}
PERMISSIONS |= eq_inventory.OPS | {'clear-history'}
DATA_PERMISSIONS={'view-sheets','search','edit-cells','save-results','add-record','remove-record','undo-remove','export-xlsx'}
FULL_REWRITE_PERMISSIONS={'import-data','empty-data','reset-data','restore-data'}
BUILTIN_CATEGORIES={'provinces','datacenters','services','carriers','equipment','costs','other'}

def packed(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), sort_keys=True, allow_nan=False)

def norm(s):
    return str(s).replace('ي','ی').replace('ى','ی').replace('ك','ک').strip().lower()

def province_key(s):
    s=re.sub(r'^(?:خودپرداز|شعبه|شعب)\s+', '', norm(s))
    s=re.sub(r'^استان\s*', '', s)
    return re.sub(r'[\s\u200c\u200d\u0640]', '', s)

def province(name):
    key=province_key(name)
    for r,names in enumerate(REGIONS,1):
        for i,n in enumerate(names,1):
            if key in [province_key(a) for a in [n]+ALIASES.get(n,[])]:return (f'{r}-{i}',str(r))
    return None

def assigned_region(name, state):
    """Return the current managed-region ID for a provincial sheet, if any."""
    p=province(name)
    if not p:return None
    assignments=dict((state.get('regionConfig') or {}).get('assignments',[]))
    return assignments.get(p[0],p[1] if not state.get('regionConfig') else 'unassigned')


def category_ids(state):
    config=state.get('categoryConfig') or {}
    configured=[item.get('id') for item in config.get('categories',[]) if isinstance(item,dict) and isinstance(item.get('id'),str)]
    return set(configured) | {'other'} if configured else set(BUILTIN_CATEGORIES)

def category_of_sheet(name,state):
    assignments=dict((state.get('categoryConfig') or {}).get('assignments',[]))
    if name in assignments:return assignments[name]
    if province(name) or re.search(r'ادغامی|تخریب',name):candidate='provinces'
    elif re.search(r'تجهیزات|EOL|EOS',name):candidate='equipment'
    elif re.search(r'جمع ?آ?اوری|جمع آوری|جمع اوری|PSP|مبین|آسیاتک|اسیاتک',name):candidate='carriers'
    elif 'هزینه' in name:candidate='costs'
    elif re.search(r'مرکز داده|ساختمان|سازمان',name):candidate='datacenters'
    elif re.search(r'شبکه|VSAT|SIP|VPN|اینترنت|MPLS|آنتی|دور کاری|نوری|PIN PAD|گزارش آماری',name):candidate='services'
    else:candidate='other'
    return candidate if candidate in category_ids(state) else 'other'

def has_permission(user, permission):
    return is_custom_user(user) and permission in user['permissions']

def can_access_data(user, name, state):
    """Fail-closed sheet scope for both legacy and explicit-access accounts."""
    if name in SYSTEM:return False
    if is_custom_user(user):
        category=category_of_sheet(name,state)
        if category not in user['categories']:return False
        if category!='provinces':return True
        region=assigned_region(name,state)
        return region is not None and region in user['regions']
    region=assigned_region(name,state)
    return region in user['regions'] if region is not None else name in user['sheets']

def can_read(user, name, state):
    if name not in state['sheets']:return False
    if is_custom_user(user):return has_permission(user,'view-sheets') and can_access_data(user,name,state)
    if user['role']<=2:return True
    return can_access_data(user,name,state)

def can_receive_data(user,name,state):
    if is_custom_user(user):return can_access_data(user,name,state) and bool((DATA_PERMISSIONS|FULL_REWRITE_PERMISSIONS) & set(user['permissions']))
    return can_read(user,name,state)

def has_full_data_scope(user,state):
    if not is_custom_user(user):return user['role']<=2
    return category_ids(state) <= set(user['categories']) and all(
        assigned_region(name,state) in user['regions'] for name in state['order'] if province(name)
    )


def may_manage_metadata(user,key):
    if not is_custom_user(user):return user['role']<=2
    return has_permission(user,'manage-categories' if key=='categoryConfig' else 'manage-regions')

class Problem(Exception):
    def __init__(self,status,message):self.status=status;self.message=message

def fail(status,message):raise Problem(status,message)

def safe_tree(obj,depth=0):
    if isinstance(obj,float) and not math.isfinite(obj):fail(400,'عدد نامعتبر است.')
    if depth>30:fail(400,'ساختار داده بیش از حد تو در تو است.')
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in FORBIDDEN:fail(400,'کلید نامعتبر در داده.')
            safe_tree(v,depth+1)
    elif isinstance(obj,list):
        for v in obj:safe_tree(v,depth+1)

def validate_category_config(value):
    """Validate only grouping metadata; it never changes worksheet contents.

    Logical category sections are server-persisted records.  Their IDs and
    worksheet assignments are bounded and canonicalised here, so a malformed
    browser payload cannot turn a section-title change into a workbook change.
    Older deployments that predate sections remain compatible because the new
    three fields are optional on input and are emitted as empty arrays.
    """
    if value is None:return None
    if not isinstance(value,dict) or value.get('version')!=1 or not isinstance(value.get('categories'),list) or not isinstance(value.get('assignments'),list):
        fail(400,'پیکربندی دسته‌بندی نامعتبر است.')
    if len(value['categories'])>100 or len(value['assignments'])>1000:fail(400,'پیکربندی دسته‌بندی بیش از حد بزرگ است.')
    ids=set();titles={norm(x) for x in ('همه بخش‌ها','سایر','سیستم')};categories=[]
    for item in value['categories']:
        if not isinstance(item,dict):fail(400,'دسته نامعتبر است.')
        ident=item.get('id');title=item.get('name')
        if not isinstance(ident,str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,79}',ident) or ident in {'all','other','system'} or ident in ids:
            fail(400,'شناسهٔ دسته نامعتبر است.')
        if not isinstance(title,str) or not (1<=len(title.strip())<=80) or norm(title) in titles:fail(400,'نام دسته نامعتبر است.')
        sub=item.get('sub','');color=item.get('color','#2fd4c4');icon=item.get('icon','layers')
        if not isinstance(sub,str) or not isinstance(color,str) or not isinstance(icon,str):fail(400,'جزئیات دسته نامعتبر است.')
        ids.add(ident);titles.add(norm(title));categories.append({'id':ident,'name':title.strip(),'sub':sub[:100],
          'color':color if re.fullmatch(r'#[0-9a-fA-F]{6}',color) else '#2fd4c4','icon':icon[:40]})
    assignments={}
    for pair in value['assignments']:
        if not isinstance(pair,list) or len(pair)!=2 or not all(isinstance(v,str) for v in pair):fail(400,'انتساب دسته نامعتبر است.')
        sheet,ident=pair
        if not (1<=len(sheet)<=31) or sheet in SYSTEM or (ident!='other' and ident not in ids):fail(400,'انتساب دسته نامعتبر است.')
        assignments[sheet]=ident
    # Keep section assignment metadata consistent with the category that the
    # browser will render. Custom categories are explicitly assigned; built-in
    # names use the same priority as the client-side category matcher.
    def category_for_sheet(sheet):
        if sheet in assignments:return assignments[sheet]
        if province(sheet) or re.search(r'ادغامی|تخریب',sheet):candidate='provinces'
        elif re.search(r'تجهیزات|EOL|EOS',sheet):candidate='equipment'
        elif re.search(r'جمع ?آ?اوری|جمع آوری|جمع اوری|PSP|مبین|آسیاتک|اسیاتک',sheet):candidate='carriers'
        elif 'هزینه' in sheet:candidate='costs'
        elif re.search(r'مرکز داده|ساختمان|سازمان',sheet):candidate='datacenters'
        elif re.search(r'شبکه|VSAT|SIP|VPN|اینترنت|MPLS|آنتی|دور کاری|نوری|PIN PAD|گزارش آماری',sheet):candidate='services'
        else:candidate='other'
        return candidate if candidate in ids else 'other'
    raw_sections=value.get('sections',[]);raw_section_assignments=value.get('sectionAssignments',[]);raw_initialized=value.get('sectionInitialized',[])
    if not isinstance(raw_sections,list) or not isinstance(raw_section_assignments,list) or not isinstance(raw_initialized,list) or len(raw_sections)>500 or len(raw_section_assignments)>1000 or len(raw_initialized)>100:
        fail(400,'پیکربندی بخش‌ها نامعتبر است.')
    section_ids=set();section_titles=set();sections=[]
    for item in raw_sections:
        if not isinstance(item,dict):fail(400,'بخش نامعتبر است.')
        ident=item.get('id');category=item.get('category');title=item.get('name')
        if not isinstance(ident,str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,99}',ident) or ident in section_ids or category not in ids or category=='provinces':
            fail(400,'شناسهٔ بخش نامعتبر است.')
        if not isinstance(title,str) or not (1<=len(title.strip())<=80) or norm(title)=='بدون بخش' or (category,norm(title)) in section_titles:
            fail(400,'نام بخش نامعتبر است.')
        section_ids.add(ident);section_titles.add((category,norm(title)));sections.append({'id':ident,'category':category,'name':title.strip()})
    section_by_id={section['id']:section for section in sections};section_assignments={}
    for pair in raw_section_assignments:
        if not isinstance(pair,list) or len(pair)!=2 or not all(isinstance(v,str) for v in pair):fail(400,'انتساب بخش نامعتبر است.')
        sheet,ident=pair;section=section_by_id.get(ident)
        if not (1<=len(sheet)<=31) or sheet in SYSTEM or not section or category_for_sheet(sheet)!=section['category']:
            fail(400,'انتساب بخش نامعتبر است.')
        section_assignments[sheet]=ident
    initialized=[]
    for ident in raw_initialized:
        if not isinstance(ident,str) or ident not in ids:fail(400,'وضعیت اولیهٔ بخش نامعتبر است.')
        if ident not in initialized:initialized.append(ident)
    return {'version':1,'categories':categories,'assignments':[[sheet,ident] for sheet,ident in assignments.items()],
      'sections':sections,'sectionAssignments':[[sheet,ident] for sheet,ident in section_assignments.items()],
      'sectionInitialized':initialized}

def validate_state(raw):
    if not isinstance(raw,dict):fail(400,'داده معتبر نیست.')
    safe_tree(raw)
    order=raw.get('order');sheets=raw.get('sheets')
    if not isinstance(order,list) or not all(isinstance(n,str) for n in order) or not isinstance(sheets,dict) or len(order)>500:fail(400,'فهرست بخش‌ها معتبر نیست.')
    if len(order)!=len(set(order)) or set(order)!=set(sheets):fail(400,'نام بخش‌ها تکراری یا ناقص است.')
    names=set();clean={}
    for name in order:
        if not isinstance(name,str) or not name.strip() or len(name)>31 or re.search(r'[\x00-\x1f\\/*?:\[\]]',name) or norm(name) in names:fail(400,'نام بخش نامعتبر است.')
        # Browser snapshots may include persisted metadata plus the display-only
        # CHANGE_LOG returned by `/api/state`; all other system sheets are
        # derived/server-owned and never valid input to a state commit.
        if name in SYSTEM and name not in META and name not in CLIENT_TRANSIENT:fail(400,'نام بخش سیستمی در داده‌های کاربر مجاز نیست.')
        names.add(norm(name));sh=sheets[name]
        if not isinstance(sh,dict) or not isinstance(sh.get('rows'),list) or not isinstance(sh.get('merges'),list):fail(400,'ساختار شیت نامعتبر است.')
        if len(sh['rows'])>250000 or len(sh['merges'])>20000:fail(413,'داده از سقف این نسخه بیشتر است.')
        for row in sh['rows']:
            if not isinstance(row,list) or len(row)>200:fail(400,'ستون‌های شیت نامعتبر است.')
            for cell in row:
                if cell is not None and type(cell) not in (str,int,float,bool):fail(400,'نوع سلول نامعتبر است.')
                if isinstance(cell,str) and len(cell)>100000:fail(413,'متن سلول بیش از حد بلند است.')
        for m in sh['merges']:
            if not isinstance(m,dict) or set(m)!={'r1','c1','r2','c2'} or any(type(v)!=int for v in m.values()) or not (1<=m['r1']<=m['r2']<=250000 and 1<=m['c1']<=m['c2']<=200):fail(400,'ادغام سلول نامعتبر است.')
        if name not in EPHEMERAL:clean[name]={'rows':sh['rows'],'merges':sh['merges']}
    locks=raw.get('lockedSheets') or {}
    if not isinstance(locks,dict) or any(type(v)!=bool for v in locks.values()):fail(400,'قفل شیت‌ها نامعتبر است.')
    category=validate_category_config(raw.get('categoryConfig'))
    if raw.get('regionConfig') is not None and not isinstance(raw['regionConfig'],dict):fail(400,'پیکربندی نامعتبر است.')
    region=raw.get('regionConfig')
    if region is not None:
        if region.get('version')!=1 or not isinstance(region.get('regions'),list) or not isinstance(region.get('assignments'),list):fail(400,'پیکربندی مناطق نامعتبر است.')
        ids=[]
        for r in region['regions']:
            if not isinstance(r,dict) or not isinstance(r.get('id'),str) or not isinstance(r.get('name'),str):fail(400,'منطقه نامعتبر است.')
            ids.append(r['id'])
        seen=set();valid={f'{r}-{i}' for r,ns in enumerate(REGIONS,1) for i,_ in enumerate(ns,1)}
        for pair in region['assignments']:
            if not isinstance(pair,list) or len(pair)!=2 or not all(isinstance(v,str) for v in pair) or pair[0] not in valid or pair[0] in seen or pair[1] not in ids+['unassigned']:fail(400,'انتساب استان نامعتبر است.')
            seen.add(pair[0])
        if seen!=valid or len(ids)!=len(set(ids)):fail(400,'همهٔ استان‌ها باید یک انتساب مشخص داشته باشند.')
    return {'v':2,'order':[n for n in order if n in clean],'sheets':clean,'lockedSheets':locks,'categoryConfig':category,'regionConfig':region,'panelProtected':raw.get('panelProtected',True) is not False}

def sequence_delta(old,new):
    """Only insertion OR deletion, never replacement/reordering. Preserve exact types."""
    a=[packed(x) for x in old];b=[packed(x) for x in new]
    small,large=(a,b) if len(a)<=len(b) else (b,a)
    i=0
    for row in large:
        if i<len(small) and row==small[i]:i+=1
    return i==len(small)

def trim_rows(rows):
    end=len(rows)
    while end>1 and all(v is None or (isinstance(v,str) and not v.strip()) for v in rows[end-1]):end-=1
    return rows[:end]

def valid_merge_shift(before,after,archive=False):
    """Mirror FAM shiftMerges; no independent merge edits by level 3.
    Both greedy alignments permit identical repeated rows at either edge.
    Ambiguous interior duplicate/merged deletions fail closed for admin review.
    """
    a=[packed(r) for r in trim_rows(before['rows'])[1:]]
    b=[packed(r) for r in trim_rows(after['rows'])[1:]]
    if a==b:return before['merges']==after['merges']
    if archive and b[:len(a)]==a and before['merges']==after['merges']:return True
    inserting=len(a)<len(b);small,large=(a,b) if inserting else (b,a)
    for reverse in (False,True):
        si=list(range(len(small)));li=list(range(len(large)))
        if reverse:si.reverse();li.reverse()
        pos=0;edits=[]
        for i in li:
            if pos<len(si) and small[si[pos]]==large[i]:pos+=1
            else:edits.append(i+2)
        if pos!=len(small):continue
        merges=copy.deepcopy(before['merges'])
        for at in sorted(edits,reverse=not inserting):
            for m in merges:
                for edge in ('r1','r2'):
                    if inserting and m[edge]>=at:m[edge]+=1
                    elif not inserting and m[edge]>at:m[edge]-=1
        if merges==after['merges']:return True
    return False

def authorise_custom_change(user,old,new):
    """Server enforcement for the same capability/scope model exposed in UI."""
    # The migrated administrator has every explicit capability and complete
    # scope. Preserve its existing full-administration behavior without a UI
    # level selector or a hidden special case in the browser.
    if PERMISSIONS <= set(user['permissions']) and has_full_data_scope(user,old):
        for name,locked in old['lockedSheets'].items():
            if locked and new['lockedSheets'].get(name) and packed(old['sheets'].get(name))!=packed(new['sheets'].get(name)):
                fail(403,'بخش قفل است؛ ابتدا قفل را باز کنید.')
        return
    # A full-scope import/restore/reset permission deliberately authorises a
    # workbook-wide replacement: the corresponding client feature can replace
    # every record, so requiring unrelated cell permissions would only break a
    # legitimate import while not reducing its inherent authority.
    if has_full_data_scope(user,old) and FULL_REWRITE_PERMISSIONS & set(user['permissions']):return
    for key in ('categoryConfig','regionConfig'):
        if packed(old.get(key))!=packed(new.get(key)) and not may_manage_metadata(user,key):
            fail(403,'مجوز مدیریت تنظیمات مربوطه را ندارید.')
    for key in ('lockedSheets','panelProtected'):
        if packed(old.get(key))!=packed(new.get(key)):
            fail(403,'تغییر این تنظیمات برای این حساب مجاز نیست.')

    old_names=[name for name in old['order'] if name not in SYSTEM]
    permitted=[name for name in old_names if can_access_data(user,name,old)]
    new_names=[name for name in new['order'] if name not in SYSTEM]
    existing=[name for name in new_names if name in old_names]
    metadata_catalog=may_manage_metadata(user,'categoryConfig')
    if metadata_catalog:
        # Category managers receive name-only worksheet stubs so assignments
        # can be edited without disclosing cells. They must carry that catalog
        # through unchanged; the server restores its real content below.
        if existing!=old_names:fail(403,'حذف یا جابه‌جایی بخش برای این حساب مجاز نیست.')
    else:
        if any(name not in permitted for name in existing):
            fail(403,'این بخش خارج از محدودهٔ دادهٔ مجاز است.')
        if existing != permitted:
            fail(403,'حذف یا جابه‌جایی بخش برای این حساب مجاز نیست.')
    additions=[name for name in new_names if name not in old_names]
    if additions:
        if not (has_permission(user,'import-data') and has_full_data_scope(user,old)):
            fail(403,'افزودن بخش فقط با مجوز ورود فایل و محدودهٔ کامل داده مجاز است.')
    for name in permitted:
        before=old['sheets'][name];after=new['sheets'].get(name)
        if after is None:fail(403,'بخش مجاز از درخواست حذف شده است.')
        if packed(before)==packed(after):continue
        if old['lockedSheets'].get(name):fail(403,'بخش قفل است.')
        if not before['rows'] or not after['rows'] or packed(before['rows'][0])!=packed(after['rows'][0]):
            fail(403,'تغییر عنوان ستون مجاز نیست.')
        before_rows,after_rows=trim_rows(before['rows']),trim_rows(after['rows'])
        if len(before_rows)==len(after_rows):
            if not has_permission(user,'edit-cells'):fail(403,'مجوز ویرایش سلول ندارید.')
            if before['merges']!=after['merges']:fail(403,'تغییر ساختار ادغام مجاز نیست.')
        elif len(before_rows)<len(after_rows):
            if not has_permission(user,'add-record') or not sequence_delta(before_rows,after_rows) or not valid_merge_shift(before,after):
                fail(403,'افزودن رکورد مجاز یا معتبر نیست.')
        else:
            if not has_permission(user,'remove-record') or not sequence_delta(before_rows,after_rows) or not valid_merge_shift(before,after):
                fail(403,'حذف رکورد مجاز یا معتبر نیست.')

    # Restore every inaccessible sheet byte-for-byte. A scoped browser never
    # receives them and can therefore never delete or overwrite them.
    for name in old_names:
        if name not in permitted:new['sheets'][name]=old['sheets'][name]
    for name in old['order']:
        if name in META:
            new['sheets'][name]=old['sheets'][name]
    new['order']=old_names+additions+[name for name in old['order'] if name in META]

def authorise_change(user,old,new):
    if is_custom_user(user):
        return authorise_custom_change(user,old,new)
    if user['role']<=2:
        for n,locked in old['lockedSheets'].items():
            if locked and new['lockedSheets'].get(n) and packed(old['sheets'].get(n))!=packed(new['sheets'].get(n)):fail(403,'بخش قفل است؛ ابتدا قفل را باز کنید.')
        return
    if user['role']!=3:fail(403,'این حساب فقط اجازهٔ مشاهده دارد.')
    for key in ('lockedSheets','categoryConfig','regionConfig','panelProtected'):
        if packed(old.get(key))!=packed(new.get(key)):fail(403,'تغییر تنظیمات برای سطح ۳ مجاز نیست.')

    # A scoped account receives only its own data sheets. Reject a crafted
    # request that names another region, then merge untouched server-side data
    # back before persisting so an ordinary scoped save never deletes it.
    old_names=[n for n in old['order'] if n not in SYSTEM]
    permitted_old=[n for n in old_names if can_access_data(user,n,old)]
    new_names=[n for n in new['order'] if n not in SYSTEM]
    if any(not can_access_data(user,n,old) for n in new_names):fail(403,'این بخش خارج از محدودهٔ مناطق مجاز شما است.')
    if [n for n in new_names if n in old_names]!=permitted_old:fail(403,'حذف یا جابه‌جایی بخش مجاز نیست.')

    for name in new_names:
        after=new['sheets'][name];before=old['sheets'].get(name)
        if before is None:fail(403,'افزودن بخش یا رکورد برای سطح ۳ مجاز نیست.')
        if packed(before)==packed(after):continue
        if old['lockedSheets'].get(name):fail(403,'بخش قفل است.')
        if not before['rows'] or not after['rows'] or packed(before['rows'][0])!=packed(after['rows'][0]):fail(403,'ویرایش عنوان ستون برای سطح ۳ مجاز نیست.')
        # Level 3 may edit cells in an authorised region, but cannot add or
        # remove records, create sheets, or alter merge/layout structure.
        if len(trim_rows(before['rows']))!=len(trim_rows(after['rows'])):fail(403,'افزودن یا حذف رکورد برای سطح ۳ مجاز نیست.')
        if before['merges']!=after['merges']:fail(403,'تغییر ساختار ادغام برای سطح ۳ مجاز نیست.')

    # Keep every inaccessible data sheet byte-for-byte as it is on the server.
    for name in old_names:
        if name not in permitted_old:new['sheets'][name]=old['sheets'][name]
    additions=[n for n in new_names if n not in old_names]
    new['order']=old_names+additions

    # Mapping/key metadata is server-owned for level 3; local reindexing is derived.
    for n in META:
        if n in old['sheets']:new['sheets'][n]=old['sheets'][n]
        else:new['sheets'].pop(n,None)
    for n in old['order']:
        if n in META and n not in new['order']:new['order'].append(n)

def public_user(row):
    """Return only safe, structurally valid account fields.

    These JSON columns are normally written only through validated code. If an
    operator has manually damaged SQLite, fail closed with an application error
    rather than leaking a raw parser exception to a browser.
    """
    def load_list(column):
        try:
            value=json.loads(row[column])
            if not isinstance(value,list):raise ValueError('expected list')
            return value
        except (json.JSONDecodeError,TypeError,ValueError) as error:
            logging.getLogger(__name__).error('Malformed users.%s for account id=%s: %s',column,row['id'],error)
            fail(500,'داده‌های حساب کاربری آسیب دیده است؛ لاگ سرور را بررسی کنید.')
    value={k:row[k] for k in ['id','username','name','role','enabled','revision']} | {'enabled':bool(row['enabled']),'regions':load_list('regions'),'sheets':load_list('sheets')}
    # Omit absent fields so older rows remain legacy-role accounts until their
    # first save through the new custom-access editor.
    if row['categories'] is not None and row['permissions'] is not None:
        value['categories']=load_list('categories');value['permissions']=load_list('permissions')
    try:
        stored=json.loads(row['equipment_scope']) if 'equipment_scope' in row.keys() and row['equipment_scope'] is not None else None
        permissions,scopes=eq_inventory.policy(value,stored)
        value['equipmentScope']=scopes;value['equipmentPolicyVersion']=1
        if 'permissions' in value:value['permissions']=value['permissions']+sorted(permissions-set(value['permissions']))
    except (ValueError,TypeError,KeyError):fail(500,'سیاست تجهیزات حساب معتبر نیست؛ مدیر باید آن را بررسی کند.')
    return value

_FA_DIGITS=str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹')

def password_min_length(raw=None):
    """Minimum length for new passwords.

    The product default is 12 characters. A lab deployment may temporarily
    lower it with FAM_PASSWORD_MIN_LENGTH (clamped to the hard 4-128 floor)
    until the owner approves a final password policy.
    """
    try:value=int(os.environ.get('FAM_PASSWORD_MIN_LENGTH','12') if raw is None else raw)
    except (TypeError,ValueError):value=12
    return min(128,max(4,value))

def credentials(password,salt=None):
    if not isinstance(password,str) or not 4<=len(password)<=128:fail(400,'رمز باید بین ۴ تا ۱۲۸ نویسه باشد.')
    minimum=password_min_length()
    if has_app_context():minimum=current_app.config.get('PASSWORD_MIN_LENGTH',minimum)
    if salt is None and has_app_context() and not current_app.config['TESTING'] and len(password)<minimum:fail(400,'رمز جدید باید حداقل '+str(minimum).translate(_FA_DIGITS)+' نویسه باشد؛ رمز قبلی تغییر نکرد.')
    salt=salt or secrets.token_hex(16)
    return salt,hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),210000).hex()

class ClosingConnection(sqlite3.Connection):
    def __exit__(self,*args):
        try:return super().__exit__(*args)
        finally:self.close()

def create_app(config=None):
    app=Flask(__name__,static_folder=None)
    app.json.ensure_ascii=False
    app.json.sort_keys=False
    app.config.update(DB_PATH=os.environ.get('FAM_DB',str(ROOT/'private'/'fam.sqlite3')),
      PUBLIC_ORIGIN=os.environ.get('FAM_PUBLIC_ORIGIN',''), COOKIE_SECURE=True,
      MAX_CONTENT_LENGTH=32*1024*1024, TESTING=False,
      # Equipment Management is an explicit FAM capability. The SSH helper runs
      # on the FAM server itself and connects directly to the device with
      # ssh.exe; the legacy VDI connector broker stays disabled.
      EQUIPMENT_OPS_ENABLED=os.environ.get('FAM_EQUIPMENT_OPS_ENABLED','0')=='1',
      EQUIPMENT_CONNECTOR_ENABLED=False,
      EQUIPMENT_PYTHON=os.environ.get('FAM_EQUIPMENT_PYTHON',str(ROOT/'.venv'/'Scripts'/'python.exe') if os.name=='nt' else str(ROOT/'.venv'/'bin'/'python3')),
      EQUIPMENT_HELPER=str(ROOT/'equipment_probe.py'),
      EQUIPMENT_SSH=os.environ.get('FAM_EQUIPMENT_SSH',''),
      EQUIPMENT_KNOWN_HOSTS=os.environ.get('FAM_EQUIPMENT_KNOWN_HOSTS',str(ROOT/'private'/'equipment'/'known_hosts')),
      EQUIPMENT_HOST_KEY_POLICY=os.environ.get('FAM_EQUIPMENT_HOST_KEY_POLICY','strict'),
      EQUIPMENT_RUNTIME_DIR=os.environ.get('FAM_EQUIPMENT_RUNTIME_DIR',''),
      EQUIPMENT_TICKET_KEY=os.environ.get('FAM_EQUIPMENT_TICKET_KEY','').encode('utf-8') or secrets.token_bytes(32),
      # New-password minimum length (12 = product default; a lab install may
      # lower it through FAM_PASSWORD_MIN_LENGTH until the policy is final).
      PASSWORD_MIN_LENGTH=password_min_length())
    if config:app.config.update(config)
    if not app.config['PUBLIC_ORIGIN']:raise RuntimeError('Set FAM_PUBLIC_ORIGIN to the HTTPS origin (no trailing slash).')
    if not app.config['TESTING'] and not app.config['PUBLIC_ORIGIN'].startswith('https://'):raise RuntimeError('Production requires HTTPS.')
    dbpath=Path(app.config['DB_PATH']).resolve()
    if dbpath.is_relative_to(ROOT/'www'):raise RuntimeError('The database must be outside the public www directory.')
    # Full SQLite backups are private server files, never browser downloads or
    # IIS content. The local server timezone is deliberately used in their
    # visible names so an administrator can find a date quickly in Explorer.
    backupdir=Path(app.config.get('BACKUP_DIR') or dbpath.parent/'backups').resolve()
    if backupdir.is_relative_to(ROOT/'www'):raise RuntimeError('The backup directory must be outside the public www directory.')
    # Validate fresh bootstrap BEFORE creating schema/files. A missing secret
    # must not leave an uninitialised schema which cannot safely be reseeded.
    needs_bootstrap=not dbpath.exists() or dbpath.stat().st_size==0
    if not needs_bootstrap:
        with closing(sqlite3.connect(dbpath.as_uri()+'?mode=ro',uri=True)) as existing_db:
            needs_bootstrap=not existing_db.execute("SELECT 1 FROM sqlite_master WHERE type='table'").fetchone()
    if needs_bootstrap and not app.config['TESTING']:
        initial=os.environ.get('FAM_INITIAL_PASSWORD');minimum=app.config['PASSWORD_MIN_LENGTH']
        if not isinstance(initial,str) or not minimum<=len(initial)<=128:
            raise RuntimeError('Fresh initialization requires a unique bootstrap password (%d+ characters); run bootstrap_admin.py.'%minimum)
    dbpath.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    backupdir.mkdir(parents=True,exist_ok=True,mode=0o700)
    try:
        fd=os.open(dbpath,os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600);os.close(fd)
    except FileExistsError:pass
    def connect():
        db=sqlite3.connect(dbpath,timeout=15,isolation_level=None,factory=ClosingConnection);db.row_factory=sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON');db.execute('PRAGMA busy_timeout=15000');db.execute('PRAGMA synchronous=FULL')
        return db
    @contextmanager
    def transaction():
        db=connect()
        try:
            db.execute('BEGIN IMMEDIATE');yield db;db.commit()
        except BaseException:db.rollback();raise
        finally:db.close()
    with connect() as db:
        existing={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        fresh=not existing
        required={'state','users','settings','sessions','receipts','audit','undo','attempts'}
        if existing and not required<=existing:raise RuntimeError('Existing database has an incomplete/unknown schema; restore a verified backup.')
        db.execute('PRAGMA journal_mode=WAL')
        db.executescript('''
        CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL, epoch TEXT NOT NULL, payload TEXT NOT NULL, saved_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL, name TEXT NOT NULL, role INTEGER NOT NULL, enabled INTEGER NOT NULL, regions TEXT NOT NULL, sheets TEXT NOT NULL, categories TEXT, permissions TEXT, revision TEXT NOT NULL, salt TEXT NOT NULL, hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY CHECK(id=1), users_revision INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, user_revision TEXT NOT NULL, csrf TEXT NOT NULL, expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS receipts(user_id TEXT NOT NULL, request_id TEXT NOT NULL, digest TEXT NOT NULL, response TEXT NOT NULL, PRIMARY KEY(user_id,request_id));
        CREATE TABLE IF NOT EXISTS audit(revision INTEGER PRIMARY KEY, at INTEGER NOT NULL, actor TEXT NOT NULL, names TEXT NOT NULL, snapshot TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS undo(user_id TEXT PRIMARY KEY, revision INTEGER NOT NULL, payload TEXT);
        CREATE TABLE IF NOT EXISTS attempts(bucket TEXT PRIMARY KEY, started INTEGER NOT NULL, failures INTEGER NOT NULL);
        ''')
        # SQLite only supports additive migrations. NULL deliberately means an
        # untouched legacy role account; custom rows always carry both arrays.
        columns={row['name'] for row in db.execute('PRAGMA table_info(users)')}
        if 'categories' not in columns:db.execute('ALTER TABLE users ADD COLUMN categories TEXT')
        if 'permissions' not in columns:db.execute('ALTER TABLE users ADD COLUMN permissions TEXT')
        if 'equipment_scope' not in columns:db.execute('ALTER TABLE users ADD COLUMN equipment_scope TEXT')
        if 'history_floor' not in {r['name'] for r in db.execute('PRAGMA table_info(settings)')}:db.execute('ALTER TABLE settings ADD COLUMN history_floor INTEGER NOT NULL DEFAULT 0')
    with transaction() as db:
        if not db.execute('SELECT 1 FROM state').fetchone():
            if not fresh:raise RuntimeError('Existing database has lost its state; refusing to reseed accounts.')
            initial = os.environ.get('FAM_INITIAL_PASSWORD')
            if initial is None and app.config['TESTING']: initial = '1109'  # isolated fixtures only
            minimum=app.config['PASSWORD_MIN_LENGTH']
            if not isinstance(initial,str) or (not app.config['TESTING'] and (len(initial)<minimum or initial=='1109')):
                raise RuntimeError('Fresh initialization requires a unique bootstrap password (%d+ characters); run bootstrap_admin.py. Existing databases are never reset.'%minimum)
            salt,digest=credentials(initial)
            db.execute('INSERT INTO state VALUES(1,0,?,?,0)',(str(uuid.uuid4()),packed(EMPTY)))
            db.execute('INSERT INTO settings(id,users_revision) VALUES(1,0)')
            db.execute('INSERT INTO users(id,username,name,role,enabled,regions,sheets,categories,permissions,revision,salt,hash) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
              (str(uuid.uuid4()),'admin','admin',1,1,packed([str(index) for index in range(1,len(REGIONS)+1)]),'[]',packed(sorted(BUILTIN_CATEGORIES)),packed(sorted(PERMISSIONS)),str(uuid.uuid4()),salt,digest))
        if not db.execute('SELECT 1 FROM settings WHERE id=1').fetchone():raise RuntimeError('Database settings missing; restore a verified backup.')
        validate_state(json.loads(db.execute('SELECT payload FROM state WHERE id=1').fetchone()[0]))
        active=[public_user(row) for row in db.execute('SELECT * FROM users WHERE enabled=1')]
        if not any(may_manage_users(user) for user in active):raise RuntimeError('No active user-access manager: restore a verified backup, do not reseed.')
    def user_and_session(db):
        token=hashlib.sha256(request.cookies.get('fam_session','').encode()).hexdigest()
        session=db.execute('SELECT * FROM sessions WHERE token=? AND expires>?',(token,int(time.time()))).fetchone()
        if not session:fail(401,'نشست معتبر نیست؛ دوباره وارد شوید.')
        user=db.execute('SELECT * FROM users WHERE id=? AND enabled=1',(session['user_id'],)).fetchone()
        if not user or user['revision']!=session['user_revision']:fail(401,'مجوز یا رمز حساب تغییر کرده است؛ دوباره وارد شوید.')
        return public_user(user),session
    @app.before_request
    def guard():
        if not request.path.startswith('/api/'):return
        # Equipment requests are ordinary authenticated browser API calls.
        # They keep the same strict HTTPS Origin + CSRF checks as every other
        # sensitive FAM action; there is no bearer-token exception.
        if request.method not in ('GET','HEAD','OPTIONS'):
            if request.headers.get('Origin')!=app.config['PUBLIC_ORIGIN']:fail(403,'مبدأ درخواست مجاز نیست.')
            if not request.is_json:fail(415,'بدنهٔ JSON لازم است.')
        if request.path=='/api/login':return
        with connect() as db:g.user,g.session=user_and_session(db)
        if request.method not in ('GET','HEAD') and not hmac.compare_digest(request.headers.get('X-FAM-CSRF',''),g.session['csrf']):fail(403,'توکن درخواست معتبر نیست.')
    @app.after_request
    def headers(response):
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='same-origin'
        return response
    @app.errorhandler(Problem)
    def problem(e):return jsonify(error=e.message),e.status
    @app.errorhandler(sqlite3.IntegrityError)
    def integrity(e):return jsonify(error='نام یا شناسهٔ تکراری؛ درخواست ثبت نشد.'),400
    @app.errorhandler(400)
    def malformed(e):return jsonify(error='بدنهٔ JSON نامعتبر است.'),400
    @app.errorhandler(413)
    def too_large(e):return jsonify(error='حجم درخواست بیش از ۳۲ مگابایت است.'),413
    def data():
        value=request.get_json()
        if not isinstance(value,dict):fail(400,'بدنهٔ JSON نامعتبر است.')
        safe_tree(value);return value
    def admin(user):
        if not may_manage_users(user):fail(403,'مجوز مدیریت کاربران و دسترسی‌ها لازم است.')
    def equipment_allowed(user,operation=None,host=None):
        if not eq_inventory.permitted(user,'equipment-repair' if operation=='recover' else 'equipment-scan'):return False
        if host is None:return True
        with connect() as db:
            row=db.execute('SELECT payload FROM equipment_state WHERE id=1').fetchone()
            inventory=json.loads(row['payload'])['inventory']
            known=[n for n in inventory['nodes'] if n['host']==host]
            # Even wildcard accounts may not run this switch-only workflow on a
            # known router. Unknown manual IPv4 still requires all five scopes.
            if known and (len(known)!=1 or not any(t['id']==known[0]['typeId'] and t['kind']=='switch' for t in inventory['catalog']['types'])):return False
            if all('*' in user['equipmentScope'][k] for k in eq_inventory.FIELDS):return True
            nodes=eq_inventory.view(user,inventory)['nodes']
        return sum(n['host']==host for n in nodes)==1

    def backup_allowed(user):
        if is_custom_user(user):
            if not has_permission(user,'backup-server'):fail(403,'مجوز پشتیبان‌گیری لازم است.')
        elif user['role']>3:fail(403,'این عملیات برای این سطح دسترسی مجاز نیست.')
    def undo_summary(db,revision):
        row=db.execute('SELECT at FROM audit WHERE revision=? AND snapshot!=?',(revision,'')).fetchone()
        return {'valid':True,'serverRevision':revision,'blockCount':1,'blocks':[],'ts':row['at']} if row else None
    @app.get('/api/undo-state')
    def undo_state():
        if (is_custom_user(g.user) and not has_permission(g.user,'undo-remove')) or (not is_custom_user(g.user) and g.user['role']>2):fail(403,'مجوز بازگردانی لازم است.')
        with connect() as db:
            db.execute('BEGIN');u,_=user_and_session(db)
            if (is_custom_user(u) and not has_permission(u,'undo-remove')) or (not is_custom_user(u) and u['role']>2):fail(403,'مجوز تغییر کرده است.')
            current=db.execute('SELECT revision,epoch FROM state WHERE id=1').fetchone()
            old=db.execute('SELECT * FROM audit WHERE revision=?',(current['revision'],)).fetchone()
            if not old or not old['snapshot']:fail(404,'نسخه‌ای برای بازگشت موجود نیست.')
            return jsonify(state=json.loads(old['snapshot']),revision=current['revision'],epoch=current['epoch'],user=u,actor=old['actor'],sheets=old['names'])
    def envelope(db,user,session=None):
        row=db.execute('SELECT * FROM state WHERE id=1').fetchone();p=json.loads(row['payload'])
        allowed=[n for n in p['order'] if can_receive_data(user,n,p)]
        # A category editor needs worksheet *names* to assign them, not their
        # cells. Supply immutable-looking stubs for the catalog; commit restores
        # their authoritative content before persistence.
        catalog=[n for n in p['order'] if n not in SYSTEM] if may_manage_metadata(user,'categoryConfig') else []
        visible=[n for n in p['order'] if n in set(allowed)|set(catalog)]
        p['order']=visible;p['sheets']={n:(p['sheets'][n] if n in allowed else {'rows':[],'merges':[]}) for n in visible}
        if not is_custom_user(user) and user['role']==4:p['categoryConfig']=None;p['lockedSheets']={n:True for n in allowed}
        p['undo']=undo_summary(db,row['revision']) if (has_permission(user,'undo-remove') if is_custom_user(user) else user['role']<=2) else None
        p['savedAt']=row['saved_at']
        may_see_log=has_permission(user,'view-history') if is_custom_user(user) else user['role']<=2
        if may_see_log:
            logs=db.execute('SELECT revision,at,actor,names FROM audit WHERE revision>(SELECT history_floor FROM settings WHERE id=1) ORDER BY revision DESC LIMIT 200').fetchall()
            p['sheets']['CHANGE_LOG']={'rows':[['Time','Action','Sheets','Revision','User','Status','Notes']]+[[time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(a['at']/1000)),'SERVER_COMMIT',a['names'],a['revision'],a['actor'],'SUCCESS','ثبت قطعی سرور'] for a in reversed(logs)],'merges':[]}
            p['order'].append('CHANGE_LOG')
        return {'revision':row['revision'],'epoch':row['epoch'],'historyFloor':db.execute('SELECT history_floor FROM settings WHERE id=1').fetchone()[0],'state':p,'user':user}
    @app.get('/')
    def root():
        # IIS serves this small public login document. Keep the loopback root
        # consistent for direct health checks without publishing the full UI.
        return send_file(ROOT/'www'/'login.html',mimetype='text/html',max_age=0,conditional=False)

    @app.get('/app')
    @app.get('/FAM.html')
    def index():
        # The interactive spreadsheet client is not an IIS static asset.  A
        # user must first hold an active FAM session before its UI code can be
        # sent.  The business/data engine and the private workbook remain on
        # the server in every case; browsers receive only authorised API data.
        with connect() as db:
            try:user_and_session(db)
            except Problem:return redirect('/login.html',code=302)
        return send_file(ROOT/'private_ui'/'FAM.html',mimetype='text/html',max_age=0,conditional=False)
    @app.post('/api/login')
    def login():
        value=data();name=str(value.get('username','')).strip().lower();pw=value.get('password','')
        bucket=hashlib.sha256((name+'|'+(request.remote_addr or '')).encode()).hexdigest();now=int(time.time())
        with transaction() as db:
            attempt=db.execute('SELECT * FROM attempts WHERE bucket=?',(bucket,)).fetchone()
            if attempt and now-attempt['started']<900 and attempt['failures']>=10:fail(429,'تلاش‌های ورود زیاد است؛ ۱۵ دقیقه بعد امتحان کنید.')
            row=db.execute('SELECT * FROM users WHERE username=? AND enabled=1',(name,)).fetchone()
            valid=False
            if isinstance(pw,str) and 4<=len(pw)<=128:
                _,hashed=credentials(pw,row['salt'] if row else '0'*32)
                valid=bool(row and hmac.compare_digest(hashed,row['hash']))
            if not valid:
                start=attempt['started'] if attempt and now-attempt['started']<900 else now
                count=attempt['failures']+1 if attempt and now-attempt['started']<900 else 1
                db.execute('INSERT OR REPLACE INTO attempts VALUES(?,?,?)',(bucket,start,count))
                # Commit failure accounting before returning, not raising/rolling back.
                return jsonify(error='نام کاربری یا رمز عبور نادرست است.'),401
            db.execute('DELETE FROM attempts WHERE bucket=?',(bucket,));db.execute('DELETE FROM sessions WHERE expires<?',(now,))
            token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32)
            db.execute('INSERT INTO sessions VALUES(?,?,?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),row['id'],row['revision'],csrf,now+8*3600))
            response=jsonify(user=public_user(row),csrf=csrf)
            response.set_cookie('fam_session',token,httponly=True,secure=app.config['COOKIE_SECURE'],samesite='Strict',max_age=8*3600,path='/')
            return response
    @app.get('/api/session')
    def session():return jsonify(user=g.user,csrf=g.session['csrf'])
    @app.post('/api/logout')
    def logout():
        with transaction() as db:db.execute('DELETE FROM sessions WHERE token=?',(g.session['token'],))
        r=jsonify(ok=True);r.delete_cookie('fam_session',path='/');return r
    @app.post('/api/reauth')
    def reauth():
        value=data()
        if (is_custom_user(g.user) and not has_permission(g.user,'manage-users')) or (not is_custom_user(g.user) and g.user['role']>2):fail(403,'تأیید مدیر لازم است.')
        with connect() as db:row=db.execute('SELECT * FROM users WHERE id=?',(g.user['id'],)).fetchone()
        _,hashed=credentials(value.get('password',''),row['salt'])
        if not hmac.compare_digest(hashed,row['hash']):fail(403,'رمز نادرست است.')
        return jsonify(ok=True)
    @app.get('/api/status')
    def status():
        # This intentionally exposes only a small, permission-safe change
        # notice. The browser uses it to announce a new central revision;
        # business data itself remains available only through /api/state.
        with connect() as db:
            row=db.execute('SELECT revision,epoch FROM state WHERE id=1').fetchone()
            audit=db.execute('SELECT actor,at FROM audit WHERE revision=?',(row['revision'],)).fetchone()
            history_floor=db.execute('SELECT history_floor FROM settings WHERE id=1').fetchone()[0]
        change={'revision':row['revision'],'at':audit['at'] if audit else None}
        # Scoped accounts do not receive the name of a colleague who changed
        # data outside their permitted scope.
        if audit and ((has_permission(g.user,'view-history')) if is_custom_user(g.user) else g.user['role']<=3):change['actor']=audit['actor']
        return jsonify(revision=row['revision'],epoch=row['epoch'],userRevision=g.user['revision'],historyFloor=history_floor,change=change)
    @app.post('/api/backups')
    def create_manual_backup():
        # A browser may request a backup, but it never receives database bytes
        # or a filesystem path. Levels 1–3 may create it; the result stays private.
        data();backup_allowed(g.user)
        now=datetime.now().astimezone()
        stamp=now.strftime('%Y-%m-%d_%H-%M-%S-')+f'{now.microsecond//1000:03d}'
        filename=f'FAM-manual-{stamp}-{uuid.uuid4().hex[:6]}.sqlite3'
        try:
            verified_backup(dbpath,backupdir/filename)
        except (OSError,ValueError,sqlite3.Error):
            app.logger.exception('Manual FAM backup failed')
            fail(500,'پشتیبان‌گیری روی سرور ناموفق بود؛ گزارش خصوصی سرور را بررسی کنید.')
        app.logger.info('Verified manual FAM backup %s created by administrator %s',filename,g.user['username'])
        return jsonify(filename=filename,createdAt=now.isoformat(timespec='seconds'))
    @app.get('/api/state')
    def state():
        with connect() as db:
            db.execute('BEGIN');u,_=user_and_session(db);return jsonify(envelope(db,u))
    @app.post('/api/state')
    def commit():
        if not is_custom_user(g.user) and g.user['role']==4:fail(403,'این حساب فقط مشاهده می‌کند.')
        body=data();rid=body.get('requestId');base=body.get('revision')
        if not isinstance(rid,str) or not re.fullmatch(r'[a-f0-9-]{36}',rid) or type(base)!=int:fail(400,'شناسه یا نسخهٔ درخواست نامعتبر است.')
        proposed=validate_state(body.get('state'));digest=hashlib.sha256(packed(body).encode()).hexdigest()
        with transaction() as db:
            u,_=user_and_session(db) # Re-authorise after acquiring the write lock.
            if not is_custom_user(u) and u['role']==4:fail(403,'این حساب فقط مشاهده می‌کند.')
            receipt=db.execute('SELECT * FROM receipts WHERE user_id=? AND request_id=?',(u['id'],rid)).fetchone()
            if receipt:
                if receipt['digest']!=digest:fail(409,'شناسهٔ درخواست با محتوای متفاوت تکرار شده است.')
                return jsonify(json.loads(receipt['response']))
            row=db.execute('SELECT * FROM state WHERE id=1').fetchone()
            if body.get('epoch')!=row['epoch'] or base!=row['revision']:fail(409,'کاربر دیگری داده‌ها را تغییر داده است. تغییر شما ثبت نشد؛ نسخهٔ تازه را دریافت و تغییر را دوباره اعمال کنید.')
            old=json.loads(row['payload']);authorise_change(u,old,proposed)
            revision=row['revision']+1;stamp=int(time.time()*1000)
            names=','.join(n for n in set(old['sheets'])|set(proposed['sheets']) if packed(old['sheets'].get(n))!=packed(proposed['sheets'].get(n)))[:1000]
            db.execute('UPDATE state SET payload=?,revision=?,saved_at=? WHERE id=1',(packed(proposed),revision,stamp))
            db.execute('INSERT INTO audit VALUES(?,?,?,?,?)',(revision,stamp,u['name'],names,row['payload']))
            db.execute("UPDATE audit SET snapshot='' WHERE revision<=? AND snapshot!=''",(revision-50,))
            result={'revision':revision,'epoch':row['epoch'],'savedAt':stamp,'undo':undo_summary(db,revision) if (has_permission(u,'undo-remove') if is_custom_user(u) else u['role']<=2) else None}
            db.execute('INSERT INTO receipts VALUES(?,?,?,?)',(u['id'],rid,digest,packed(result)))
            return jsonify(result)
    def users_result(db):
        return {'revision':db.execute('SELECT users_revision FROM settings WHERE id=1').fetchone()[0], 'users':[public_user(r) for r in db.execute('SELECT * FROM users ORDER BY username')]}
    @app.get('/api/users')
    def users():
        admin(g.user)
        with connect() as db:
            db.execute('BEGIN');u,_=user_and_session(db);admin(u);return jsonify(users_result(db))
    @app.post('/api/users')
    def save_users():
        body=data();admin(g.user);values=body.get('users')
        if not isinstance(values,list) or not 1<=len(values)<=200:fail(400,'فهرست کاربران نامعتبر است.')
        with transaction() as db:
            u,session=user_and_session(db);admin(u)
            if body.get('revision')!=db.execute('SELECT users_revision FROM settings WHERE id=1').fetchone()[0]:fail(409,'فهرست کاربران تغییر کرده است؛ دوباره باز کنید.')
            old={row['id']:dict(row) for row in db.execute('SELECT * FROM users')};ids=set();names=set();normal=[]
            for x in values:
                if not isinstance(x,dict):fail(400,'کاربر نامعتبر است.')
                uid=x.get('id');name=x.get('username','');display=x.get('name','');enabled=x.get('enabled')
                if not isinstance(uid,str) or not re.fullmatch(r'[a-zA-Z0-9-]{10,60}',uid) or uid in ids or not isinstance(name,str) or not re.fullmatch(r'[a-z0-9_.-]{3,40}',name) or name in names or not isinstance(display,str) or not 1<=len(display.strip())<=60 or type(enabled)!=bool:
                    fail(400,'مشخصات کاربر معتبر نیست.')
                ids.add(uid);names.add(name)
                for field in ['regions','sheets']:
                    if not isinstance(x.get(field),list) or len(x[field])>500 or any(not isinstance(v,str) or len(v)>100 for v in x[field]):fail(400,'محدودهٔ کاربر نامعتبر است.')
                previous=old.get(uid);custom=('categories' in x or 'permissions' in x)
                if custom:
                    categories=x.get('categories');permissions=x.get('permissions')
                    if not isinstance(categories,list) or not isinstance(permissions,list) or len(categories)>100 or len(permissions)>len(PERMISSIONS) or any(not isinstance(v,str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,79}',v) for v in categories) or any(v not in PERMISSIONS for v in permissions):
                        fail(400,'دسترسی‌های سفارشی کاربر معتبر نیست.')
                    categories=list(dict.fromkeys(categories));permissions=list(dict.fromkeys(permissions))
                    # Kept only for legacy compatibility. It is never exposed in
                    # the custom-access editor and does not grant capabilities.
                    role=previous['role'] if previous else 4
                    cat_value,perm_value=packed(categories),packed(permissions)
                else:
                    if previous and previous['categories'] is not None:fail(400,'حساب دسترسی سفارشی باید دسته‌ها و مجوزهای خود را حفظ کند.')
                    role=x.get('role')
                    if type(role)!=int or role not in [1,2,3,4]:fail(400,'سطح دسترسی قدیمی معتبر نیست.')
                    categories=permissions=None;cat_value=perm_value=None
                try:
                    eq_scope=eq_inventory.scope(x['equipmentScope']) if 'equipmentScope' in x else (eq_inventory.scope(json.loads(previous['equipment_scope'])) if previous and previous['equipment_scope'] else eq_inventory.policy({'role':role})[1] if not custom else {k:[] for k in eq_inventory.FIELDS})
                except (ValueError,TypeError,KeyError):fail(400,'محدودهٔ تجهیزات معتبر نیست.')
                password=x.get('password')
                if previous is None and not password:fail(400,'رمز کاربر جدید لازم است.')
                salt,digest=credentials(password) if password else (previous['salt'],previous['hash'])
                pub={'id':uid,'username':name,'name':display.strip(),'role':role,'enabled':enabled,'regions':x['regions'],'sheets':x['sheets']}
                if custom:pub['categories']=categories;pub['permissions']=permissions
                pub['equipmentScope']=eq_scope;pub['equipmentPolicyVersion']=1
                changed=not previous or password or any(public_user(previous).get(key)!=value for key,value in pub.items()) or (previous and (previous['categories']!=cat_value or previous['permissions']!=perm_value))
                revision=str(uuid.uuid4()) if changed else previous['revision']
                normal.append({'id':uid,'username':name,'name':display.strip(),'role':role,'enabled':enabled,'regions':x['regions'],'sheets':x['sheets'],'categories':cat_value,'permissions':perm_value,'revision':revision,'salt':salt,'hash':digest,'public':pub,'equipment_scope':packed(eq_scope)})
            if not any(item['enabled'] and may_manage_users(item['public']) for item in normal):fail(400,'حداقل یک مدیر فعال مدیریت کاربران لازم است.')
            for uid in set(old)-ids:db.execute('DELETE FROM users WHERE id=?',(uid,))
            # Update in-place: REPLACE would cascade-delete active sessions.
            for item in normal:
                db.execute('''INSERT INTO users(id,username,name,role,enabled,regions,sheets,categories,permissions,revision,salt,hash) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                  ON CONFLICT(id) DO UPDATE SET username=excluded.username,name=excluded.name,role=excluded.role,enabled=excluded.enabled,regions=excluded.regions,sheets=excluded.sheets,categories=excluded.categories,permissions=excluded.permissions,revision=excluded.revision,salt=excluded.salt,hash=excluded.hash''',
                  (item['id'],item['username'],item['name'],item['role'],int(item['enabled']),packed(item['regions']),packed(item['sheets']),item['categories'],item['permissions'],item['revision'],item['salt'],item['hash']))
                db.execute('UPDATE users SET equipment_scope=? WHERE id=?',(item['equipment_scope'],item['id']))
                if item['id']==u['id'] and item['enabled'] and may_manage_users(item['public']):db.execute('UPDATE sessions SET user_revision=? WHERE token=?',(item['revision'],session['token']))
            db.execute('UPDATE settings SET users_revision=users_revision+1 WHERE id=1')
            return jsonify(users_result(db))
    @app.post('/api/password')
    def change_password():
        value=data()
        if set(value)!={'currentPassword','newPassword'}:fail(400,'فقط تغییر رمز حساب جاری مجاز است.')
        with transaction() as db:
            u,session=user_and_session(db);old=db.execute('SELECT * FROM users WHERE id=?',(u['id'],)).fetchone()
            _,hashed=credentials(value['currentPassword'],old['salt'])
            if not hmac.compare_digest(hashed,old['hash']):fail(403,'رمز فعلی نادرست است.')
            salt,digest=credentials(value['newPassword']);rev=str(uuid.uuid4())
            db.execute('UPDATE users SET salt=?,hash=?,revision=? WHERE id=?',(salt,digest,rev,u['id']))
            db.execute('UPDATE sessions SET user_revision=? WHERE token=?',(rev,session['token']))
            db.execute('UPDATE settings SET users_revision=users_revision+1 WHERE id=1')
            return jsonify(user=public_user(db.execute('SELECT * FROM users WHERE id=?',(u['id'],)).fetchone()))

    @app.post('/api/history/clear')
    def clear_history():
        body=data()
        if body!={'confirm':True}:fail(400,'تأیید پاک‌سازی لازم است.')
        with transaction() as db:
            u,_=user_and_session(db)
            if not ((has_permission(u,'clear-history') and has_permission(u,'view-history')) if is_custom_user(u) else u['role']==1):fail(403,'مجوز پاک‌سازی تاریخچه ندارید.')
            revision=db.execute('SELECT revision FROM state WHERE id=1').fetchone()[0]
            db.execute('UPDATE settings SET history_floor=? WHERE id=1',(revision,))
            return jsonify(ok=True)

    eq_inventory.register(app,connect,transaction,user_and_session,data,fail,packed)

    def page_session():
        with connect() as db:
            try:user_and_session(db)
            except Problem:return False
        return True

    if register_equipment_ops is not None:
        register_equipment_ops(app, data=data, fail=fail, allowed=equipment_allowed)
    return app

if __name__=='__main__':
    from waitress import serve
    serve(create_app(),host=os.environ.get('FAM_BIND','127.0.0.1'),port=int(os.environ.get('FAM_PORT','8765')),threads=16,max_request_body_size=32*1024*1024)
