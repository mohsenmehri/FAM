"""Bounded classic-2960 group repair and port-MAC replacement.

No caller CLI/MAC/IP. A fresh, signed preview binds exact target ports, identities
and each previewed secure-address removal, plus explicit conditional discovery
within the idle-access-VLAN100 relocation policy. Idle old access ports only.
All target shutdowns precede cleanup; all removals are checked before reopening.
No save/enable, blind retry, clear-all or configuration of unrelated ports.
"""
import hashlib
import ipaddress
import json
import re
import time
try:
    from . import equipment_diagnostics as d, equipment_replacement as r
except ImportError:
    import equipment_diagnostics as d, equipment_replacement as r


def interfaces(value):
    if not isinstance(value,list) or not 1<=len(value)<=24:raise ValueError('interfaces')
    for port in value:r.interface(port)
    if len(set(value))!=len(value):raise ValueError('duplicate ports')
    return sorted(value,key=lambda x:int(x[4:]))


def ranges(ports):
    ports=interfaces(ports);spans=[]
    for port in ports:
        value=int(port[4:])
        if spans and value==spans[-1][1]+1:spans[-1][1]=value
        else:spans.append([value,value])
    clauses=['FastEthernet0/'+str(a)+((' - '+str(b)) if a!=b else '') for a,b in spans]
    return ['interface range '+' , '.join(clauses[i:i+5]) for i in range(0,len(clauses),5)]


def port_commands(ports, action):
    if action not in ('shutdown','no shutdown','no ip verify source','ip verify source port-security'):raise ValueError('action')
    return tuple(c for group in ranges(ports) for c in (group,action,'exit'))


def stats(text):
    values={}
    patterns={
        'enabled':r'Port Security\s*:\s*(Enabled|Disabled)',
        'state':r'Port Status\s*:\s*(Secure-up|Secure-down|Secure-shutdown)',
        'mode':r'Violation Mode\s*:\s*(Shutdown|Restrict|Protect)',
        'last':r'Last Source Address:Vlan\s*:\s*('+d.MAC+r'):(\d{1,4})',
        'count':r'Security Violation Count\s*:\s*(\d{1,12})',
    }
    for key,pattern in patterns.items():
        found=re.findall(r'^\s*'+pattern+r'\s*$',text,re.M|re.I)
        if len(found)!=1:raise ValueError('port-security stats')
        values[key]=found[0]
    return {'enabled':values['enabled'].lower()=='enabled','state':values['state'].lower(),
            'mode':values['mode'].lower(),'mac':d.mac(values['last'][0]),'vlan':int(values['last'][1]),'count':int(values['count'])}


def cfg(text, port, secure, *, shutdown=None, protected=None):
    # Reuse strict access/VLAN/max/voice/trunk gate; allow exactly the one
    # configured identity actually present in the independently read secure table.
    local=[s for s in secure if s['interface']==port]
    if len(local)>1 or any(s['vlan']!=100 for s in local):raise ValueError('multi client')
    mac=local[0]['mac'] if local else ''
    is_shutdown=bool(re.search(r'^\s*shutdown\s*$',text,re.M))
    is_protected=bool(re.search(r'^\s*ip verify source port-security\s*$',text,re.M))
    if shutdown is not None and is_shutdown!=shutdown:raise ValueError('admin state')
    if protected is not None and is_protected!=protected:raise ValueError('protection')
    return r.config(text,port,protected=is_protected,allow_shutdown=is_shutdown,allowed_mac=mac)


def read_commands(ports, static):
    ports=interfaces(ports)
    return ('show interfaces status','show port-security address','show ip source binding',
            *(('show running-config | section ^arp access-list Inspection$',) if static else ()),
            *(command for port in ports for command in ('show running-config interface FastEthernet'+port[2:],
                                                        'show port-security interface '+port,
                                                        'show mac address-table interface '+port)))


