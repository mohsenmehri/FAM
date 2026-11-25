{
  id:'f1', num:'۱', title:'دانشکدهٔ اول — CCNA کامل', duration:'۵ ماه (ماه ۲ تا ۶)', tag:'مدرک هدف: 200-301 CCNA',
  intro:'این دانشکده شش بخش رسمی آزمون 200-301 را پوشش می‌دهد؛ هر بخش با چهار خروجی اجرا می‌شود: مفهوم، دستور، لاب و عیب‌یابی. حداقل ۲۵ سناریوی عملی الزامی است و پروژهٔ پایان، یک شبکهٔ سازمانی سه‌طبقه با مستندات کامل. شرط عبور: تئوری ۸۵، لاب ۸۵ و تأیید پروژه.',
  lessons:[
    { id:'f1-p1', title:'بخش اول: Network Fundamentals', sub:'CCNA · بخش ۱ از ۶', lessonsCount:'۱۲ موضوع', minutes:'۳ هفته',
      lead:'پایه‌ترین بخش CCNA همان چیزی است که در دانشکدهٔ صفر ساختی؛ اینجا آن را تا سطح استاندارد آزمون بالا می‌آوریم: اجزای شبکه، توپولوژی‌ها، مدل‌ها، Ethernet، آدرس‌دهی دو نسخه، بی‌سیم، کابل‌ها و مجازی‌سازی. تمرکز بر «کاربرد» است، نه فهرست.',
      sec:{
        goal:[['p','شناخت کامل اجزای شبکه (سوئیچ، روتر، AP، WLC، فایروال، سرور) و توپولوژی‌ها؛ تحلیل ارتباط دو دستگاه؛ طراحی آدرس‌دهی IPv4/IPv6 و درک TCP/UDP در برابر پروتکل‌های برنامه.']],
        prereq:[['ul',['دانشکدهٔ صفر (۴ هفته)','آشنایی با Packet Tracer']]],
        concept:[
          ['h3','Network Components و Topologies'],
          ['p','هر شبکه‌ای از چهار جزء ساخته می‌شود: دستگاه‌های انتهایی (Host)، دستگاه‌های انتقال (سوئیچ لایهٔ ۲ و روتر لایهٔ ۳)، رسانه (کابل مسی، فیبر، بی‌سیم) و سرویس‌ها (DNS، DHCP، دسترسی از راه دور). توپولوژی (ستاره‌ای، مش، درختی، هیبرید) شکل اتصال را توصیف می‌کند؛ در دنیای واقعی امروز تقریباً همهٔ LANها ستاره‌ای‌اند و WAN از هیبرید استفاده می‌کند.'],
          ['h3','سوئیچینگ، Ethernet و MAC'],
          ['p','سوئیچ در لایهٔ ۲ کار می‌کند: جدول MAC می‌سازد، فریم را فقط به پورت مقصد می‌فرستد و دامنهٔ برخورد را پورت‌به‌پورت جدا می‌کند. سرعت‌های رایج 10/100/1000 و 10G و استانداردهای 802.3 برای سیم و 802.11 برای بی‌سیم.'],
          ['h3','آدرس‌دهی IPv4 و IPv6'],
          ['p','IPv4 با ماسک و زیرشبکه (دانشکدهٔ صفر) و IPv6 با آدرس‌های Global و Link-Local و SLAAC. در CCNA باید هر دو را هم‌زمان بلد باشی چون پیکربندی‌ها معمولاً دوزبانه‌اند.'],
          ['h3','Wireless، کابل و مجازی‌سازی'],
          ['p','کابل‌های مسی Cat5e/6/6a و فیبرهای Single-mode و Multi-mode با کاربردشان؛ در بی‌سیم: باند، کانال، SSID و تفاوت AP با WLC. مجازی‌سازی (VM، Container، vSwitch) امروز بخشی از شبکه است چون سرور مجازی هم مثل سرور واقعی آدرس و پورت دارد.'],
          ['h3','TCP، UDP و پروتکل‌های برنامه'],
          ['p','نقطهٔ اتصال لایهٔ ۴ به ۷: پورت‌ها. HTTP/HTTPS (80/443)، DNS (53)، DHCP (67/68)، SSH (22)، SMTP (25) و… را باید با پروتکل زیرین (TCP یا UDP) بشناسی — سؤال همیشگی آزمون.']
        ],
        protocol:[['cli','خواندن جدول روت و اتصال','Router# show ip route\nCodes: C - connected, S - static, O - OSPF\nC  192.168.1.0/24 is directly connected, Gi0/0\nS  10.0.0.0/8 [1/0] via 192.168.1.254\n\nPC> ping 192.168.1.1\nPC> nslookup cisco.com']],
        ios:[['cli','مشاهدهٔ اجزا','Switch# show version\nSwitch# show ip interface brief\nSwitch# show mac address-table\nRouter# show cdp neighbors      ! همسایگان لایهٔ ۲\nRouter# show lldp neighbors']],
        diagram:[['svg','topo'],['p','توپولوژی سه‌طبقهٔ پروژهٔ CCNA — در این بخش با نقش هر طبقه آشنا می‌شوی؛ پیاده‌سازی کاملش پروژهٔ پایان است.']],
        lab:[['labs',[{t:'آزمایشگاه ۱ — ساخت شبکهٔ LAN',steps:['یک سوئیچ و ۴ کلاینت بساز','کابل‌ها و وضعیت پورت‌ها را چک کن','با ping ارتباط داخلی و با show cdp همسایگی را اثبات کن']},{t:'آزمایشگاه ۲۳ — Wireshark و Packet Analysis',steps:['ترافیک وب و DNS را capture کن','فیلترها و ستون‌های Info را سفارشی کن','سه پروتکل مختلف را پیدا و مستند کن']}]]],
        trouble:[['ul',['لینک up ولی ارتباط نیست: VLAN پورت، سرعت دوطرفه (auto/auto) و کابل را چک کن','CDP همسایه را نشان نمی‌دهد: لینک فیزیکی یا پورت روی VLAN اشتباه','سرعت 100 مگا بجای 1000: کابل یا پورت معیوب — show interfaces counters errors']]],
        exercise:[['ol',['پنج توپولوژی را رسم کن و برای هر کدام یک کاربرد واقعی بنویس','لیست ۱۰ پورت پرکاربرد با پروتکل زیرینشان','تفاوت collision domain و broadcast domain را برای یک سوئیچ و یک روتر توضیح بده']]],
        quiz:[['quiz',[
          {q:'کدام دستگاه دامنهٔ پخش (broadcast domain) را جدا می‌کند؟',opts:['سوئیچ لایهٔ ۲','هاب','روتر','مودم'],a:2,exp:'روتر مرز لایهٔ ۳ است و broadcast را عبور نمی‌دهد؛ سوئیچ فقط collision domain را جدا می‌کند.'},
          {q:'پورت HTTPS روی کدام پروتکل لایهٔ ۴ است؟',opts:['UDP 443','TCP 443','TCP 80','UDP 80'],a:1,exp:'HTTPS از TCP/443 استفاده می‌کند؛ HTTP روی TCP/80.'}
        ]]],
        notes:[['ul',['فهرست پورت‌ها و پروتکل‌ها را در دفترچهٔ آکادمی جدولی بنویس','هر اصطلاح انگلیسی جدید را با یک مثال فارسی معادل‌سازی کن']]
        ]
      }
    },
    { id:'f1-p2', title:'بخش دوم: Network Access — VLAN و Trunk', sub:'CCNA · بخش ۲ از ۶', minutes:'۴ هفته',
      lead:'قلب عملی CCNA همین‌جاست: سوئیچ، VLAN، Trunk و STP. هدف این است که وقتی گفتند «دو VLAN نباید قاطی شوند»، دقیقاً بدانی چه اتفاقی در کابل می‌افتد و چه دستوری آن را می‌سازد.',
      sec:{
        goal:[['p','پیکربندی VLAN و Access/Trunk/Native VLAN، مسیریابی بین VLANها، EtherChannel با LACP و پایداری STP/RSTP — و عیب‌یابی هر کدام با خروجی واقعی CLI.']],
        prereq:[['ul',['فایل‌های MAC و فریم Ethernet','دانشکدهٔ صفر: آدرس‌دهی زیرشبکه','آزمایشگاه ۱ — ساخت LAN']]],
        concept:[
          ['h3','چرا VLAN؟'],
          ['p','بدون VLAN، هر دستگاه متصل به سوئیچ در یک دامنهٔ پخش بزرگ است: طوفان broadcast، امنیت صفر و انعطاف صفر. VLAN یعنی سوئیچ منطقی را به چند سوئیچ مجازی تکه‌تکه کنی؛ هر تکه یک broadcast domain مستقل. پورتی که فقط به یک VLAN تعلق دارد Access است.'],
          ['h3','Trunk و تگ 802.1Q'],
          ['p','وقتی دو سوئیچ باید چند VLAN را هم‌زمان حمل کنند، لینک بین آن‌ها Trunk می‌شود: هر فریم با یک تگ ۴ بایتی VLAN برچسب می‌خورد تا گیرنده بداند برای کدام VLAN است. Native VLAN همان VLAN بدون تگ است — و اگر دو طرف Native متفاوت داشته باشند، دقیقاً همان جایی است که مهاجمان VLAN hopping را اجرا می‌کنند؛ پس باید روی هر دو طرف یکسان و ترجیحاً غیرفعال باشد.'],
          ['h3','Inter-VLAN Routing'],
          ['p','VLANها قطعه‌قطعه‌اند؛ برای حرف زدن بین آن‌ها یا روتر لازم است (روی هر VLAN یک sub-interface با router-on-a-stick) یا سوئیچ لایهٔ ۳ با SVI. هر دو را باید بسازی.'],
          ['h3','EtherChannel و LACP'],
          ['p','چند لینک موازی بدون EtherChannel توسط STP یکی‌شان مسدود می‌شود؛ با LACP یا PAgP همان لینک‌ها یک لینک منطقی می‌شوند: پهنای باند جمع، افزونگی و بدون حلقه.'],
          ['h3','STP و RSTP'],
          ['p','استپینگ‌تری (STP) جلوی حلقهٔ لایهٔ ۲ را با انتخاب Root Bridge و مسدود کردن یک پورت می‌گیرد؛ RSTP سریع‌تر (ثانیه‌ای) و مدرن‌تر است. در اجرای واقعی، BPDU Guard روی پورت‌های کاربری و Root Guard روی لینک‌های حساس ضروری‌اند.'],
          ['h3','CDP/LLDP و Wireless مقدماتی'],
          ['p','CDP (سیسکو) و LLDP (استاندارد) همسایه‌ها را معرفی می‌کنند؛ در عیب‌یابی لینک، اولین نگاه همین است. در بی‌سیم: SSID، باند، کانال و تفاوت AP مستقل با Lightweight که به WLC وصل می‌شود.']
        ],
        protocol:[
          ['svg','vlan'],
          ['p','در دیاگرام: دو VLAN روی یک لینک Trunk — تگ 802.1Q (۴ بایت: TPID + TCI) هویت هر فریم را حمل می‌کند. بدون تگ، فریم در Native VLAN قرار می‌گیرد.'],
          ['cli','نگاه به تگ در خروجی','Switch# show interfaces trunk\nPort    Mode         Encapsulation   Status        Native vlan\nGi0/1   on           802.1q          trunking      99\n\nSwitch# show interfaces g0/1 switchport\nName: Gi0/1\nMode: trunk\nNegotiation of Trunking: On\nAccess Mode VLAN: 1 (default)\nTrunking Native Mode VLAN: 99 (MANAGEMENT)']
        ],
        ios:[
          ['cli','پیکربندی کامل VLAN و Trunk','Switch(config)# vlan 10\nSwitch(config-vlan)# name STUDENTS\nSwitch(config)# vlan 20\nSwitch(config-vlan)# name VOICE\n\nSwitch(config)# interface range g0/1 - 4\nSwitch(config-if-range)# switchport mode access\nSwitch(config-if-range)# switchport access vlan 10\nSwitch(config-if-range)# spanning-tree portfast\nSwitch(config-if-range)# spanning-tree bpduguard enable\n\nSwitch(config)# interface g0/1\nSwitch(config-if)# switchport mode trunk\nSwitch(config-if)# switchport trunk native vlan 99\nSwitch(config-if)# switchport trunk allowed vlan 10,20,99\n\n! --- Inter-VLAN روی روتر (router-on-a-stick) ---\nRouter(config)# interface g0/0.10\nRouter(config-subif)# encapsulation dot1Q 10\nRouter(config-subif)# ip address 192.168.10.1 255.255.255.0\nRouter(config)# interface g0/0.20\nRouter(config-subif)# encapsulation dot1Q 20\nRouter(config-subif)# ip address 192.168.20.1 255.255.255.0'],
          ['cli','EtherChannel با LACP','Switch(config)# interface range g0/1 - 2\nSwitch(config-if-range)# channel-group 1 mode active\nSwitch(config)# port-channel 1\nSwitch(config-if)# switchport mode trunk'],
          ['note','warn','Native VLAN دو طرف Trunk باید یکسان باشد؛ و بهتر است از VLAN 1 خارج و غیرفعال شود.']
        ],
        diagram:[['svg','vlan'],['p','بالا: دو سوئیچ با Trunk برچسب‌دار — همان چیزی که در show interfaces trunk می‌بینی.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۳ — VLAN و Access Port',steps:['VLAN 10 و 20 بساز و نام بگذار','۴ پورت را access و تقسیم کن','بین دو کلاینت همان VLAN ping و بین دو VLAN عدم ارتباط را اثبات کن','show vlan brief خروجی را مستند کن']},
          {t:'آزمایشگاه ۴ — Trunk و Native VLAN',steps:['لینک بین دو سوئیچ را trunk کن','native vlan 99 تعریف و روی دو طرف یکسان کن','allowed vlan محدود کن و با show interfaces trunk بررسی کن','عمداً native دو طرف را متفاوت کن و با capture ببین چه اتفاقی می‌افتد']},
          {t:'آزمایشگاه ۵ — Inter-VLAN Routing',steps:['روی روتر subinterface با dot1Q بساز','هر VLAN یک gateway بگیرد','بین سه VLAN روتینگ کن و با traceroute مسیر را نشان بده']},
          {t:'آزمایشگاه ۷ — EtherChannel و LACP',steps:['دو لینک را با channel-group active جمع کن','وضعیت port-channel را با show etherchannel چک کن','یک لینک را قطع کن و اثبات کن ارتباط قطع نمی‌شود']}
        ]]],
        trouble:[['ul',['کلاینت VLAN 10 به سرور VLAN 20 نمی‌رسد: gateway تعریف شده؟ SVI/subinterface up است؟','Trunk بالا نمی‌آید: mode access/trunk؟ allowed vlan؟ دو طرف LACP هم‌شکل؟','دستگاه‌های VLAN 1 ناگهان قطع شدند: کسی native را عوض کرده — show interfaces trunk','حلقهٔ STP: کابل اضافی زده؟ با show spanning-tree پورت blocked را پیدا کن']]],
        exercise:[['ol',['یک نقشهٔ ۴ VLANی برای یک دفتر طراحی کن (کاربر، VoIP، سرور، مدیریت) و جدول پورت‌ها را بنویس','چرا LACP بهتر از دو لینک مستقل با STP است؟','آزمون امنیتی: چرا native VLAN پیش‌فرض خطرناک است؟']]],
        quiz:[['quiz',[
          {q:'فریم در Trunk با تگ VLAN 5 — چه اتفاقی برایش می‌افتد؟',opts:['دور انداخته می‌شود','با تگ به گیرنده می‌رسد و گیرنده تگ را برمی‌دارد','به VLAN 1 می‌رود','رمز می‌شود'],a:1,exp:'گیرنده تگ 802.1Q را می‌خواند، فریم را به VLAN مربوطه تحویل می‌دهد و تگ را برای دستگاه انتهایی حذف می‌کند.'},
          {q:'دستور spanning-tree portfast چه می‌کند؟',opts:['سرعت پورت را زیاد می‌کند','پورت را فوراً forwarding می‌کند (بدون listen/learn)','STP را غیرفعال می‌کند','لینک را trunk می‌کند'],a:1,exp:'portfast پورت کاربری را از حالت listen/learn عبور می‌دهد؛ معمولاً با bpduguard همراه می‌شود.'},
          {q:'بهترین راه جلوگیری از VLAN hopping چیست؟',opts:['افزایش تعداد VLANها','یکسان‌سازی و غیرفعال‌سازی Native VLAN غیراستفاده','استفاده از hub','تغییر SSID'],a:1,exp:'حمله روی ناهمسانی یا پیش‌فرض بودن Native VLAN سوار می‌شود؛ یکسان و غیرفعالش کن.'},
          {q:'در router-on-a-stick چه دستوری VLAN را به subinterface وصل می‌کند؟',opts:['ip address','encapsulation dot1Q 10','switchport access vlan','channel-group'],a:1,exp:'encapsulation dot1Q شمارهٔ VLAN را روی subinterface تعریف می‌کند؛ بعد IP می‌دهیم.'}
        ]]],
        notes:[['ul',['خروجی show interfaces trunk و show vlan brief را در دفترچه نگه دار','لیست پورت‌های هر VLAN را برای پروژهٔ نهایی همین‌جا طراحی کن','اشتباه native VLAN را یک بار عمداً بساز و رفعش کن']]
        ]
      },
      faq:[{q:'فرق access port با trunk port در یک جمله؟',a:'access فقط یک VLAN را می‌بیند و تگ ندارد؛ trunk همهٔ VLANهای مجاز را با تگ حمل می‌کند.'},{q:'چرا STP لازم است اگر لایهٔ ۳ روترینگ دارد؟',a:'چون در لایهٔ ۲ حلقه = طوفان broadcast بدون TTL؛ روتر حلقه را نمی‌بیند چون broadcast را عبور نمی‌دهد.'},{q:'Inter-VLAN با سوئیچ لایهٔ ۳ بهتر است یا روتر؟',a:'سوئیچ لایهٔ ۳ (SVI) سریع‌تر و یکپارچه‌تر است؛ router-on-a-stick برای لاب و شبکه‌های کوچک اقتصادی است. هر دو در آزمون هست.'}]
    },
    { id:'f1-p3', title:'بخش سوم: IP Connectivity — استاتیک و OSPF', sub:'CCNA · بخش ۳ از ۶', minutes:'۴ هفته',
      lead:'تا اینجا لایهٔ ۲ را ساختیم؛ حالا باید بسته از شبکه‌ای به شبکهٔ دیگر برود. جدول روت، Longest Prefix Match، روت‌های استاتیک و OSPF تک‌ناحیه در این بخش جمع می‌شوند.',
      sec:{
        goal:[['p','خواندن و ساخت جدول روت، اعمال Longest Prefix Match، پیکربندی روت استاتیک/پیش‌فرض/شناور، و راه‌اندازی OSPF تک‌ناحیه با همسایگی، DR/BDR، AD و متریک — همراه عیب‌یابی.']],
        prereq:[['ul',['زیرشبکه و ماسک (دانشکدهٔ صفر)','لایهٔ ۳ و IP Header','آزمایشگاه‌های ۳ تا ۵']]],
        concept:[
          ['h3','جدول روت و Longest Prefix Match'],
          ['p','روتر برای هر بسته در جدولش دنبال بهترین مسیر می‌گردد؛ اگر چند مسیر همپوشان باشد، بلندترین پیشوند (بیشترین تعداد بیت یکسان) برنده است. جدول از منابع مختلفی پر می‌شود: connected (C)، static (S)، OSPF (O) و… که هرکدام اولویت (Administrative Distance) خودشان را دارند.'],
          ['h3','روت‌های استاتیک، پیش‌فرض و شناور'],
          ['p','استاتیک: «برای رسیدن به این شبکه، از اینجا برو» — ساده و قابل پیش‌بینی، اما بدون افزونگی. روت پیش‌فرض (0.0.0.0/0) یعنی «هر چه نشناختم، از اینجا» — همان گیت‌وی خروج. روت شناور (Floating Static) با AD بالاتر، پشت‌یبانِ پروتکل پویا است: وقتی OSPF قطع شد، بالا می‌آید.'],
          ['h3','OSPF تک‌ناحیه'],
          ['p','OSPF یک پروتکل لینک‌-state است: هر روتر لینک‌هایش را با Hello پیدا می‌کند، LSDB می‌سازد و با الگوریتم Dijkstra بهترین مسیر را حساب می‌کند. برای تشکیل همسایگی، چند شرط لازم است: همان Area، همان Subnet و Mask، همان پورت‌ها (mtu، authentication) و Timers یکسان. نقش DR/BDR در شبکه‌های broadcast کاهش تعداد نشست‌هاست.'],
          ['h3','AD و Metric'],
          ['p','Administrative Distance اعتماد به منبع است (connected=0، static=1، OSPF=110) و Metric هزینهٔ مسیر داخلی همان پروتکل (در OSPF: 10^8 / پهنای باند). وقتی دو مسیر با AD یکسان داری، متریک تصمیم می‌گیرد؛ وقتی AD متفاوت، AD برنده است.']
        ],
        protocol:[
          ['svg','ospf'],
          ['cli','دست زدن به جدول روت','R1# show ip route\nO   10.1.1.0/24 [110/2] via 192.168.12.2, 00:05:22, GigabitEthernet0/0\nS*  0.0.0.0/0 [1/0] via 192.168.12.2\n\nR1# show ip ospf neighbor\nNeighbor ID     Pri   State           Dead Time   Address         Interface\n10.2.2.2          1   FULL/  -       00:00:34    192.168.12.2    GigabitEthernet0/0'],
          ['p','خط O یعنی OSPF، عدد داخل [110/2] یعنی AD=110 و Metric=2. در همسایگی، FULL شدن یعنی دیتابیس‌ها هم‌اند.']
        ],
        ios:[
          ['cli','روت استاتیک و شناور','Router(config)# ip route 172.16.0.0 255.255.0.0 10.0.0.2\nRouter(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.1\n! شناور: AD بالاتر از OSPF (مثلاً 130)\nRouter(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.3 130'],
          ['cli','OSPF تک‌ناحیه','Router(config)# router ospf 1\nRouter(config-router)# router-id 1.1.1.1\nRouter(config-router)# network 192.168.12.0 0.0.0.0 area 0\nRouter(config-router)# network 10.1.1.0 0.0.0.255 area 0\nRouter(config-router)# passive-interface g0/1\n\nR1# show ip ospf interface brief\nR1# show ip protocols'],
          ['note','tip','network با wildcard است: 0.0.0.0 یعنی دقیقاً همان آدرس. اشتباه رایج: netmask به‌جای wildcard.']
        ],
        diagram:[['svg','ospf'],['p','همسایگی سه روتر — HELLO تا FULL و سه جدول (Neighbor، Database، Routing).']],
        lab:[['labs',[
          {t:'آزمایشگاه ۸ — Static Routing',steps:['دو شبکهٔ جدا با یک روتر وصل کن','روت استاتیک دوطرفه بده','با ping و traceroute اثبات کن','بدون روت، بستهٔ unreachable را ببین']},
          {t:'آزمایشگاه ۹ — Default و Floating Route',steps:['روت پیش‌فرض به سمت ISP بساز','روت شناور با AD 130 اضافه کن','لینک اصلی را قطع و بالا آمدن خودکار شناور را اثبات کن']},
          {t:'آزمایشگاه ۱۰ — OSPF Single Area',steps:['روی سه روتر OSPF area 0 با router-id یکتا فعال کن','neighbor را با show ip ospf neighbor تا FULL بررسی کن','MTU و timers را چک کن','یکی از لینک‌ها را قطع و مسیر جایگزین را در جدول ببین']}
        ]]],
        trouble:[['ul',['همسایه FULL نمی‌شود: area/mask/timers یکسان؟ پورت passive نیست؟ MTU یکسان؟','روت استاتیک کار نمی‌کند: next-hop در دسترس است؟ مسیر خروجی درست؟ AD را چک کن','دو مسیر داری و اشتباهی انتخاب می‌شود: LPM را روی پیشوندها حساب کن — گاهی /32 برندهٔ /8 است']]],
        exercise:[['ol',['جدول روتی با ۴ مسیر همپوشان بساز و با LPM برنده را مشخص کن','محاسبهٔ Metric OSPF برای لینک 1Gbps و 100Mbps','چرا روت شناور AD بالاتر می‌خواهد؟']]],
        quiz:[['quiz',[
          {q:'AD روت استاتیک پیش‌فرض چند است؟',opts:['0','1','90','110'],a:1,exp:'static = 1؛ فقط connected (0) از آن مطمئن‌تر است.'},
          {q:'در OSPF Metric چطور حساب می‌شود؟',opts:['تعداد hop','10^8 تقسیم بر پهنای باند','زمان تأخیر صفر','تعداد همسایگان'],a:1,exp:'Cost = Reference Bandwidth / Bandwidth پورت؛ هرچه پهنای باند بیشتر، هزینه کمتر.'},
          {q:'کدام عامل جلوی همسایگی OSPF را می‌گیرد؟',opts:['پورت passive','یکسان بودن router-id','روت داشتن','نام hostname'],a:0,exp:'passive-interface فقط Hello نمی‌فرستد؛ پس همسایگی تشکیل نمی‌شود.'}
        ]]],
        notes:[['ul',['جدول AD همهٔ منابع را حفظ کن (متداول‌ترها: 0،1،90،110،170)','خروجی show ip route را رنگی و توضیح‌دار کن']]
        ]
      }
    },
    { id:'f1-p4', title:'بخش چهارم: IP Services', sub:'CCNA · بخش ۴ از ۶', minutes:'۳ هفته',
      lead:'سرویس‌هایی که شبکه را «قابل استفاده» می‌کنند: DHCP با relay، DNS، NAT/PAT، NTP برای هم‌زمانی، SNMP و Syslog برای دیدن، QoS برای اولویت‌بندی، SSH برای مدیریت، FHRP برای گیت‌وی افزوده و Port Mirroring برای تحلیل.',
      sec:{
        goal:[['p','پیکربندی و عیب‌یابی سرویس‌های لایهٔ ۳/۴ شبکه؛ درک نقش هر کدام در یک شبکهٔ واقعی و اثبات رفتارشان با خروجی CLI یا capture.']],
        prereq:[['ul',['دانشکدهٔ صفر: DNS/DHCP/NAT/SSH','روتینگ استاتیک و OSPF','آزمایشگاه‌های ۱۱، ۱۲، ۱۷']]],
        concept:[
          ['h3','DHCP و Relay'],
          ['p','DHCP چهار پیام DISCOVER/OFFER/REQUEST/ACK را برای آدرس‌دهی خودکار می‌فرستد؛ در شبکه‌های چند-VLAN چون broadcast به بیرون نمی‌رود، با ip helper-address (DHCP Relay) پیام را به سرور مرکزی می‌رسانیم. سرور علاوه بر IP، ماسک، گیت‌وی، DNS و Lease را می‌دهد.'],
          ['h3','NAT و PAT'],
          ['p','NAT آدرس خصوصی را عمومی می‌کند؛ PAT (Overload) با پورت‌ها ده‌ها کلاینت را پشت یک IP می‌نشاند. سه نوع: static (برای سرور داخلی)، dynamic pool و overload پرکاربردترین.'],
          ['h3','NTP، SNMP و Syslog'],
          ['p','NTP ساعت دستگاه‌ها را هم‌زمان می‌کند (بدون آن، لاگ‌ها بی‌معنا می‌شوند). SNMP نسخهٔ ۳ امن است و وضعیت را می‌خواند؛ Syslog خطاها را به سرور مرکزی می‌فرستد. ترکیب هر سه = چشم و حافظهٔ شبکه.'],
          ['h3','QoS Fundamentals و FHRP'],
          ['p','QoS با علامت‌گذاری (DSCP/CoS) ترافیک حساس مثل VoIP را جلوی صف می‌نشاند. FHRP (HSRP/VRRP/GLBP) دو روتر را پشت یک گیت‌وی مجازی جمع می‌کند تا خرابی روتر اول قطعی ندهد.'],
          ['h3','Port Mirroring (SPAN)'],
          ['p','با SPAN ترافیک یک پورت را روی پورت تحلیل کپی می‌کنیم تا Wireshark بدون وصل فیزیکی، ترافیک را ببیند — پل اجباری بین «دیدن» و «عیب‌یابی».']
        ],
        protocol:[['cli','چهار سرویس کلیدی','! DHCP Relay\nRouter(config)# interface vlan 20\nRouter(config-if)# ip helper-address 10.10.10.20\n\n! NAT Overload\nRouter(config)# access-list 1 permit 192.168.0.0 0.0.0.255\nRouter(config)# interface g0/0\nRouter(config-if)# ip nat outside\nRouter(config)# interface g0/1\nRouter(config-if)# ip nat inside\nRouter(config)# ip nat inside source list 1 interface g0/0 overload\n\n! HSRP\nRouter(config)# interface g0/0\nRouter(config-if)# standby 1 ip 192.168.1.254\nRouter(config-if)# standby 1 priority 110\nRouter(config-if)# standby 1 preempt\n\n! SPAN\nSwitch(config)# monitor session 1 source interface g0/3\nSwitch(config)# monitor session 1 destination interface g0/10']],
        ios:[['cli','مشاوره‌ها','Router# show ip nat translations\nRouter# show ip dhcp binding\nRouter# show standby brief\nSwitch# show monitor session 1\nRouter# show ntp status\nRouter# show logging']],
        diagram:[['svg','topo'],['p','لبهٔ شبکه: NAT بیرون، DHCP/DNS داخل، HSRP روی دو روتر گیت‌وی و SPAN روی سوئیچ — همین چهار جعبه، خدمات این بخش‌اند.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱۱ — DHCP Server و Relay',steps:['pool با network/default-router/dns','helper-address در VLAN دیگر','رزرو IP و بررسی binding']},
          {t:'آزمایشگاه ۱۲ — NAT و PAT',steps:['inside/outside و overload','چند کلاینت پشت یک IP خروجی','static NAT برای یک سرور داخلی']},
          {t:'آزمایشگاه ۱۵ — HSRP',steps:['دو روتر با standby group و priority','preempt و تست failover با قطع روتر اول','بررسی با show standby brief']},
          {t:'آزمایشگاه ۲۱ و ۲۲ — SNMP و NTP',steps:['SNMPv3 با کاربر امن','NTP server/client و هم‌زمانی','Syslog به سرور مرکزی و خواندن لاگ']}
        ]]],
        trouble:[['ul',['کلاینت IP نمی‌گیرد: helper-address، pool و وضعیت پورت VLAN را چک کن','NAT کار نمی‌کند: inside/outside جا به جا؟ ACL مبدأ را می‌گیرد؟','ساعت دستگاه اشتباه: NTP reachability — لاگ‌ها را قابل اعتماد نکن','HSRP فعال نمی‌شود: گروه و پورت یکسان؟ preempt؟']]],
        exercise:[['ol',['یک IP Plan برای سه VLAN با DHCP مرکزی و relay بنویس','سه تفاوت static NAT و dynamic و overload را در جدول','چرا بدون NTP، تحلیل Syslog شکست می‌خورد؟']]],
        quiz:[['quiz',[
          {q:'ip helper-address دقیقاً چه می‌کند؟',opts:['روت پیش‌فرض می‌دهد','broadcast های خاص (مثل DHCP) را unicast به سرور می‌فرستد','NAT می‌کند','DNS را کش می‌کند'],a:1,exp:'relay یعنی broadcast مرز VLAN را رد نمی‌کند؛ helper آن را به سرور دور می‌رساند.'},
          {q:'کدام QoS برای VoIP مناسب‌تر است؟',opts:['بهترین کلاس Best Effort','اولویت (Priority queuing) برای کلاس EF','بدون علامت‌گذاری','افزایش queue depth'],a:1,exp:'صدا تأخیر را تحمل نمی‌کند؛ EF با priority queue همیشه اول سرویس می‌گیرد.'}
        ]]],
        notes:[['ul',['خروجی show ip nat translations و show standby brief را نمونه‌وار ثبت کن','پورت‌های SPAN و نحوهٔ وصل Wireshark را تمرین کن']]
        ]
      }
    },
    { id:'f1-p5', title:'بخش پنجم: Security Fundamentals', sub:'CCNA · بخش ۵ از ۶', minutes:'۳ هفته',
      lead:'امنیت در CCNA یعنی چند لایهٔ ساده اما اجباری: رمز محکم، ACL برای فیلتر، Port Security برای کنترل دسترسی لایهٔ ۲، DHCP Snooping و DAI برای دفاع از LAN و 802.1X برای ورود کنترل‌شده.',
      sec:{
        goal:[['p','تهدیدهای رایج را شناختن، ACL استاندارد و گسترش‌یافته را نوشتن، hardening دستگاه و دفاع‌های لایهٔ ۲ (Port Security، Snooping، DAI) را پیاده‌سازی کردن، و VPN و 802.1X را مفهومی فهمیدن.']],
        prereq:[['ul',['پورت‌ها و پروتکل‌ها','روتینگ و VLAN','دانشکدهٔ صفر: SSH']]],
        concept:[
          ['h3','تهدید و AAA'],
          ['p','تهدید رایج LAN:شنود (Sniffing)، ARP Spoofing، DHCP Rogue، دسترسی فیزیکی غیرمجاز و حملات رمز. AAA چارچوب پاسخ است: Authentication (کیستی؟)، Authorization (چه کاری؟) و Accounting (چه کردی؟) با TACACS+ (سیسکو، پورت جدا) یا RADIUS (استاندارد، پورت 1812).'],
          ['h3','ACL — درِ ورودی'],
          ['p','ACL لیستی از قواعد است که روی بسته اعمال می‌شود؛ از بالا به پایین می‌خوانده، اولین تطبیق برنده است و در انتها implicit deny. استاندارد (شماره ۱ تا ۹۹) فقط آدرس مبدأ را می‌بیند؛ گسترش‌یافته (100-199 و 2000-2699) پروتکل و پورت و مقصد را هم. جایگذاری: «near the source برای استاندارد، near the destination برای گسترش‌یافته».'],
          ['h3','Hardening و Port Security'],
          ['p','پسورد enable، سطوح line، غیرفعال کردن سرویس‌های بی‌استفاده (http server، CDP روی پورت کاربری)، no ip unreachables و فقط SSH. Port Security تعداد MAC مجاز هر پورت را محدود می‌کند و با violation shutdown یا protect واکنش نشان می‌دهد.'],
          ['h3','DHCP Snooping و DAI'],
          ['p','Snooping جدول اعتماد (IP ↔ MAC ↔ پورت) می‌سازد و پورت‌های کاربری را «untrusted» می‌کند تا سرور قلابی جواب ندهد. DAI با همان جدول، ARPهای دروغین را فیلتر می‌کند؛ IP Source Guard هم آدرس مبدأ را کنترل می‌کند. این سه، واکسن LAN در برابر spoofing هستند.'],
          ['h3','802.1X و VPN'],
          ['p','802.1X ورود کنترل‌شدهٔ پورت را با Supplicant/Authenticator/Server سه‌طرفه می‌کند؛ VPN (IPsec یا SSL) تونل رمزگذاری‌شدهٔ امن از راه دور می‌سازد — پایهٔ هر کار از راه دور امن.']
        ],
        protocol:[['cli','ACL در عمل','! استاندارد: فقط مبدأ\nRouter(config)# access-list 10 deny 192.168.1.100\nRouter(config)# access-list 10 permit any\nRouter(config)# interface g0/0\nRouter(config-if)# ip access-group 10 in\n\n! گسترش‌یافته: مبدأ، مقصد، پروتکل، پورت\nRouter(config)# ip access-list extended BLOCK_WEB\nRouter(config-acl)# deny tcp host 192.168.1.50 host 10.10.10.80 eq 80\nRouter(config-acl)# deny tcp host 192.168.1.50 host 10.10.10.80 eq 443\nRouter(config-acl)# permit ip any any\nRouter(config-acl)# exit\nRouter(config)# interface g0/1\nRouter(config-if)# ip access-group BLOCK_WEB out\n\n! Port Security\nSwitch(config)# interface g0/3\nSwitch(config-if)# switchport port-security\nSwitch(config-if)# switchport port-security maximum 2\nSwitch(config-if)# switchport port-security violation shutdown\n\n! DHCP Snooping\nSwitch(config)# ip dhcp snooping\nSwitch(config)# ip dhcp snooping vlan 10,20\nSwitch(config)# interface g0/3\nSwitch(config-if)# ip dhcp snooping trust        ! فقط پورت سرور/سوئیچ\n\n! DAI\nSwitch(config)# ip arp inspection vlan 10,20']],
        ios:[['cli','بررسی امنیتی','Switch# show port-security\nSwitch# show port-security address\nSwitch# show ip dhcp snooping binding\nSwitch# show ip arp inspection statistics vlan 10\nRouter# show access-lists']],
        diagram:[['p','نقشهٔ لایه‌های دفاع: فیزیکی (پورت) ← لایهٔ ۲ (PortSec/Snooping/DAI) ← لایهٔ ۳ (ACL) ← دسترسی (AAA/802.1X) ← تونل (VPN). هر لایه بدون لایهٔ پایین بی‌معناست.']],
        lab:[['labs',[
          {t:'آزمایشگاه ۱۳ — Standard ACL',steps:['ACL شماره‌ای با deny مشخص و permit any','در نزدیک‌ترین نقطهٔ مبدأ اعمال کن','با ping اثبات کن چه کسی رد شد و چه کسی نه','show access-lists ترتیب تطبیق را نشان می‌دهد']},
          {t:'آزمایشگاه ۱۴ — Extended ACL',steps:['فیلتر ترافیک وب به یک سرور خاص','شمارش hit counter برای اثبات','جابه‌جایی to/from و دیدن تفاوت نتیجه']},
          {t:'آزمایشگاه ۱۸ — Port Security',steps:['maximum 2 و violation shutdown','اتصال سومین MAC و دیدن err-disable','بازیابی با errdisable recovery']},
          {t:'آزمایشگاه ۱۹ و ۲۰ — DHCP Snooping و DAI',steps:['Snooping و trust/untrust','ساخت ARP دروغین و فیلتر شدن با DAI','binding table را با show ببین']}
        ]]],
        trouble:[['ul',['ACL اعمال شد ولی ترافیک همچنان می‌رود: implicit permit در انتهای لیست نداری؟ ترتیب قواعد؟','به خودت lock out شدی: always یک permit برای management از مسیر امن در اول لیست','err-disable پورت: show port-security violation — مهاجم یا loop؟','ARP دروغین با DAI رد نشد: binding کامل است؟ پورت trust؟']]],
        exercise:[['ol',['ACL بنویس: فقط VLAN 10 به سرور HTTP دسترسی دارد، بقیه نه','سه خط hardening استاندارد برای یک سوئیچ تازه اضافه‌شده','چرا DAI بدون Snooping کار نمی‌کند؟']]],
        quiz:[['quiz',[
          {q:'ACL استاندارد چه چیزی را بررسی نمی‌کند؟',opts:['آدرس مبدأ','پورت مقصد','هر دو','هیچ‌کدام'],a:1,exp:'استاندارد فقط آدرس مبدأ (و در بعضی موارد مبدأ+مقصد طبقه‌ای) را می‌بیند؛ پورت نه.'},
          {q:'پس از همهٔ قواعد ACL چه اتفاقی می‌افتد؟',opts:['permit همه','deny همه (implicit deny)','بسته دور انداخته نمی‌شود','به مبدأ برمی‌گردد'],a:1,exp:'implicit deny any در انتهای هر ACL هست — به همین دلیل همیشه permit صریح لازم است.'},
          {q:'کدام ویژگی جلوی ARP Spoofing را می‌گیرد؟',opts:['STP','Dynamic ARP Inspection','PortFast','EtherChannel'],a:1,exp:'DAI با جدول Snooping، ARPهای مغایر با binding را رد می‌کند.'}
        ]]],
        notes:[['ul',['قالب hardening شخصی‌ات را برای هر دستگاه بنویس و به آن پایبند باش','هر ACL را با hit counter مستند کن']]
        ]
      }
    },
    { id:'f1-p6', title:'بخش ششم: Automation and Programmability', sub:'CCNA · بخش ۶ از ۶', minutes:'۲ هفته',
      lead:'شبکه‌های امروز با CLI تک‌به‌تک مدیریت نمی‌شوند؛ SDN، کنترلرها، REST API و JSON پایهٔ اتوماسیون‌اند. در CCNA همین‌قدر که مفهوم، ساختار و یک نمونهٔ واقعی را ببینی کافی است — عمق عملی در دانشکدهٔ Automation می‌آید.',
      sec:{
        goal:[['p','تفاوت مدل سنتی با کنترلر-محور، فهم SDN و DNA Center/Catalyst Center، خواندن یک پاسخ REST API به‌صورت JSON، و درک نقش اتوماسیون و AI در شبکهٔ مدرن.']],
        prereq:[['ul',['کار با CLI و پیکربندی دستی','مفاهیم لایه‌ها و API چیست؟','آشنایی مقدماتی با HTTP']]],
        concept:[
          ['h3','Traditional vs Controller-Based'],
          ['p','در مدل سنتی هر دستگاه مستقل تصمیم می‌گیرد (چرخشی ۳۰ دستگاه × ۲۰ دقیقه). در مدل کنترلر-محور، یک سیاست مرکزی (Controller) تعریف می‌شود و دستگاه‌ها اجرا می‌کنند: تغییر در ثانیه‌ها، نه ساعت‌ها.'],
          ['h3','SDN و سه لایه'],
          ['p','SDN سه لایه دارد: داده (Data Plane — انتقال بسته)، کنترل (Control Plane — تصمیم‌گیری با کنترلر) و مدیریت (Management Plane — پیکربندی و مانیتور). DNA Center / Catalyst Center سیاست‌محور (Policy-Based) شبکه‌های سیسکو را از یک داشبورد مدیریت می‌کند.'],
          ['h3','REST API و JSON'],
          ['p','REST یعنی با HTTP و متدهای GET/POST/PUT/DELETE روی «منابع» کار کنی؛ خروجی معمولاً JSON است — همان آرایه‌ها و جفت‌کلید-مقدارهایی که در فایل‌های پیکربندی جدید می‌بینی. یک GET ساده می‌تواند وضعیت هزار پورت را در یک ثانیه بدهد.'],
          ['h3','Configuration Management و AI'],
          ['p',' Ansible/Terraform/Python تغییرات را تکرارپذیر و نسخه‌دار می‌کنند (با Git). AI/ML در شبکه برای الگویابی ترافیک، پیش‌بینی خرابی و پیشنهاد رفع به کار می‌رود — جایی که انسان نمی‌تواند میلیون‌ها نمونه را ببیند.']
        ],
        protocol:[['cli','یک REST API واقعی با cURL','GET https://sandboxdnacenter.com/dna/intent/api/v1/network-device\nHeaders: X-Auth-Token: <token>\n\n{\n  "response": [\n    {\n      "hostname": "access-sw-01",\n      "reachabilityStatus": "Reachable",\n      "platformId": "C9300"\n    }\n  ]\n}'],
          ['cli','از CLI تا API','! پیکربندی سنتی\nSwitch(config)# vlan 30\n\n! همان تغییر با RESTCONF (مفهومی)\nPATCH /restconf/data/...\nContent-Type: application/yang-data+json\n\n{"vlan":{"id":30}}']],
        ios:[['cli','ابزارهای مشاهده','Switch# show running-config | section vlan\n! خروجی JSON مانند (در دستگاه‌های مدرن):\nSwitch# show interfaces brief | format json']],
        diagram:[['p','سه لایهٔ SDN: Management (سیاست و داشبورد) ← Control (کنترلر تصمیم می‌گیرد) ← Data (بسته را جابه‌جا می‌کند). در مدل سنتی هر سه در خودِ دستگاه‌اند.']],
        lab:[['labs',[{t:'آزمایشگاه — اولین API شبکه',steps:['یک سندسند devnet sandbox وصل شو (حساب رایگان)','اولین GET را با cURL بزن و JSON را بخوان','یک تغییر را با POST/PATCH اعمال و با show تأیید کن','نتیجه را در Git مستند کن']}]]],
        trouble:[['ul',['401 Unauthorized: توکن یا header اشتباه است','404: مسیر منابع را با مستندات API چک کن','تغییر اعمال نشد: مدل دستگاه از آن منبع YANG پشتیبانی نمی‌کند — show version + مستندات']]],
        exercise:[['ol',['تفاوت Data و Control و Management Plane را با یک مثال CLI بنویس','یک نمونهٔ JSON از خروجی show خودت بساز','چرا Git برای پیکربندی شبکه لازم است؟']]],
        quiz:[['quiz',[
          {q:'در SDN، کدام لایه تصمیم مسیر را می‌گیرد؟',opts:['Data Plane دستگاه‌ها','Control Plane کنترلر','Management Plane کاربر','لایهٔ فیزیک'],a:1,exp:'کنترلر (مثل DNA Center یا SDN controller) سیاست و مسیر را مرکزی تصمیم می‌گیرد و به دستگاه‌ها می‌دهد.'},
          {q:'کدام متد HTTP یک منبع را می‌خواند؟',opts:['GET','POST','DELETE','PATCH'],a:0,exp:'GET = خواندن؛ POST = ساختن؛ PUT/PATCH = ویرایش؛ DELETE = حذف.'},
          {q:'JSON در شبکه عمدتاً چه نقشی دارد؟',opts:['روتینگ لایهٔ ۳','قالب دادهٔ API ها و خروجی‌ها','جایگزین CLI','استاندارد کابل'],a:1,exp:'JSON زبان مشترک API هاست تا اسکریپت‌ها بتوانند داده را پردازش کنند.'}
        ]]],
        notes:[['ul',['یک حساب DevNet Sandbox بساز و اولین API را همین هفته بزن','تفاوت سه لایهٔ SDN را با نقشهٔ ساده ثبت کن']]
        ]
      }
    },
    { id:'f1-labs', title:'آزمایشگاه‌های الزامی CCNA — ۲۵ سناریو', sub:'خروجی: مستندات و فایل تنظیمات', minutes:'۲۵ × ۵۰ دقیقه',
      lead:'شرط عبور از دانشکدهٔ CCNA: حداقل ۲۵ سناریوی عملی با مستندات کامل (فایل تنظیمات + خروجی‌ها + گزارش یک‌صفحه‌ای). هر سناریو یک مهارت را از «ساخت» تا «عیب‌یابی» پوشش می‌دهد.',
      sec:{
        goal:[['p','اجرای ۲۵ سناریوی زیر در Packet Tracer یا PNETLab، با ثبت خروجی show هر مرحله و گزارش یک‌صفحه‌ای برای هرکدام. نمرهٔ لاب: حداقل ۸۵.']],
        prereq:[['ul',['بخش‌های ۱ تا ۶ CCNA پیش رفته باشند','دفترچهٔ آکادمی و قالب گزارش']]],
        concept:[['p','لاب‌ها تصادفی نیستند: ردیف ۱ تا ۵ ساخت و اتصال، ۶ تا ۱۰ روتینگ، ۱۱ تا ۱۲ سرویس، ۱۳ تا ۱۵ امنیت و دسترسی، ۱۶ تا ۲۲ پیکربندی پیشرفتهٔ خدمات و امنیت، ۲۳ تا ۲۵ تحلیل و عیب‌یابی ترکیبی. اگر سناریویی را بدون مستندات اجرا کنی، انجام‌نشده حساب می‌شود.']],
        protocol:[['table',['شماره','آزمایشگاه','مهارت کلیدی'],[
          ['۱','ساخت شبکهٔ LAN','کابل، پورت، تست ارتباط'],
          ['۲','IP Addressing و Subnetting','VLSM و جدول IP Plan'],
          ['۳','VLAN و Access Port','تفکیک پخش'],
          ['۴','Trunk و Native VLAN','802.1Q و امنیت'],
          ['۵','Inter-VLAN Routing','router-on-a-stick / SVI'],
          ['۶','STP و Root Bridge','انتخاب ریشه و blocked'],
          ['۷','EtherChannel و LACP','لینک منطقی و افزونگی'],
          ['۸','Static Routing','روت دستی دوطرفه'],
          ['۹','Default و Floating Route','خروج و پشتیبان'],
          ['۱۰','OSPF Single Area','همسایگی و جدول'],
          ['۱۱','DHCP Server و Relay','آدرس‌دهی خودکار چند VLAN'],
          ['۱۲','NAT و PAT','خصوصی به عمومی'],
          ['۱۳','Standard ACL','فیلتر مبدأ'],
          ['۱۴','Extended ACL','فیلتر پروتکل/پورت'],
          ['۱۵','HSRP','گیت‌وی افزوده'],
          ['۱۶','IPv6 و SLAAC','آدرس‌دهی نسل دو'],
          ['۱۷','SSH و Hardening','مدیریت امن'],
          ['۱۸','Port Security','کنترل MAC پورت'],
          ['۱۹','DHCP Snooping','دفاع از DHCP'],
          ['۲۰','DAI','دفاع از ARP'],
          ['۲۱','SNMP و Syslog','دیدن و لاگ'],
          ['۲۲','NTP','هم‌زمانی ساعت'],
          ['۲۳','Wireshark و Packet Analysis','دیدن بسته'],
          ['۲۴','WLAN مقدماتی','SSID و AP'],
          ['۲۵','عیب‌یابی شبکهٔ ترکیبی','ترکیب همهٔ مهارت‌ها']
        ]]],
        ios:[['note','tip','قالب گزارش هر لاب: هدف ← توپولوژی (اسکرین‌شات) ← مراحل ← خروجی show کلیدی ← مشکل احتمالی و رفعش ← یک بند «چه یاد گرفتم».']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'استاندارد قبولی هر سناریو',steps:['اجرا بدون راهنمای قدم‌به‌قدم (فقط برای بار اول نگاه می‌کنی)','خروجی showهای کلیدی ثبت شده باشد','یک خطای عمدی ایجاد و رفع شده باشد','فایل .pkt یا پیکربندی کامل ذخیره شده باشد']}]]],
        trouble:[['ul',['سناریو ۲۵ ترکیبی است: اگر قبلاً ۲۴ تا را مستند نکرده باشی، اینجا گیر می‌کنی — مرور کن، نه حفظ','اگر لابی دو بار نیاز به راهنما داشت، آن مهارت را در دفترچه علامت «نیاز به تکرار» بزن']]],
        exercise:[['ol',['از ۲۵ لاب، سه موردی که بیشتر درشان گیر کردی را لیست کن و برای هرکدام یک تکرار ۳۰ دقیقه‌ای برنامه‌ریزی کن']]],
        quiz:[['quiz',[
          {q:'شرایط قبولی آزمایشگاه CCNA چیست؟',opts:['هر نمره‌ای','حداقل ۸۵ از ۱۰۰ + مستندات','فقط اجرا','فکس گزارش'],a:1,exp:'هم نمرهٔ حداقل ۸۵، هم تکمیل مستندات الزامی — نمره جایگزین انجام نمی‌شود.'},
          {q:'کدام سناریو مهارت‌های همهٔ بخش‌ها را جمع می‌کند؟',opts:['سناریوی ۳','سناریوی ۲۵','سناریوی ۱','سناریوی ۱۰'],a:1,exp:'عیب‌یابی ترکیبی (۲۵) آخرین آزمون عملی دانشکده است.'}
        ]]],
        notes:[['ul',['وضعیت ۲۵ لاب را در جدول پیشرفت علامت بزن (localStorage داشبورد)','هر فایل تنظیمات را با نام سناریو در Git ذخیره کن']]
        ]
      }
    },
    { id:'f1-proj', title:'پروژهٔ پایان CCNA — شبکهٔ سازمانی سه‌طبقه', sub:'خروجی: طراحی + اجرا + عیب‌یابی + مستندات', minutes:'۲ هفته',
      lead:'آزمون بزرگ دانشکدهٔ CCNA: یک شبکهٔ واقعی از صفر تا مستندات. یک Core Switch، دو Distribution، چهار Access، چهار VLAN، روتینگ، سرویس‌ها و امنیت — همه با هم، مثل پروژهٔ واقعی.',
      sec:{
        goal:[['p','طراحی، پیاده‌سازی و عیب‌یابی شبکهٔ سه‌طبقه با مشخصات زیر + مستندات کامل (IP Plan، نقشه، پیکربندی، گزارش). شرط قبولی: تأیید طراحی، اجرا و عیب‌یابی.']],
        prereq:[['ul',['۲۵ آزمایشگاه الزامی','نمرهٔ تئوری حداقل ۸۵','نمرهٔ لاب حداقل ۸۵']]],
        concept:[
          ['h3','مشخصات الزامی'],
          ['ul',['یک Core Switch (لایهٔ ۳)','دو Distribution Switch','چهار Access Switch','VLAN های مدیریت، کاربران، سرورها و VoIP','Inter-VLAN Routing','OSPF تک‌ناحیه (حداقل)','DHCP مرکزی با Relay','NAT در لبه','ACL دسترسی سرور','HSRP برای گیت‌وی','مستندسازی کامل شبکه']],
          ['h3','معیار تأیید'],
          ['p','طراحی (IP Plan و نقشه) باید قبل از پیکربندی تأیید شود؛ اجرا باید بدون خطای پایدار (ping بین همهٔ VLANها، خروجی show سالم)؛ عیب‌یابی یعنی سه خطای عمداً واردشده (مثلاً native VLAN ناهمسان، روت اشتباه، ACL بیش از حد) را پیدا و رفع کنی.']
        ],
        protocol:[['svg','topo'],['p','نقشهٔ نهایی: Core وسط، دو Distribution با افزونگی، چهار Access زیر هر کدام — دقیقاً همان چیزی که در مستندات تحویل می‌دهی.']],
        ios:[['cli','نمونهٔ بخشی از پیکربندی نهایی','! Inter-VLAN روی Core\nCore(config)# interface vlan 10\nCore(config-if)# ip address 192.168.10.1 255.255.255.0\n\n! OSPF بین Core و Distribution\nCore(config)# router ospf 1\nCore(config-router)# network 10.0.0.0 0.0.0.3 area 0\n\n! HSRP روی گیت‌وی کاربران\nDist-A(config)# interface vlan 10\nDist-A(config-if)# standby 10 ip 192.168.10.254\nDist-A(config-if)# standby 10 priority 110\nDist-A(config-if)# standby 10 preempt']],
        diagram:[['svg','topo']],
        lab:[['labs',[{t:'چک‌لیست تحویل پروژه',steps:['IP Plan تأییدشده (جدول VLAN/Subnet/Range/Gateway)','نقشهٔ فیزیکی و منطقی','پیکربندی کامل هر دستگاه (فایل جدا)','گزارش عیب‌یابی ۳ خرابی عمداً','فایل نهایی در Git با تاریخچهٔ commit']}]]],
        trouble:[['ul',['پروژه گیر می‌کند: از پایین به بالا بررسی کن — لینک، VLAN، IP، روت، سرویس، ACL','اختلاف نمرهٔ لاب و تئوری: اگر تئوری ۸۵ شد ولی لاب نه، پروژه را شروع نکن — اول لاب']]],
        exercise:[['ol',['قبل از اجرا، یک صفحه «Risk» بنویس: سه احتمال خرابی و راه‌حلشان']]],
        quiz:[['quiz',[
          {q:'شرط عبور از دانشکدهٔ CCNA؟',opts:['فقط آزمون تئوری ۸۵','تئوری ۸۵ + لاب ۸۵ + تأیید پروژه','فقط پروژه','حضور منظم'],a:1,exp:'سه پای شرط با هم؛ نمرهٔ بالا جایگزین بخش‌های الزامی نمی‌شود.'},
          {q:'کدام VLAN معمولاً HSRP می‌خواهد؟',opts:['VLAN سرور فقط','هر VLAN کاربری با گیت‌وی دو روتری','VLAN مدیریت تک‌روتری','VLAN خالی'],a:1,exp:'گیت‌وی کاربران باید افزوده باشد تا خرابی یک روتر شبکه را نخواباند.'}
        ]]],
        notes:[['ul',['نمرات تئوری/لاب/پروژه را در داشبورد ثبت کن','گواهی داخلی دانشکدهٔ CCNA پس از تأیید صادر می‌شود (جایگزین مدرک رسمی Cisco نیست)']]
        ]
      }
    }
  ]
},
