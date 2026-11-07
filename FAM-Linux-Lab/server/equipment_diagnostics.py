"""Bounded read-only evidence for the classic branch WS-C2960-24TT-L.

No configuration, raw CLI release, history database or automatic enrollment.
DAI logs are HISTORICAL; bindings/sticky entries are records, not proof of a move.
Unsupported output is unavailable, never healthy. Only VLAN 100 is assessed.
"""
import ipaddress
import re

MODEL = 'WS-C2960-24TT-L'
READS = ('show port-security address', 'show ip source binding',
         'show mac address-table dynamic vlan 100', 'show ip arp inspection log')
SOURCE_IDS = ('secure', 'bindings', 'mac', 'dai')
REASONS = {'mac_table_seen', 'dai_denied_historical', 'binding_port_conflict',
           'binding_mac_conflict', 'secure_mac_conflict'}
MAC = r'[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}'
PORT = r'(?:Fa(?:stEthernet)?0/(?:[1-9]|1[0-9]|2[0-4])|Gi(?:gabitEthernet)?0/[12])'
IOS = r'(?:12\.2|15\.[02])\([0-9]{1,3}\)[A-Za-z0-9.]{0,20}'
IMAGE = r'c2960-[a-zA-Z0-9_.-]{1,110}\.bin'


def mac(value):
    if not isinstance(value, str):raise ValueError('invalid MAC')
    if re.fullmatch(MAC, value):return value.lower()
    if re.fullmatch(r'(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', value):
        compact=re.sub('[:-]', '', value).lower()
        return '.'.join(compact[i:i+4] for i in (0,4,8))
    raise ValueError('invalid MAC')


def port(value):
    if not isinstance(value,str) or not re.fullmatch(PORT,value,re.I):raise ValueError('invalid port')
    return ('Fa' if value.lower().startswith('fa') else 'Gi')+value[value.index('0/'):]


def client(ip, address):
    if not isinstance(ip,str) or not isinstance(address,str):raise ValueError('invalid client')
    ip=ip.strip();address=address.strip()
    if ip:ip=str(ipaddress.IPv4Address(ip))
    if address:address=mac(address)
    if not ip and not address:raise ValueError('client IP or MAC required')
    return {'ip':ip,'mac':address}


def profile(output):
    if not isinstance(output,str) or len(output)>131072:raise ValueError('unsupported platform')
    version=re.search(r'Cisco IOS Software,[^\n]*\bVersion ('+IOS+r')(?:,|\s|$)',output)
    model=re.search(r'^\s*Model number\s*:\s*('+MODEL+r')\s*$',output,re.M|re.I)
    image=re.search(r'^\s*System image file is "(?:flash[0-9]?:/?)?(?:c2960-[a-zA-Z0-9_.-]{1,110}/){0,2}('+IMAGE+r')"\s*$',output,re.M)
    if not all((version,model,image)):raise ValueError('unsupported platform')
    return {'model':MODEL,'ios':version[1],'image':image[1]}


def sections(output):
    if not isinstance(output,str) or len(output)>524288 or re.search(r'[\x00-\x08\x0b-\x1f\x7f\u202a-\u202e\u2066-\u2069]',output.replace('\r\n','\n')) or '--More--' in output:
        raise ValueError('unreadable diagnosis')
    # Exact echoed fixed commands bound each source. No guessed header split.
    lines=output.replace('\r\n','\n').splitlines();marks=[]
    for i,line in enumerate(lines):
        for command in (*READS,'exit'):
            if re.fullmatch(r'[^\s#>]{1,64}[#>]\s*'+re.escape(command),line.strip()):marks.append((i,command))
    if [command for _,command in marks]!=[*READS,'exit']:raise ValueError('missing command boundaries')
    return {name:'\n'.join(lines[marks[i][0]+1:marks[i+1][0]]) for i,name in enumerate(SOURCE_IDS)}


