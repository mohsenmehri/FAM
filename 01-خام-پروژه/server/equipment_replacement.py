"""Explicit, port-scoped MAC replacement. No IP allocation, clear-all or CLI input.

Preflight and application re-read the switch. Writes are split by verification
boundaries. Failure after the first write attempts a bounded, shutdown-only
compensation; loss of transport is UNCERTAIN, never success or automatic retry.
Old configured/sticky secure addresses require an operator; not silently erased.
"""
import hashlib
import ipaddress
import json
import re
import time

try:
    from . import equipment_diagnostics as d
except ImportError:
    import equipment_diagnostics as d

ACCESS = re.compile(r'Fa0/(?:[1-9]|1[0-9]|2[0-4])\Z')
HASH = re.compile(r'[a-f0-9]{64}\Z')


def interface(value):
    if not isinstance(value, str) or not ACCESS.fullmatch(value):raise ValueError('port')
    return value


def reads(port, static):
    interface(port)
    return ('show running-config interface FastEthernet'+port[2:],
            'show ip source binding', 'show port-security address',
            'show mac address-table interface '+port, 'show interfaces status',
            *(('show running-config | section ^arp access-list Inspection$',) if static else ()))


def blocks(output, commands):
    if (not isinstance(output,str) or len(output)>524288 or '--More--' in output or
            re.search(r'[\x00-\x08\x0b-\x1f\x7f\u202a-\u202e\u2066-\u2069]',output.replace('\r\n','\n'))):raise ValueError('output')
    lines=output.replace('\r\n','\n').splitlines(); marks=[]
    for i,line in enumerate(lines):
        echo=re.fullmatch(r'[^\s#>]{1,64}[#>]\s*(.+)',line.strip())
        if echo and echo[1] not in (*commands,'exit','terminal length 0'):raise ValueError('unexpected command')
        for cmd in (*commands,'exit'):
            if re.fullmatch(r'[^\s#>]{1,64}[#>]\s*'+re.escape(cmd),line.strip()):marks.append((i,cmd))
    if [c for _,c in marks]!=[*commands,'exit']:raise ValueError('boundaries')
    result=[]
    for i in range(len(commands)):
        text='\n'.join(lines[marks[i][0]+1:marks[i+1][0]])
        if re.search(r'^\s*%\s+\S',text,re.M):raise ValueError('CLI')
        result.append(text)
    return result


def config(text, port, *, protected=True, allow_shutdown=False, allowed_mac=''):
    lines=[s.strip() for s in text.splitlines() if s.strip()]
    if lines.count('interface FastEthernet'+port[2:])!=1 or lines.count('end')!=1:raise ValueError('config')
    start=lines.index('interface FastEthernet'+port[2:]); end=lines.index('end')
    if end<=start:raise ValueError('config')
    cfg=[s for s in lines[start+1:end] if s!='!']
    if any(s.startswith('interface ') for s in cfg):raise ValueError('config')
    required={'switchport mode access','switchport access vlan 100','switchport port-security'}
    if not required.issubset(cfg):raise ValueError('access config')
    verify=[s for s in cfg if s.startswith('ip verify source')]
    if verify!=(['ip verify source port-security'] if protected else []):raise ValueError('IPSG')
    if ('shutdown' in cfg) != allow_shutdown:raise ValueError('shutdown')
    for s in cfg:
        if s.startswith(('switchport voice','switchport trunk','channel-group','authentication ','dot1x ','switchport protected')):raise ValueError('shared port')
        if s.startswith('switchport port-security maximum') and s!='switchport port-security maximum 1':raise ValueError('multiple clients')
        if s.startswith('switchport port-security violation') and s!='switchport port-security violation shutdown':raise ValueError('violation mode')
        if s.startswith('switchport port-security mac-address '):
            if s=='switchport port-security mac-address sticky':continue
            m=re.fullmatch(r'switchport port-security mac-address (?:sticky )?('+d.MAC+r')',s,re.I)
            if not m or not (d.mac(m[1])==allowed_mac or (allowed_mac=='learning' and s.startswith('switchport port-security mac-address sticky '))):raise ValueError('configured_secure_mac')
    return cfg


def arp_rows(text):
    lines=[s.strip() for s in text.splitlines() if s.strip() and s.strip()!='!']
    if not lines or lines.pop(0)!='arp access-list Inspection':raise ValueError('ACL')
    result=[]
    for line in lines:
        m=re.fullmatch(r'permit ip host ([0-9.]{7,15}) mac host ('+d.MAC+r')',line,re.I)
        if not m:raise ValueError('complex ACL')
        result.append((str(ipaddress.IPv4Address(m[1])),d.mac(m[2])))
    if len(result)>4096 or len(result)!=len(set(result)):raise ValueError('ACL')
    return result


def cam_rows(text, port):
    # Secure addresses can be represented as STATIC in the CAM table.
    text=re.sub(r'\bSTATIC\b','DYNAMIC',text,flags=re.I)
    rows=d.table('mac',text,all_vlans=True)
    if any(r['interface']!=port or r['vlan']!=100 for r in rows):raise ValueError('CAM scope')
    return rows


