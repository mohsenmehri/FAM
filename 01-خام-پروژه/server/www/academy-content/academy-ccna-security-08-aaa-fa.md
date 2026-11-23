# CCNA SEC-08 — Authentication، Authorization و Accounting

**سطح:** CCNA. **پیش‌نیاز:** SEC-03. **هدف رسمی:** `5.8` مقایسهٔ مفاهیم Authentication، Authorization و Accounting. **وضعیت:** پیش‌نویس محتوایی؛ سناریو طراحی‌شده و **اجرا‌نشده**؛ هیچ سرور AAA واقعی نصب نشده است.

## اهداف

1. تفاوت دقیق سه A را بیان کنید و بگویید هر کدام به چه سؤالی پاسخ می‌دهد.
2. تفاوت AAA محلی و متمرکز را توضیح دهید.
3. RADIUS و TACACS+ را از نظر مناسب‌بودن مقایسه کنید.
4. تصمیم **Fail Open / Fail Closed** را برای یک سناریوی مشخص بگیرید و پیامدش را توضیح دهید.

## ۱. سه A — نه یکی، سه تصمیم مستقل

| مفهوم | سؤال | اتفاق در عمل | شکست آن |
|---|---|---|---|
| **Authentication (AuthN)** | «شما کی هستید؟» | کاربر با نام و گذرواژه/گواهی/MFA هویت خود را اثبات می‌کند | کاربر ناشناس وارد می‌شود |
| **Authorization (AuthZ)** | «چه کاری مجازید؟» | سطح دسترسی و مجوز فرمان تعیین می‌شود | کاربر از حد مجاز فراتر می‌رود (**Privilege Escalation**) |
| **Accounting (Acct)** | «چه کاری انجام دادید؟» | شروع، پایان و فرمان‌ها ثبت می‌شود | رخداد قابل ردیابی نیست |

**این سه مستقل‌اند.** سه ترکیب واقعی را در نظر بگیرید:

1. هویت تایید شد، ولی مجوز `configure terminal` نداشت → کاربر احراز شد، ولی دسترسی محدود ماند. (AuthN ✅، AuthZ ❌)
2. هویت تایید شد و دسترسی داشت، ولی رخداد ثبت نشد → مدیر همه‌کاره است و هیچ ردی نمی‌ماند. (AuthN ✅، AuthZ ✅، Acct ❌)
3. مدیری از یک دستگاه ناشناس با گذرواژهٔ مشترک تیم تایید شد → همه یک هویت دارند، هیچ‌کس قابل ردیابی نیست. (AuthN ضعیف، Acct بی‌فایده)

این تفکیک مهم است چون در آزمون و در طراحی واقعی، سؤالات معمولاً نزدیک همین مرزها هستند.

## ۲. authN/local یا متمرکز؟

| جنبه | AAA محلی | AAA متمرکز (Server) |
|---|---|---|
| محل پیکربندی | روی خود دستگاه | سرور RADIUS/TACACS+ |
| تعداد کاربر | تعداد کم | هزاران |
| یکپارچگی | همان کاربر باید روی هر دستگاه تعریف شود | یک منبع |
| تغییر سیاست | روی هر دستگاه جدا | یک‌جا |
| دسترسی در قطع شبکه | به سرور بیرونی وابسته نیست؛ اگر دستگاه و پیکربندی محلی قابل دسترس باشد | وابسته به سرور/مسیر شبکه |
| مناسب برای | دسترسی اضطراری، شبکهٔ کوچک | سازمان، شبکهٔ متوسط و بزرگ |

AAA محلی از نظر مقیاس و مدیریت ضعیف است، ولی وابسته‌نبودن به سرور بیرونی آن را برای مسیر اضطراری (**Break-Glass**) مفید می‌کند؛ دسترسی همچنان به سلامت دستگاه، خط Console/شبکه و تنظیم درست وابسته است.

## ۳. RADIUS در برابر TACACS+

