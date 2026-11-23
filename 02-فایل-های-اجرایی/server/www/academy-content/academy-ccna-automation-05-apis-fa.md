# CCNA AUT-05 — Northbound و Southbound API

**سطح:** CCNA. **پیش‌نیاز:** AUT-04. **هدف رسمی:** `6.3.b` توصیف Northbound و Southbound APIها. **محدودهٔ این درس:** جهت رابط، REST/RESTCONF، NETCONF/YANG و مقایسهٔ مفهومی؛ Objective مستقل `6.4` دربارهٔ AI/ML در AUT-06 است. **وضعیت:** پیش‌نویس محتوایی؛ طراحی عملی انجام شده و **اجرا نشده**؛ هیچ API واقعی فراخوانی نشده و هیچ پاسخی از دستگاه واقعی دریافت نشده است.

## اهداف

1. دو جهت API را از **دید کنترلر** تعریف کنید و بگویید هر کدام چه کسی را به چه کسی وصل می‌کند.
2. بفهمید چرا **Northbound معمولاً REST** است و **Southbound متنوع** است.
3. تفاوت **NETCONF** و **RESTCONF** را با معیار عملی تشخیص دهید.
4. نقش **YANG** را بفهمید — و بدانید چه چیزی **نیست**.
5. یک فراخوانی REST را بخوانید و بدانید هر بخش چه معنایی دارد.

## ۱. دو جهت — از دید کنترلر

**قاعدهٔ حافظه:** جهت‌ها را همیشه از **دید کنترلر** تعریف می‌کنیم. مرکز، کنترلر است.

```text
   ┌────────────┐   Northbound   ┌────────────┐   Southbound   ┌────────────┐
   │ برنامه‌ها  │ ◄──────────────► │ کنترلر    │ ◄────────────► │ دستگاه‌ها │
   │ Dashboard  │   REST/JSON     │            │   NETCONF      │ سوییچ/روتر │
   │ اسکریپت    │                 │            │   RESTCONF     │            │
   └────────────┘                 └────────────┘                └────────────┘
```

| API | دو سر | معمولاً | چه کسی آن را می‌بیند |
|---|---|---|---|
| **Northbound** | برنامه ↔ کنترلر | در بسیاری از محصولات REST/JSON؛ شکل API را همان محصول تعریف می‌کند | برنامه‌نویس، اپلیکیشن |
| **Southbound** | کنترلر ↔ دستگاه | NETCONF، RESTCONF، OpenFlow، CLI یا روش‌های پشتیبانی‌شدهٔ دیگر | کنترلر (یا سامانهٔ مدیریت) |

Northbound/Southbound **جهت و مرز ارتباط** را نام‌گذاری می‌کنند، نه یک پروتکل ثابت را. RESTCONF معمولاً برای دسترسی مدل‌محور به دستگاه مطرح است، اما اگر کنترلر نیز آن را ارائه دهد، می‌تواند در مرز دیگری به‌کار رود. پشتیبانی واقعی را از مستندات همان دو Endpoint تعیین کنید.

**چرا Northbound اغلب REST/JSON است؟** برنامه‌ها/Workflowها می‌توانند با API محصول کنترلر کار کنند و بخشی از تفاوت زیرساخت را پشت Abstraction پنهان کنند. این یک گرایش رایج است، نه الزام؛ یک API واحد هم تضمین نمی‌کند همهٔ قابلیت‌های Vendorها کاملاً یکسان مدل شوند.

**چرا Southbound متنوع است؟** Controller باید با Device/Agentهای پشتیبانی‌شده حرف بزند؛ سازوکار ممکن است NETCONF، RESTCONF، OpenFlow، CLI یا روش اختصاصی باشد. یک Controller الزاماً با «همهٔ دستگاه‌ها» صحبت نمی‌کند؛ Compatibility Matrix و مدل/نسخه را بررسی کنید.

## ۲. نمونهٔ واقع‌نما از قالب یک فراخوانی REST

**طراحی‌شده، اجرا‌نشده.** ساختار بر اساس DNA Center / Catalyst Center است، ولی هیچ درخواستی ارسال نشده:

```text
GET https://dnac.lab.local/dna/intent/api/v1/network-device HTTP/1.1
Host: dnac.lab.local
X-Auth-Token: <token>
Accept: application/json
```

پاسخ **طراحی‌شده** (نمونه، اجرا نشده):