def snapshot(output, port, static, *, protected=True, shutdown=False, allowed_mac=''):
    if __package__:from . import equipment_probe as p
    else:import equipment_probe as p
    b=blocks(output,reads(port,static))
    cfg=config(b[0],port,protected=protected,allow_shutdown=shutdown,allowed_mac=allowed_mac)
    binding=d.table('bindings',b[1],all_vlans=True);secure=d.table('secure',b[2],all_vlans=True);cam=cam_rows(b[3],port)
    table=p.validate_status_output(b[4]);state=[r for r in p._table_rows(table) if r[0]==port]
    if len(state)!=1 or state[0][2].lower() not in {'connected','notconnect','err-disabled','disabled'}:raise ValueError('status')
    if shutdown and state[0][2].lower()!='disabled':raise ValueError('shutdown not verified')
    acl=arp_rows(b[5]) if static else []
    return {'config':cfg,'bindings':binding,'secure':secure,'cam':cam,'state':state[0][2].lower(),'acl':acl}


def plan_from(s, port, static):
    entries=[r for r in s['bindings'] if r['interface']==port]
    if static:
        if len(entries)!=1 or entries[0]['kind']!='static' or entries[0]['vlan']!=100:raise ValueError('one_static_binding_required')
        old=entries[0];ip=old['ip'];mac=old['mac']
        if len([r for r in s['bindings'] if r['ip']==ip or r['mac']==mac])!=1:raise ValueError('shared_binding')
        if [r for r in s['acl'] if r[0]==ip or r[1]==mac]!=[(ip,mac)]:raise ValueError('matching_acl_required')
    else:
        if any(r['kind']=='static' for r in entries):raise ValueError('static_checkbox_required')
        ip=''; addresses={r['mac'] for r in s['secure'] if r['interface']==port}
        if len(addresses)>1:raise ValueError('multiple clients')
        mac=next(iter(addresses),'')
    local=[r for r in s['secure'] if r['interface']==port]
    if len(local)>1 or any(r['vlan']!=100 for r in local):raise ValueError('multiple clients/VLANs')
    if mac and any(r['mac']==mac and r['interface']!=port for r in s['secure']):raise ValueError('MAC elsewhere')
    if any(r['interface']==port and r['kind']!='securedynamic' for r in s['secure']):raise ValueError('configured_secure_mac')
    if s['state']=='disabled':raise ValueError('admin down')
    # Fingerprint actual config/ACL/bindings (not volatile MAC/counters/status).
    stable={'config':s['config'],'bindings':s['bindings'],'acl':s['acl']}
    digest=hashlib.sha256(json.dumps(stable,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return validate_plan({'interface':port,'staticIp':static,'ip':ip,'oldMac':mac,'planHash':digest,'vlan':100,'acl':'Inspection' if static else ''})


def unicast(value):
    address=d.mac(value)
    if address=='0000.0000.0000' or int(address[:2],16)&1:raise ValueError('MAC')
    return address


def validate_plan(value):
    if not isinstance(value,dict) or set(value)!={'interface','staticIp','ip','oldMac','planHash','vlan','acl'}:raise ValueError('plan')
    interface(value['interface'])
    if type(value['staticIp']) is not bool or type(value['vlan']) is not int or value['vlan']!=100 or not isinstance(value['planHash'],str) or not HASH.fullmatch(value['planHash']):raise ValueError('plan')
    if value['oldMac'] and unicast(value['oldMac'])!=value['oldMac']:raise ValueError('MAC')
    if value['staticIp']:
        if not value['oldMac'] or str(ipaddress.IPv4Address(value['ip']))!=value['ip'] or value['acl']!='Inspection':raise ValueError('IP')
    elif value['ip']!='' or value['acl']!='':raise ValueError('plan')
    return value


def binding(plan, mac):
    validate_plan(plan);unicast(mac)
    return f"ip source binding {mac} vlan 100 {plan['ip']} interface {plan['interface']}"


def permit(plan, mac):
    validate_plan(plan);unicast(mac)
    return f"permit ip host {plan['ip']} mac host {mac}"


def commands(plan, stage, new_mac=''):
    validate_plan(plan);port=plan['interface'];static=plan['staticIp']
    head=['terminal length 0','configure terminal','interface '+port,'shutdown']
    tail=['end','exit']
    if stage=='open':
        body=['no ip verify source','exit']
        if static:body+=['no '+binding(plan,plan['oldMac']),'arp access-list Inspection','no '+permit(plan,plan['oldMac']),'exit']
        return tuple(head+body+tail)
    if stage=='protect' or stage=='quarantine':
        mac=unicast(new_mac) if stage=='protect' else plan['oldMac']
        body=['exit']
        if static:
            if stage=='quarantine' and new_mac and new_mac!=mac:
                body+=['no '+binding(plan,unicast(new_mac)),'arp access-list Inspection','no '+permit(plan,new_mac),'exit']
            body+=[binding(plan,mac),'arp access-list Inspection',permit(plan,mac),'exit']
        body+=['interface '+port,'ip verify source port-security']
        return tuple(head+body+tail)
    if stage=='up':return ('terminal length 0','configure terminal','interface '+port,'no shutdown','end','exit')
    raise ValueError('stage')


def run(job, apply=False):
    if __package__:from . import equipment_probe as p
    else:import equipment_probe as p
    port=interface(job['interface']);static=job['staticIp'];changed=False;new='';plan=None
    workdir=p.runtime_directory();askpass=None
    # Leave 30 seconds of the overall 150 second helper for protective cleanup.
    active=p.Deadline(115 if apply else 65);overall=p.Deadline(150 if apply else 70)
    try:
        askpass=p.prepare_askpass(workdir);job={**job,'_askpass':(askpass,workdir)}
        try:d.profile(p.session_output(job,('terminal length 0','show version','exit'),active))
        except ValueError:raise p.ProbeError('unsupported_platform') from None
        def read(deadline=active, **kwargs):
            return snapshot(p.session_output(job,('terminal length 0',*reads(port,static),'exit'),deadline,25),port,static,**kwargs)
        def write(cmds,deadline=active):
            out=p.session_output(job,cmds,deadline,15)
            # Require echo of every command in order, not just an exit status.
            echoed=[]
            for line in out.replace('\r\n','\n').splitlines():
                m=re.fullmatch(r'[^\s#>]{1,96}[#>]\s*(.*)',line.strip())
                if m and m[1] in cmds:echoed.append(m[1])
            if p.cli_errors(out) or echoed!=list(cmds):raise ValueError('write not verified')
        try:
            s=read();plan=plan_from(s,port,static)
        except ValueError as e:
            raise p.ProbeError('replacement_sticky' if str(e)=='configured_secure_mac' else 'replacement_preflight') from None
        if not apply:return {'ok':True,'plan':plan}
        if plan['planHash']!=job['planHash']:raise p.ProbeError('replacement_changed')
        changed=True;write(commands(plan,'open'))
        opened=read(protected=False,shutdown=True)
        if any(r['interface']==port and r['kind']=='static' for r in opened['bindings']):raise ValueError('binding remains')
        if static and (plan['ip'],plan['oldMac']) in opened['acl']:raise ValueError('ACL remains')
        write(commands(plan,'up'))
        # At most one error recovery; no assumption that an err-disable MUST occur.
        recovered=False
        for attempt in range(4):
            if attempt:time.sleep(2)
            current=read(protected=False,allowed_mac='learning')
            if current['state']=='err-disabled':
                if recovered:raise ValueError('repeated violation')
                recovered=True;write(p.recovery_commands(port));continue
            seen={r['mac'] for r in current['cam']}
            secure={r['mac'] for r in current['secure'] if r['interface']==port}
            if any(r['interface']==port and r['vlan']!=100 for r in current['secure']):raise ValueError('multiple VLANs')
            if len(current['cam'])>1 or len([r for r in current['secure'] if r['interface']==port])>1:raise ValueError('multiple clients')
            if len(seen)==1 and seen==secure:
                candidate=unicast(next(iter(seen)))
                if candidate!=plan['oldMac']:
                    if any(r['mac']==candidate and r['interface']!=port for r in current['secure']):raise ValueError('MAC elsewhere')
                    if any((r['mac']==candidate and (static or r['interface']!=port or r['kind']=='static')) or (static and r['ip']==plan['ip']) for r in current['bindings']):raise ValueError('binding conflict')
                    new=candidate;break
        if not new:raise ValueError('new MAC not learned')
        write(commands(plan,'protect',new))
        protected=read(shutdown=True,allowed_mac=new)
        if static:
            entries=[r for r in protected['bindings'] if r['interface']==port or r['ip']==plan['ip'] or r['mac']==new]
            if entries!=[{'mac':new,'ip':plan['ip'],'kind':'static','vlan':100,'interface':port}]:raise ValueError('binding verification')
            if [r for r in protected['acl'] if r[0]==plan['ip']]!=[(plan['ip'],new)]:raise ValueError('ACL verification')
        write(commands(plan,'up'))
        final=read(allowed_mac=new)
        if final['state']!='connected' or len(final['cam'])!=1 or {r['mac'] for r in final['cam']}!={new}:raise ValueError('final link')
        local=[r for r in final['secure'] if r['interface']==port]
        if len(local)!=1 or local[0]['mac']!=new or local[0]['vlan']!=100:raise ValueError('final secure MAC')
        if static and (final['bindings']!=protected['bindings'] or final['acl']!=protected['acl']):raise ValueError('concurrent change')
        return {'ok':True,'replacement':'replaced','interface':port,'staticIp':static,'ip':plan['ip'],'oldMac':plan['oldMac'],'newMac':new,'protectionRestored':True}
    except Exception:
        if changed:
            # Never re-open on failure. Recreate old IP/MAC policy if reachable.
            try:
                write(commands(plan,'quarantine',new),overall)
                read(overall,shutdown=True,allowed_mac=new)
            except Exception:raise p.ProbeError('replacement_uncertain') from None
            raise p.ProbeError('replacement_quarantined') from None
        raise
    finally:p._cleanup_runtime(workdir,askpass)