def snapshot(output, ports, static, *, shutdown=None, protected=None, allow_empty_acl=False):
    if __package__:from . import equipment_probe as p
    else:import equipment_probe as p
    ports=interfaces(ports);blocks=r.blocks(output,read_commands(ports,static));status=p.validate_status_output(blocks[0])
    states={row[0]:row[2].lower() for row in p._table_rows(status)}
    secure=d.table('secure',blocks[1],all_vlans=True);bindings=d.table('bindings',blocks[2],all_vlans=True)
    acl=([] if allow_empty_acl and not blocks[3].strip() else r.arp_rows(blocks[3])) if static else [];offset=4 if static else 3;items={}
    for index,port in enumerate(ports):
        if states.get(port) not in ('connected','notconnect','err-disabled','disabled'):raise ValueError('status')
        if shutdown is True and states[port]!='disabled':raise ValueError('shutdown not verified')
        base=offset+3*index
        items[port]={'config':cfg(blocks[base],port,secure,shutdown=shutdown,protected=protected),
                     'stats':stats(blocks[base+1]),'cam':r.cam_rows(blocks[base+2],port)}
    return {'states':states,'secure':secure,'bindings':bindings,'acl':acl,'items':items}


def cleanup_rows(s, targets, mode, static):
    items=[];removals=[];expected=set()
    for port in targets:
        item=s['items'][port];local=[x for x in s['secure'] if x['interface']==port]
        stat=item['stats'];state=s['states'][port]
        if not stat['enabled'] or stat['mode']!='shutdown' or 'shutdown' in item['config']:raise ValueError('target unavailable')
        if mode=='recover' and state!='err-disabled':raise ValueError('target not errdisabled')
        if mode=='replace' and 'ip verify source port-security' not in item['config']:raise ValueError('IPSG required')
        candidate=''
        if state=='err-disabled' and stat['state']=='secure-shutdown':
            if stat['count']<1 or stat['vlan']!=100:raise ValueError('unknown violating MAC')
            candidate=r.unicast(stat['mac'])
        if candidate:
            if candidate in expected:raise ValueError('duplicate expected MAC')
            expected.add(candidate)
        entries=[b for b in s['bindings'] if b['interface']==port and b['kind']=='static']
        old=local[0]['mac'] if local else '';ip=''
        if mode=='replace' and static:
            if len(entries)!=1 or entries[0]['vlan']!=100:raise ValueError('one static binding required')
            old=entries[0]['mac'];ip=entries[0]['ip'];r.unicast(old)
            if len([b for b in s['bindings'] if b['ip']==ip or b['mac']==old])!=1:raise ValueError('shared binding')
            if [pair for pair in s['acl'] if pair[0]==ip or pair[1]==old]!=[(ip,old)]:raise ValueError('matching ACL required')
        elif mode=='replace' and entries:raise ValueError('static checkbox required')
        if mode=='recover' and candidate and local and local[0]['mac']!=candidate:raise ValueError('occupied target: use replacement')
        if mode=='replace' and local:
            if local[0]['mac']!=old:raise ValueError('local secure/binding conflict')
            removals.append({**local[0],'reason':'target_previous_mac'})
        if candidate:
            matches=[row for row in s['secure'] if row['mac']==candidate]
            if len(matches)>1:raise ValueError('shared MAC')
            if matches and matches[0]['interface']!=port:
                foreign=matches[0]
                if foreign['vlan']!=100 or foreign['interface'] in targets or not r.ACCESS.fullmatch(foreign['interface']):raise ValueError('unsafe old port')
                if any(b['mac']==candidate and b['kind']=='static' for b in s['bindings']):raise ValueError('static binding at old port')
                removals.append({**foreign,'reason':'old_port_conflict'})
        items.append({'interface':port,'ip':ip,'oldMac':old,'expectedMac':candidate})
    if len({(x['interface'],x['mac']) for x in removals})!=len(removals):raise ValueError('duplicate cleanup')
    return items,sorted(removals,key=lambda x:(int(x['interface'][4:]),x['mac']))