| ویژگی | RADIUS | TACACS+ |
|---|---|---|
| استاندارد/مشخصات | RADIUS: RFC 2865 (احراز/مجوز) و RFC 2866 (Accounting) | TACACS+: توسعه‌یافته توسط Cisco و مستند در RFC 8907 (Informational) |
| پروتکل انتقال | معمولاً UDP | معمولاً TCP |
| پورت پیش‌فرض | `1812` (AuthN)، `1813` (Acct) — قدیمی‌تر: `1645/1646` | `49` |
| حفاظت پیام | در RADIUS معمولی، ویژگی `User-Password` با روش قدیمی پنهان می‌شود؛ کل بسته رمز نمی‌شود (RadSec/TLS در صورت پشتیبانی، لایهٔ انتقال را محافظت می‌کند) | بدنه با مبهم‌سازی مبتنی بر MD5 و Shared Secret پوشانده می‌شود؛ Header آشکار است و این روش جای حفاظت امن Transport را نمی‌گیرد |
| تفکیک سه A | AuthZ در ویژگی‌های پاسخ Access-Accept می‌آید؛ جداسازی پروتکلی مستقل مثل TACACS+ ندارد | پیام‌های AuthN، AuthZ و Accounting جدا هستند |
| دستور (Command) Authorization | در IOS معمولاً به ظرافت TACACS+ نیست | Authorization ریزدانهٔ فرمان در پیاده‌سازی‌های پشتیبان |
| مناسب برای | دسترسی شبکه (802.1X، VPN، Wi-Fi) | **مدیریت دستگاه (CLI)** |
| نمونهٔ سرور | FreeRADIUS، Windows NPS | Cisco ISE، TACACS+ daemon |

**چرا TACACS+ برای مدیریت دستگاه بهتر است؟**

1. از TCP استفاده می‌کند؛ TCP ترتیب و بازفرستادن را مدیریت می‌کند، اما به‌تنهایی تحویل پایدار Accounting یا دسترس‌پذیری سرور را تضمین نمی‌کند.
2. بدنهٔ پیام با مبهم‌سازی مبتنی بر MD5 و Shared Secret پوشانده می‌شود و Header آشکار می‌ماند؛ آن را رمزنگاری مدرن یا جایگزین حفاظت Transport ندانید. شبکهٔ مدیریتی را هم محدود و محافظت کنید.
3. **Command Authorization** دارد: می‌توانید بگویید «مدیر X می‌تواند `show` بزند ولی `configure` نه». RADIUS این را به این دقت پشتیبانی نمی‌کند.
4. سه A کاملاً جدا هستند، پس می‌توانید Authorization یا Accounting را از یک سرور دیگر بگیرید.

**چرا RADIUS برای دسترسی شبکه رایج است؟** چون استاندارد باز و در تجهیزات VPN، Wi-Fi و 802.1X گسترده‌پشتیبانی‌شده است؛ قابلیت‌ها و Interoperability را همچنان با دستگاه و سرور هدف بررسی کنید.

در عمل، خیلی از سازمان‌ها **هر دو** را دارند: RADIUS برای 802.1X و VPN، TACACS+ برای مدیریت دستگاه.

## ۴. زنجیرهٔ AAA و مفهوم Method List

روی IOS، ترتیب منابع در **Method List** تعیین می‌شود:

```text
aaa authentication login default group tacacs+ local
```

یعنی: «اول از TACACS+ بپرس؛ اگر پاسخ نداد (خطا، Timeout، سرور inaccessible)، از `local` بپرس».

نکتهٔ ظریف که در آزمون زیاد می‌آید: `local` **فقط** در صورت **خطا** یا **عدم دسترسی به سرور** استفاده می‌شود. اگر سرور در دسترس باشد و پاسخ `Access-Reject` بدهد، `local` **امتحان نمی‌شود** و ورود رد می‌شود. این تفاوت با تصور رایج متفاوت است.