def table(kind, text, *, all_vlans=False):
    """All-or-unavailable per source, with strict schemas and bounded rows."""
    rows=[];header=False
    for line in text.splitlines():
        line=line.strip()
        if not line or re.fullmatch(r'[-= ]+',line):continue
        if re.fullmatch(r'[^\s#>]{1,64}[#>]',line):continue
        if line.startswith('%') or '--More--' in line:raise ValueError('unavailable source')
        normalized=' '.join(line.split()).lower()
        if kind=='secure' and normalized in {'secure mac address table','vlan mac address type ports remaining age','vlan mac address type ports remaining age (mins)','(mins)'}:
            if normalized.startswith('vlan '):header=True
            continue
        if kind=='bindings' and re.fullmatch(r'macaddress ipaddress lease\(sec\) type vlan interface',normalized):header=True;continue
        if kind=='mac' and normalized in {'mac address table','vlan mac address type ports'}:
            if normalized.startswith('vlan '):header=True
            continue
        if kind=='dai' and normalized=='interface vlan sender mac sender ip num pkts reason time':header=True;continue
        if re.fullmatch(r'(?:Total (?:number of bindings|Mac Addresses for this criterion)|Total Addresses in System(?: \(excluding one mac per port\))?|Max Addresses limit in System)\s*:\s*\d+',line,re.I):continue
        if kind=='dai' and re.fullmatch(r'(?:Total Log Buffer Size\s*:\s*\d+|Syslog rate\s*:\s*\d+ entries per \d+ seconds\.)',line,re.I):continue
        if not header:raise ValueError('missing table header')
        if kind=='secure':
            match=re.fullmatch(r'(\d{1,4})\s+('+MAC+r')\s+(SecureSticky|SecureDynamic|SecureConfigured)\s+('+PORT+r')\s+(?:-|\d+)',line,re.I)
            if not match:raise ValueError('bad secure row')
            row={'vlan':int(match[1]),'mac':mac(match[2]),'interface':port(match[4]),'kind':match[3].lower()}
        elif kind=='bindings':
            match=re.fullmatch(r'('+MAC+r')\s+([0-9.]{7,15})\s+(?:infinite|\d+)\s+(static|dhcp-snooping)\s+(\d{1,4})\s+('+PORT+r')',line,re.I)
            if not match:raise ValueError('bad binding row')
            row={'mac':mac(match[1]),'ip':str(ipaddress.IPv4Address(match[2])),'kind':match[3].lower(),'vlan':int(match[4]),'interface':port(match[5])}
        elif kind=='mac':
            match=re.fullmatch(r'(\d{1,4})\s+('+MAC+r')\s+DYNAMIC\s+('+PORT+r')',line,re.I)
            if not match:raise ValueError('bad MAC row')
            row={'vlan':int(match[1]),'mac':mac(match[2]),'interface':port(match[3])}
        else:
            match=re.fullmatch(r'('+PORT+r')\s+(\d{1,4})\s+('+MAC+r')\s+([0-9.]{7,15})\s+\d+\s+(ACL Deny|DHCP Deny|ACL Permit|DHCP Permit|Probe Permit)\s+\d{2}:\d{2}:\d{2}(?: [A-Za-z0-9 :.+-]{1,64})?',line,re.I)
            if not match:raise ValueError('bad DAI row')
            row={'interface':port(match[1]),'vlan':int(match[2]),'mac':mac(match[3]),'ip':str(ipaddress.IPv4Address(match[4])),'denied':match[5].lower().endswith('deny')}
        if not 1<=row['vlan']<=4094:raise ValueError('bad VLAN')
        rows.append(row)
        if len(rows)>4096:raise ValueError('too many rows')
    if not header:raise ValueError('missing table header')
    return rows if all_vlans else [r for r in rows if r['vlan']==100]


