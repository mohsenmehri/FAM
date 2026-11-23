"""Central equipment metadata, never device configuration or credentials.
Strict validation + current-session scopes + revision-checked atomic merges.
Demo jobs remain RAM-only in the client; the existing SSH helper is separate.
"""
import hashlib
import copy
import ipaddress
import json
import re
from flask import jsonify

FIELDS={'types':'typeId','models':'modelId','regions':'regionId','siteKinds':'siteKindId','sites':'siteId'}
OPS={'equipment-operations','equipment-add','equipment-edit','equipment-delete','equipment-catalog','equipment-cards','equipment-import','equipment-export','equipment-configuration','equipment-standards','equipment-audit','equipment-scan','equipment-repair'}
DEFAULT_INVENTORY = {"version":3,"catalog":{"types":[{"id":"type-router","name":"روتر","kind":"router"},{"id":"type-switch","name":"سوئیچ","kind":"switch"}],"models":[{"id":"model-1841","name":"1841","typeId":"type-router"},{"id":"model-1300","name":"1300","typeId":"type-router"},{"id":"model-2960","name":"2960","typeId":"type-switch"}],"regions":[{"id":"region-1","name":"منطقه 1"},{"id":"region-2","name":"منطقه 2"},{"id":"region-3","name":"منطقه 3"},{"id":"region-4","name":"منطقه 4"}],"siteKinds":[{"id":"kind-branch","name":"شعبه","kind":"branch"},{"id":"kind-building","name":"ساختمان اداره","kind":"building"},{"id":"kind-datacenter","name":"دیتا سنتر","kind":"datacenter"},{"id":"kind-area","name":"حوزه","kind":"other"},{"id":"kind-other","name":"انبار و غیره","kind":"other"}],"sites":[{"id":"building-0","name":"ساختمان مرکزی رضوان","siteKindId":"kind-building"},{"id":"building-1","name":"ساختمان 68 شرقی فام","siteKindId":"kind-building"},{"id":"building-2","name":"ساختمان 68 شرقی ملل","siteKindId":"kind-building"},{"id":"building-3","name":"ساختمان 68 شرقی شرکت ها","siteKindId":"kind-building"},{"id":"building-4","name":"ساختمان مرکزی فام","siteKindId":"kind-building"},{"id":"building-5","name":"ساختمان ملاصدرا فام","siteKindId":"kind-building"},{"id":"datacenter-0","name":"تهران","siteKindId":"kind-datacenter"},{"id":"datacenter-1","name":"سمنان","siteKindId":"kind-datacenter"}]},"nodes":[]}

def scope(value):
    if not isinstance(value,dict) or set(value)!=set(FIELDS):raise ValueError('scope')
    out={}
    for key in FIELDS:
        values=value[key]
        if not isinstance(values,list) or len(values)>2001 or any(not isinstance(x,str) or not (x=='*' or re.fullmatch(r'[\w-]{1,80}',x,flags=re.ASCII)) for x in values):raise ValueError('scope')
        out[key]=list(dict.fromkeys(values))
    return out

def policy(user,stored=None):
    legacy=not isinstance(user.get('permissions'),list)
    entry=user.get('role',4)<=2 if legacy else bool({'equipment-operations','manage-users'} & set(user['permissions']))
    if stored is None:
        permissions=set(OPS) if entry else set()
        if not legacy:permissions|=set(user['permissions'])
        if (user.get('role')==1 if legacy else 'manage-users' in user.get('permissions',[])):permissions.add('clear-history')
        scopes={k:['*'] if entry else [] for k in FIELDS}
    else:
        scopes=scope(stored);permissions=set(user.get('permissions',[])) if not legacy else (set(OPS) if entry else set())
    return permissions,scopes

def permitted(user,operation='equipment-operations'):
    permissions=set(user.get('permissions',[]))
    if not isinstance(user.get('permissions'),list):return user.get('role',4)<=2 and operation in OPS
    return bool({'equipment-operations','manage-users'} & permissions) and (operation=='equipment-operations' or operation in permissions)

def ref(user,key,ident):
    values=user.get('equipmentScope',{}).get(key,[])
    return '*' in values or ident is not None and ident in values

def node_allowed(user,node):return all(ref(user,key,node.get(field)) for key,field in FIELDS.items())