def validate_plan(plan):
    if not isinstance(plan,dict) or set(plan)!={'mode','interfaces','staticIp','items','removals','planHash','relocationPolicy'}:raise ValueError('plan')
    if plan['relocationPolicy']!='idle-access-vlan100':raise ValueError('relocation policy')
    ports=interfaces(plan['interfaces'])
    if ports!=plan['interfaces'] or plan['mode'] not in ('recover','replace') or type(plan['staticIp']) is not bool or (plan['mode']=='recover' and plan['staticIp']):raise ValueError('plan')
    if not isinstance(plan['planHash'],str) or not r.HASH.fullmatch(plan['planHash']):raise ValueError('fingerprint')
    if not isinstance(plan['items'],list) or len(plan['items'])!=len(ports):raise ValueError('items')
    for port,item in zip(ports,plan['items']):
        if not isinstance(item,dict) or set(item)!={'interface','ip','oldMac','expectedMac'} or item['interface']!=port:raise ValueError('item')
        for key in ('oldMac','expectedMac'):
            if not isinstance(item[key],str) or (item[key] and r.unicast(item[key])!=item[key]):raise ValueError('MAC')
        if plan['staticIp']:
            if not item['oldMac'] or str(ipaddress.IPv4Address(item['ip']))!=item['ip']:raise ValueError('IP')
        elif item['ip']!='':raise ValueError('IP')
    expected=[x['expectedMac'] for x in plan['items'] if x['expectedMac']]
    if len(set(expected))!=len(expected):raise ValueError('duplicate expected MAC')
    if plan['staticIp'] and (len({x['ip'] for x in plan['items']})!=len(ports) or len({x['oldMac'] for x in plan['items']})!=len(ports)):raise ValueError('shared static identity')
    if not isinstance(plan['removals'],list) or len(plan['removals'])>48:raise ValueError('removals')
    seen=set()
    for row in plan['removals']:
        if not isinstance(row,dict) or set(row)!={'interface','mac','kind','vlan','reason'}:raise ValueError('removal')
        r.interface(row['interface'])
        if r.unicast(row['mac'])!=row['mac'] or type(row['vlan']) is not int or row['vlan']!=100 or row['kind'] not in ('securedynamic','securesticky','secureconfigured'):raise ValueError('removal')
        key=(row['interface'],row['mac'])
        if key in seen:raise ValueError('removal')
        seen.add(key)
        if row['reason']=='target_previous_mac':
            if plan['mode']!='replace' or not any(x['interface']==row['interface'] and x['oldMac']==row['mac'] for x in plan['items']):raise ValueError('target removal')
        elif row['reason']=='old_port_conflict':
            if row['interface'] in ports or not any(x['expectedMac']==row['mac'] for x in plan['items']):raise ValueError('old port removal')
        else:raise ValueError('reason')
    if len({x['mac'] for x in plan['removals']})!=len(plan['removals']):raise ValueError('shared removal MAC')
    return plan


def removals_commands(rows):
    commands=[]
    for row in rows:
        r.interface(row['interface']);r.unicast(row['mac'])
        if row['kind']=='securedynamic':
            # IOS syntax is address OR interface; uniqueness is checked globally.
            commands+=['end','clear port-security dynamic address '+row['mac'],'configure terminal']
        else:
            commands+=['interface '+row['interface'],'no switchport port-security mac-address '+('sticky ' if row['kind']=='securesticky' else '')+row['mac'],'exit']
    return tuple(commands)


def policy_commands(plan, identities, remove=False):
    if not plan['staticIp']:return ()
    output=[]
    for item in plan['items']:
        mac=r.unicast(identities[item['interface']]);ip=str(ipaddress.IPv4Address(item['ip']));r.interface(item['interface'])
        prefix='no ' if remove else ''
        output += [prefix+f"ip source binding {mac} vlan 100 {ip} interface {item['interface']}",
                   'arp access-list Inspection',prefix+f'permit ip host {ip} mac host {mac}','exit']
    return tuple(output)


def verify_removals(s, plan):
    for row in plan['removals']:
        if any(x['interface']==row['interface'] and x['mac']==row['mac'] for x in s['secure']):raise ValueError('secure MAC remains')
        if row['kind']!='securedynamic' and any(re.search(re.escape(row['mac'])+r'$',line,re.I) for line in s['items'][row['interface']]['config']):raise ValueError('configured MAC remains')