def assess(hardware, target, output):
    blocks=sections(output);tables={};sources=[]
    for kind in SOURCE_IDS:
        try:
            tables[kind]=table(kind,blocks[kind]);sources.append({'id':kind,'state':'parsed','count':len(tables[kind])})
        except ValueError:
            tables[kind]=[];sources.append({'id':kind,'state':'unavailable','count':0})
    bindings=[r for r in tables['bindings'] if (target['ip'] and r['ip']==target['ip']) or (target['mac'] and r['mac']==target['mac'])]
    denied=[r for r in tables['dai'] if r['denied'] and ((target['ip'] and r['ip']==target['ip']) or (target['mac'] and r['mac']==target['mac']))]
    addresses={r['mac'] for r in bindings+denied}|({target['mac']} if target['mac'] else set())
    observations=[(r,'mac_table_seen') for r in tables['mac'] if r['mac'] in addresses]+[(r,'dai_denied_historical') for r in denied]
    candidates={}
    for row,reason in observations:
        # Gi uplinks describe a downstream path, not a directly attached client.
        if not row['interface'].startswith('Fa'):continue
        key=(row['interface'],row['mac'])
        item=candidates.setdefault(key,{'interface':row['interface'],'observedMac':row['mac'],'recordedPorts':[],'reasons':[],'confidence':'low','historical':True})
        if len(candidates)>48:raise ValueError('too many candidate identities')
        reasons=set(item['reasons']);reasons.add(reason)
        if reason=='mac_table_seen':item.update(confidence='medium',historical=False)
        relevant=[b for b in bindings if b['mac']==row['mac'] or (target['ip'] and b['ip']==target['ip'])]
        item['recordedPorts']=sorted(set(item['recordedPorts'])|{b['interface'] for b in relevant})
        if any(b['interface']!=row['interface'] for b in relevant):reasons.add('binding_port_conflict')
        if any(b['mac']!=row['mac'] for b in relevant):reasons.add('binding_mac_conflict')
        secure=[s for s in tables['secure'] if s['interface']==row['interface']]
        if secure and not any(s['mac']==row['mac'] for s in secure):reasons.add('secure_mac_conflict')
        item['reasons']=sorted(reasons)
    return {'profile':hardware,'client':target,'sources':sources,'candidates':sorted(candidates.values(),key=lambda r:(r['interface'],r['observedMac'])),
            'assessment':'evidence' if candidates else 'unknown','readOnly':True,'movementConfirmed':False,'vlan':100}


def validate_report(report):
    """Revalidate helper output at the API boundary; never pass arbitrary text."""
    if not isinstance(report,dict) or set(report)!={'profile','client','sources','candidates','assessment','readOnly','movementConfirmed','vlan'}:raise ValueError('bad report')
    p=report['profile']
    if not isinstance(p,dict) or set(p)!={'model','ios','image'} or p['model']!=MODEL or not isinstance(p['ios'],str) or not re.fullmatch(IOS,p['ios']) or not isinstance(p['image'],str) or not re.fullmatch(IMAGE,p['image']):raise ValueError('bad profile')
    if not isinstance(report['client'],dict) or set(report['client'])!={'ip','mac'} or client(report['client']['ip'],report['client']['mac'])!=report['client']:raise ValueError('bad client')
    if report['readOnly'] is not True or report['movementConfirmed'] is not False or type(report['vlan']) is not int or report['vlan']!=100:raise ValueError('bad policy')
    if not isinstance(report['sources'],list) or len(report['sources'])!=4:raise ValueError('bad sources')
    for expected,source in zip(SOURCE_IDS,report['sources']):
        if not isinstance(source,dict) or set(source)!={'id','state','count'} or source['id']!=expected or source['state'] not in {'parsed','unavailable'} or type(source['count']) is not int or not 0<=source['count']<=4096 or (source['state']=='unavailable' and source['count']!=0):raise ValueError('bad source')
    if not isinstance(report['candidates'],list) or len(report['candidates'])>48:raise ValueError('bad candidates')
    seen=set()
    for row in report['candidates']:
        if not isinstance(row,dict) or set(row)!={'interface','observedMac','recordedPorts','reasons','confidence','historical'}:raise ValueError('bad candidate')
        if port(row['interface'])!=row['interface'] or not row['interface'].startswith('Fa') or mac(row['observedMac'])!=row['observedMac']:raise ValueError('bad identity')
        key=(row['interface'],row['observedMac'])
        if key in seen:raise ValueError('duplicate candidate')
        seen.add(key)
        if not isinstance(row['recordedPorts'],list) or len(row['recordedPorts'])>26 or any(port(p)!=p for p in row['recordedPorts']):raise ValueError('bad record')
        if not isinstance(row['reasons'],list) or not row['reasons'] or len(row['reasons'])>5 or any(not isinstance(r,str) or r not in REASONS for r in row['reasons']):raise ValueError('bad reasons')
        if row['confidence'] not in {'medium','low'} or type(row['historical']) is not bool or (row['confidence']=='medium')!=('mac_table_seen' in row['reasons']) or row['historical']!=('mac_table_seen' not in row['reasons']):raise ValueError('bad confidence')
        if not {'mac_table_seen','dai_denied_historical'}&set(row['reasons']):raise ValueError('no observation')
        for reason,source_id in [('mac_table_seen','mac'),('dai_denied_historical','dai')]:
            source=next(s for s in report['sources'] if s['id']==source_id)
            if reason in row['reasons'] and (source['state']!='parsed' or not source['count']):raise ValueError('missing observation source')
    if report['assessment']!=('evidence' if report['candidates'] else 'unknown'):raise ValueError('bad assessment')
    return report