منابع ممکن در Method List:

| کلیدواژه | معنا |
|---|---|
| `group tacacs+` / `group radius` | سرور تعریف‌شده |
| `local` | پایگاه کاربر محلی روی خود دستگاه |
| `enable` | گذرواژهٔ `enable` |
| `none` | هیچ احراز هویتی انجام نمی‌شود (بدون بررسی) |
| `line` | گذرواژهٔ خط (Console/VTY) |

`none` احراز هویت را حذف می‌کند؛ آن را برای مدیریت راه‌دور به‌کار نبرید. Break-Glass باید حساب محلی محدود و قابل حسابرسی داشته باشد، نه ورود بی‌احراز.

## ۵. Fail Open یا Fail Closed — تصمیم آگاهانه

**تعریف:**

- **Fail Open** — اگر سرور AAA در دسترس نبود، **اجازه** داده می‌شود.
- **Fail Closed** — اگر سرور در دسترس نبود، **رد** می‌شود.

این تصمیم، تصمیم **ریسک** است، نه تصمیم فنی:

| معیار | Fail Open | Fail Closed |
|---|---|---|
| دسترسی در قطع شبکه | حفظ می‌شود | قطع می‌شود |
| ریسک امنیتی | اگر شبکه قطع شده، مهاجم می‌تواند وارد شود | دسترسی کامل قطع |
| اثر کسب‌وکار | پایین | می‌تواند فاجعه باشد (مدیر نمی‌تواند وارد شود) |
| جایگزین توصیه‌شده | مسیر Break-Glass جدا و محدود | — |

### رویکرد توصیه‌شده برای شبکهٔ واقعی

یک الگوی رایج به‌جای Fail Open/Closed خالص:

1. **مدیریت اصلی** → `group tacacs+ local` — در خطای/Timeout سرور، کاربر محلی معتبر امتحان می‌شود (Fail Local، نه Fail Open؛ Access-Reject از سرور به‌تنهایی fallback نمی‌کند).
2. **کاربر محلی فقط برای اضطراری** — حساب محدود از نظر تعداد و نگهداری‌شده در Vault، با Privilege مطابق نیاز و رویدادنگاری.
3. **Console** → برایش Method List محلیِ صریح بسازید و به خط Console اعمال کنید؛ روش پیش‌فرض ممکن است روی خطوطی که override نشده‌اند اعمال شود. Console فیزیکی هم کنترل شود.
4. **هیچ‌گاه** `none` در خط VTY مدیریتی نمی‌گذارید.

چرا «`group tacacs+ local`» Fail Open نیست؟ چون کاربر باید **همچنان** کاربر معتبر محلی باشد. Fail Open واقعی یعنی `none` — هر کسی وارد می‌شود. تفاوت مهمی است.

### تصمیم برای سناریوی این درس

سازمان فرضی: «شبکهٔ ۲۴ ساعته با SLA ۹۹.۹٪. اگر مدیر در ساعت ۳ صبح نتواند وارد شود، تیم عملیات نمی‌تواند رخداد را رفع کند.»

تصمیم طراحی: `group tacacs+ local` با دو حساب اضطراری و بدون `none`.

اگر Fail Open خالص با `none` می‌گذاشتید، هر مبدأیی که به VTY دسترسی شبکه‌ای دارد بدون اعتبارسنجی هویت وارد می‌شد؛ محدودیت شبکه یا ACL جلوی احراز هویت‌نشده را نمی‌گیرد. اگر Fail Closed خالص می‌خواستید، حتی برای یک رخداد کوچک، شبکه بدون مدیر می‌ماند. گزینهٔ وسط (کاربر اضطراری محلی) هر دو ریسک را کاهش می‌دهد.

## ۶. سناریوی طراحی‌شده و پیکربندی

**PNETLab مستقل، طراحی‌شده و اجرا‌نشده.**