def run(job, apply=False):
    if __package__:from . import equipment_probe as p
    else:import equipment_probe as p
    targets=interfaces(job['interfaces']);mode=job['mode'];static=job['staticIp'];changed=False;plan=None;new={};affected=set()
    active=p.Deadline(112 if apply else 95);overall=p.Deadline(150 if apply else 100)
    workdir=p.runtime_directory();askpass=None
    try:
        askpass=p.prepare_askpass(workdir);job={**job,'_askpass':(askpass,workdir)}
        try:d.profile(p.session_output(job,('terminal length 0','show version','exit'),active,15))
        except ValueError:raise p.ProbeError('unsupported_platform') from None
        def read(ports, deadline=active, **options):
            return snapshot(p.session_output(job,('terminal length 0',*read_commands(ports,static),'exit'),deadline,35),ports,static,**options)
        def write(body, deadline=active):
            commands=('terminal length 0','configure terminal',*body,'end','exit')
            out=p.session_output(job,commands,deadline,20);echo=[]
            for line in out.replace('\r\n','\n').splitlines():
                match=re.fullmatch(r'[^\s#>]{1,96}[#>]\s*(.*)',line.strip())
                if match and match[1] in commands:echo.append(match[1])
            if p.cli_errors(out) or echo!=list(commands):raise ValueError('unverified write')
        initial=read(targets,shutdown=False)
        items,removals=cleanup_rows(initial,targets,mode,static)
        all_ports=interfaces(sorted(set(targets)|{x['interface'] for x in removals}))
        old_ports=[port for port in all_ports if port not in targets]
        baseline=read(all_ports) if old_ports else initial
        if old_ports:
            check_items,check_removals=cleanup_rows(baseline,targets,mode,static)
            if (items,removals)!=(check_items,check_removals):raise ValueError('changing evidence')
        for port in old_ports:
            if baseline['states'][port] not in ('notconnect','disabled'):raise p.ProbeError('group_old_port_active')
        stable={'mode':mode,'staticIp':static,'targets':targets,'relocationPolicy':'idle-access-vlan100','items':baseline['items'],
                'secure':baseline['secure'],'bindings':baseline['bindings'],'acl':baseline['acl'],
                'states':{port:baseline['states'][port] for port in all_ports}}
        digest=hashlib.sha256(json.dumps(stable,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        plan=validate_plan({'mode':mode,'interfaces':targets,'staticIp':static,'items':items,'removals':removals,'planHash':digest,'relocationPolicy':'idle-access-vlan100'})
        if not apply:return {'ok':True,'plan':plan}
        if job['planHash']!=digest:raise p.ProbeError('group_changed')
        changed=True;write(port_commands(targets,'shutdown'))
        closed=read(all_ports)
        for port in targets:
            if closed['states'][port]!='disabled' or 'shutdown' not in closed['items'][port]['config']:raise ValueError('shutdown not verified')
        for port in old_ports:
            if closed['states'][port] not in ('notconnect','disabled') or closed['items'][port]['config']!=baseline['items'][port]['config']:raise ValueError('old port changed')
        if [b for b in closed['bindings'] if b['kind']=='static']!=[b for b in baseline['bindings'] if b['kind']=='static'] or closed['acl']!=baseline['acl']:raise ValueError('policy changed before cleanup')
        pending=[]
        for row in removals:
            matches=[x for x in closed['secure'] if x['mac']==row['mac']]
            exact={k:v for k,v in row.items() if k!='reason'}
            if not matches and row['kind']=='securedynamic':continue  # shutdown already aged it out
            if matches!=[exact]:raise ValueError('approved secure identity changed')
            pending.append(row)
        affected.update(row['interface'] for row in pending if row['reason']=='old_port_conflict')
        if pending:write(removals_commands(pending))
        if mode=='replace':
            write((*port_commands(targets,'no ip verify source'),*policy_commands(plan,{x['interface']:x['oldMac'] for x in items},True)))
        cleaned=read(all_ports,allow_empty_acl=True);verify_removals(cleaned,plan)
        for port in targets:
            if cleaned['states'][port]!='disabled' or 'shutdown' not in cleaned['items'][port]['config']:raise ValueError('target reopened')
            if mode=='replace' and any(c.startswith('ip verify source') for c in cleaned['items'][port]['config']):raise ValueError('IPSG remains')
        if static:
            for item in items:
                if any(b['interface']==item['interface'] and b['kind']=='static' for b in cleaned['bindings']) or (item['ip'],item['oldMac']) in cleaned['acl']:raise ValueError('old policy remains')
        if mode=='recover':
            if [b for b in cleaned['bindings'] if b['kind']=='static']!=[b for b in baseline['bindings'] if b['kind']=='static']:raise ValueError('unexpected binding change')
            for port in targets:
                original=[c for c in baseline['items'][port]['config'] if c.startswith('ip verify source')]
                if original!=[c for c in cleaned['items'][port]['config'] if c.startswith('ip verify source')]:raise ValueError('IPSG changed')
        write(port_commands(targets,'no shutdown'))
        if mode=='recover':
            final=read(all_ports)
            rows=[]
            for item in items:
                port=item['interface'];state=final['states'][port]
                if state not in ('connected','notconnect','err-disabled') or 'shutdown' in final['items'][port]['config']:raise ValueError('final status')
                if [c for c in final['items'][port]['config'] if c.startswith('ip verify source')]!=[c for c in baseline['items'][port]['config'] if c.startswith('ip verify source')]:raise ValueError('final IPSG')
                rows.append({**item,'newMac':'','state':'still_errdisabled' if state=='err-disabled' else 'recovered'})
            if [b for b in final['bindings'] if b['kind']=='static']!=[b for b in baseline['bindings'] if b['kind']=='static']:raise ValueError('binding changed')
            return {'ok':True,'mode':mode,'interfaces':targets,'rows':rows,'removed':removals,'protectionRestored':True}
        actual_removals=list(removals);relocated=False
        # Replacement learning is bounded. The first range bounce already clears
        # an initial err-disable; repeated violation is NOT bounced in a loop.
        for attempt in range(4):
            if attempt:time.sleep(2)
            current=read(all_ports,allow_empty_acl=True)
            for port in targets:
                if not current['items'][port]['stats']['enabled'] or current['items'][port]['stats']['mode']!='shutdown':raise ValueError('security state changed')
            errors=[item for item in items if current['states'][item['interface']]=='err-disabled']
            if errors:
                if relocated:raise ValueError('repeated violation after relocation')
                discoveries=[]
                for item in errors:
                    port=item['interface'];st=current['items'][port]['stats'];before=baseline['items'][port]['stats']
                    if st['state']!='secure-shutdown' or st['vlan']!=100 or st['count']<=before['count']:raise ValueError('no fresh violating MAC')
                    mac=r.unicast(st['mac'])
                    if mac==item['oldMac'] or (item['expectedMac'] and mac!=item['expectedMac']):raise ValueError('unapproved identity')
                    matches=[row for row in current['secure'] if row['mac']==mac]
                    if len(matches)!=1:raise ValueError('ambiguous fresh MAC')
                    old=matches[0]
                    if old['vlan']!=100 or old['interface'] in targets or not r.ACCESS.fullmatch(old['interface']):raise ValueError('unsafe fresh old port')
                    if any(b['mac']==mac and b['kind']=='static' for b in current['bindings']):raise ValueError('static binding on discovered old port')
                    discoveries.append({**old,'reason':'old_port_conflict'})
                if len({row['mac'] for row in discoveries})!=len(discoveries):raise ValueError('duplicate discovered identity')
                all_ports=interfaces(sorted(set(all_ports)|{row['interface'] for row in discoveries}))
                fresh=read(all_ports,allow_empty_acl=True)
                for row in discoveries:
                    port=row['interface']
                    if fresh['states'][port] not in ('notconnect','disabled') or [x for x in fresh['secure'] if x['mac']==row['mac']]!=[{k:v for k,v in row.items() if k!='reason'}]:raise ValueError('discovered old port not idle/unique')
                write(port_commands(targets,'shutdown'));closed_fresh=read(all_ports,allow_empty_acl=True)
                for port in targets:
                    if closed_fresh['states'][port]!='disabled' or 'shutdown' not in closed_fresh['items'][port]['config']:raise ValueError('discovery shutdown not verified')
                for row in discoveries:
                    port=row['interface']
                    if closed_fresh['states'][port] not in ('notconnect','disabled') or closed_fresh['items'][port]['config']!=fresh['items'][port]['config'] or [x for x in closed_fresh['secure'] if x['mac']==row['mac']]!=[{k:v for k,v in row.items() if k!='reason'}]:raise ValueError('discovered old port changed')
                    if any(b['mac']==row['mac'] and b['kind']=='static' for b in closed_fresh['bindings']):raise ValueError('discovered static reference')
                affected.update(row['interface'] for row in discoveries)
                write(removals_commands(discoveries));verified=read(all_ports,allow_empty_acl=True)
                verify_removals(verified,{'removals':discoveries})
                for port in targets:
                    if verified['states'][port]!='disabled' or 'shutdown' not in verified['items'][port]['config']:raise ValueError('discovery target reopened')
                actual_removals+=discoveries;write(port_commands(targets,'no shutdown'));relocated=True;new={};continue
            new={}  # Every member must have coherent evidence in this same round.
            for item in items:
                port=item['interface'];local=[x for x in current['secure'] if x['interface']==port];cam=current['items'][port]['cam']
                if current['states'][port]=='err-disabled':raise ValueError('repeated violation; new approval required')
                if len(local)>1 or len(cam)>1:raise ValueError('multiple clients')
                if len(local)==len(cam)==1 and local[0]['mac']==cam[0]['mac']:
                    mac=r.unicast(cam[0]['mac'])
                    if mac==item['oldMac'] or (item['expectedMac'] and mac!=item['expectedMac']):raise ValueError('unexpected MAC')
                    if any(x['mac']==mac and x['interface']!=port for x in current['secure']):raise ValueError('unapproved old port')
                    if any(b['mac']==mac and (static or b['interface']!=port or b['kind']=='static') for b in current['bindings']):raise ValueError('binding conflict')
                    new[port]=mac
            if len(new)==len(targets):break
        if len(new)!=len(targets) or len(set(new.values()))!=len(new):raise ValueError('MAC not learned')
        write(port_commands(targets,'shutdown'))
        write((*policy_commands(plan,new),*port_commands(targets,'ip verify source port-security')))
        protected=read(all_ports)
        for port in targets:
            if protected['states'][port]!='disabled' or 'shutdown' not in protected['items'][port]['config'] or 'ip verify source port-security' not in protected['items'][port]['config']:raise ValueError('protection')
        if static:
            for item in items:
                port=item['interface'];mac=new[port]
                if [b for b in protected['bindings'] if b['interface']==port or b['ip']==item['ip'] or b['mac']==mac]!=[{'interface':port,'mac':mac,'ip':item['ip'],'vlan':100,'kind':'static'}]:raise ValueError('new binding')
                if [pair for pair in protected['acl'] if pair[0]==item['ip']]!=[(item['ip'],mac)]:raise ValueError('new ACL')
        write(port_commands(targets,'no shutdown'));final=read(all_ports)
        for port in targets:
            local=[x for x in final['secure'] if x['interface']==port]
            if final['states'][port]!='connected' or 'shutdown' in final['items'][port]['config'] or 'ip verify source port-security' not in final['items'][port]['config'] or len(local)!=1 or local[0]['mac']!=new[port] or {x['mac'] for x in final['items'][port]['cam']}!={new[port]}:raise ValueError('final verification')
        if static and (final['bindings']!=protected['bindings'] or final['acl']!=protected['acl']):raise ValueError('policy changed')
        return {'ok':True,'mode':mode,'interfaces':targets,'rows':[{**item,'newMac':new[item['interface']],'state':'replaced'} for item in items],'removed':actual_removals,'protectionRestored':True}
    except Exception:
        if changed:
            try:
                body=port_commands(targets,'shutdown')
                if mode=='replace':
                    body+=policy_commands(plan,new,True) if static and len(new)==len(targets) else ()
                    body+=policy_commands(plan,{x['interface']:x['oldMac'] for x in plan['items']})
                    body+=port_commands(targets,'ip verify source port-security')
                write(body,overall);safe=read(targets,overall,shutdown=True,protected=True if mode=='replace' else None)
                if mode=='recover':
                    for port in targets:
                        if [c for c in safe['items'][port]['config'] if c.startswith('ip verify source')]!=[c for c in baseline['items'][port]['config'] if c.startswith('ip verify source')]:raise ValueError('IPSG')
            except Exception:return {'ok':False,'error':'group_uncertain',**({'affectedOldPorts':interfaces(sorted(affected))} if affected else {})}
            return {'ok':False,'error':'group_quarantined',**({'affectedOldPorts':interfaces(sorted(affected))} if affected else {})}
        raise
    finally:p._cleanup_runtime(workdir,askpass)