```json
{
  "response": [
    {
      "id": "a1b2c3d4-0000-1111-2222-333344445555",
      "hostname": "SW1",
      "managementIpAddress": "10.10.0.11",
      "platformId": "C9300-48P",
      "softwareVersion": "17.9.4a",
      "reachabilityStatus": "Reachable"
    },
    {
      "id": "e5f6a7b8-6666-7777-8888-9999aaaabbbb",
      "hostname": "SW2",
      "managementIpAddress": "10.10.0.12",
      "platformId": "C9300-48P",
      "softwareVersion": "17.9.4a",
      "reachabilityStatus": "Reachable"
    }
  ],
  "version": "1.0"
}
```

**تفسیر خط‌به‌خط:**

| بخش | معنا |
|---|---|
| `GET` | روش HTTP — فقط خواندن، تغییر نمی‌دهد |
| `/dna/intent/api/v1/network-device` | مسیر منبع (Resource Path) |
| `v1` | نسخهٔ API — در تغییرات بزرگ عوض می‌شود |
| `X-Auth-Token` | توکن احراز — **نه نام کاربری و گذرواژه** |
| `Accept: application/json` | فرمت پاسخ را تعیین می‌کند |
| `response[]` | آرایه — همیشه ممکن است چند نتیجه باشد |
| `reachabilityStatus` | وضعیت دسترسی — همیشه باید بررسی شود |

**نکتهٔ عملی مهم:** پاسخ موفق HTTP (`200 OK`) به‌معنای **همه‌چیز درست** نیست. ممکن است `reachabilityStatus: "Unreachable"` باشد. همیشه محتوا را بررسی کنید، نه فقط کد وضعیت.

### چهار روش HTTP

| روش | کار رایج | ویژگی معنایی HTTP |
|---|---|---|
| `GET` | خواندن Representation | Safe و Idempotent؛ طبق قرارداد، تغییر موردنظر کاربر ایجاد نمی‌کند |
| `POST` | ایجاد/پردازش بر اساس منبع مقصد | عموماً نه Safe و نه Idempotent؛ API می‌تواند قرارداد ویژه داشته باشد |
| `PUT` | ایجاد یا جایگزینی کامل منبع در URI مشخص | Idempotent؛ تکرار همان درخواست باید به همان وضعیت نهایی برسد |
| `PATCH` | تغییر جزئی منبع | Idempotency به عملیات/قرارداد بستگی دارد؛ خود PATCH تضمین نمی‌کند |
| `DELETE` | درخواست حذف منبع | Idempotent از نظر وضعیت نهایی؛ پاسخ تکراری می‌تواند متفاوت باشد |

**Safe** یعنی عملیات طبق قرارداد نباید وضعیت منبع را به‌قصد تغییر عوض کند؛ **Idempotent** یعنی تکرار درخواست اثر نهاییِ اضافه نداشته باشد. این معناها را با تضمین موفقیت یا بی‌خطر بودن هر API خاص یکی نگیرید.

Idempotent بودن دربارهٔ **اثر نهایی روی منبع** است، نه لزوماً یکسان‌بودن کد پاسخ در هر بار. `POST` عموماً چنین تضمینی ندارد؛ معنای دقیق هر Endpoint را مستندات API تعیین می‌کند.

## ۳. NETCONF، RESTCONF و YANG

### YANG — مدل داده، نه پروتکل

**YANG** زبان مدل‌سازی داده است. مشخص می‌کند یک دستگاه چه فیلدهایی دارد و چه نوعی دارند. مثلاً مدل یک Interface:

```text
module: ietf-interfaces
  +--rw interfaces
     +--rw interface* [name]
        +--rw name              string
        +--rw description?      string
        +--rw type              identityref
        +--rw enabled?          boolean
```

معنای نمادها:

- `rw` = خواندن و نوشتن
- `ro` = فقط خواندن (Config نیست)
- `?` = اختیاری
- `*` = چندتایی
- `[name]` = کلید یکتا

**YANG یک پروتکل نیست.** این زبان Schema/مدل را تعریف می‌کند. RESTCONF بر مدل‌های YANG بنا شده است؛ NETCONF می‌تواند با مدل‌های YANG کار کند، اما خود NETCONF به YANG محدود نیست. این پروتکل‌ها معمولاً با دادهٔ مطابق مدل تبادل می‌کنند؛ لزوماً فایل Schema را در هر درخواست «منتقل» نمی‌کنند.

### NETCONF

- پروتکل مبتنی بر **XML**
- روی **SSH** (پورت **830**)
- عملیات‌های پایه‌ای مانند `<get>`، `<get-config>`، `<edit-config>` و `<copy-config>` دارد.
- قابلیت‌هایی مثل datastore `candidate`، `<commit>`، `confirmed-commit` و `rollback-on-error` به Capabilityهای اعلام‌شدهٔ دستگاه وابسته‌اند و نباید روی هر پیاده‌سازی مفروض گرفته شوند.