```text
   [Admin workstation 10.10.0.50]
                 |
      ┌──────────┴──────────┐
      |                     |
   [R1 10.10.0.1]       [R2 10.10.0.2]
      |                     |
      └──────────┬──────────┘
                 |
      [TACACS+ Server 10.10.0.200] · [RADIUS Server 10.10.0.200]
```

| مؤلفه | آدرس | نقش |
|---|---|---|
| سرور TACACS+ | `10.10.0.200:49` | مدیریت دستگاه (AuthN/AuthZ/Acct) |
| سرور RADIUS | `10.10.0.200:1812/1813` | دسترسی شبکه |
| Admin-ws | `10.10.0.50` | ایستگاه مدیر |
| R1، R2 | `10.10.0.1`، `10.10.0.2` | دستگاه‌های مدیریت‌شده |

![نمودار قابل ویرایش سرور AAA و دستگاه‌های مدیریت‌شده؛ اجرا‌نشده](academy-images/sec-08-aaa.svg)

**همهٔ فرمان‌ها اجرا‌نشده‌اند.**

### گام ۱ — تعریف سرور TACACS+

```text
enable
configure terminal
tacacs server TAC1
 address ipv4 10.10.0.200
 key 0 <shared-secret>
 exit
```

- `tacacs server TAC1` — یک سرور با نام محلی `TAC1`.
- `address ipv4` — آدرس سرور.
- `key 0` — Shared Secret را به‌صورت ورودیِ روشن می‌گیرد (۰ یعنی ورودی clear-text، نه رمزگذاری امن در Configuration). در سند از Placeholder استفاده کنید و Secret واقعی را افشا نکنید؛ مقدار/نوع ذخیره‌شده و نحو را با IOS هدف بررسی کنید. کلید دستگاه و سرور باید دقیقاً یکسان باشد.

### گام ۲ — حساب محلی، سپس AAA و Console صریح

پیش از فعال‌کردن AAA، حساب اضطراری محلی را بسازید؛ از Secret یکتا و تصادفی و مطابق سیاست طول استفاده کنید. سپس فهرست احراز محلی را صریحاً به Console وصل کنید:

```text
username netadmin privilege 15 secret <long-unique-secret>
aaa new-model
aaa authentication login CONSOLE local
line console 0
 login authentication CONSOLE
 exit
```

`aaa new-model` رفتار احراز هویت را تغییر می‌دهد. فهرست `default` می‌تواند به Console هم اعمال شود؛ Console را «خودکار مستثنا» فرض نکنید. حساب محلی را قبل از تغییر بسازید و Console را در دسترس نگه دارید؛ سپس Method List مخصوص Console را پیکربندی و جداگانه آزمایش کنید. خطای ترتیب یا Named List می‌تواند دسترسی را قطع کند.

### گام ۳ — تعریف Method Listها

```text
aaa group server tacacs+ TAC-GRP
 server name TAC1
 exit
aaa authentication login default group TAC-GRP local
aaa authorization exec default group TAC-GRP local
aaa authorization commands 15 default group TAC-GRP local
aaa accounting exec default start-stop group TAC-GRP
aaa accounting commands 15 default start-stop group TAC-GRP
line vty 0 4
 login authentication default
 transport input ssh
 exit
```

بازهٔ `VTY 0–4` نمونه است؛ همهٔ VTYهای موجود را با `show line` پیدا و روی هر بازه فهرست مناسب و SSH اعمال کنید. پیش‌نیازهای SSH در Services-08 است. Syntax و فرمان‌های AAA به پلتفرم/IOS وابسته‌اند و باید پیش از تولید روی Image هدف بررسی شوند.

