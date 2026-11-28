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
  "show ip bgp summary": "[Educational Mock Output — NOT live router]\nBGP router identifier 10.255.0.1, local AS number 65100\nNeighbor        V           AS MsgRcvd MsgSent   TblVer  Up/Down State/PfxRcd\n10.255.0.2      4        65100     142     139       24 02:14:09           12\n198.51.100.1    4        64500     310     128       24 05:40:11          420",
  "show ip ospf neighbor": "[Educational Mock Output — NOT live router]\nNeighbor ID     Pri   State           Dead Time   Address         Interface\n10.255.0.2        1   FULL/DR         00:00:34    10.0.12.2       GigabitEthernet0/0\n10.255.0.3        0   FULL/  -        00:00:38    10.0.13.2       GigabitEthernet0/1",
  "show standby brief": "[Educational Mock Output — NOT live router]\nInterface   Grp  Pri P State   Active          Standby         Virtual IP\nVl10        10   110 P Active  local           10.10.10.3      10.10.10.1",
  "show ntp status": "Clock is synchronized, stratum 3, reference is 10.99.0.5\nnominal freq is 250.0000 Hz, actual freq is 250.0000 Hz, precision is 2**10",
  "show access-lists": "Extended IP access list 110\n    10 deny tcp 192.168.10.0 0.0.0.255 host 10.50.0.10 eq 22 (14 matches)\n    20 permit ip any any (382 matches)",
  "show interfaces gi0/2 switchport": "Name: Gi0/2\nSwitchport: Enabled\nAdministrative Mode: static access",
  "show spanning-tree": "VLAN0001\n  Spanning tree enabled protocol rstp\n  Root ID    Priority    24577\n             Address     0050.56ab.1100",
  "show interfaces gi0/3 switchport": "Name: Gi0/3\nSwitchport: Enabled\nAdministrative Mode: static access",
  "show ip cef": "[Educational Mock Output — NOT live router]\nPrefix               Next Hop             Interface\n0.0.0.0/0            198.51.100.1         GigabitEthernet0/0\n10.10.0.0/24         attached             Vlan10 (Adjacency ready)\n10.20.1.0/24         10.0.12.2            GigabitEthernet0/1",
  "show interfaces tunnel0": "Tunnel0 is up, line protocol is up\n  Hardware is Tunnel\n  MTU 17916 bytes, BW 100 Kbit/sec, DLY 50000 usec\n  Tunnel source 203.0.113.1 (GigabitEthernet0/0), destination 198.51.100.2\n  Tunnel protocol/transport GRE/IP",
  "show dmvpn": "[Educational Mock Output — NOT live router]\nInterface: Tunnel0, IPv4 NHRP Details\nType:Spoke, NHRP Peers:2 (Phase 3 Redirect/Shortcut enabled)\n # Ent  Peer NBMA Addr Peer Tunnel Add State  UpDn Tm Attrb\n ----- --------------- --------------- ----- -------- -----\n     1 203.0.113.10       172.16.0.1      UP 04:12:10     S\n     1 203.0.113.22       172.16.0.3      UP 00:08:44     D (Shortcut)",
  "show isis neighbors": "Tag UNDERLAY:\nSystem Id       Type Interface   IP Address      State Holdtime Circuit Id\nR2-BORDER       L2   Gi0/0       10.10.0.2       UP    27       00",
  "show clns interface gi0/0": "GigabitEthernet0/0 is up, line protocol is up\n  Checksums enabled, MTU 1497, Encapsulation SAP\n  ERPDUs enabled, min. interval 10 msec.\n  CLNS fast switching enabled\n  Routing Protocol: IS-IS (UNDERLAY)\n    Circuit Type: level-2-only",
  "show authentication sessions interface gi0/6 details": "Interface:  GigabitEthernet0/6\nMAC Address:  0200.0000.0066\nIPv4 Address: 10.10.10.66\nStatus:  Authorized\nDomain:  DATA\nOper Host Mode:  multi-auth\nMethod status list:\n   Method           State\n   dot1x            Authc Success",
  "show cts role-based sgt-map all": "Active IPv4-SGT Bindings Information\nIP Address              SGT     Source\n--------------------------------------------\n10.10.10.66             15      LOCAL",
  "show mpls forwarding-table": "Local      Outgoing   Prefix           Bytes Label   Outgoing   Next Hop\nLabel      Label      or Tunnel Id     Switched      interface\n16         Pop Label  10.255.0.2/32    418200        Gi0/0      10.10.0.2\n17         24         10.255.0.3/32    920140        Gi0/0      10.10.0.2\n18         No Label   10.50.1.0/24[V]  12840         Gi0/6      10.50.1.2",
  "show bgp vpnv4 unicast all summary": "BGP router identifier 10.255.0.1, local AS number 65100\nNeighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd\n10.255.0.2      4 65100     840     835       42    0    0 04:12:08       12",
  "show wireless summary": "Wireless Summary:\nTotal APs: 24 (Up: 24)\nTotal Clients: 312 (802.11ax: 240, 802.11ac: 72)",
  "show ap tag summary": "AP Name          Policy Tag     Site Tag       RF Tag\n--------------------------------------------------------\nAP-FL3-01        CORP_PTAG      BRANCH_FLEX    OFFICE_RF",
  "show ip dhcp binding": "Bindings from all pools not associated with VRF:\nIP address      Client-ID/Hardware address     Lease expiration        Type\n192.168.10.21   0102.0000.0010.21              Nov 24 2026 04:12 PM    Automatic",
  "show ip nat translations": "Pro Inside global      Inside local       Outside local      Outside global\ntcp 203.0.113.10:51200 192.168.10.10:51200 198.51.100.80:443 198.51.100.80:443\ntcp 203.0.113.10:51201 192.168.10.11:51200 198.51.100.80:443 198.51.100.80:443",
  "show ip ssh": "SSH Enabled - version 2.0\nAuthentication timeout: 120 secs; Authentication retries: 3",
  "show crypto isakmp sa": "IPv4 Crypto ISAKMP SA\ndst             src             state          conn-id status\n203.0.113.2     203.0.113.1     QM_IDLE        1001    ACTIVE",
  "show vlan private-vlan": "[Educational Mock Output — NOT live Catalyst switch]\nPrimary Secondary Type              Ports\n------- --------- ----------------- ------------------------------------------\n100     101       isolated          Gi1/0/1, Gi1/0/2, Gi1/0/24\n100     102       community         Gi1/0/5, Gi1/0/6, Gi1/0/24",
  "show etherchannel summary": "[Educational Mock Output — NOT live switch]\nFlags:  D - down        P - bundled in port-channel\n        I - stand-alone s - suspended\nGroup  Port-channel  Protocol    Ports\n------+-------------+-----------+-----------------------------------------------\n1      Po1(RU)         LACP      Gi1/0/21(P) Gi1/0/22(P) Gi1/0/23(P) Gi1/0/24(P)",
  "show policy-map interface gi0/0": "GigabitEthernet0/0\n  Service-policy output: WAN-OUT\n    Class-map: VOICE (match-all)\n      0 packets, 0 bytes\n      Priority: 20% (20000 kbps), burst bytes 500000, b/w exceed drops: 0",
  "show ip mroute": "[Educational Mock Output — NOT live router]\n(*, 239.10.10.10), 01:12:04/stopped, RP 10.255.0.10, flags: SJC\n  Incoming interface: GigabitEthernet0/0, RPF nbr 10.0.12.2\n  Outgoing interface list: GigabitEthernet0/1, Forward/Sparse",
  "show bfd neighbors": "IPv4 Sessions\nNeighAddr                              LD/RD         RH/RS     State     Int\n10.10.0.2                               1/2          Up        Up        Gi0/0",
  "show policy-map control-plane": "Control Plane\n  Service-policy input: COPP_POLICY\n    Class-map: CM_ROUTING (match-all)\n      Match: access-group name ACL_ROUTING\n      police: cir 512000 bps, bc 16000 bytes\n        conformed 4210 packets, 310200 bytes; actions: transmit\n        exceeded 0 packets, 0 bytes; actions: drop",
  "show event manager policy registered": "No.  Class     Type    Event Type          Trap  Time Registered           Name\n1    applet    user    syslog              Off   Mon Nov 23 09:12:04 2026  WAN_DOWN_ALERT",
  "show sdwan omp routes": "[Educational Mock Output — NOT live SD-WAN router]\nVPN  PREFIX          FROM PEER     TLOC IP      COLOR         STATUS\n---------------------------------------------------------------------\n10   10.200.10.0/24  10.255.0.100  10.255.2.1   mpls          C,I,R\n10   10.200.10.0/24  10.255.0.100  10.255.2.1   biz-internet  C,I,R",
  "show sdwan app-route stats": "app-route statistics 10.255.0.12 10.255.0.14\n remote-system-ip  local-color  remote-color  mean-loss  mean-latency  mean-jitter\n 10.255.0.14       mpls         mpls          0.00%      18            2\n 10.255.0.14       biz-internet biz-internet  2.40%      95            18",
  "show netconf-yang sessions": "[Educational Mock Output — NOT live IOS-XE device]\nNumber of sessions : 1\nsession-id  transport    username    source-host    global-lock\n---------------------------------------------------------------\n42          netconf-ssh  netops      10.255.99.5    None",
  "show ip bgp neighbors 203.0.113.2 advertised-routes": "BGP table version is 19, local router ID is 10.255.0.1\n   Network          Next Hop            Metric LocPrf Weight Path\n*> 10.128.0.0/16    0.0.0.0                  0         32768 i\n\nTotal number of prefixes 1",
  "show app-hosting list": "App id                                   State\n---------------------------------------------------------\nthousandeyes_enterprise_agent            RUNNING",
  "show stackwise-virtual link": "Stackwise Virtual Link(SVL) Information:\nFlags: LC - Link configured, U - Up, D - Down, R - Removed\nSwitch  SVL     Ports                           Link-Status\n------  ---     -----                           -----------\n1       1       HundredGigE1/0/49               U\n                HundredGigE1/0/50               U\n2       1       HundredGigE2/0/49               U\n                HundredGigE2/0/50               U",
  "show stackwise-virtual dual-active-detection": "In Dual-Active Detection:\nRecovery Mode: Enabled\nDual-Active-Detection Links:\nSwitch  Dad port                        Status\n------  --------                        ------\n1       TenGigabitEthernet1/0/1         up\n2       TenGigabitEthernet2/0/1         up",
  "show pnp trace": "PnP Discovery Status: Option 43 found -> Controller 10.10.20.5\nSUDI Certificate verified; Waiting for Day-0 configuration push...",
  "show sdwan control connections": "[Educational Mock Output — NOT live SD-WAN router]\nPEER    PEER TYPE  PROTOCOL  SYSTEM IP     SITE ID  DOMAIN ID  STATE\n---------------------------------------------------------------------\nvsmart  vsmart     dtls      10.255.0.100  1        1          up\nvbond   vbond      dtls      10.255.0.101  1        0          up\nvmanage vmanage    dtls      10.255.0.102  1        0          up",
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
  "show ip eigrp topology": "[Educational Mock Output — NOT live router]\nEIGRP-IPv4 Topology Table for AS(100)/ID(10.255.0.1)\nP 10.50.0.0/24, 1 successors, FD is 1500\n        via 10.0.12.2 (1500/1000), GigabitEthernet0/0\n        via 10.0.13.2 (2600/1400), GigabitEthernet0/1  [Feasible Successor: RD < FD]",
  "show policy-map interface": "[Educational Mock Output — NOT live router]\nGigabitEthernet0/0\n  Service-policy output: PARENT_SHAPE\n    Class-map: class-default (match-any)\n      shape (average) cir 200000000, bc 2000000, be 2000000\n      Service-policy : CHILD_QOS\n        Class-map: VOICE (match-any) -> Priority: 20%, Match dscp ef (46), Drops: 0\n        Class-map: class-default -> random-detect dscp-based (WRED active)",
  "show ip rpf 10.20.1.50": "[Educational Mock Output — NOT live router]\nRPF information for ? (10.20.1.50)\n  RPF interface: GigabitEthernet0/0\n  RPF neighbor: ? (10.0.12.2)\n  RPF route/mask: 10.20.1.0/24\n  RPF type: unicast (ospf 1)",
  "show ntp associations": "[Educational Mock Output — NOT live router]\n  address         ref clock       st   when   poll reach  delay  offset   disp\n*~10.255.0.10     .GPS.            1     18     64   377  1.210  -0.042  0.315\n+~10.255.0.11     10.255.0.10      2     22     64   377  1.840  +0.019  0.410",
  "show authentication sessions": "[Educational Mock Output — NOT live switch]\nInterface  MAC Address     Method   Domain   Status         Session ID\nGi1/0/10   0050.56ab.1101  dot1x    DATA     Authz Success  0A0A0A0100000012\nGi1/0/11   0050.56ab.2202  mab      DATA     Authz Success  0A0A0A0100000013",
  "show sdwan bfd sessions": "[Educational Mock Output — NOT live SD-WAN router]\nSITE  SYSTEM IP    SRC COLOR     DST COLOR     STATE  LOSS%  LATENCY(ms)  JITTER(ms)\n-------------------------------------------------------------------------------------\n200   10.255.2.1   mpls          mpls          up     0.0    18           2\n200   10.255.2.1   biz-internet  biz-internet  up     0.1    34           4",
  "show vlan brief": "[Educational Mock Output — NOT live switch]\nVLAN Name                             Status    Ports\n---- -------------------------------- --------- -------------------------------\n1    default                          active    Gi0/10\n10   SALES                            active    Gi0/1, Gi0/2\n20   ENGINEERING                      active    Gi0/3, Gi0/4\n50   VOICE                            active    Gi0/1, Gi0/2\n999  BLACKHOLE                        active    Gi0/20",
  "show running-config": "! Simulated Educational Running-Config (Client-Side Mock — NOT live IOS)\nhostname FAM-LAB-R1\n!\nip cef\n!\ninterface GigabitEthernet0/0\n description Uplink-Core\n ip address 10.0.12.1 255.255.255.252\n ip ospf network point-to-point\n!\nrouter ospf 1\n router-id 10.255.0.1\n passive-interface default\n no passive-interface GigabitEthernet0/0\n!\nend",
  "show standby": "[Educational Mock Output — NOT live router]\nVlan10 - Group 10 (version 2)\n  State is Active\n  Virtual IP address is 10.10.10.1\n  Active virtual MAC address is 0000.0c9f.f00a\n  Hello time 3 sec, hold time 10 sec\n  Preemption enabled, delay min 60 secs\n  Priority 110 (configured 110)\n    Track object 10 state Up decrement 20",
  "show track": "[Educational Mock Output — NOT live router]\nTrack 10\n  IP SLA 10 reachability\n  Reachability is Up (3 changes, last change 01:42:15)\n  Tracked by: HSRP Vlan10 10 (decrement 20)",
  "show cdp neighbors": "[Educational Mock Output — NOT live switch]\nDevice ID        Local Intrfce     Holdtme    Capability  Platform  Port ID\nCORE-SW1.lab     Gig 1/0/24        148         R S I      C9500     Gig 1/0/1\nSEP005056AB1101  Gig 1/0/10        162         H P M      IP Phone  Port 1",
  "show cdp neighbors detail": "[Educational Mock Output — NOT live switch]\nDevice ID: CORE-SW1.lab\nEntry address(es): IP address: 10.255.0.2\nPlatform: cisco C9500-48Y4C, Capabilities: Router Switch IGMP\nInterface: GigabitEthernet1/0/24, Port ID (outgoing port): GigabitEthernet1/0/1\nHoldtime : 148 sec | Version: Cisco IOS XE Software (simulated)",
  "show interfaces": "[Educational Mock Output — NOT live device]\nGigabitEthernet0/0 is up, line protocol is up (connected)\n  Hardware is CSR vNIC, address is 0050.56ab.0101\n  Internet address is 10.0.12.1/30\n  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec\n  5 minute input rate 142000 bits/sec, 0 input errors, 0 CRC, 0 output drops",
  "show interface tunnel": "[Educational Mock Output — NOT live device]\nTunnel0 is up, line protocol is up\n  Internet address is 172.16.0.1/30, MTU 1400 bytes, TCP MSS 1360\n  Tunnel source 198.51.100.1 (Gi0/0), destination 203.0.113.2\n  Tunnel protocol/transport GRE/IP (IPsec profile IPSEC_PROF active)",
  "show ip bgp": "[Educational Mock Output — NOT live router]\nBGP table version is 24, local router ID is 10.255.0.1\nStatus codes: * valid, > best, i - internal\n   Network          Next Hop            Metric LocPrf Weight Path\n*> 10.50.0.0/24     198.51.100.1             0    150      0 64500 64600 i\n*  10.50.0.0/24     203.0.113.1              0    100      0 64501 i",
  "show ip bgp vpnv4": "[Educational Mock Output — NOT live PE router]\nRoute Distinguisher: 65100:10 (default for vrf CORP)\n   Network          Next Hop            Metric LocPrf Weight Path\n*> 10.10.1.0/24     0.0.0.0                  0         32768 ?\n*>i10.10.2.0/24     10.255.0.22              0    100      0 ? (label 24010)",
  "show ip vrf": "[Educational Mock Output — NOT live router]\n  Name                             Default RD            Interfaces\n  CORP                             65100:10              Gi0/1.10\n  OT_ISOLATED                      65100:20              Gi0/1.20",
  "show ip cef vrf": "[Educational Mock Output — NOT live router]\nVRF CORP CEF Table:\nPrefix               Next Hop             Interface\n10.10.1.0/24         attached             GigabitEthernet0/1.10\n10.10.2.0/24         10.255.0.22          MPLS label [16022, 24010]",
  "show ip policy": "[Educational Mock Output — NOT live router]\nInterface      Route map\nVlan10         PBR_GUEST_WAN (match ACL 120 -> set ip next-hop 203.0.113.1)",
  "show mpls interfaces": "[Educational Mock Output — NOT live router]\nInterface              IP            Tunnel   BGP Static Operational\nGigabitEthernet0/0     Yes (ldp)     No       No  No     Yes\nGigabitEthernet0/1     Yes (ldp)     No       No  No     Yes",
  "show mpls ldp neighbors": "[Educational Mock Output — NOT live router]\nPeer LDP Ident: 10.255.0.2:0; Local LDP Ident 10.255.0.1:0\n  TCP connection: 10.255.0.2.646 - 10.255.0.1.49152\n  State: Oper; Msgs sent/rcvd: 812/815; Up time: 03:20:11",
  "show mpls l3vpn routes": "[Educational Mock Output — NOT live PE router]\nVRF CORP (RT import/export 65100:10):\n  10.10.1.0/24  connected   Gi0/1.10      local label: 24001\n  10.10.2.0/24  via 10.255.0.22 (BGP VPNv4) label stack: [16022, 24010]",
  "show policy-map": "[Educational Mock Output — NOT live router]\nPolicy Map PARENT_SHAPE\n  Class class-default -> Average Rate Traffic Shaping cir 200000000 (bps)\n  service-policy CHILD_QOS\nPolicy Map CHILD_QOS\n  Class VOICE -> priority percent 20 (DSCP EF 46)\n  Class class-default -> random-detect dscp-based (WRED)",
  "show crypto ipsec sa": "[Educational Mock Output — NOT live router]\ninterface: Tunnel0 | Crypto map tag: Tunnel0-head-0\n  local ident (addr/mask/prot/port): (0.0.0.0/0.0.0.0/0/0)\n  current_peer 203.0.113.2 port 4500\n  #pkts encaps: 1420, #pkts decaps: 1418, #pkts decrypt errors: 0\n  inbound esp sas: spi 0xA1B2C3D4, transform: esp-gcm 256",
  "show crypto pki certificates verbose": "[Educational Mock Output — NOT live router]\nCertificate (Trustpoint CORP_PKI):\n  Status: Available | Serial: 0x4A91F02C\n  Subject: CN=edge-r1.corp.example | SAN: DNS:edge-r1.corp.example\n  Issuer: CN=CORP-SubCA-01 | Key: RSA 2048 | Valid: 2026-01-01 to 2028-01-01",
  "show cts sgt": "[Educational Mock Output — NOT live switch]\nSGT-to-Name Table (Cisco TrustSec):\n  SGT 2  : TrustSec_Devices\n  SGT 10 : Employees\n  SGT 20 : Contractors (restricted policy)\n  SGT 50 : PCI_Servers",
  "show ip inspect": "[Educational Mock Output — NOT live router]\nZone-Based Firewall / Inspect Policy Summary:\n  Zone-Pair INSIDE_TO_OUTSIDE -> policy-map ZBFW_OUT (inspect TCP/UDP/ICMP)\n  Active sessions: 42 | Half-open sessions: 1",
  "show ip inspect sessions": "[Educational Mock Output — NOT live router]\nEstablished Sessions (Simulated):\n  Session 101: TCP 10.10.1.25:51420 -> 198.51.100.50:443 (SIS_OPEN, ttl 3590s)\n  Session 102: UDP 10.10.1.25:53112 -> 198.51.100.53:53  (SIS_OPEN, ttl 28s)",
  "show ip http server status": "[Educational Mock Output — NOT live router]\nHTTP server status: Disabled (hardened)\nHTTP secure server status: Enabled | Port: 443\nHTTP secure server ciphersuite: TLS 1.3 / ECDHE-RSA-AES256-GCM-SHA384",
  "show redundancy": "[Educational Mock Output — NOT live chassis]\nRedundant System Information:\n  Configured Redundancy Mode = sso\n  Operating Redundancy Mode  = sso\n  Active Supervisor: Slot 3 (ACTIVE) | Standby Supervisor: Slot 4 (STANDBY HOT)",
  "show platform software": "[Educational Mock Output — NOT live IOS-XE device]\nPlatform Software Status Summary:\n  Control-Plane CPU (5s/1m/5m): 4% / 5% / 4%\n  Memory Used: 41% | Forwarding Engine (QFP/FED): Healthy",
  "show vpc": "[Educational Mock Output — NOT live Nexus switch]\nvPC domain id                     : 10\nPeer status                       : peer adjacency formed ok\nvPC keep-alive status             : peer is alive\nConfiguration consistency status  : success\nvPC role                          : primary",
  "show fex": "[Educational Mock Output — NOT live Nexus switch]\n  FEX         FEX           FEX                       FEX\nNumber    Description      State            Model            Serial\n------------------------------------------------------------------------\n101       TOR-RACK-A1      Online           N2K-C2348UPQ     FOC2101SIM1",
  "show vxlan": "[Educational Mock Output — NOT live VTEP]\nVXLAN Interface: nve1 (UDP port 4789, Source Loopback1 10.255.1.11)\n  VNI 10010 (L2, VLAN 10) -> Control-Plane: BGP EVPN | State: Up\n  VNI 50001 (L3, VRF CORP) -> Anycast Gateway active | State: Up",
  "show ap summary": "[Educational Mock Output — NOT live WLC 9800]\nNumber of APs: 2\nAP Name         Slots  AP Model       IP Address     State       Location\n----------------------------------------------------------------------------\nAP-FL1-WEST     3      C9130AXI-B     10.10.185.21   Registered  Floor-1\nAP-FL2-EAST     3      C9130AXI-B     10.10.185.22   Registered  Floor-2",
  "show sip-ua calls": "[Educational Mock Output — NOT live CUBE / Voice Gateway]\nTotal SIP call legs: 2, User Agent Client: 1, User Agent Server: 1\n  Call 1 (UAC): Call-ID=sim-8821@10.30.0.10 | State=STATE_ACTIVE | Codec=G.711ulaw\n  Call 2 (UAS): Call-ID=sim-8822@198.51.100.20 | State=STATE_ACTIVE | RTP=10.30.0.10:16402",
  "show sip-ua register": "[Educational Mock Output — NOT live CUBE / Voice Gateway]\nLine                             peer       expires(sec) reg survival P-Associ-URI\n================================ ========== ============ === ======== ============\n2100                             20001      2840         yes normal   sip:2100@sip.example",
  "show call active voice compact": "[Educational Mock Output — NOT live Voice Gateway]\n <callID>  A/O FAX T<sec> Codec       type        Peer Address       IP R<ip>:<udp>\nTotal call-legs: 2\n   1042    ORG     T124   g711ulaw    VOIP        P2100              10.30.0.10:16402\n   1043    ANS     T124   g711ulaw    VOIP        P98215550100       198.51.100.20:18204",
  "show voice call summary": "[Educational Mock Output — NOT live Voice Gateway]\nPORT           CODEC     VAD VTSP STATE            VPM STATE\n============== ========= === ==================== ======================\n0/1/0:15.1     g711ulaw   n  S_CONNECT             S_UP (Active simulated call)",
  "show dial-peer voice": "[Educational Mock Output — NOT live Voice Gateway]\ndial-peer voice 100 voip (Up/Up) | destination-pattern 2... | session protocol sipv2\ndial-peer voice 200 voip (Up/Up) | destination-pattern 9T   | session target ipv4:198.51.100.20",
  "show netconf-yang datastores": "[Educational Mock Output — NOT live IOS-XE device]\nDatastore Name : running   (read-write, active)\nDatastore Name : candidate (read-write, lock/validate/commit supported)",
  "show netconf-yang modules": "[Educational Mock Output — NOT live IOS-XE device]\nietf-interfaces              (2018-02-20)\nopenconfig-interfaces        (2021-04-06)\nCisco-IOS-XE-native          (2023-07-01)",
  "show restconf status": "[Educational Mock Output — NOT live IOS-XE device]\nRESTCONF service status: Enabled (HTTPS port 443, media-type application/yang-data+json)",
  "show run | section netconf": "[Educational Mock Output — NOT live IOS-XE device]\nnetconf-yang\nrestconf",
  "show yang": "[Educational Mock Output — NOT live IOS-XE device]\nYANG Management Plane: netconf-yang=Active | restconf=Active | gNMI=Active",
  "terraform plan": "[Educational Mock Output — NOT live Terraform CLI or cloud API]\nTerraform used the selected providers to generate the following execution plan:\n  # fam_vlan.sales will be created\n  + resource \"fam_vlan\" \"sales\" {\n      + id   = 10\n      + name = \"SALES\"\n    }\nPlan: 1 to add, 0 to change, 0 to destroy. (Dry-run simulation only)",
  "terraform apply": "[Educational Mock Output — NOT live Terraform CLI or cloud API]\nApply complete (simulated)! Resources: 1 added, 0 changed, 0 destroyed.\nNote: No real infrastructure or remote state backend was modified.",
  "ansible-playbook site.yml --check --diff": "[Educational Mock Output — NOT live Ansible run]\nPLAY [Configure Core VLANs] ************************************\nTASK [Ensure VLAN 10 exists] *** changed: [sw1] (check-mode diff: +vlan 10 / name SALES)\nPLAY RECAP: sw1 : ok=2 changed=1 unreachable=0 failed=0 (--check dry-run)",
  "ansible -i inventory.yml ios_routers -m cisco.ios.ios_command -a \"commands='show version'\"": "[Educational Mock Output — NOT live Ansible SSH execution]\nr1.lab | SUCCESS => {\"changed\": false, \"stdout\": [\"Cisco IOS XE Software (Simulated Mock)\"]}",
  "git status && git diff --staged": "[Educational Mock Output — NOT live Git repo]\nOn branch feat/vlan-automation\nChanges to be committed:\n  modified:   inventory/vlans.yml\ndiff --git a/inventory/vlans.yml b/inventory/vlans.yml\n+  - id: 50\n+    name: VOICE",
  "git switch -c feat/vlan-automation": "[Educational Mock Output — NOT live Git repo]\nSwitched to a new branch 'feat/vlan-automation'",
  "curl -i -h \"accept: application/json\" --cacert corp-ca.pem https://10.255.0.1/api/v1/vlans": "[Educational Mock Output — NOT live HTTP/TLS request]\nHTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"vlans\": [{\"id\": 10, \"name\": \"SALES\"}, {\"id\": 50, \"name\": \"VOICE\"}]}",
  "ssh -p 830 admin@10.255.0.1 -s netconf": "[Educational Mock Output — NOT live SSH/NETCONF session]\n<hello xmlns=\"urn:ietf:params:xml:ns:netconf:base:1.0\">\n  <capabilities>\n    <capability>urn:ietf:params:netconf:base:1.1</capability>\n    <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>\n  </capabilities>\n  <session-id>42</session-id>\n</hello>]]>]]>",
  "openssl s_client -connect 10.255.0.1:443 -tls1_3 -showcerts": "[Educational Mock Output — NOT live TLS handshake]\nCONNECTED (simulated)\nProtocol  : TLSv1.3 | Cipher : TLS_AES_256_GCM_SHA384\nSubject   : CN=api.corp.example | Verify return code: 0 (ok)",
  "python3 -m json.tool device.json": "[Educational Mock Output — NOT live filesystem]\n{\n  \"hostname\": \"R1-CORE\",\n  \"mgmt_ip\": \"10.255.0.1\",\n  \"bgp_asn\": 65100\n}",
  "python3 -m venv .venv": "[Educational Mock Output — NOT live shell]\nCreated isolated Python virtual environment at ./.venv (simulated).",
  "pip freeze > requirements.txt": "[Educational Mock Output — NOT live shell]\nPinned dependencies written to requirements.txt (simulated: requests==2.32.3, PyYAML==6.0.2).",
  "yamllint hosts.yaml": "[Educational Mock Output — NOT live linter]\nhosts.yaml: 0 errors, 0 warnings (YAML syntax valid — simulated).",
  "ip -br addr show": "[Educational Mock Output — NOT live Linux host]\nlo               UNKNOWN        127.0.0.1/8 ::1/128\neth0             UP             10.10.20.15/24 fe80::50:56ff:feab:1001/64",
  "ss -tulnp": "[Educational Mock Output — NOT live Linux host]\nNetid State  Recv-Q Send-Q Local Address:Port  Peer Address:Port Process\ntcp   LISTEN 0      128    0.0.0.0:22          0.0.0.0:*         users:((\"sshd\",pid=901))\ntcp   LISTEN 0      128    127.0.0.1:8765      0.0.0.0:*         users:((\"python3\",pid=1420))",
  "nso_cli --context admin show devices": "[Educational Mock Output — NOT live Cisco NSO]\nNAME      ADDRESS      PORT  NED-ID               ADMIN-STATE\nedge-r1   10.255.0.1   830   cisco-iosxe-nc-7.9   unlocked\ncore-sw1  10.255.0.2   830   cisco-iosxe-nc-7.9   unlocked",
  "nso_cli --context admin show services": "[Educational Mock Output — NOT live Cisco NSO]\nSERVICE-INSTANCE         DEVICES             SYNC-STATUS\nl3vpn-corp-site1         edge-r1, core-sw1   in-sync",
  "show version": "[Educational Mock Output — NOT live Cisco IOS-XE]\nCisco IOS XE Software, Version 17.09.04a (Simulated Educational Model)\nCisco IOS Software [Cupertino], Catalyst L3 Switch / C8000V Software, Version 17.9.4a\nSystem image file is \"bootflash:packages.conf\"\nUptime is 14 days, 6 hours, 22 minutes (simulated)\nConfiguration register is 0x2102",
  "show ip protocols": "[Educational Mock Output — NOT live router]\n*** IP Routing is NSF aware ***\nRouting Protocol is \"ospf 1\"\n  Outgoing update filter list for all interfaces is not set\n  Router ID 10.255.0.1\n  Number of areas in this router is 1. 1 normal 0 stub 0 nssa\n  Routing for Networks:\n    10.0.12.0 0.0.0.3 area 0\n    10.10.0.0 0.0.255.255 area 0\n  Routing Information Sources:\n    Gateway         Distance      Last Update\n    10.255.0.2           110      00:08:14\n  Distance: (default is 110)",
  "show ip ospf interface": "[Educational Mock Output — NOT live router]\nGigabitEthernet0/0 is up, line protocol is up\n  Internet Address 10.0.12.1/30, Interface ID 1, Area 0\n  Process ID 1, Router ID 10.255.0.1, Network Type POINT_TO_POINT, Cost: 1\n  Transmit Delay is 1 sec, State POINT_TO_POINT\n  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5\n  Adjacent with neighbor 10.255.0.2 (FULL)",
  "show ip ospf interface brief": "[Educational Mock Output — NOT live router]\nInterface    PID   Area            IP Address/Mask    Cost  State Nbrs F/C\nLo0          1     0               10.255.0.1/32      1     LOOP  0/0\nGi0/0        1     0               10.0.12.1/30       1     P2P   1/1\nGi0/1        1     0               10.10.10.1/24      1     DR    0/0",
  "show ip ospf database": "[Educational Mock Output — NOT live router]\n            OSPF Router with ID (10.255.0.1) (Process ID 1)\n                Router Link States (Area 0)\nLink ID         ADV Router      Age         Seq#       Checksum Link count\n10.255.0.1      10.255.0.1      412         0x80000007 0x00A14C 3\n10.255.0.2      10.255.0.2      398         0x80000006 0x008F12 2",
  "show ip eigrp neighbors": "[Educational Mock Output — NOT live router]\nEIGRP-IPv4 Neighbors for AS(100)\nH   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq\n                                                   (sec)         (ms)       Cnt Num\n0   10.0.12.2               Gi0/0                    12 04:18:10   11   100  0  48",
  "show ip bgp neighbors": "[Educational Mock Output — NOT live router]\nBGP neighbor is 10.0.12.2,  remote AS 65200, external link\n  BGP version 4, remote router ID 10.255.0.2\n  BGP state = Established, up for 03:42:19\n  Hold time is 180, keepalive interval is 60 seconds\n  Address tracking is enabled, the RIB does have a route to 10.0.12.2\n  Prefixes Current: 24 (Consumes 4224 bytes)",
  "show startup-config": "[Educational Mock Output — NOT live router]\n! Simulated NVRAM startup-config\nhostname FAM-LAB\ninterface GigabitEthernet0/0\n ip address 10.0.12.1 255.255.255.252\n no shutdown\nend",
  "show lldp neighbors": "[Educational Mock Output — NOT live switch]\nCapability codes: (R) Router, (B) Bridge, (T) Telephone, (W) WLAN Access Point\nDevice ID           Local Intf     Hold-time  Capability      Port ID\nDIST-SW2            Gi0/0          120        B,R             Gi0/0\nAP-FLOOR2           Gi0/2          120        W,B             Gi0"
};

  const ALIASES = {
    'sh ver': 'show version',
    'sh ip prot': 'show ip protocols',
    'sh ip ospf int': 'show ip ospf interface',
    'sh ip ospf int br': 'show ip ospf interface brief',
    'sh ip ospf db': 'show ip ospf database',
    'sh ip eigrp nei': 'show ip eigrp neighbors',
    'sh ip bgp nei': 'show ip bgp neighbors',
    'sh start': 'show startup-config',
    'sh lldp nei': 'show lldp neighbors',
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
    'sh cdp nei': 'show cdp neighbors',
    'sh vpc': 'show vpc',
    'conf t': 'configure terminal',
    'en': 'enable'
  };

  // Explicit per-lesson scenarios (exact matchType='exact').
  // Lessons not listed here use an honest track/domain default (matchType='track-default').
  const LESSON_SCENARIOS = {
    'academy-stage-zero-osi-fa': { host: 'HOST-OSI', goal: 'مشاهده وضعیت اینترفیس، جدول ARP و مسیر لایه ۳ در سفر بسته OSI', cmds: ['show interfaces status', 'show arp', 'show ip route'] },
    s02: { host: 'SW-L2', goal: 'بررسی جدول MAC، فریم Ethernet و کش ARP', cmds: ['show mac address-table', 'show arp', 'show interfaces status'] },
    s10: { host: 'SW-VLAN', goal: 'بررسی VLANها و لینک ترانک 802.1Q', cmds: ['show vlan brief', 'show interfaces trunk', 'show mac address-table'] },
    s11: { host: 'LEAF-01', goal: 'بررسی معماری Leaf-Spine، EVPN و VXLAN NVE Peers', cmds: ['show bgp l2vpn evpn summary', 'show nve peers', 'show vxlan'] },
    s12: { host: 'AUTO-XE1', goal: 'بررسی نشست‌های NETCONF/YANG و وضعیت RESTCONF', cmds: ['show netconf-yang sessions', 'show restconf status', 'show yang'] },
    ccna_01: { host: 'R1-CORE', goal: 'بررسی وضعیت اینترفیس‌های IP و جدول مسیریابی پایه', cmds: ['show ip interface brief', 'show interfaces', 'show ip route'] },
    ccna_02: { host: 'SW1-STP', goal: 'بررسی درخت پوشا (STP)، VLAN و EtherChannel', cmds: ['show spanning-tree', 'show vlan brief', 'show etherchannel summary'] },
    ccna_02_vlan: { host: 'SW-VLAN', goal: 'بررسی پورت‌های Access/Trunk، جدول MAC و هرس VLAN', cmds: ['show vlan brief', 'show interfaces trunk', 'show mac address-table'] },
    ccna_v1: { host: 'SW-CORE', goal: 'بررسی اینترفیس‌ها، CDP و توپولوژی پایه', cmds: ['show interfaces status', 'show cdp neighbors', 'show ip interface brief'] },
    ccna_v6: { host: 'R1-RIB', goal: 'بررسی جدول مسیریابی RIB و جدول فوروارد CEF', cmds: ['show ip route', 'show ip cef', 'show ip ospf neighbor'] },
    ccna_acl: { host: 'R1-EDGE', goal: 'بررسی Access-List و سیاست‌های فیلتر بسته', cmds: ['show access-lists', 'show ip interface brief', 'show running-config'] },
    ccna_dhcp: { host: 'R1-DHCP', goal: 'بررسی نگاشت‌های فعال DHCP و جدول ARP', cmds: ['show ip dhcp binding', 'show arp', 'show ip interface brief'] },
    ccna_nat: { host: 'R1-NAT', goal: 'بررسی جدول ترجمه NAT/PAT و اینترفیس‌های Inside/Outside', cmds: ['show ip nat translations', 'show ip interface brief', 'show ip route'] },
    ccna_qos_ssh: { host: 'R1-SEC', goal: 'بررسی وضعیت SSH نسخه ۲ و سیاست QoS اینترفیس', cmds: ['show ip ssh', 'show policy-map interface', 'show running-config'] },
    ccna_wl: { host: 'WLC-9800', goal: 'بررسی وضعیت APها و کانال‌های بی‌سیم ۵ گیگاهرتز', cmds: ['show ap summary', 'show ap dot11 5ghz summary', 'show wireless summary'] },
    adv_01: { host: 'DIST-SW1', goal: 'بررسی STP و وضعیت StackWise Virtual', cmds: ['show spanning-tree', 'show stackwise-virtual link', 'show stackwise-virtual dual-active-detection'] },
    adv_02: { host: 'ABR-R1', goal: 'بررسی همسایگی‌های OSPF و جدول مسیر', cmds: ['show ip ospf neighbor', 'show ip route', 'show ip cef'] },
    adv_03: { host: 'R1-VRF', goal: 'بررسی VRFها، Track/IP SLA و جدول CEF هر VRF', cmds: ['show ip vrf', 'show track', 'show ip cef vrf'] },
    adv_04: { host: 'R1-MTU', goal: 'بررسی اینترفیس تونل GRE/IPsec، CEF و مسیر', cmds: ['show interface tunnel', 'show crypto ipsec sa', 'show ip cef'] },
    adv_bfd: { host: 'R1-BFD', goal: 'بررسی نشست‌های BFD و همسایگی‌های مسیریابی', cmds: ['show bfd neighbors', 'show ip ospf neighbor', 'show ip bgp summary'] },
    adv_pvl: { host: 'SW-PVLAN', goal: 'بررسی نگاشت Primary/Secondary در Private VLAN و هرس ترانک', cmds: ['show vlan private-vlan', 'show interfaces trunk', 'show vlan brief'] },
    adv_ec: { host: 'DIST-SW1', goal: 'بررسی وضعیت LACP Port-Channel و نقش Active/Standby در HSRP', cmds: ['show etherchannel summary', 'show standby brief', 'show standby'] },
    adv_eigrp: { host: 'R1-EIGRP', goal: 'بررسی Successor و Feasible Successor (شرط RD < FD) در EIGRP', cmds: ['show ip eigrp topology', 'show ip route', 'show ip interface brief'] },
    adv_redist: { host: 'ASBR1', goal: 'بررسی مسیرهای OSPF/EIGRP و کنترل Route Feedback در روتر مرزی', cmds: ['show ip route', 'show ip ospf neighbor', 'show running-config'] },
    adv_bgp: { host: 'EDGE-BGP1', goal: 'بررسی نشست‌های eBGP/iBGP و جدول Best-Path در BGP', cmds: ['show ip bgp summary', 'show ip bgp', 'show ip route'] },
    adv_qos: { host: 'WAN-CE1', goal: 'بررسی سیاست سلسله‌مراتبی HQoS، صف اولویت EF و WRED', cmds: ['show policy-map', 'show policy-map interface', 'show ip interface brief'] },
    adv_mcast: { host: 'MCAST-R1', goal: 'بررسی درخت PIM-SM و کنترل مسیر بازگشت RPF', cmds: ['show ip mroute', 'show ip rpf 10.20.1.50', 'show ip route'] },
    ccnp_01: { host: 'ENCOR-R1', goal: 'بررسی VRF-Lite، تونل GRE/IPsec و جدول VXLAN/CEF', cmds: ['show ip vrf', 'show interface tunnel', 'show vxlan'] },
    ccnp_02: { host: 'ENARSI-R1', goal: 'عیب‌یابی همسایگی OSPF، BGP، PBR و تونل DMVPN Phase 3', cmds: ['show ip ospf neighbor', 'show ip bgp summary', 'show dmvpn'] },
    ccnp_enc_arch: { host: 'CORE-SW1', goal: 'راستی‌آزمایی جدول CEF و افزونگی شاسی SSO', cmds: ['show ip cef', 'show redundancy', 'show etherchannel summary'] },
    ccnp_enc_inf: { host: 'INFRA-R1', goal: 'بررسی سلسله‌مراتب Stratum در NTP، Track و NAT/PAT', cmds: ['show ntp associations', 'show track', 'show ip nat translations'] },
    ccnp_enc_sec: { host: 'SEC-SW1', goal: 'بررسی نشست‌های 802.1X/MAB، CoPP و سرورهای AAA', cmds: ['show authentication sessions', 'show policy-map control-plane', 'show aaa servers'] },
    ccnp_enc_auto: { host: 'AUTO-XE1', goal: 'بررسی نشست‌های NETCONF-YANG، Datastoreها و EEM', cmds: ['show netconf-yang sessions', 'show netconf-yang datastores', 'show event manager policy registered'] },
    ccnp_ensdwi: { host: 'cEdge-BR1', goal: 'بررسی اتصالات کنترلی vSmart/vBond/vManage، سنجش BFD و مسیرهای OMP', cmds: ['show sdwan control connections', 'show sdwan bfd sessions', 'show sdwan omp routes'] },
    ccnp_ensld: { host: 'DESIGN-R1', goal: 'بررسی خلاصه‌سازی مسیرها و افزونگی لایه ۳ در طرح شبکه', cmds: ['show ip route', 'show ip ospf neighbor', 'show ip bgp summary'] },
    ccnp_enauto: { host: 'NETOPS-XE1', goal: 'بررسی وضعیت NETCONF/RESTCONF و خط لوله اتوماسیون (Mock)', cmds: ['show netconf-yang modules', 'show restconf status', 'ansible-playbook site.yml --check --diff'] },
    ccnp_encc: { host: 'CLOUD-GW1', goal: 'بررسی نشست BGP ابری و وضعیت تونل IKEv2/IPsec', cmds: ['show ip bgp summary', 'show crypto ikev2 sa detailed', 'show crypto ipsec sa'] },
    ccnp_enna: { host: 'ASSURE-R1', goal: 'بررسی هم‌زمانی NTP، کیفیت مسیر BFD و مسیرهای لایه ۳', cmds: ['show ntp associations', 'show sdwan bfd sessions', 'show ip route'] },
    'academy-automation-terraform': { host: 'NETOPS-TF', goal: 'تمرین خوانش خروجی مرجع Terraform Plan/Apply (شبیه‌ساز Mock)', cmds: ['terraform plan', 'terraform apply', 'git status && git diff --staged'] },
    auto_04: { host: 'NETOPS-GIT', goal: 'تمرین جریان کار شاخه‌سازی و Diff در Git (شبیه‌ساز Mock)', cmds: ['git switch -c feat/vlan-automation', 'git status && git diff --staged', 'yamllint hosts.yaml'] },
    auto_08: { host: 'AUTO-NC1', goal: 'بررسی قابلیت‌های NETCONF و Datastoreهای YANG', cmds: ['show netconf-yang sessions', 'show netconf-yang datastores', 'ssh -p 830 admin@10.255.0.1 -s netconf'] },
    auto_09: { host: 'AUTO-RC1', goal: 'بررسی RESTCONF، سرویس HTTPS و پاسخ نمونه API', cmds: ['show restconf status', 'show ip http server status', 'curl -i -h "accept: application/json" --cacert corp-ca.pem https://10.255.0.1/api/v1/vlans'] },
    spec_collab_gw: { host: 'CUBE-GW1', goal: 'بررسی تماس‌های فعال SIP، ثبت‌نام SIP-UA و Dial-Peerهای صوتی', cmds: ['show sip-ua calls', 'show sip-ua register', 'show dial-peer voice'] },
    spec_dc_nx: { host: 'NEXUS-L1', goal: 'بررسی دامنه vPC، پورت‌های FEX و VXLAN EVPN', cmds: ['show vpc', 'show fex', 'show vxlan'] },
    spec_dc_aci: { host: 'APIC-LEAF1', goal: 'بررسی کشف نودهای ACI Fabric و Endpointها', cmds: ['acidiag fnvread', 'show endpoint', 'show vxlan'] },
    spec_sp_sr: { host: 'PE-SR1', goal: 'بررسی جدول برچسب Segment Routing و MPLS LDP/VPNv4', cmds: ['show isis segment-routing label-table', 'show mpls forwarding-table', 'show ip bgp vpnv4'] },
    spec_sec_ise: { host: 'ISE-SW1', goal: 'بررسی 802.1X، نگاشت TrustSec SGT و سرورهای AAA', cmds: ['show authentication sessions', 'show cts sgt', 'show aaa servers'] }
  };

  function isValidIPv4(raw) {
    if (typeof raw !== 'string') return false;
    const parts = raw.split('.');
    if (parts.length !== 4) return false;
    for (const part of parts) {
      if (!/^(0|[1-9][0-9]{0,2})$/.test(part)) return false;
      const n = Number(part);
      if (!Number.isInteger(n) || n < 0 || n > 255) return false;
    }
    return true;
  }

  function isValidIPv6(raw) {
    if (typeof raw !== 'string' || !raw.includes(':')) return false;
    if (raw.includes(':::')) return false;
    const halves = raw.split('::');
    if (halves.length > 2) return false;
    const checkPart = side => {
      if (side === '') return [];
      const groups = side.split(':');
      for (const g of groups) {
        if (!/^[0-9a-fA-F]{1,4}$/.test(g)) return null;
      }
      return groups;
    };
    const left = checkPart(halves[0]);
    if (left === null) return false;
    if (halves.length === 1) return left.length === 8;
    const right = checkPart(halves[1]);
    if (right === null) return false;
    return (left.length + right.length) < 8;
  }

  function isValidIP(raw) {
    return isValidIPv4(raw) || isValidIPv6(raw);
  }

  function scenarioForLesson(bp) {
    const id = typeof bp === 'string' ? bp : String(bp?.lessonId || bp?.id || '');
    if (Object.prototype.hasOwnProperty.call(LESSON_SCENARIOS, id)) {
      return { ...LESSON_SCENARIOS[id], matchType: 'exact' };
    }
    if (id.startsWith('auto_')) {
      return { matchType: 'track-default', host: 'NETOPS-XE1', goal: 'سناریوی پیش‌فرض مسیر اتوماسیون: بررسی NETCONF/RESTCONF و ابزارهای NetDevOps', cmds: ['show netconf-yang sessions', 'show restconf status', 'ansible-playbook site.yml --check --diff'] };
    }
    if (id.startsWith('ccna_') || id.startsWith('ccna-')) {
      return { matchType: 'track-default', host: 'R1-CCNA', goal: 'سناریوی پیش‌فرض مسیر CCNA: بررسی اینترفیس‌ها، ARP و جدول مسیریابی', cmds: ['show ip interface brief', 'show arp', 'show ip route', 'show ip ospf neighbor'] };
    }
    if (id.startsWith('spec_collab')) {
      return { matchType: 'track-default', host: 'CUBE-GW1', goal: 'سناریوی پیش‌فرض مسیر Collaboration: بررسی تماس‌های SIP و Dial-Peer', cmds: ['show sip-ua calls', 'show call active voice compact', 'show dial-peer voice'] };
    }
    if (id.startsWith('spec_sp')) {
      return { matchType: 'track-default', host: 'PE-SP1', goal: 'سناریوی پیش‌فرض مسیر Service Provider: بررسی MPLS LDP، VPNv4 و IS-IS', cmds: ['show mpls ldp neighbors', 'show mpls l3vpn routes', 'show isis neighbors'] };
    }
    if (id.startsWith('spec_') || id.startsWith('ccie_') || id.startsWith('ccde_')) {
      return { matchType: 'track-default', host: 'CORE-R1', goal: 'سناریوی پیش‌فرض مسیر معماری/خبره: بررسی BGP، EVPN و جدول CEF', cmds: ['show ip bgp summary', 'show bgp l2vpn evpn summary', 'show ip cef', 'show ip route'] };
    }
    return { matchType: 'track-default', host: 'LAB-SW1', goal: 'سناریوی پیش‌فرض مبانی شبکه: بررسی پورت‌ها، جدول MAC، ARP و مسیریابی', cmds: ['show interfaces status', 'show mac address-table', 'show arp', 'show ip route'] };
  }

  function createSession(initialHost) {
    const state = {
      host: initialHost || 'FAM-LAB',
      mode: 'priv', // 'user' (>), 'priv' (#), 'config' ((config)#), 'config-if' ((config-if)#)
      activeInterface: null,
      voiceVlans: {},
      interfaces: {},
      vlans: {},
      history: []
    };

    function ensureIf(name) {
      if (!state.interfaces[name]) {
        state.interfaces[name] = {
          ip: 'unassigned',
          mask: '',
          adminDown: false,
          description: '',
          mode: '',
          accessVlan: null,
          voiceVlan: null
        };
      }
      return state.interfaces[name];
    }

    function renderStatefulShow(cmdKey) {
      const base = CLI_DB[cmdKey] || '';
      const ifNames = Object.keys(state.interfaces);
      if (cmdKey === 'show ip interface brief' && ifNames.length) {
        const extra = ifNames.map(name => {
          const cfg = state.interfaces[name];
          const status = cfg.adminDown ? 'administratively down' : 'up';
          const proto = cfg.adminDown ? 'down' : 'up';
          return `${name.padEnd(23, ' ')} ${String(cfg.ip).padEnd(15, ' ')} YES manual ${status.padEnd(21, ' ')} ${proto}`;
        }).join('\n');
        return `${base}\n--- Session Configured Interfaces (Stateful Mock) ---\n${extra}`;
      }
      if (cmdKey === 'show interfaces status' && ifNames.length) {
        const extra = ifNames.map(name => {
          const cfg = state.interfaces[name];
          const st = cfg.adminDown ? 'disabled' : 'connected';
          const vl = cfg.mode === 'trunk' ? 'trunk' : (cfg.accessVlan ? String(cfg.accessVlan) : '1');
          const vNote = cfg.voiceVlan ? ` (voice:${cfg.voiceVlan})` : '';
          const desc = cfg.description ? cfg.description.slice(0, 18) : 'session-cfg';
          return `${name.padEnd(12, ' ')} ${desc.padEnd(18, ' ')} ${st.padEnd(10, ' ')} ${(vl + vNote).padEnd(14, ' ')} a-full  a-1000 10/100/1000BaseTX`;
        }).join('\n');
        return `${base}\n--- Session Configured Ports (Stateful Mock) ---\n${extra}`;
      }
      if (cmdKey === 'show vlan brief' && (Object.keys(state.vlans).length || ifNames.some(n => state.interfaces[n].accessVlan))) {
        const vlanMap = { ...state.vlans };
        ifNames.forEach(n => {
          const vid = state.interfaces[n].accessVlan;
          if (vid) vlanMap[vid] = vlanMap[vid] || { name: `VLAN${String(vid).padStart(4, '0')}`, ports: [] };
          if (vid && !vlanMap[vid].ports.includes(n)) vlanMap[vid].ports.push(n);
        });
        const extra = Object.keys(vlanMap).sort((a, b) => Number(a) - Number(b)).map(vid => {
          const v = vlanMap[vid];
          return `${String(vid).padEnd(4, ' ')} ${String(v.name || 'VLAN' + vid).padEnd(32, ' ')} active    ${(v.ports || []).join(', ')}`;
        }).join('\n');
        return `${base}\n--- Session Created VLANs (Stateful Mock) ---\n${extra}`;
      }
      if (cmdKey === 'show running-config') {
        const lines = [
          '[Educational Stateful Mock — NOT live Cisco IOS device]',
          '!',
          `hostname ${state.host}`,
          '!'
        ];
        Object.keys(state.vlans).sort((a, b) => Number(a) - Number(b)).forEach(vid => {
          lines.push(`vlan ${vid}`);
          if (state.vlans[vid].name) lines.push(` name ${state.vlans[vid].name}`);
          lines.push('!');
        });
        ifNames.forEach(name => {
          const cfg = state.interfaces[name];
          lines.push(`interface ${name}`);
          if (cfg.description) lines.push(` description ${cfg.description}`);
          if (cfg.mode) lines.push(` switchport mode ${cfg.mode}`);
          if (cfg.accessVlan) lines.push(` switchport access vlan ${cfg.accessVlan}`);
          if (cfg.voiceVlan) lines.push(` switchport voice vlan ${cfg.voiceVlan}`);
          if (cfg.ip && cfg.ip !== 'unassigned' && cfg.mask) lines.push(` ip address ${cfg.ip} ${cfg.mask}`);
          lines.push(cfg.adminDown ? ' shutdown' : ' no shutdown');
          lines.push('!');
        });
        if (!ifNames.length && !Object.keys(state.vlans).length) {
          return base.replace(/hostname\s+\S+/i, `hostname ${state.host}`);
        }
        lines.push('end');
        return lines.join('\n');
      }
      return base;
    }

    function prompt() {
      if (state.mode === 'user') return `${state.host}> `;
      if (state.mode === 'config') return `${state.host}(config)# `;
      if (state.mode === 'config-if') return `${state.host}(config-if)# `;
      return `${state.host}# `;
    }

    function execute(rawInput) {
      const input = String(rawInput || '').trim();
      if (!input) return { output: '', prompt: prompt(), matched: true };
      state.history.push(input);
      const lower = input.toLowerCase().replace(/\s+/g, ' ');
      const normalized = ALIASES[lower] || lower;

      if (normalized.startsWith('do ') && (state.mode === 'config' || state.mode === 'config-if')) {
        const subCmd = input.slice(3).trim();
        const savedMode = state.mode;
        const savedIf = state.activeInterface;
        state.mode = 'priv';
        const res = execute(subCmd);
        state.mode = savedMode;
        state.activeInterface = savedIf;
        return { ...res, prompt: prompt() };
      }

      if (normalized === 'clear') {
        return { output: '', clear: true, prompt: prompt(), matched: true };
      }
      if (normalized === 'help' || normalized === '?') {
        return {
          output: [
            'شبیه‌ساز آموزشی CLI سمت مرورگر (Stateful Mock — بدون اتصال به تجهیز واقعی):',
            'حالت‌ها و پیکربندی Stateful: enable | disable | configure terminal | hostname <NAME> | vlan <1-4094> | interface <name> | ip address <IPv4> <MASK> | no shutdown | shutdown | description <text> | switchport mode access|trunk | switchport access vlan <1-4094> | switchport voice vlan <1-4094> | do <show ...> | exit | end | clear',
            'تست IP معتبر (IPv4/IPv6): ping <valid-ip> | traceroute <valid-ip>',
            'نمونه فرمان‌های نمایشی: show version | show running-config | show ip interface brief | show interfaces status | show vlan brief | show interfaces trunk | show ip protocols | show ip ospf neighbor | show ip ospf interface | show ip eigrp topology | show ip bgp summary | show ip route | show ip cef | show lldp neighbors | terraform plan | ansible-playbook site.yml --check --diff'
          ].join('\n'),
          prompt: prompt(),
          matched: true
        };
      }
      if (normalized === 'enable') {
        state.mode = 'priv';
        state.activeInterface = null;
        return { output: '', prompt: prompt(), matched: true };
      }
      if (normalized === 'disable') {
        state.mode = 'user';
        state.activeInterface = null;
        return { output: '', prompt: prompt(), matched: true };
      }
      if (normalized === 'configure terminal') {
        if (state.mode === 'user') {
          return { output: '% ابتدا با دستور enable وارد حالت Privileged EXEC (#) شوید.', prompt: prompt(), matched: false };
        }
        state.mode = 'config';
        state.activeInterface = null;
        return { output: 'Enter configuration commands, one per line. End with exit/end.', prompt: prompt(), matched: true };
      }
      if (normalized === 'end') {
        if (state.mode === 'config' || state.mode === 'config-if') {
          state.mode = 'priv';
          state.activeInterface = null;
        }
        return { output: '', prompt: prompt(), matched: true };
      }
      if (normalized === 'exit') {
        if (state.mode === 'config-if') { state.mode = 'config'; state.activeInterface = null; }
        else if (state.mode === 'config') { state.mode = 'priv'; }
        else if (state.mode === 'priv') { state.mode = 'user'; }
        return { output: '', prompt: prompt(), matched: true };
      }
      if (normalized.startsWith('vlan ')) {
        if (state.mode !== 'config' && state.mode !== 'config-if') {
          return { output: '% دستور vlan فقط در حالت (config)# مجاز است. ابتدا configure terminal وارد کنید.', prompt: prompt(), matched: false };
        }
        const vidStr = normalized.slice(5).trim();
        if (!/^[1-9][0-9]{0,3}$/.test(vidStr) || Number(vidStr) > 4094) {
          return { output: '% شناسه VLAN نامعتبر است (عدد صحیح بین 1 تا 4094 وارد کنید).', prompt: prompt(), matched: false };
        }
        const vid = Number(vidStr);
        state.vlans[vid] = state.vlans[vid] || { name: `VLAN${String(vid).padStart(4, '0')}`, ports: [] };
        return { output: `[Stateful Mock] VLAN ${vid} created/updated. با show vlan brief یا show running-config بررسی کنید.`, prompt: prompt(), matched: true };
      }
      if (normalized.startsWith('interface ')) {
        if (state.mode !== 'config' && state.mode !== 'config-if') {
          return { output: '% دستور interface فقط در حالت (config)# مجاز است. ابتدا configure terminal وارد کنید.', prompt: prompt(), matched: false };
        }
        const ifName = input.slice(10).trim();
        if (!/^[A-Za-z][A-Za-z0-9/.:-]{0,31}$/.test(ifName)) {
          return { output: '% نام اینترفیس نامعتبر است.', prompt: prompt(), matched: false };
        }
        state.mode = 'config-if';
        state.activeInterface = ifName;
        ensureIf(ifName);
        return { output: `[Mock] Selected interface ${ifName}`, prompt: prompt(), matched: true };
      }
      if (normalized.startsWith('ip address ')) {
        if (state.mode !== 'config-if') {
          return { output: '% دستور ip address فقط در حالت (config-if)# مجاز است (configure terminal -> interface <name>).', prompt: prompt(), matched: false };
        }
        const parts = input.slice(11).trim().split(/\s+/);
        if (parts.length !== 2 || !isValidIPv4(parts[0]) || !isValidIPv4(parts[1])) {
          return { output: '% قالب صحیح: ip address <IPv4> <Subnet-Mask> (مثلاً ip address 10.10.10.1 255.255.255.0).', prompt: prompt(), matched: false };
        }
        const cfg = ensureIf(state.activeInterface);
        cfg.ip = parts[0];
        cfg.mask = parts[1];
        return { output: `[Stateful Mock] IP ${parts[0]} ${parts[1]} configured on ${state.activeInterface}.`, prompt: prompt(), matched: true };
      }
      if (normalized === 'no shutdown' || normalized === 'no shut') {
        if (state.mode !== 'config-if') {
          return { output: '% دستور no shutdown فقط در حالت (config-if)# مجاز است.', prompt: prompt(), matched: false };
        }
        const cfg = ensureIf(state.activeInterface);
        cfg.adminDown = false;
        return { output: `%LINK-3-UPDOWN: Interface ${state.activeInterface}, changed state to up (Stateful Mock)`, prompt: prompt(), matched: true };
      }
      if (normalized === 'shutdown' || normalized === 'shut') {
        if (state.mode !== 'config-if') {
          return { output: '% دستور shutdown فقط در حالت (config-if)# مجاز است.', prompt: prompt(), matched: false };
        }
        const cfg = ensureIf(state.activeInterface);
        cfg.adminDown = true;
        return { output: `%LINK-5-CHANGED: Interface ${state.activeInterface}, changed state to administratively down (Stateful Mock)`, prompt: prompt(), matched: true };
      }
      if (normalized.startsWith('description ')) {
        if (state.mode !== 'config-if') {
          return { output: '% دستور description فقط در حالت (config-if)# مجاز است.', prompt: prompt(), matched: false };
        }
        const cfg = ensureIf(state.activeInterface);
        cfg.description = input.slice(12).trim().slice(0, 64);
        return { output: `[Stateful Mock] Description set on ${state.activeInterface}.`, prompt: prompt(), matched: true };
      }
      if (normalized === 'switchport mode access' || normalized === 'switchport mode trunk') {
        if (state.mode !== 'config-if') {
          return { output: '% دستور switchport mode فقط در حالت (config-if)# مجاز است.', prompt: prompt(), matched: false };
        }
        const modeVal = normalized.endsWith('trunk') ? 'trunk' : 'access';
        ensureIf(state.activeInterface).mode = modeVal;
        return { output: `[Stateful Mock] ${state.activeInterface} switchport mode set to ${modeVal}.`, prompt: prompt(), matched: true };
      }
      if (normalized.startsWith('switchport access vlan ')) {
        if (state.mode !== 'config-if') {
          return { output: '% دستور switchport access vlan فقط در حالت (config-if)# مجاز است.', prompt: prompt(), matched: false };
        }
        const vidStr = normalized.slice(23).trim();
        if (!/^[1-9][0-9]{0,3}$/.test(vidStr) || Number(vidStr) > 4094) {
          return { output: '% شناسه VLAN نامعتبر است (عدد صحیح بین 1 تا 4094 وارد کنید).', prompt: prompt(), matched: false };
        }
        const vid = Number(vidStr);
        const cfg = ensureIf(state.activeInterface);
        cfg.accessVlan = vid;
        if (!cfg.mode) cfg.mode = 'access';
        state.vlans[vid] = state.vlans[vid] || { name: `VLAN${String(vid).padStart(4, '0')}`, ports: [] };
        if (!state.vlans[vid].ports.includes(state.activeInterface)) state.vlans[vid].ports.push(state.activeInterface);
        return { output: `[Stateful Mock] Access VLAN ${vid} assigned to ${state.activeInterface}.`, prompt: prompt(), matched: true };
      }
      if (normalized.startsWith('switchport voice vlan ')) {
        if (state.mode !== 'config-if') {
          return { output: '% دستور switchport voice vlan فقط در حالت (config-if)# مجاز است (configure terminal -> interface <name>).', prompt: prompt(), matched: false };
        }
        const vidStr = normalized.slice(22).trim();
        if (!/^[1-9][0-9]{0,3}$/.test(vidStr) || Number(vidStr) > 4094) {
          return { output: '% شناسه VLAN نامعتبر است (عدد صحیح بین 1 تا 4094 وارد کنید).', prompt: prompt(), matched: false };
        }
        state.voiceVlans[state.activeInterface] = Number(vidStr);
        ensureIf(state.activeInterface).voiceVlan = Number(vidStr);
        return { output: `[Simulated Mock] Voice VLAN ${vidStr} assigned to ${state.activeInterface} (not applied to live hardware).`, prompt: prompt(), matched: true };
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
        if (!isValidIP(target)) {
          return { output: `% آدرس IP نامعتبر است ("${target}"). یک آدرس معتبر IPv4 (مانند 10.0.12.2) یا IPv6 (مانند 2001:db8::1) وارد کنید.`, prompt: prompt(), matched: false };
        }
        return {
          output: `[Simulated Mock Ping — هیچ بسته واقعی شبکه ارسال نشد]\nSending 5, 100-byte ICMP Echos to ${target}, timeout is 2 seconds:\n!!!!!\nSuccess rate is 100 percent (5/5), simulated round-trip min/avg/max = 1/2/4 ms`,
          prompt: prompt(),
          matched: true
        };
      }
      if (normalized.startsWith('traceroute ')) {
        const target = input.slice(11).trim();
        if (!isValidIP(target)) {
          return { output: `% آدرس IP نامعتبر است ("${target}"). یک آدرس معتبر IPv4 یا IPv6 وارد کنید.`, prompt: prompt(), matched: false };
        }
        return {
          output: `[Simulated Mock Traceroute — هیچ بسته واقعی ارسال نشد]\nTracing the route to ${target}\n  1 10.0.12.2 2 msec 1 msec 1 msec\n  2 ${target} 4 msec 3 msec 4 msec`,
          prompt: prompt(),
          matched: true
        };
      }

      if (Object.prototype.hasOwnProperty.call(CLI_DB, normalized)) {
        return { output: renderStatefulShow(normalized), prompt: prompt(), matched: true };
      }
      const prefixHits = Object.keys(CLI_DB).filter(k => k.startsWith(normalized));
      if (prefixHits.length === 1) {
        return { output: renderStatefulShow(prefixHits[0]), prompt: prompt(), matched: true };
      }

      return {
        output: `% فرمان "${input}" در شبیه‌ساز آموزشی محلی پشتیبانی نمی‌شود. برای دیدن فرمان‌های پشتیبانی‌شده، help را وارد کنید.`,
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
    card.setAttribute('data-sim-match-type', scenario.matchType);
    card.style.cssText = 'margin:22px 0;padding:16px;border-radius:12px;border:1px solid #334155;background:#0b1220;color:#e2e8f0;';

    const title = document.createElement('h3');
    title.style.cssText = 'margin:0 0 6px;font-size:16px;color:#38bdf8;';
    title.textContent = scenario.matchType === 'exact'
      ? 'شبیه‌ساز تعاملی CLI — سناریوی اختصاصی این درس (نسخه آموزشی Mock)'
      : 'شبیه‌ساز تعاملی CLI — سناریوی پیش‌فرض مسیر/دامنه (نسخه آموزشی Mock)';

    const honesty = document.createElement('p');
    honesty.setAttribute('data-sim-honesty', '1');
    honesty.style.cssText = 'margin:0 0 10px;padding:8px 10px;border-radius:8px;background:rgba(245,158,11,0.14);border:1px solid rgba(245,158,11,0.4);color:#fde68a;font-size:12.5px;';
    honesty.textContent = 'توجه: این محیط یک شبیه‌ساز آموزشی سمت مرورگر (Mock) است؛ هیچ تجهیز واقعی شبکه، SSH، Terraform یا IOS زنده متصل نیست. خروجی‌ها صرفاً مدل آموزشی/مرجع برای تمرین تحلیل فرمان هستند.';

    const goal = document.createElement('p');
    goal.style.cssText = 'margin:0 0 10px;font-size:13px;color:#cbd5e1;';
    goal.textContent = 'هدف تمرین: ' + scenario.goal;

    const chips = document.createElement('div');
    chips.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;';

    const term = document.createElement('pre');
    term.setAttribute('dir', 'ltr');
    term.setAttribute('data-sim-output', '1');
    term.style.cssText = 'margin:0 0 10px;padding:12px;min-height:130px;max-height:300px;overflow:auto;border-radius:8px;background:#020617;border:1px solid #1e293b;color:#a7f3d0;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px;line-height:1.5;white-space:pre-wrap;';
    term.textContent = `[FAM Educational CLI Mock · Lesson: ${bp.lessonId || bp.id} · Scenario: ${scenario.matchType}]\nType "help" or click a suggested command below.\n`;

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
      if (trimmed && res.matched && typeof window !== 'undefined' && typeof window.dispatchEvent === 'function') {
        window.dispatchEvent(new CustomEvent('fam-cli-executed', {
          detail: { cmd: trimmed, matched: res.matched, lessonId: bp.lessonId || bp.id || '' }
        }));
      }
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
    isValidIP,
    isValidIPv4,
    isValidIPv6,
    commandCount: Object.keys(CLI_DB).length,
    exactScenarioCount: Object.keys(LESSON_SCENARIOS).length,
    getSupportedCommands: () => Object.keys(CLI_DB),
    getCommandOutput: cmd => Object.prototype.hasOwnProperty.call(CLI_DB, cmd) ? CLI_DB[cmd] : null
  };
})();