**احتیاط:** NETCONF به‌تنهایی تضمین نمی‌کند هر دستگاه هر تغییر چندبخشی را با Commit/Rollback کامل اجرا کند. پیش از طراحی تراکنش، datastoreها و capabilityهای Endpoint را بررسی کنید؛ `running` نیز ممکن است مستقیماً قابل ویرایش باشد.

نمونهٔ طراحی‌شده، اجرانشده:

```xml
<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <edit-config>
    <target><running/></target>
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>GigabitEthernet0/1</name>
          <description>Uplink to SW2</description>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
  </edit-config>
</rpc>
```

### RESTCONF

- رابط RESTful مبتنی بر HTTP و مدل دادهٔ YANG؛ Payload می‌تواند JSON یا XML باشد.
- برای حفاظت از داده و اعتبارنامه در استقرار واقعی، HTTPS/TLS به‌کار ببرید؛ 443 پورت رایج HTTPS است، اما پورت و تنظیم Endpoint را باید از محصول هدف بخوانید.
- از روش‌های HTTP مانند `GET`، `POST`، `PUT`، `PATCH` و `DELETE` استفاده می‌کند؛ دسترسی و پشتیبانی روش‌ها به Capability و Policy وابسته است.
- مسیر منبع از مدل YANG/نحو RESTCONF ساخته می‌شود.

نمونهٔ طراحی‌شده، اجرانشده:

```text
PATCH https://10.10.0.11/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet0%2F1
Content-Type: application/yang-data+json
Accept: application/yang-data+json
Authorization: Basic <base64>

{
  "ietf-interfaces:interface": {
    "name": "GigabitEthernet0/1",
    "description": "Uplink to SW2",
    "enabled": true
  }
}
```

`Basic` هویت را با Base64 کدگذاری می‌کند؛ Base64 **رمزنگاری نیست**. در محیط واقعی از TLS، اعتبارنامهٔ کم‌امتیاز و مدیریت امن Secret استفاده کنید؛ Secret را در فایل، Git، لاگ یا خط فرمانِ قابل‌مشاهده رها نکنید. این درخواست نمونه همچنان اجرا‌نشده است.

**تفسیر مسیر:** `/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet0%2F1`

- `restconf/data` — بخش داده
- `ietf-interfaces:interfaces` — نام Module:Container
- `interface=GigabitEthernet0%2F1` — نمونهٔ مشخص (`/` به `%2F` کدگذاری شده، چون `/` در REST جداکننده است)

### مقایسهٔ NETCONF و RESTCONF

| ویژگی | NETCONF | RESTCONF |
|---|---|---|
| فرمت | XML | JSON یا XML |
| انتقال رایج | SSH؛ 830 پورت پیش‌فرض/رایج NETCONF روی SSH | HTTP؛ استقرار امن معمولاً HTTPS/TLS است و 443 رایج است |
| سبک | RPC | **RESTful** |
| تراکنش پیکربندی | `candidate`/`commit` و `confirmed-commit` در صورت پشتیبانی؛ رفتار وابسته به Capability | روش‌های HTTP؛ پروتکل به‌تنهایی همان گردش کار `candidate`/`commit` را تضمین نمی‌کند |
| یادگیری | RPC/XML و Capabilityهای NETCONF باید فهمیده شوند | برای ابزارهای HTTP معمولاً آشناتر، اما همچنان به مدل و مجوز نیاز دارد |
| کاربرد معمول | پیکربندی/خواندن مدل‌محور با عملیات RPC | خواندن/تغییر منبع مدل‌محور از راه HTTP |

**نکتهٔ آزمونی:** NETCONF و RESTCONF هر دو می‌توانند با مدل‌های YANG کار کنند، اما YANG زبان مدل‌سازی است، نه پروتکل؛ NETCONF/RESTCONF پروتکل/رابط‌های متفاوت‌اند. قابلیت تراکنش را از دستگاه هدف بررسی کنید؛ اصطلاح **Intent** به‌تنهایی تفاوت یا تراکنش را تضمین نمی‌کند.

## ۴. OpenFlow — Southbound متفاوت

**OpenFlow** پروتکل Southbound است که **جدول Forwarding** را مستقیماً برنامه‌ریزی می‌کند. برخلاف NETCONF/RESTCONF که **پیکربندی** می‌دهند، OpenFlow **جریان (Flow)** تعریف می‌کند: «بسته با مشخصات X، به پورت Y برود».