| فرمان | معنا |
|---|---|
| `aaa authentication login default group TAC-GRP local` | ورود: اول TACACS+، در خطا/عدم پاسخ `local` |
| `aaa authorization exec default group TAC-GRP local` | مجوز ورود به EXEC و سطح دسترسی از TACACS+؛ Fallback طبق رفتار Method List |
| `aaa authorization commands 15 ...` | مجوز فرمان‌های Privilege 15 از TACACS+ |
| `aaa accounting exec ... start-stop` | ثبت شروع و پایان جلسهٔ EXEC |
| `aaa accounting commands 15 ... start-stop` | ثبت فرمان‌های Privilege 15؛ برای سطوح دیگر Method List جدا لازم است |

`start-stop` یعنی **هم شروع و هم پایان** ثبت شود. گزینهٔ `stop-only` فقط پایان را ثبت می‌کند و برای بررسی «چه کسی چه کاری انجام داد» کافی نیست.

### گام ۴ — رادیوس برای دسترسی شبکه (در صورت نیاز)

```text
radius server RAD1
 address ipv4 10.10.0.200 auth-port 1812 acct-port 1813
 key 0 <shared-secret>
 exit
aaa group server radius RADIUS-GRP
 server name RAD1
 exit
```

این بخش در سناریوی مدیریت دستگاه لازم نیست، ولی برای 802.1X و VPN کاربرد دارد. تفکیک دو سرویس (TACACS+ برای مدیریت، RADIUS برای دسترسی) یک طراحی رایج است. در هر دو مورد، `key 0` به معنی ورودی روشن است؛ فایل پیکربندی و Secret را محافظت کنید و قابلیت رمزنگاری/ذخیره‌سازی را روی IOS هدف بررسی کنید.

## ۷. Verification و تفسیر خروجی

**نمونهٔ طراحی‌شده، اجرا‌نشده.**

```text
R1# show aaa servers
RADIUS: id 1, priority 1, host 10.10.0.200, auth-port 1812, acct-port 1813
     State: current UP, duration 00:32:14, previous state retries 0
     Total Dead Time: 00:00:00, Dead Time period: 00:05:00
     Queries: 48, Successes: 46, Failures: 2, Timeouts: 0

TACACS+: id 1, priority 1, host 10.10.0.200, port 49
     State: current UP, duration 00:32:14, previous state retries 0
     Total Dead Time: 00:00:00, Dead Time period: 00:05:00
     Queries: 31, Successes: 31, Failures: 0, Timeouts: 0
```

تفسیر:

- `State: current UP` — سرور در دسترس است.
- `Queries/Successes/Failures/Timeouts` — شمارنده‌ها را با رفتار سامانه تطبیق دهید. `Failures` می‌تواند Reject سیاستی، کلید/پیکربندی ناهماهنگ یا خطای دیگر باشد؛ فقط با آن علت را تعیین نکنید و Log سمت سرور را هم ببینید.
- `Dead Time period: 00:05:00` — مدت نگه‌داشتن سرور در وضعیت Dead پیش از تلاش مجدد/پروب است؛ در زمان عدم پاسخ، Method List می‌تواند فوراً سراغ روش بعدی برود. زمان‌بندی و فیلد دقیق به IOS بستگی دارد.

```text
R1# test aaa group TAC-GRP netadmin <secret> legacy
User successfully authenticated
```

`test aaa` بدون نیاز به خروج و ورود، اعتبار کاربر را آزمایش می‌کند. بسیار مفید است، ولی خروجی و نحو بین نسخه‌ها تفاوت دارد.

```text
R1# show running-config | include ^aaa
aaa new-model
aaa authentication login CONSOLE local
aaa group server tacacs+ TAC-GRP
aaa authentication login default group TAC-GRP local
aaa authorization exec default group TAC-GRP local
aaa authorization commands 15 default group TAC-GRP local
aaa accounting exec default start-stop group TAC-GRP
aaa accounting commands 15 default start-stop group TAC-GRP
```

این گزیدهٔ طراحی‌شده از تنظیمات است؛ `show running-config` کامل و خطوط/سرورهای متصل را جداگانه بررسی کنید. خروجی به نسخه بستگی دارد.

