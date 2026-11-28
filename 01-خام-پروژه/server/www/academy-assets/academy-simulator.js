(() => {
  'use strict';

  const CLI_DB = {
  "show interfaces status": "Port      Name            Status       Vlan       Duplex  Speed   Type\nGi0/1     UPLINK          connected    trunk      a-full  a-1000  10/100/1000BaseTX\nGi0/2     PC-TEST         disabled     1          a-full  a-1000  10/100/1000BaseTX",
  "show ip interface brief": "Interface              IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0     10.10.0.1       YES manual up                    up\nGigabitEthernet0/2     unassigned      YES manual administratively down down",
  "show arp": "Protocol  Address          Age (min)  Hardware Addr   Type   Interface\nInternet  10.10.0.1               -   aabb.cc00.0100  ARPA   GigabitEthernet0/0\nInternet  10.10.0.2               4   aabb.cc00.0200  ARPA   GigabitEthernet0/0",
  "show mac address-table": "Mac Address Table\n-------------------------------------------\nVlan    Mac Address       Type        Ports\n----    -----------       --------    -----\n   1    0050.56ab.1101    DYNAMIC     Gi0/1\n  10    001a.2b3c.4d5e    DYNAMIC     Gi0/3",
  "show ip route": "Codes: C - connected, S - static, O - OSPF, B - BGP\nC    10.10.0.0/24 is directly connected, GigabitEthernet0/0\nO    10.255.0.2/32 [110/2] via 10.10.0.2, 00:12:41, GigabitEthernet0/0",
  "show interfaces trunk": "Port        Mode             Encapsulation  Status        Native vlan\nGi0/1       on               802.1q         trunking      1\n\nPort        Vlans allowed on trunk\nGi0/1       10,20,30",
  "show bgp l2vpn evpn summary": "BGP router identifier 10.255.0.11, local AS number 65100\nNeighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd\n10.255.0.1      4 65100     842     839       64    0    0 04:12:18       48",
  "show nve peers": "Interface Peer-IP                                 State LearnType Uptime   Router-Mac\n--------- --------------------------------------- ----- --------- -------- -----------------\nnve1      10.255.0.12                             Up    CP        04:10:05 0200.0000.0012",
  "show ip bgp summary": "BGP router identifier 10.255.0.1, local AS number 65100\nNeighbor        V           AS MsgRcvd MsgSent   TblVer  Up/Down State/PfxRcd\n10.255.0.2      4        65100     142     139       24 02:14:09           12\n198.51.100.1    4        64500     310     128       24 05:40:11          420",
  "traceroute 10.255.0.2": "Tracing the route to 10.255.0.2\n  1 10.10.0.2 2 msec 1 msec 2 msec\n  2 10.255.0.2 3 msec 2 msec *",
  "configure terminal": "R1# configure terminal\nR1(config)#",
  "ping 10.255.0.2": "Type escape sequence to abort.\nSending 5, 100-byte ICMP Echos to 10.255.0.2, timeout is 2 seconds:\n!!!!!\nSuccess rate is 100 percent (5/5), round-trip min/avg/max = 1/2/3 ms",
  "show ip ospf neighbor": "Neighbor ID     Pri   State           Dead Time   Address         Interface\n10.255.0.2        1   FULL/DR         00:00:34    10.0.12.2       GigabitEthernet0/0\n10.255.0.3        0   FULL/  -        00:00:38    10.0.13.2       GigabitEthernet0/1",
  "show standby brief": "Interface   Grp  Pri P State   Active          Standby         Virtual IP\nVl10        10   110 P Active  local           10.10.10.3      10.10.10.1",
  "show ntp status": "Clock is synchronized, stratum 3, reference is 10.99.0.5\nnominal freq is 250.0000 Hz, actual freq is 250.0000 Hz, precision is 2**10",
  "show access-lists": "Extended IP access list 110\n    10 deny tcp 192.168.10.0 0.0.0.255 host 10.50.0.10 eq 22 (14 matches)\n    20 permit ip any any (382 matches)",
  "show interfaces gi0/2 switchport": "Name: Gi0/2\nSwitchport: Enabled\nAdministrative Mode: static access",
  "show spanning-tree": "VLAN0001\n  Spanning tree enabled protocol rstp\n  Root ID    Priority    24577\n             Address     0050.56ab.1100",
  "show interfaces gi0/3 switchport": "Name: Gi0/3\nSwitchport: Enabled\nAdministrative Mode: static access",
  "show ip cef": "Prefix               Next Hop             Interface\n0.0.0.0/0            198.51.100.1         GigabitEthernet0/0\n10.10.0.0/24         attached             Vlan10 (Adjacency ready)\n10.20.1.0/24         10.0.12.2            GigabitEthernet0/1",
  "show interfaces tunnel0": "Tunnel0 is up, line protocol is up\n  Hardware is Tunnel\n  MTU 17916 bytes, BW 100 Kbit/sec, DLY 50000 usec\n  Tunnel source 203.0.113.1 (GigabitEthernet0/0), destination 198.51.100.2\n  Tunnel protocol/transport GRE/IP",
  "show dmvpn": "Interface: Tunnel0, IPv4 NHRP Details\nType:Spoke, NHRP Peers:2 (Phase 3 Redirect/Shortcut enabled)\n # Ent  Peer NBMA Addr Peer Tunnel Add State  UpDn Tm Attrb\n ----- --------------- --------------- ----- -------- -----\n     1 203.0.113.10       172.16.0.1      UP 04:12:10     S\n     1 203.0.113.22       172.16.0.3      UP 00:08:44     D (Shortcut)",
  "show isis neighbors": "Tag UNDERLAY:\nSystem Id       Type Interface   IP Address      State Holdtime Circuit Id\nR2-BORDER       L2   Gi0/0       10.10.0.2       UP    27       00",
  "show clns interface gi0/0": "GigabitEthernet0/0 is up, line protocol is up\n  Checksums enabled, MTU 1497, Encapsulation SAP\n  ERPDUs enabled, min. interval 10 msec.\n  CLNS fast switching enabled\n  Routing Protocol: IS-IS (UNDERLAY)\n    Circuit Type: level-2-only",
  "show authentication sessions interface gi0/6 details": "Interface:  GigabitEthernet0/6\nMAC Address:  0200.0000.0066\nIPv4 Address: 10.10.10.66\nStatus:  Authorized\nDomain:  DATA\nOper Host Mode:  multi-auth\nMethod status list:\n   Method           State\n   dot1x            Authc Success",
  "show cts role-based sgt-map all": "Active IPv4-SGT Bindings Information\nIP Address              SGT     Source\n--------------------------------------------\n10.10.10.66             15      LOCAL",
  "show mpls forwarding-table": "Local      Outgoing   Prefix           Bytes Label   Outgoing   Next Hop\nLabel      Label      or Tunnel Id     Switched      interface\n16         Pop Label  10.255.0.2/32    418200        Gi0/0      10.10.0.2\n17         24         10.255.0.3/32    920140        Gi0/0      10.10.0.2\n18         No Label   10.50.1.0/24[V]  12840         Gi0/6      10.50.1.2",
  "show bgp vpnv4 unicast all summary": "BGP router identifier 10.255.0.1, local AS number 65100\nNeighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd\n10.255.0.2      4 65100     840     835       42    0    0 04:12:08       12",
  "show wireless summary": "Wireless Summary:\nTotal APs: 24 (Up: 24)\nTotal Clients: 312 (802.11ax: 240, 802.11ac: 72)",
  "show ap tag summary": "AP Name          Policy Tag     Site Tag       RF Tag\n--------------------------------------------------------\nAP-FL3-01        CORP_PTAG      BRANCH_FLEX    OFFICE_RF",
  "switchport voice vlan 30": "خروجی شبیه‌ساز برای: switchport voice vlan 30",
  "show cdp neighbors detail": "خروجی شبیه‌ساز برای: show cdp neighbors detail",
  "show ip dhcp binding": "Bindings from all pools not associated with VRF:\nIP address      Client-ID/Hardware address     Lease expiration        Type\n192.168.10.21   0102.0000.0010.21              Nov 24 2026 04:12 PM    Automatic",
  "show ip nat translations": "Pro Inside global      Inside local       Outside local      Outside global\ntcp 203.0.113.10:51200 192.168.10.10:51200 198.51.100.80:443 198.51.100.80:443\ntcp 203.0.113.10:51201 192.168.10.11:51200 198.51.100.80:443 198.51.100.80:443",
  "show ip ssh": "SSH Enabled - version 2.0\nAuthentication timeout: 120 secs; Authentication retries: 3",
  "show crypto isakmp sa": "IPv4 Crypto ISAKMP SA\ndst             src             state          conn-id status\n203.0.113.2     203.0.113.1     QM_IDLE        1001    ACTIVE",
  "show vlan private-vlan": "Primary Secondary Type              Ports\n------- --------- ----------------- ------------------------------------------\n100     101       isolated          Gi1/0/1, Gi1/0/2, Gi1/0/24\n100     102       community         Gi1/0/5, Gi1/0/6, Gi1/0/24",
  "show etherchannel summary": "Flags:  D - down        P - bundled in port-channel\n        I - stand-alone s - suspended\nGroup  Port-channel  Protocol    Ports\n------+-------------+-----------+-----------------------------------------------\n1      Po1(RU)         LACP      Gi1/0/21(P) Gi1/0/22(P) Gi1/0/23(P) Gi1/0/24(P)",
  "show policy-map interface gi0/0": "GigabitEthernet0/0\n  Service-policy output: WAN-OUT\n    Class-map: VOICE (match-all)\n      0 packets, 0 bytes\n      Priority: 20% (20000 kbps), burst bytes 500000, b/w exceed drops: 0",
  "show ip mroute": "(*, 239.10.10.10), 01:12:04/stopped, RP 10.255.0.10, flags: SJC\n  Incoming interface: GigabitEthernet0/0, RPF nbr 10.0.12.2\n  Outgoing interface list: GigabitEthernet0/1, Forward/Sparse",
  "show bfd neighbors": "IPv4 Sessions\nNeighAddr                              LD/RD         RH/RS     State     Int\n10.10.0.2                               1/2          Up        Up        Gi0/0",
  "show policy-map control-plane": "Control Plane\n  Service-policy input: COPP_POLICY\n    Class-map: CM_ROUTING (match-all)\n      Match: access-group name ACL_ROUTING\n      police: cir 512000 bps, bc 16000 bytes\n        conformed 4210 packets, 310200 bytes; actions: transmit\n        exceeded 0 packets, 0 bytes; actions: drop",
  "show event manager policy registered": "No.  Class     Type    Event Type          Trap  Time Registered           Name\n1    applet    user    syslog              Off   Mon Nov 23 09:12:04 2026  WAN_DOWN_ALERT",
  "show sdwan omp routes": "VPN  PREFIX          FROM PEER     TLOC IP      COLOR         STATUS\n---------------------------------------------------------------------\n10   10.200.10.0/24  10.255.0.100  10.255.2.1   mpls          C,I,R\n10   10.200.10.0/24  10.255.0.100  10.255.2.1   biz-internet  C,I,R",
  "show sdwan app-route stats": "app-route statistics 10.255.0.12 10.255.0.14\n remote-system-ip  local-color  remote-color  mean-loss  mean-latency  mean-jitter\n 10.255.0.14       mpls         mpls          0.00%      18            2\n 10.255.0.14       biz-internet biz-internet  2.40%      95            18",
  "show netconf-yang sessions": "Number of sessions : 1\nsession-id  transport    username    source-host    global-lock\n---------------------------------------------------------------\n42          netconf-ssh  netops      10.255.99.5    None",
  "show ip bgp neighbors 203.0.113.2 advertised-routes": "BGP table version is 19, local router ID is 10.255.0.1\n   Network          Next Hop            Metric LocPrf Weight Path\n*> 10.128.0.0/16    0.0.0.0                  0         32768 i\n\nTotal number of prefixes 1",
  "show app-hosting list": "App id                                   State\n---------------------------------------------------------\nthousandeyes_enterprise_agent            RUNNING",
  "# خروجی مرجع تست http + path (thousandeyes reference)": "Agent: Esfahan-Ent-01 -> Target: https://crm.example.com\nHTTP: DNS=14ms | Connect=290ms | SSL=85ms | Wait=115ms | Response=504ms\nPath Hop 4 (LocalGW): 0% loss, 4ms | Hop 5 (ISP-AS65400): 18% loss | Hop 6-End: 0% loss (Case A) OR 18% loss (Case B)",
  "show stackwise-virtual link": "Stackwise Virtual Link(SVL) Information:\nFlags: LC - Link configured, U - Up, D - Down, R - Removed\nSwitch  SVL     Ports                           Link-Status\n------  ---     -----                           -----------\n1       1       HundredGigE1/0/49               U\n                HundredGigE1/0/50               U\n2       1       HundredGigE2/0/49               U\n                HundredGigE2/0/50               U",
  "show stackwise-virtual dual-active-detection": "In Dual-Active Detection:\nRecovery Mode: Enabled\nDual-Active-Detection Links:\nSwitch  Dad port                        Status\n------  --------                        ------\n1       TenGigabitEthernet1/0/1         up\n2       TenGigabitEthernet2/0/1         up",
  "show pnp trace": "PnP Discovery Status: Option 43 found -> Controller 10.10.20.5\nSUDI Certificate verified; Waiting for Day-0 configuration push...",
  "show sdwan control connections": "PEER    PEER TYPE  PROTOCOL  SYSTEM IP     SITE ID  DOMAIN ID  STATE\n---------------------------------------------------------------------\nvsmart  vsmart     dtls      10.255.0.100  1        1          up\nvbond   vbond      dtls      10.255.0.101  1        0          up\nvmanage vmanage    dtls      10.255.0.102  1        0          up",
  "show crypto ikev2 sa detailed": "Tunnel-id Local                 Remote                fvrf/ivrf            Status\n1         203.0.113.1/4500      198.51.100.1/4500     none/none            READY\n      Encr: AES-GCM, keysize: 256, Hash: N/A, DH Grp:19, Auth sign: PSK, Auth verify: PSK\n      Life/Active Time: 86400/1420 sec",
  "show crypto ipsec sa interface tunnel0": "interface: Tunnel0\n   protected vrf: (none)\n   local  ident (addr/mask/prot/port): (0.0.0.0/0.0.0.0/0/0)\n   remote ident (addr/mask/prot/port): (0.0.0.0/0.0.0.0/0/0)\n   #pkts encaps: 412, #pkts encrypt: 412\n   #pkts decaps: 410, #pkts decrypt: 410",
  "show tacacs": "Server status: Alive\nServer address: 10.10.90.10, port: 49\n  Socket opens: 14, closes: 13\n  Errors: 0, Packets sent: 128, Packets received: 128",
  "show aaa servers": "RADIUS: id 1, priority 1, host 10.10.90.10, auth-port 1812, acct-port 1813\n  State: current UP, duration 1842s\n  Authen: request 94, timeouts 0, fail 2, success 92",
  "show vpc brief": "vPC domain id                     : 10\nPeer status                       : peer adjacency formed ok\nvPC keep-alive status             : peer is alive\nConfiguration consistency status  : success\nPer-vlan consistency status       : success\nType-2 consistency status         : success\nvPC role                          : primary\nNumber of vPCs configured         : 12\n\nvPC Peer-link status\n---------------------------------------------------------------------\nid    Port   Status Active vlans\n1     Po1    up     1,10,20,100",
  "show vpc orphan-ports": "Note:\n--------\nPort        Orphan status\nEth1/12     Yes",
  "show endpoint": "Legend:\n s - static   v - vpc   p - peer   L - local\nVLAN/Encap      MAC Address       IP Address       Interface        Flags\n--------------  ----------------- ---------------  ---------------  -----\nvlan-110        0200.0000.0110    10.110.0.10      eth1/11          L",
  "acidiag fnvread": "ID   Pod ID  Name      Serial Number  IP Address     Role   State\n-------------------------------------------------------------------\n101  1       Leaf-101  FDO2100101A    10.0.0.64/32   leaf   active\n201  1       Spine-201 FDO2100201A    10.0.0.65/32   spine  active",
  "show flogi database": "--------------------------------------------------------------------------------\nINTERFACE        VSAN    FCID           PORT NAME               NODE NAME\n--------------------------------------------------------------------------------\nfc1/1            10    0xef0001  20:00:00:25:b5:00:00:11 10:00:00:25:b5:00:00:01\nfc1/5            10    0xef0002  50:06:01:60:47:e0:11:22 50:06:01:60:47:e0:11:00\nTotal number of flogi = 2.",
  "show zoneset active vsan 10": "zoneset name ZSET_PROD vsan 10\n  zone name Z_SRV1_STOR1 vsan 10\n   * fcid 0xef0001 [pwwn 20:00:00:25:b5:00:00:11]\n   * fcid 0xef0002 [pwwn 50:06:01:60:47:e0:11:22]",
  "show configuration": "Building configuration...\n!! IOS XR Configuration\nroute-policy PASS_ALL\n  pass\nend-policy\n!\nrouter bgp 65100\n neighbor 10.10.0.2\n  address-family ipv4 unicast\n   route-policy PASS_ALL in\n   route-policy PASS_ALL out",
  "show configuration commit list": "SNo. Label/ID              User      Line                Client      Time Stamp\n~~~~ ~~~~~~~~              ~~~~      ~~~~                ~~~~~~      ~~~~~~~~~~\n1    1000000042            admin     vty0:node0_RP0_CPU0 CLI         Mon Nov 23 10:14:02 2026\n2    1000000041            admin     vty0:node0_RP0_CPU0 CLI         Mon Nov 23 09:50:11 2026",
  "show isis segment-routing label-table": "IS-IS CORE Label Table\nLabel     Prefix                Interface\n16001     10.255.0.1/32         Loopback0 (Index 1)\n16002     10.255.0.2/32         (Index 2)\n16005     10.255.0.5/32         (Index 5)",
  "show isis fast-reroute summary": "IS-IS CORE Fast-Reroute Summary\nTopology       LFA Protected    Total Prefixes    Coverage\nIPv4 Unicast   128              128               100%",
  "show ap dot11 5ghz channel": "Leader IP                                        : 10.10.185.10\nChannel Assignment Mode                          : AUTO\nChannel Update Interval                          : 600 seconds\nChannel Assignment Method                        : RX-NEIGHBOR\nChannel Width                                    : 40 MHz\nDCA Channel List                                 : 36,40,44,48,52,56,60,64,100,104...",
  "show ap dot11 5ghz summary": "AP Name            Slots  AP Model           Ethernet MAC       Radio Status   Channel  TxPwr\n-----------------------------------------------------------------------------------------------\nAP-FL5-01          2      C9120AXI-B         aabb.cc00.1101     Up             36       3/8 (14 dBm)\nAP-FL5-02          2      C9120AXI-B         aabb.cc00.1102     Up             52       4/8 (11 dBm)",
  "show sip-ua calls": "خروجی شبیه‌ساز برای: show sip-ua calls",
  "show call active voice compact": "خروجی شبیه‌ساز برای: show call active voice compact",
  "ip -br addr show": "خروجی شبیه‌ساز برای: ip -br addr show",
  "ss -tulnp": "خروجی شبیه‌ساز برای: ss -tulnp",
  "python3 -m venv .venv": "خروجی شبیه‌ساز برای: python3 -m venv .venv",
  "pip freeze > requirements.txt": "خروجی شبیه‌ساز برای: pip freeze > requirements.txt",
  "git status && git diff --staged": "خروجی شبیه‌ساز برای: git status && git diff --staged",
  "git switch -c feat/vlan-automation": "خروجی شبیه‌ساز برای: git switch -c feat/vlan-automation",
  "python3 -m json.tool device.json": "خروجی شبیه‌ساز برای: python3 -m json.tool device.json",
  "yamllint hosts.yaml": "خروجی شبیه‌ساز برای: yamllint hosts.yaml",
  "show ip http server status": "خروجی شبیه‌ساز برای: show ip http server status",
  "curl -i -h \"accept: application/json\" --cacert corp-ca.pem https://10.255.0.1/api/v1/vlans": "خروجی شبیه‌ساز برای: curl -i -H \"Accept: application/json\" --cacert corp-ca.pem https://10.255.0.1/api/v1/vlans",
  "openssl s_client -connect 10.255.0.1:443 -tls1_3 -showcerts": "خروجی شبیه‌ساز برای: openssl s_client -connect 10.255.0.1:443 -tls1_3 -showcerts",
  "show crypto pki certificates verbose": "خروجی شبیه‌ساز برای: show crypto pki certificates verbose",
  "ssh -p 830 admin@10.255.0.1 -s netconf": "خروجی شبیه‌ساز برای: ssh -p 830 admin@10.255.0.1 -s netconf",
  "show restconf status": "خروجی شبیه‌ساز برای: show restconf status",
  "show netconf-yang datastores": "خروجی شبیه‌ساز برای: show netconf-yang datastores",
  "show yang": "خروجی شبیه‌ساز برای: show yang",
  "show netconf-yang modules": "خروجی شبیه‌ساز برای: show netconf-yang modules",
  "ansible -i inventory.yml ios_routers -m cisco.ios.ios_command -a \"commands='show version'\"": "خروجی شبیه‌ساز برای: ansible -i inventory.yml ios_routers -m cisco.ios.ios_command -a \"commands='show version'\"",
  "ansible-playbook site.yml --check --diff": "خروجی شبیه‌ساز برای: ansible-playbook site.yml --check --diff",
  "terraform plan": "خروجی شبیه‌ساز برای: terraform plan",
  "terraform apply": "خروجی شبیه‌ساز برای: terraform apply",
  "nso_cli --context admin show services": "خروجی شبیه‌ساز برای: nso_cli --context admin show services",
  "nso_cli --context admin show devices": "خروجی شبیه‌ساز برای: nso_cli --context admin show devices",
  "show ip inspect": "خروجی شبیه‌ساز برای: show ip inspect",
  "show ip inspect sessions": "خروجی شبیه‌ساز برای: show ip inspect sessions",
  "show vxlan": "خروجی شبیه‌ساز برای: show vxlan",
  "show mpls ldp neighbors": "خروجی شبیه‌ساز برای: show mpls ldp neighbors",
  "show mpls l3vpn routes": "خروجی شبیه‌ساز برای: show mpls l3vpn routes",
  "show ip bgp vpnv4": "خروجی شبیه‌ساز برای: show ip bgp vpnv4",
  "show ap summary": "خروجی شبیه‌ساز برای: show ap summary",
  "show sip-ua register": "خروجی شبیه‌ساز برای: show sip-ua register",
  "show voice call summary": "خروجی شبیه‌ساز برای: show voice call summary",
  "show dial-peer voice": "خروجی شبیه‌ساز برای: show dial-peer voice",
  "show run | section netconf": "خروجی شبیه‌ساز برای: show run | section netconf",
  "show platform software": "خروجی شبیه‌ساز برای: show platform software",
  "show mpls interfaces": "خروجی شبیه‌ساز برای: show mpls interfaces",
  "show vpc": "خروجی شبیه‌ساز برای: show vpc",
  "show fex": "خروجی شبیه‌ساز برای: show fex",
  "show ip bgp": "خروجی شبیه‌ساز برای: show ip bgp",
  "show crypto ipsec sa": "خروجی شبیه‌ساز برای: show crypto ipsec sa",
  "show interface tunnel": "خروجی شبیه‌ساز برای: show interface tunnel",
  "show ip vrf": "خروجی شبیه‌ساز برای: show ip vrf",
  "show ip cef vrf": "خروجی شبیه‌ساز برای: show ip cef vrf",
  "show cts sgt": "خروجی شبیه‌ساز برای: show cts sgt",
  "show standby": "خروجی شبیه‌ساز برای: show standby",
  "show track": "خروجی شبیه‌ساز برای: show track",
  "show redundancy": "خروجی شبیه‌ساز برای: show redundancy",
  "show interfaces": "خروجی شبیه‌ساز برای: show interfaces",
  "show ip policy": "خروجی شبیه‌ساز برای: show ip policy",
  "show policy-map": "خروجی شبیه‌ساز برای: show policy-map",
  "show cdp neighbors": "خروجی شبیه‌ساز برای: show cdp neighbors",
  "show ip eigrp topology": "EIGRP-IPv4 Topology Table for AS(100)/ID(10.255.0.1)\nP 10.50.0.0/24, 1 successors, FD is 1500\n        via 10.0.12.2 (1500/1000), GigabitEthernet0/0\n        via 10.0.13.2 (2600/1400), GigabitEthernet0/1  [Feasible Successor: RD < FD]",
  "show policy-map interface": "GigabitEthernet0/0\n  Service-policy output: PARENT_SHAPE\n    Class-map: class-default (match-any)\n      shape (average) cir 200000000, bc 2000000, be 2000000\n      Service-policy : CHILD_QOS\n        Class-map: VOICE (match-any) -> Priority: 20%, Match dscp ef (46), Drops: 0\n        Class-map: class-default -> random-detect dscp-based (WRED active)",
  "show ip rpf 10.20.1.50": "RPF information for ? (10.20.1.50)\n  RPF interface: GigabitEthernet0/0\n  RPF neighbor: ? (10.0.12.2)\n  RPF route/mask: 10.20.1.0/24\n  RPF type: unicast (ospf 1)",
  "show ntp associations": "  address         ref clock       st   when   poll reach  delay  offset   disp\n*~10.255.0.10     .GPS.            1     18     64   377  1.210  -0.042  0.315\n+~10.255.0.11     10.255.0.10      2     22     64   377  1.840  +0.019  0.410",
  "show authentication sessions": "Interface  MAC Address     Method   Domain   Status         Session ID\nGi1/0/10   0050.56ab.1101  dot1x    DATA     Authz Success  0A0A0A0100000012\nGi1/0/11   0050.56ab.2202  mab      DATA     Authz Success  0A0A0A0100000013",
  "show sdwan bfd sessions": "SITE  SYSTEM IP    SRC COLOR     DST COLOR     STATE  LOSS%  LATENCY(ms)  JITTER(ms)\n-------------------------------------------------------------------------------------\n200   10.255.2.1   mpls          mpls          up     0.0    18           2\n200   10.255.2.1   biz-internet  biz-internet  up     0.1    34           4",
  "show vlan brief": "VLAN Name                             Status    Ports\n---- -------------------------------- --------- -------------------------------\n1    default                          active    Gi0/10\n10   SALES                            active    Gi0/1, Gi0/2\n20   ENGINEERING                      active    Gi0/3, Gi0/4\n50   VOICE                            active    Gi0/1, Gi0/2\n999  BLACKHOLE                        active    Gi0/20",
  "show running-config": "! Simulated Educational Running-Config (Client-Side Mock — NOT live IOS)\nhostname FAM-LAB-R1\n!\nip cef\n!\ninterface GigabitEthernet0/0\n description Uplink-Core\n ip address 10.0.12.1 255.255.255.252\n ip ospf network point-to-point\n!\nrouter ospf 1\n router-id 10.255.0.1\n passive-interface default\n no passive-interface GigabitEthernet0/0\n!\nend"
};

  const ALIASES = {
    'sh ip int br': 'show ip interface brief',
    'sh int status': 'show interfaces status',
    'sh int trunk': 'show interfaces trunk',
    'sh vlan br': 'show vlan brief',
    'sh mac addr': 'show mac address-table',
    'sh ip ro': 'show ip route',
    'sh run': 'show running-config',
    'sh ip ospf nei': 'show ip ospf neighbor',
    'sh ip bgp sum': 'show ip bgp summary',
    'sh bgp sum': 'show ip bgp summary',
    'sh bgp ipv4 unicast summary': 'show ip bgp summary',
    'sh eth sum': 'show etherchannel summary',
    'sh standby br': 'show standby brief',
    'sh ip eigrp top': 'show ip eigrp topology',
    'sh policy-map int': 'show policy-map interface',
    'sh ip mroute': 'show ip mroute',
    'sh ip cef': 'show ip cef',
    'sh ntp assoc': 'show ntp associations',
    'sh auth sess': 'show authentication sessions',
    'sh sdwan control conn': 'show sdwan control connections',
    'sh sdwan bfd sess': 'show sdwan bfd sessions',
    'conf t': 'configure terminal',
    'en': 'enable'
  };

  const LESSON_SCENARIOS = {
    adv_pvl: { host: 'SW-PVLAN', goal: 'بررسی نگاشت Primary/Secondary در Private VLAN و هرس ترانک', cmds: ['show vlan private-vlan', 'show interfaces trunk', 'show vlan brief'] },
    adv_ec: { host: 'DIST-SW1', goal: 'بررسی وضعیت LACP Port-Channel و نقش Active/Standby در HSRP', cmds: ['show etherchannel summary', 'show standby brief', 'show interfaces trunk'] },
    adv_eigrp: { host: 'R1-EIGRP', goal: 'بررسی Successor و Feasible Successor (شرط RD < FD) در EIGRP', cmds: ['show ip eigrp topology', 'show ip route', 'show ip interface brief'] },
    adv_redist: { host: 'ASBR1', goal: 'بررسی مسیرهای OSPF/EIGRP و کنترل Route Feedback در روتر مرزی', cmds: ['show ip route', 'show ip ospf neighbor', 'show running-config'] },
    adv_bgp: { host: 'EDGE-BGP1', goal: 'بررسی نشست‌های eBGP/iBGP و وضعیت Established (عدد در State/PfxRcd)', cmds: ['show ip bgp summary', 'show ip route', 'show ip interface brief'] },
    adv_qos: { host: 'WAN-CE1', goal: 'بررسی سیاست سلسله‌مراتبی HQoS، صف اولویت EF و WRED', cmds: ['show policy-map interface', 'show ip interface brief'] },
    adv_mcast: { host: 'MCAST-R1', goal: 'بررسی درخت PIM-SM و کنترل مسیر بازگشت RPF', cmds: ['show ip mroute', 'show ip rpf 10.20.1.50', 'show ip route'] },
    ccnp_01: { host: 'ENCOR-R1', goal: 'بررسی جدول مسیریابی، CEF و ساختار مجازی‌سازی', cmds: ['show ip cef', 'show ip route', 'show running-config'] },
    ccnp_02: { host: 'ENARSI-R1', goal: 'عیب‌یابی همسایگی OSPF، BGP و تونل DMVPN Phase 3', cmds: ['show ip ospf neighbor', 'show ip bgp summary', 'show dmvpn'] },
    ccnp_enc_arch: { host: 'CORE-SW1', goal: 'راستی‌آزمایی جدول FIB در CEF و مسیرهای لایه ۳', cmds: ['show ip cef', 'show ip route', 'show etherchannel summary'] },
    ccnp_enc_inf: { host: 'INFRA-R1', goal: 'بررسی هم‌زمانی Stratum در NTP و وضعیت اینترفیس‌ها', cmds: ['show ntp associations', 'show ip interface brief', 'show running-config'] },
    ccnp_enc_sec: { host: 'SEC-SW1', goal: 'بررسی نشست‌های احراز هویت 802.1X و MAB', cmds: ['show authentication sessions', 'show running-config', 'show vlan brief'] },
    ccnp_enc_auto: { host: 'AUTO-XE1', goal: 'بررسی نشست‌های فعال NETCONF-YANG و پیکربندی پایه', cmds: ['show netconf-yang sessions', 'show running-config', 'show ip interface brief'] },
    ccnp_ensdwi: { host: 'cEdge-BR1', goal: 'بررسی اتصالات کنترلی vSmart/vBond/vManage، سنجش BFD و مسیرهای OMP', cmds: ['show sdwan control connections', 'show sdwan bfd sessions', 'show sdwan omp routes'] },
    ccnp_ensld: { host: 'DESIGN-R1', goal: 'بررسی خلاصه‌سازی مسیرها و افزونگی لایه ۳ در طرح شبکه', cmds: ['show ip route', 'show ip ospf neighbor', 'show ip bgp summary'] },
    ccnp_enauto: { host: 'NETOPS-XE1', goal: 'بررسی وضعیت NETCONF و انطباق پیکربندی', cmds: ['show netconf-yang sessions', 'show running-config', 'show ip route'] },
    ccnp_encc: { host: 'CLOUD-GW1', goal: 'بررسی نشست BGP ابری و مسیرهای ترانزیت', cmds: ['show ip bgp summary', 'show ip route', 'show ip interface brief'] },
    ccnp_enna: { host: 'ASSURE-R1', goal: 'بررسی مسیرها، هم‌زمانی NTP و کیفیت مسیر BFD', cmds: ['show ntp associations', 'show sdwan bfd sessions', 'traceroute 10.255.0.2'] }
  };

  function scenarioForLesson(bp) {
    const id = String(bp?.lessonId || bp?.id || '');
    if (LESSON_SCENARIOS[id]) return LESSON_SCENARIOS[id];
    if (id.startsWith('auto_') || id === 'academy-automation-terraform') {
      return { host: 'AUTO-XE1', goal: 'تمرین فرمان‌های تشخیصی مرجع مرتبط با اتوماسیون شبکه', cmds: ['show netconf-yang sessions', 'show ip interface brief', 'show running-config'] };
    }
    if (id.startsWith('ccna_02') || id === 's10') {
      return { host: 'SW1', goal: 'تمرین بررسی VLAN، جدول MAC و پورت‌های Trunk 802.1Q', cmds: ['show vlan brief', 'show interfaces trunk', 'show mac address-table'] };
    }
    if (id.startsWith('ccna_') || id.startsWith('ccna-')) {
      return { host: 'R1', goal: 'تمرین فرمان‌های پایه CCNA برای اینترفیس، ARP و مسیریابی', cmds: ['show ip interface brief', 'show arp', 'show ip route', 'show ip ospf neighbor'] };
    }
    if (id.startsWith('spec_') || id.startsWith('ccie_') || id.startsWith('ccde_')) {
      return { host: 'CORE-R1', goal: 'تمرین فرمان‌های معماری، EVPN/BGP و تشخیص مسیر', cmds: ['show ip bgp summary', 'show bgp l2vpn evpn summary', 'show ip cef', 'show ip route'] };
    }
    return { host: 'LAB-SW1', goal: 'آشنایی با محیط تعاملی CLI شبیه‌سازی‌شده برای مفاهیم پایه شبکه', cmds: ['show interfaces status', 'show mac address-table', 'show arp', 'show ip route'] };
  }

  function createSession(initialHost) {
    const state = {
      host: initialHost || 'FAM-LAB',
      mode: 'priv', // 'user' (>), 'priv' (#), 'config' ((config)#)
      history: []
    };

    function prompt() {
      if (state.mode === 'user') return `${state.host}> `;
      if (state.mode === 'config') return `${state.host}(config)# `;
      return `${state.host}# `;
    }

    function execute(rawInput) {
      const input = String(rawInput || '').trim();
      if (!input) return { output: '', prompt: prompt(), matched: true };
      state.history.push(input);
      const lower = input.toLowerCase().replace(/\s+/g, ' ');
      const normalized = ALIASES[lower] || lower;

      if (normalized === 'clear') {
        return { output: '', clear: true, prompt: prompt(), matched: true };
      }
      if (normalized === 'help' || normalized === '?') {
        return {
          output: [
            'شبیه‌ساز آموزشی CLI سمت مرورگر (Mock — بدون اتصال به تجهیز واقعی):',
            'فرمان‌های پایه: enable | configure terminal | hostname <NAME> | exit | end | clear',
            'نمونه فرمان‌های نمایش: show ip interface brief | show vlan brief | show interfaces trunk | show mac address-table | show arp | show ip route | show ip ospf neighbor | show ip bgp summary | show ip eigrp topology | show etherchannel summary | show standby brief | show policy-map interface | show ip mroute | show ip cef | show dmvpn | show ntp associations | show authentication sessions | show sdwan control connections | show sdwan bfd sessions | show netconf-yang sessions | show running-config',
            'تست اتصال شبیه‌سازی‌شده: ping <IP> | traceroute <IP>'
          ].join('\n'),
          prompt: prompt(),
          matched: true
        };
      }
      if (normalized === 'enable') {
        state.mode = 'priv';
        return { output: '', prompt: prompt(), matched: true };
      }
      if (normalized === 'disable') {
        state.mode = 'user';
        return { output: '', prompt: prompt(), matched: true };
      }
      if (normalized === 'configure terminal') {
        if (state.mode === 'user') {
          return { output: '% ابتدا با دستور enable وارد حالت Privileged EXEC (#) شوید.', prompt: prompt(), matched: false };
        }
        state.mode = 'config';
        return { output: 'Enter configuration commands, one per line. End with exit/end.', prompt: prompt(), matched: true };
      }
      if (normalized === 'exit' || normalized === 'end') {
        if (state.mode === 'config') state.mode = 'priv';
        else if (state.mode === 'priv' && normalized === 'exit') state.mode = 'user';
        return { output: '', prompt: prompt(), matched: true };
      }
      if (normalized.startsWith('hostname ')) {
        if (state.mode !== 'config') {
          return { output: '% دستور hostname فقط در حالت (config)# مجاز است. ابتدا configure terminal بزنید.', prompt: prompt(), matched: false };
        }
        const nextHost = input.slice(9).trim().replace(/[^A-Za-z0-9_-]/g, '').slice(0, 24);
        if (!nextHost) return { output: '% نام میزبان نامعتبر است.', prompt: prompt(), matched: false };
        state.host = nextHost;
        return { output: '', prompt: prompt(), matched: true };
      }
      if (normalized.startsWith('ping ')) {
        const target = input.slice(5).trim();
        if (!/^[0-9a-fA-F.:]+$/.test(target)) {
          return { output: '% قالب آدرس IP در شبیه‌ساز نامعتبر است.', prompt: prompt(), matched: false };
        }
        return {
          output: `[Simulated Mock Ping — هیچ بسته واقعی شبکه ارسال نشد]\nSending 5, 100-byte ICMP Echos to ${target}, timeout is 2 seconds:\n!!!!!\nSuccess rate is 100 percent (5/5), simulated round-trip min/avg/max = 1/2/4 ms`,
          prompt: prompt(),
          matched: true
        };
      }
      if (normalized.startsWith('traceroute ')) {
        const target = input.slice(11).trim();
        if (!/^[0-9a-fA-F.:]+$/.test(target)) {
          return { output: '% قالب آدرس IP در شبیه‌ساز نامعتبر است.', prompt: prompt(), matched: false };
        }
        return {
          output: `[Simulated Mock Traceroute — هیچ بسته واقعی ارسال نشد]\nTracing the route to ${target}\n  1 10.0.12.2 2 msec 1 msec 1 msec\n  2 ${target} 4 msec 3 msec 4 msec`,
          prompt: prompt(),
          matched: true
        };
      }

      if (Object.prototype.hasOwnProperty.call(CLI_DB, normalized)) {
        return { output: CLI_DB[normalized], prompt: prompt(), matched: true };
      }
      // Prefix fallback for common abbreviations
      const prefixHits = Object.keys(CLI_DB).filter(k => k.startsWith(normalized));
      if (prefixHits.length === 1) {
        return { output: CLI_DB[prefixHits[0]], prompt: prompt(), matched: true };
      }

      return {
        output: `% فرمان "${input}" در شبیه‌ساز آموزشی محلی تعریف نشده است. برای دیدن فرمان‌های پشتیبانی‌شده، help را وارد کنید.`,
        prompt: prompt(),
        matched: false
      };
    }

    return { execute, prompt, state };
  }

  function mount(container, bp) {
    if (!container || !bp) return null;
    const old = container.querySelector('[data-fam-cli-simulator]');
    if (old) old.remove();

    const scenario = scenarioForLesson(bp);
    const session = createSession(scenario.host);

    const card = document.createElement('section');
    card.className = 'lesson-simulator-card';
    card.setAttribute('data-fam-cli-simulator', bp.lessonId || bp.id || '');
    card.style.cssText = 'margin:22px 0;padding:16px;border-radius:12px;border:1px solid #334155;background:#0b1220;color:#e2e8f0;';

    const title = document.createElement('h3');
    title.style.cssText = 'margin:0 0 6px;font-size:16px;color:#38bdf8;';
    title.textContent = 'شبیه‌ساز تعاملی CLI مرتبط با این درس (نسخه آموزشی Mock)';

    const honesty = document.createElement('p');
    honesty.setAttribute('data-sim-honesty', '1');
    honesty.style.cssText = 'margin:0 0 10px;padding:8px 10px;border-radius:8px;background:rgba(245,158,11,0.14);border:1px solid rgba(245,158,11,0.4);color:#fde68a;font-size:12.5px;';
    honesty.textContent = 'توجه: این محیط یک شبیه‌ساز آموزشی سمت مرورگر (Mock) است؛ هیچ تجهیز واقعی شبکه، SSH یا IOS زنده متصل نیست. هدف تمرین خوانش و تفسیر خروجی فرمان‌های مرتبط با درس است.';

    const goal = document.createElement('p');
    goal.style.cssText = 'margin:0 0 10px;font-size:13px;color:#cbd5e1;';
    goal.textContent = 'هدف تمرین مرتبط با درس: ' + scenario.goal;

    const chips = document.createElement('div');
    chips.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;';

    const term = document.createElement('pre');
    term.setAttribute('dir', 'ltr');
    term.setAttribute('data-sim-output', '1');
    term.style.cssText = 'margin:0 0 10px;padding:12px;min-height:130px;max-height:300px;overflow:auto;border-radius:8px;background:#020617;border:1px solid #1e293b;color:#a7f3d0;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px;line-height:1.5;white-space:pre-wrap;';
    term.textContent = `[FAM Educational CLI Mock · Lesson: ${bp.lessonId || bp.id}]\nType "help" or click a suggested command below.\n`;

    const form = document.createElement('form');
    form.style.cssText = 'display:flex;gap:8px;align-items:center;direction:ltr;';

    const promptSpan = document.createElement('span');
    promptSpan.setAttribute('data-sim-prompt', '1');
    promptSpan.style.cssText = 'font-family:ui-monospace,monospace;font-size:13px;color:#38bdf8;white-space:nowrap;';
    promptSpan.textContent = session.prompt();

    const input = document.createElement('input');
    input.type = 'text';
    input.setAttribute('data-sim-input', '1');
    input.setAttribute('aria-label', 'ورود فرمان شبیه‌ساز CLI');
    input.placeholder = 'e.g. show ip route  or  help';
    input.style.cssText = 'flex:1;padding:8px 10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#f8fafc;font-family:ui-monospace,monospace;font-size:13px;';

    const runBtn = document.createElement('button');
    runBtn.type = 'submit';
    runBtn.className = 'btn primary';
    runBtn.textContent = 'اجرا';

    let histIndex = -1;
    function runCommand(cmdText) {
      const trimmed = String(cmdText || '').trim();
      const beforePrompt = session.prompt();
      const res = session.execute(trimmed);
      if (res.clear) {
        term.textContent = '';
      } else {
        const line = `${beforePrompt}${trimmed}\n` + (res.output ? `${res.output}\n` : '');
        term.textContent += line;
        term.scrollTop = term.scrollHeight;
      }
      promptSpan.textContent = res.prompt;
      input.value = '';
      histIndex = session.state.history.length;
      return res;
    }

    for (const cmd of [...scenario.cmds, 'help']) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'btn';
      b.setAttribute('dir', 'ltr');
      b.setAttribute('data-sim-quick', cmd);
      b.style.cssText = 'font-size:12px;padding:4px 10px;font-family:ui-monospace,monospace;';
      b.textContent = cmd;
      b.addEventListener('click', () => runCommand(cmd));
      chips.appendChild(b);
    }

    form.addEventListener('submit', e => {
      e.preventDefault();
      runCommand(input.value);
    });

    input.addEventListener('keydown', e => {
      const h = session.state.history;
      if (!h.length) return;
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        histIndex = Math.max(0, histIndex - 1);
        input.value = h[histIndex] || '';
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        histIndex = Math.min(h.length, histIndex + 1);
        input.value = h[histIndex] || '';
      }
    });

    form.append(promptSpan, input, runBtn);
    card.append(title, honesty, goal, chips, term, form);

    const quizEl = container.querySelector('[data-lesson-quiz]');
    if (quizEl && quizEl.parentElement) {
      quizEl.parentElement.insertBefore(card, quizEl);
    } else {
      container.appendChild(card);
    }
    return { card, session, runCommand };
  }

  window.FamAcademySimulator = {
    mount,
    createSession,
    scenarioForLesson,
    commandCount: Object.keys(CLI_DB).length
  };
})();