| ابزار | چه می‌فرستد | چه چیزی تغییر می‌کند |
|---|---|---|
| NETCONF / RESTCONF | پیکربندی | Config دستگاه |
| **OpenFlow** | **Flow Entry** | **جدول Forwarding** |
| CLI | فرمان | Config دستگاه |

**تفاوت مهم:** با NETCONF می‌گویید «VLAN 10 بساز»؛ با OpenFlow می‌گویید «بسته با ingress port 1 به port 2 برو». OpenFlow سطح **پایین‌تر** است.

## ۵. سناریوی طراحی‌شده

**PNETLab مستقل، طراحی‌شده و اجرا‌نشده:** کنترلر فرضی، یک برنامهٔ پایش از Northbound استفاده می‌کند و دو سوییچ از Southbound پیکربندی می‌شوند. **هیچ API واقعی در دسترس نبوده و هیچ درخواستی ارسال نشده است.**

```text
┌─────────────────────────────────────────────────────┐
│  برنامهٔ پایش (اسکریپت Python)                       │
└──────────────────────┬──────────────────────────────┘
                       │ Northbound: GET /api/v1/devices (REST)
                       ↓
┌─────────────────────────────────────────────────────┐
│  Controller (فرضی)                                  │
└──────────────────────┬──────────────────────────────┘
                       │ Southbound: NETCONF / RESTCONF
        ┌──────────────┼──────────────┐
        ↓                             ↓
     [SW1:830]                     [SW2:830]
```

![نمودار قابل ویرایش API‌ها؛ اجرا‌نشده](academy-images/aut-05-apis.svg)

**سناریوی نقص طراحی‌شده (اجرا نشده):** اسکریپت Northbound پاسخ `200 OK` می‌گیرد ولی `reachabilityStatus` را بررسی نمی‌کند. تعداد دستگاه‌ها اشتباه گزارش می‌شود. **درس:** بررسی کد HTTP کافی نیست، محتوا هم لازم است.

## ۶. کاربرگ تحلیلی و تمرین اختیاری

Objective `6.3.b` فعل Describe دارد؛ تمرین اصلی را بدون Controller/PNETLab حل کنید. سناریو و جواب‌های زیر فرضی‌اند، نه Capture:

1. برنامهٔ `App-A` به API کنترلر `GET /api/v1/devices` می‌فرستد؛ کدام سمت Northbound است؟ **پاسخ:** App-A↔Controller.
2. Controller با Device `SW1` از NETCONF استفاده می‌کند؛ کدام سمت Southbound است؟ **پاسخ:** Controller↔SW1.
3. اگر Controller به App پاسخ HTTP 200 بدهد ولی JSON برای SW1 مقدار `reachabilityStatus: Unreachable` داشته باشد، چه نتیجه می‌گیرید؟ **پاسخ:** درخواست API از نظر HTTP پاسخ گرفته، اما وضعیت Device جداست؛ علت Reachability باید در مسیر مدیریت/Device بررسی شود.
4. YANG، NETCONF و RESTCONF را دسته‌بندی کنید: **پاسخ:** YANG مدل داده؛ NETCONF و RESTCONF روش/پروتکل دسترسی و تبادل با ویژگی‌های متفاوت.
5. آیا RESTCONF الزاماً Northbound است؟ **پاسخ:** خیر؛ اصطلاح جهت Endpoint را می‌گوید و RESTCONF معمولاً برای APIهای مدل‌محور Device به‌کار می‌رود، اما جای استفاده به طراحی بستگی دارد.

### تمرین اختیاری برای Endpoint سازگار (طراحی‌شده و اجرا‌نشده)

**این تمرین روی هر PNETLab Image قابل‌اجرا فرض نشده است.** فقط در Lab ایزوله با Deviceی انجام دهید که مستندات دقیق Model/IOS XE آن NETCONF/RESTCONF را پشتیبانی کند، Client مجاز، Certificate معتبر و Console/روش بازگشت داشته باشد. Credential را در Git، screenshot، command history یا سند ثبت نکنید.