```text
R1# show users
    Line       User       Host(s)              Idle       Location
   0 con 0                idle                 00:00:00
*  2 vty 0     netadmin   10.10.0.50           00:00:12
```

- `*` — جلسهٔ فعلی شما.
- `con 0` — جلسه از Console است؛ خود این خروجی روش احراز را نشان نمی‌دهد. در این طرح Console با Method List صریح `CONSOLE local` به پایگاه محلی وصل شده است، نه این‌که بدون AAA باشد.

## ۸. عیب‌یابی

| نشانه | علت محتمل | بررسی |
|---|---|---|
| همه ورودها رد می‌شوند | Method List به گروه/سرور نادرست اشاره می‌کند، سرور Reject می‌دهد یا حساب محلی/Console تعریف نشده | `show running-config`، `show aaa servers` و Log سرور |
| ورود با کاربر محلی کار نمی‌کند | `local` در فهرست آن خط نیست، کاربر/Secret نادرست است یا حساب fallback مجاز نیست | Method List همان خط، پایگاه محلی و Log AAA |
| ورود کار می‌کند ولی Privilege 1 | `authorization exec` تنظیم نشده یا سرور سطح نمی‌دهد | `show aaa servers` |
| Accounting خالی است | `aaa accounting` تنظیم نشده یا سرور Acct را نمی‌گیرد | پورت 49/TCP و `show aaa servers` |
| ورود به‌طور ناگهانی همه رد می‌شود | سرور Down است و `local` وجود ندارد | `show aaa servers` |
| کاربر Privilege 15 شده بدون مجوز | `authorization commands 15` تنظیم نشده | همان |
| `show aaa servers` Timeouts بالا دارد | فایروال بین دستگاه و سرور | پورت‌های `49` (TACACS+) و `1812/1813` (RADIUS) |
| کلید اشتباه | `key` متفاوت روی دستگاه و سرور | `Successes` در برابر `Failures` |

**سناریوی نقص طراحی‌شده (اجرا نشده):** `aaa new-model` فعال است، ولی Method List مورد استفاده نه fallback معتبر دارد و نه حساب محلی؛ سرور هم در دسترس نیست یا درخواست را رد می‌کند. ورود می‌تواند روی VTY و حتی Console قفل شود، مگر Console به‌طور جداگانه با Method List محلیِ معتبر تنظیم و دسترسی فیزیکی واقعاً آزموده شده باشد. قبل از تغییر، مسیر بازیابی و حساب محلی را آماده کنید؛ `no aaa new-model` را راه بازیابی تضمینی فرض نکنید.

## ۹. کاربرگ مستقل PNETLab

1. یک سرور TACACS+ آزمایشگاهی و Shared Secret بسازید؛ Secret واقعی را در خروجی/گزارش منتشر نکنید.
2. **قبل از** `aaa new-model` حساب محلی اضطراری بسازید و روش دسترسی Console را کنترل کنید.
3. AAA را فعال کنید و Method List محلیِ صریح را روی Console اعمال کنید؛ فرض نکنید Console از فهرست `default` مستثنا است.
4. گروه `TAC-GRP` بسازید و `TAC1` را با `server name` به آن وصل کنید؛ سپس Method List را با `group TAC-GRP local` و VTYهای واقعی تنظیم کنید.
5. در حالت دسترس‌بودن سرور، با حساب آزمایشی TACACS+ وارد شوید و وضعیت را ثبت کنید.
6. سرور را موقتاً قطع کنید و fallback به **حساب محلی معتبر** را بررسی کنید؛ سپس Access-Reject را جداگانه آزمایش کنید—Reject نباید به‌عنوان Timeout تعبیر شود.
7. `show aaa servers` را ثبت کنید و `Queries`، `Failures`، `Timeouts` و Log سمت سرور را با رویدادها تطبیق دهید.
8. `aaa accounting` را اضافه و فقط سطح‌های فرمانی پیکربندی‌شده را در سرور بررسی کنید.
9. Command Authorization را روی یک فرمان (`shutdown`) محدود کنید و نتیجه را در محیط ایزوله بسنجید.
10. Console را جداگانه آزمایش و همهٔ VTY rangeها و سیاست SSH را Verification کنید.