def inventory(value):
    if not isinstance(value,dict) or set(value)!={'version','catalog','nodes'} or value.get('version')!=3 or not isinstance(value.get('catalog'),dict) or set(value['catalog'])!=set(FIELDS) or not isinstance(value.get('nodes'),list) or len(value['nodes'])>4000:raise ValueError('inventory')
    ids=set();out={'version':3,'catalog':{},'nodes':[]}
    def identity(item,allowed):
        if not isinstance(item,dict) or set(item)-allowed:raise ValueError('fields')
        ident=item.get('id');name=item.get('name')
        if not isinstance(ident,str) or not re.fullmatch(r'[\w-]{1,80}',ident,flags=re.ASCII) or ident in ids or len(ids)>=12000 or not isinstance(name,str) or not 1<=len(name.strip())<=80 or re.search(r'[\x00-\x1f\x7f]',name):raise ValueError('identity')
        ids.add(ident);return {'id':ident,'name':name.strip()}
    for key in FIELDS:
        items=value['catalog'][key]
        if not isinstance(items,list) or len(items)>2000:raise ValueError('catalog')
        clean=[];names=set()
        for item in items:
            extra={'kind'} if key in ('types','siteKinds') else {'typeId'} if key=='models' else {'siteKindId'} if key=='sites' else set()
            row=identity(item,{'id','name'}|extra)
            if key in ('types','siteKinds'):
                if item.get('kind') not in (('router','switch','other') if key=='types' else ('branch','building','datacenter','other')):raise ValueError('kind')
                row['kind']=item['kind']
            if key in ('models','sites'):
                field,parent=('typeId','types') if key=='models' else ('siteKindId','siteKinds')
                if item.get(field) not in {x['id'] for x in out['catalog'][parent]}:raise ValueError('parent')
                row[field]=item[field]
            unique=(row.get('typeId',row.get('siteKindId','')),row['name'])
            if unique in names:raise ValueError('duplicate')
            names.add(unique);clean.append(row)
        out['catalog'][key]=clean
    lookups={key:{x['id']:x for x in rows} for key,rows in out['catalog'].items()}
    hosts=set()
    for item in value['nodes']:
        row=identity(item,{'id','name','host','legacyPath'}|set(FIELDS.values()))
        host=item.get('host')
        if not isinstance(host,str):raise ValueError('host')
        ip=ipaddress.ip_address(host)
        if ip.version!=4 or str(ip)!=host or not any(ip in ipaddress.ip_network(n) for n in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16','100.64.0.0/10')):raise ValueError('host')
        if host in hosts:raise ValueError('duplicate host')
        hosts.add(host);row['host']=host
        for key,field in FIELDS.items():
            ident=item.get(field)
            if field not in item or ident is not None and ident not in lookups[key]:raise ValueError('reference')
            row[field]=ident
        if row['modelId'] and lookups['models'][row['modelId']]['typeId']!=row['typeId'] or row['siteId'] and lookups['sites'][row['siteId']]['siteKindId']!=row['siteKindId']:raise ValueError('parent')
        if 'legacyPath' in item:
            if not isinstance(item['legacyPath'],str) or len(item['legacyPath'])>300 or re.search(r'[\x00-\x1f\x7f]',item['legacyPath']):raise ValueError('legacy')
            row['legacyPath']=item['legacyPath']
        out['nodes'].append(row)
    return out

def view(user,value):
    out=copy.deepcopy(value)
    for key in FIELDS:out['catalog'][key]=[x for x in out['catalog'][key] if ref(user,key,x['id']) and (key!='models' or ref(user,'types',x['typeId'])) and (key!='sites' or ref(user,'siteKinds',x['siteKindId']))]
    out['nodes']=[n for n in out['nodes'] if node_allowed(user,n)]
    return out

def merge(user,old,next_value,fail):
    before=view(user,old);next_value=inventory(next_value);out=copy.deepcopy(old)
    for key in ('nodes',*FIELDS):
        a=before['nodes'] if key=='nodes' else before['catalog'][key];b=next_value['nodes'] if key=='nodes' else next_value['catalog'][key];whole=out['nodes'] if key=='nodes' else out['catalog'][key]
        aa={x['id']:x for x in a};bb={x['id']:x for x in b}
        for ident in aa.keys()|bb.keys():
            x,y=aa.get(ident),bb.get(ident)
            if x==y:continue
            if not x and any(z['id']==ident for z in whole):fail(403,'رکورد خارج از محدوده است.')
            operation=('equipment-add' if x is None else 'equipment-delete' if y is None else 'equipment-edit') if key=='nodes' else 'equipment-catalog'
            if not permitted(user,operation):fail(403,'مجوز تغییر تجهیزات ندارید.')
            if key=='nodes':
                if x and not node_allowed(user,x) or y and not node_allowed(user,y):fail(403,'تجهیز خارج از محدوده است.')
                if y and any(z['id']!=ident and z['host']==y['host'] for z in old['nodes']):fail(400,'IP در کل موجودی تکراری است.')
            elif not ref(user,key,ident) or y and key=='models' and not ref(user,'types',y['typeId']) or y and key=='sites' and not ref(user,'siteKinds',y['siteKindId']):fail(403,'دسته خارج از محدوده است.')
            whole[:]=[z for z in whole if z['id']!=ident]
            if y:whole.append(y)
    return inventory(out)

def standards(value):
    if not isinstance(value,dict) or set(value)!={'version','items'} or value.get('version')!=1 or not isinstance(value.get('items'),list) or len(value['items'])>100:raise ValueError('standards')
    ids=set();total=0
    def ident(x):
        if not isinstance(x,str) or not re.fullmatch(r'[\w-]{1,80}',x,flags=re.ASCII) or x in ids:raise ValueError('id')
        ids.add(x)
    def text(x,limit):
        if not isinstance(x,str) or not 1<=len(x.strip())<=limit or re.search(r'[\x00-\x1f\x7f\u202a-\u202e\u2066-\u2069]',x) or re.search(r'\b(?:password|secret|community|key-string|token)\s+\S+|BEGIN[^\n]*PRIVATE KEY|(?:radius|tacacs)[^\n]*\bkey\s+\S+',x,re.I):raise ValueError('sensitive')
    for s in value['items']:
        if not isinstance(s,dict) or set(s)!={'id','name','modelId','siteKindId','siteId','checks'}:raise ValueError('standard')
        ident(s['id']);text(s['name'],80)
        for field in ('modelId','siteKindId','siteId'):
            if s[field] is None and field!='modelId':continue
            if not isinstance(s[field],str) or not re.fullmatch(r'[\w-]{1,80}',s[field],flags=re.ASCII):raise ValueError('ref')
        if not isinstance(s['checks'],list) or not 1<=len(s['checks'])<=50:raise ValueError('checks')
        for check in s['checks']:
            if not isinstance(check,dict) or set(check)!={'id','name','operator','pattern'} or check['operator'] not in ('contains','not-contains','exact-line'):raise ValueError('check')
            ident(check['id']);text(check['name'],80);text(check['pattern'],300);total+=1
            if total>1000:raise ValueError('checks')
    return copy.deepcopy(value)

def policy_visible(user,s,allowed):return s['modelId'] in {m['id'] for m in allowed['catalog']['models']} and (not s['siteKindId'] or s['siteKindId'] in {x['id'] for x in allowed['catalog']['siteKinds']}) and (not s['siteId'] or s['siteId'] in {x['id'] for x in allowed['catalog']['sites']})

def cards(value):
    if not isinstance(value,dict) or set(value)!={'version','cards'} or value.get('version')!=1 or not isinstance(value.get('cards'),list) or len(value['cards'])>60:raise ValueError('cards')
    ids=set()
    for c in value['cards']:
        if not isinstance(c,dict) or set(c)!={'id','name','facet','refId'} or c['facet'] not in ('types','models','regions','siteKinds','buildings','datacenters') or not isinstance(c['id'],str) or not re.fullmatch(r'[\w-]{1,80}',c['id'],flags=re.ASCII) or c['id'] in ids or not isinstance(c['name'],str) or not 1<=len(c['name'].strip())<=80 or re.search(r'[\x00-\x1f\x7f]',c['name']) or c['refId'] is not None and (not isinstance(c['refId'],str) or not re.fullmatch(r'[\w-]{1,80}',c['refId'],flags=re.ASCII)):raise ValueError('card')
        ids.add(c['id'])
    return copy.deepcopy(value)

def card_visible(user,c,allowed):return c['refId'] is None or c['refId'] in {x['id'] for x in allowed['catalog']['sites' if c['facet'] in ('buildings','datacenters') else c['facet']]}

def register(app,connect,transaction,session,data,fail,packed):
    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS equipment_state(id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL, payload TEXT NOT NULL)')
        default={'inventory':DEFAULT_INVENTORY,'standards':{'version':1,'items':[]},'cards':{'version':1,'cards':[{'id':'view-'+k,'name':n,'facet':k,'refId':None} for k,n in [('types','نوع تجهیز'),('models','مدل تجهیز'),('regions','منطقه'),('siteKinds','نوع محل'),('buildings','ساختمان‌ها'),('datacenters','دیتا سنتر')]]}}
        db.execute('INSERT OR IGNORE INTO equipment_state VALUES(1,0,?)',(packed(default),))
    def envelope(user,row):
        d=json.loads(row['payload']);allowed=view(user,d['inventory'])
        return {'revision':row['revision'],'inventory':allowed,'standards':{'version':1,'items':[s for s in d['standards']['items'] if policy_visible(user,s,allowed)]},'cards':{'version':1,'cards':[c for c in d['cards']['cards'] if card_visible(user,c,allowed)]}}
    @app.get('/api/equipment/state')
    def equipment_get():
        with connect() as db:
            db.execute('BEGIN');user,_=session(db)
            if not permitted(user):fail(403,'مجوز ورود به تجهیزات ندارید.')
            return jsonify(envelope(user,db.execute('SELECT * FROM equipment_state WHERE id=1').fetchone()))
    @app.post('/api/equipment/state')
    def equipment_save():
        body=data()
        if not isinstance(body,dict) or set(body)!={'revision','requestId','kind','value'} or type(body['revision'])!=int or not isinstance(body['requestId'],str) or not re.fullmatch(r'[a-f0-9-]{36}',body['requestId']) or body['kind'] not in ('inventory','import','standards','cards'):fail(400,'درخواست تجهیزات نامعتبر است.')
        with transaction() as db:
            user,_=session(db)
            if not permitted(user):fail(403,'مجوز تجهیزات ندارید.')
            receipt_id='equipment:'+body['requestId'];digest=packed(body);receipt=db.execute('SELECT digest,response FROM receipts WHERE user_id=? AND request_id=?',(user['id'],receipt_id)).fetchone()
            if receipt:
                if receipt['digest']!=hashlib.sha256(digest.encode()).hexdigest():fail(409,'شناسهٔ درخواست تکراری است.')
                return jsonify(envelope(user,db.execute('SELECT * FROM equipment_state WHERE id=1').fetchone()))
            row=db.execute('SELECT * FROM equipment_state WHERE id=1').fetchone()
            if row['revision']!=body['revision']:fail(409,'موجودی سرور تغییر کرده؛ صفحه را تازه و تغییر را دوباره بازبینی کنید.')
            old=json.loads(row['payload']);out=copy.deepcopy(old);kind=body['kind'];allowed=view(user,old['inventory'])
            try:
                if kind in ('inventory','import'):
                    if kind=='import' and not permitted(user,'equipment-import'):fail(403,'مجوز ورود اکسل ندارید.')
                    out['inventory']=merge(user,old['inventory'],body['value'],fail)
                    available=out['inventory']['catalog']
                    if any(s['modelId'] not in {x['id'] for x in available['models']} or s['siteKindId'] and s['siteKindId'] not in {x['id'] for x in available['siteKinds']} or s['siteId'] and s['siteId'] not in {x['id'] for x in available['sites']} for s in old['standards']['items']):raise ValueError('standard dependency')
                elif kind=='standards':
                    if not permitted(user,'equipment-standards'):fail(403,'مجوز استاندارد ندارید.')
                    proposed=standards(body['value']);previous={s['id']:s for s in old['standards']['items']};visible={s['id'] for s in previous.values() if policy_visible(user,s,allowed)}
                    if any(s['id'] in previous and s['id'] not in visible or not policy_visible(user,s,allowed) for s in proposed['items']):fail(403,'استاندارد خارج از محدوده است.')
                    models={m['id']:m for m in out['inventory']['catalog']['models']};kinds={k['id'] for k in out['inventory']['catalog']['siteKinds']};sites={s['id']:s for s in out['inventory']['catalog']['sites']}
                    for s in proposed['items']:
                        if s['modelId'] not in models or s['siteKindId'] and s['siteKindId'] not in kinds or s['siteId'] and (s['siteId'] not in sites or sites[s['siteId']]['siteKindId']!=s['siteKindId']):raise ValueError('policy parent')
                    out['standards']={'version':1,'items':[s for s in previous.values() if s['id'] not in visible]+proposed['items']}
                else:
                    if not permitted(user,'equipment-cards'):fail(403,'مجوز کارت‌ها ندارید.')
                    proposed=cards(body['value']);previous={c['id']:c for c in old['cards']['cards']};visible={c['id'] for c in previous.values() if card_visible(user,c,allowed)}
                    if any(not card_visible(user,c,allowed) or c['id'] in previous and c['id'] not in visible for c in proposed['cards']):fail(403,'کارت خارج از محدوده است.')
                    out['cards']={'version':1,'cards':[c for c in previous.values() if c['id'] not in visible]+proposed['cards']}
                # Canonical validation also rejects dependencies on hidden nodes.
                inventory(out['inventory']);standards(out['standards']);cards(out['cards'])
            except (ValueError,TypeError,KeyError,OverflowError):fail(400,'مشخصات، وابستگی یا محتوای تجهیزات معتبر نیست؛ چیزی ثبت نشد.')
            db.execute('UPDATE equipment_state SET revision=revision+1,payload=? WHERE id=1',(packed(out),))
            db.execute('INSERT INTO receipts VALUES(?,?,?,?)',(user['id'],receipt_id,hashlib.sha256(digest.encode()).hexdigest(),'{}'))
            return jsonify(envelope(user,db.execute('SELECT * FROM equipment_state WHERE id=1').fetchone()))