1. پیش از تغییر، پشتیبانی NETCONF/RESTCONF، روش مجوز/AAA، TLS، مدل YANG و دستورات Enable را از همان نسخه بررسی کنید؛ اگر پشتیبانی مستند نیست، «قابل اجرا نیست» ثبت کنید.
2. Enable کردن Service (برای نمونه بعضی IOS XEها از `netconf-yang`, `restconf` و Secure HTTP استفاده می‌کنند) فقط در Snapshot دورریختنی و با دستور دقیق مستند همان Image انجام شود.
3. NETCONF روی TCP/830 را با **NETCONF client/subsystem** و RPC معتبر بیازمایید؛ SSH معمولی به‌صورت Interactive Shell روی Port 830، خودبه‌خود `<get-config>` اجرا نمی‌کند. خروجی `get` را با فرمت/Capability ثبت کنید.
4. برای RESTCONF از HTTP Client به Endpoint مستند استفاده کنید؛ HTTPS/TLS و CA/Certificate را Verify، Method/Accept/Content-Type را ثبت و Status Code را همراه Body بررسی کنید. Secret را از log/command line پنهان کنید.
5. برای این Objective به `PATCH` یا تغییر Config نیاز نیست. هر Mutation فقط با مجوز، Snapshot، Change Plan و Rollback در Lab مجزا انجام شود؛ در غیر این صورت فقط GET را آزمایش کنید.

**وضعیت این سند:** هیچ Controller، PNETLab Image، NETCONF Session، RESTCONF Request یا پاسخ واقعی آزمایش/دریافت نشده است.

## ۷. سؤال‌ها و پاسخ

1. **Northbound API چیست؟** ارتباط کنترلر با برنامه‌ها (بالا). معمولاً REST.

2. **Southbound API چیست؟** ارتباط کنترلر با دستگاه‌ها (پایین). NETCONF، RESTCONF، OpenFlow یا اختصاصی.

3. **جهت را از دید چه کسی تعریف می‌کنیم؟** کنترلر. همیشه.

4. **YANG چیست؟** زبان مدل‌سازی داده. **پروتکل نیست.**

5. **NETCONF معمولاً روی چه پروتکلی و پورتی است؟** روی SSH، معمولاً TCP/830؛ Capability/انتقال پشتیبانی‌شده را در Endpoint هدف بررسی کنید.

6. **RESTCONF معمولاً از چه انتقالی استفاده می‌کند؟** HTTP؛ برای حفاظت از اعتبارنامه و داده در استقرار واقعی HTTPS/TLS به‌کار ببرید. TCP/443 رایج است، ولی تنظیم واقعی Endpoint ملاک است.

7. **NETCONF از چه فرمتی استفاده می‌کند؟** XML.

8. **RESTCONF از چه فرمتی استفاده می‌کند؟** JSON یا XML.

9. **تفاوت اصلی NETCONF و RESTCONF؟** NETCONF عملیات RPC و XML را به‌کار می‌گیرد؛ RESTCONF رابط HTTP/RESTful و JSON یا XML دارد. هر دو می‌توانند از مدل YANG استفاده کنند، اما Capability و تراکنش را باید در دستگاه هدف بررسی کرد.

10. **OpenFlow چه تفاوتی با NETCONF دارد؟** NETCONF پیکربندی می‌دهد؛ OpenFlow جدول Forwarding را مستقیماً برنامه‌ریزی می‌کند.

11. **چرا Northbound در بسیاری از محصولات REST است؟** برنامه‌ها و ابزار وب اغلب با APIهای HTTP/REST کار می‌کنند؛ این یک گرایش رایج است، نه الزام یا قرارداد واحد.

12. **HTTP 200 کافی است؟** نه. محتوا (مثلاً `reachabilityStatus`) هم باید بررسی شود.

13. **Abstraction چه مزیتی دارد؟** برنامه‌نویس با مدل کار می‌کند، نه با CLI دستگاه. تغییر کنترلر یا دستگاه لزوماً API برنامه را عوض نمی‌کند.

14. **آیا در این درس API واقعی فراخوانی شده است؟** خیر. همهٔ درخواست‌ها و پاسخ‌ها طراحی‌شده‌اند.

## واژه‌نامه و چک‌لیست

**Northbound**: به سمت برنامه؛ **Southbound**: به سمت دستگاه؛ **REST**: سبک معماری HTTP؛ **RESTCONF**: پیکربندی RESTful با YANG؛ **NETCONF**: پروتکل XML روی SSH؛ **YANG**: مدل داده؛ **OpenFlow**: برنامه‌ریزی جدول Forwarding؛ **VTEP**: نقطهٔ پایانی تونل؛ **Idempotent**: تکرارپذیر بدون اثر اضافه؛ **Resource**: منبع REST.

- [ ] دو جهت را از دید کنترلر می‌دانم.
- [ ] می‌دانم YANG **پروتکل نیست**.
- [ ] NETCONF و RESTCONF را با پورت و فرمت تفکیک می‌کنم.
- [ ] OpenFlow را از NETCONF در سطح عملیات تفکیک می‌کنم.
- [ ] می‌دانم بررسی کد HTTP کافی نیست.
- [ ] هیچ API را فراخوانی‌شده اعلام نمی‌کنم.