هیچ‌کدام اجرا نشده و هیچ خروجی واقعی ثبت نشده است.

## ۱۰. سؤال‌ها و پاسخ

1. **AuthN و AuthZ چه تفاوتی دارند؟** AuthN هویت را تایید می‌کند؛ AuthZ مجوزهای عمل را تعیین می‌کند. ممکن است هویت تایید شود ولی دسترسی معینی نداشته باشد.

2. **چرا سه A مستقل‌اند؟** چون هر کدام امکان شکست جدا دارند. AuthN درست با AuthZ غلط یعنی کاربر وارد می‌شود ولی بیشتر از حد دسترسی دارد. AuthN و AuthZ درست با Acct غلط یعنی هیچ ردی نمی‌ماند.

3. **TACACS+ از TCP یا UDP استفاده می‌کند؟** TCP، پورت 49.

4. **RADIUS از چه پورتی استفاده می‌کند؟** `1812` برای AuthN و `1813` برای Acct (پورت‌های قدیمی `1645/1646`).

5. **کدام پروتکل Command Authorization کامل دارد؟** TACACS+.

6. **`local` در Method List چه زمانی استفاده می‌شود؟** **فقط** در خطای اتصال یا عدم دسترسی به سرور. اگر سرور در دسترس باشد و `Access-Reject` بدهد، `local` امتحان نمی‌شود.

7. **`none` در Method List چه می‌کند؟** هیچ احراز هویتی انجام نمی‌شود. برای VTY مدیریتی خطرناک است.

8. **Fail Open چیست؟** در نبود پاسخ AAA، روش جایگزین بدون احراز (مثل `none`) اجازه می‌دهد؛ فقط اتصالاتی که به خط/شبکه دسترسی دارند وارد می‌شوند، اما هویت بررسی نمی‌شود.

9. **Fail Local چیست؟** در قطع سرور، Authen از کاربر محلی. این نه Fail Open است و نه Fail Closed.

10. **پیش از `aaa new-model` چه باید کرد؟** حساب محلی اضطراری و دسترسی فیزیکی Console را آماده کنید؛ پس از فعال‌سازی، Method List محلیِ جداگانه را صریحاً روی Console اعمال و آزمون کنید.

11. **`start-stop` با `stop-only` چه تفاوتی دارد؟** `start-stop` شروع و پایان را ثبت می‌کند؛ `stop-only` فقط پایان را.

12. **چرا RADIUS برای 802.1X رایج است؟** استاندارد باز با پشتیبانی گسترده است؛ TACACS+ برای مدیریت CLI معمولاً Command Authorization دقیق‌تری دارد. پشتیبانی نهایی را در تجهیز/سرور مقصد بررسی کنید.

## واژه‌نامه و چک‌لیست

AAA: احراز، مجوز، ثبت؛ RADIUS: پروتکل دسترسی شبکه (UDP)؛ TACACS+: پروتکل مدیریت دستگاه (TCP)؛ Method List: ترتیب منابع؛ Fail Open: اجازه در قطع سرور؛ Fail Closed: رد در قطع سرور؛ Fail Local: کاربر محلی در قطع سرور؛ Break-Glass: مسیر اضطراری.

- [ ] سه A را با مثال جدا می‌کنم.
- [ ] می‌دانم `local` **فقط** در خطا استفاده می‌شود، نه در `Access-Reject`.
- [ ] پیش از `aaa new-model` حساب محلی می‌سازم و Console را با Method List مستقل و محلی پیکربندی/آزمایش می‌کنم.
- [ ] تصمیم Fail Open/Closed/Local را صریح می‌گیرم.
- [ ] RADIUS و TACACS+ را در جای درست به‌کار می‌برم.
