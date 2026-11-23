# CCNA IS-08 — دسترسی از راه دور با SSH

**سطح:** CCNA. **پیش‌نیاز:** NA-09. **هدف رسمی:** `4.8` پیکربندی دستگاه‌ها برای دسترسی از راه دور با SSH. **وضعیت:** بازبینی هدفمند طرح پیکربندی/Verification در این نوبت؛ ممیزی جامع درس انجام نشده و Objective عملی تا اجرا و تأیید روی IOS واقعی باز است. Image/نسخه انتخاب نشده است.

## اهداف

SSH را روی دستگاه فعال کنید، کاربر محلی و Domain Name لازم را تنظیم کنید و Telnet را غیرفعال نگه دارید.

## ۱. چرا SSH و نه Telnet؟

**Telnet** نام کاربری و گذرواژه را به‌صورت متن روشن می‌فرستد؛ هر کسی در مسیر می‌تواند آن را ببیند. **SSH** ارتباط رمزنگاری‌شده می‌سازد و احراز هویت و یکپارچگی داده را فراهم می‌کند. در عمل، Telnet باید غیرفعال و SSH جای آن استفاده شود.

برای SSH روی IOS به سه چیز نیاز است: **Hostname** و **Domain Name** (برای تولید کلید RSA)، **کاربر محلی** با سطح دسترسی، و **خطوط VTY** که فقط SSH را بپذیرند.

## ۲. سناریوی طراحی‌شده

**PNETLab مستقل، طراحی‌شده و اجرا‌نشده:** R1 با Hostname `R1`، دامنهٔ `lab.local` و کاربر `netadmin` با Privilege 15. مدیریت از `10.10.0.0/24` انجام می‌شود. نام تصویر و نسخهٔ IOS تأیید نشده‌اند؛ نسخهٔ 1.5 و 2 هر دو در طراحی بررسی می‌شوند.

![نمودار قابل ویرایش SSH؛ اجرا‌نشده](academy-images/is-08-ssh.svg)

## ۳. پیکربندی پیشنهادی

**فرمان‌ها اجرا‌نشده‌اند.**

```text
configure terminal
hostname R1
ip domain-name lab.local
crypto key generate rsa modulus 2048
username netadmin privilege 15 secret <long-unique-secret>
ip ssh version 2
line vty 0 4
 login local
 transport input ssh
end
```

`crypto key generate rsa` فقط با Hostname و Domain Name کار می‌کند. طول کلید 2048 حداقل منطقی است؛ 1024 امروز کافی نیست. `transport input ssh` روی همان خطوط VTY، Telnet را می‌بندد. این نمونه فقط `VTY 0–4` را پیکربندی می‌کند؛ با `show line` و `show running-config | section line vty` همهٔ بازه‌های VTY دستگاه را پیدا و تنظیم کنید، چون بعضی Imageها خطوط بیشتری دارند. `login local` احراز هویت را به کاربر محلی می‌سپارد.

## ۴. Verification

**فرمان و خروجی آموزشی، اجرا‌نشده:**

```text
R1# show ip ssh
SSH Enabled - version 2.0
Authentication timeout: 120 secs; Authentication retries: 3
Minimum expected Diffie Hellman key size : 2048 bits
```

```text
R1# show ssh
Connection Version Mode Encryption  Hmac         State           Username
0          2.0     IN   aes256-ctr  hmac-sha2-256 Session started netadmin
```

`show ip ssh` تنظیمات سرور و `show ssh` جلسات فعال را نشان می‌دهد. فرمان `show users` کاربران متصل را می‌آورد. هیچ خروجی واقعی ثبت نشده است.

## ۵. کاربرگ مستقل PNETLab — SSH فقط از VTY مجاز

**Objective عملی `4.8`:** پیکربندی و Verification دسترسی مدیریتی از راه دور با SSH. **طراحی‌شده و اجرا‌نشده است.** یک روتر IOS، یک Linux Client دارای SSH client، دو Console و یک LAN کاملاً ایزوله لازم است؛ VPCS ممکن است SSH client نداشته باشد، پس از VM لینوکس استفاده کنید.

```text
ADMIN-VM 192.0.2.10/24 ── SW-LAB ── R1 Gi0/0 192.0.2.1/24
                                   R1 VTY: SSH only
```

قبل از اجرا Image/نسخه، تعداد/بازهٔ VTYها، پشتیبانی SSH و حداقل RSA Key Size را ثبت و Snapshot بگیرید. از Console وارد شوید، IP را تنظیم کنید، Hostname/Domain/کاربر Secret و RSA/SSHv2 را مطابق §۳ بسازید و `transport input ssh` را روی **همهٔ** بازه‌های VTY اعمال کنید. مقدار Secret در فایل/گزارش/Capture ننویسید؛ Placeholder را با رمز یکتای فقط آزمایشگاهی جایگزین کنید.

### گام‌های آزمون و Verification

1. با `show ip interface brief`, `show line`, `show running-config | section line vty`, `show ip ssh` و در صورت پشتیبانی `show crypto key mypubkey rsa` رابط، همهٔ VTYها، Transport، SSH version و وجود Key را بررسی کنید.
2. از ADMIN-VM به R1 Ping مجاز بزنید؛ بعد `ssh <lab-user>@192.0.2.1` اجرا کنید. روی R1 با `show users` یا `show ssh` نشست واقعی را ببینید؛ پس از خروج، نشست پایان یابد. پیام کلاینت، Cipher و Key Size به نسخهٔ هر دو سمت بستگی دارد.
3. در محدودهٔ لاب، یک بار با Username اشتباه یا Transport غیر SSH تلاش کنید؛ باید احراز رد شود/نشست ساخته نشود. **تعداد زیاد رمزهای حدسی آزمایش نکنید.** از Console بررسی و سپس Config صحیح را بازیابی کنید.
4. از یک کلاینت دارای Telnet، اتصال Telnet را امتحان کنید؛ انتظار این است که VTY آن را نپذیرد. فقط بررسی نکنید که SSH کار می‌کند—ممنوع‌بودن Telnet را هم Verification کنید.
5. در R1 همهٔ رنج‌های VTY را مجدداً با `show line` و Config تأیید و از تصویر/خروجی پاک‌سازی‌شدهٔ شواهد استفاده کنید؛ Secret و کلید خصوصی را منتشر نکنید.

| نشانه | ترتیب عیب‌یابی |
|---|---|
| TCP/22 در دسترس نیست | IP/Mask، Link/Route/ACL، `show ip ssh`، وجود RSA Key و سرویس SSH را بررسی کنید |
| اتصال برقرار است، ورود رد می‌شود | نام کاربر/روش Secret، `login local` و سیاست AAA/Access را از Console بررسی کنید؛ رمز را در Log ننویسید |
| SSH کار می‌کند ولی Telnet هم باز است | همهٔ VTY rangeها، `transport input` و lineهای بالاتر از 0–4 را وارسی کنید |
| Client الگوریتم امن مشترک ندارد | الگوریتم‌ها و حداقل Key Size را با مستند هر دو نسخه تطبیق دهید؛ الگوریتم ضعیف را بی‌بررسی فعال نکنید |
| جلسه بی‌دلیل بسته می‌شود | `exec-timeout`, ACL/CoPP و Logهای مجاز را بررسی کنید |

**بازگشت امن:** Console را در تمام تمرین در دسترس نگه دارید؛ در صورت قفل‌شدن VTY از همان Console، Snapshot و Config نسخه‌دار برای بازگرداندن استفاده کنید. بعد از آزمون، حساب/Keyهای لاب را پاک یا Snapshot را Restore کنید؛ روتر عملیاتی را تغییر ندهید.

**معیار موفقیت:** SSHv2 با کاربر لاب احراز می‌شود، VTYها فقط SSH می‌پذیرند، Telnet رد می‌شود، نشست در `show users`/`show ssh` دیده و بعد بسته می‌شود، همهٔ بازه‌های VTY بررسی شده‌اند، و هیچ Secret در شواهد باقی نمانده است. تا اجرای IOS واقعی، Objective 4.8 تأیید عملی نشده است.

## ۶. سؤال‌ها و پاسخ

1. **چرا SSH بهتر از Telnet است؟** رمزنگاری و احراز هویت.
2. **چه چیزی قبل از RSA لازم است؟** Hostname و Domain Name.
3. **`crypto key generate rsa` چه می‌کند؟** کلید رمزنگاری می‌سازد.
4. **طول کلید مناسب؟** حداقل 2048.
5. **`login local` چه می‌کند؟** احراز هویت با کاربر محلی.
6. **`transport input ssh` چه اثری دارد؟** فقط SSH پذیرفته می‌شود.
7. **VTY چیست؟** خطوط دسترسی از راه دور.
8. **`show ip ssh` چه نشان می‌دهد؟** تنظیمات سرور SSH.
9. **`show ssh` چه نشان می‌دهد؟** جلسات فعال.
10. **چرا Privilege 15 خطرناک است؟** دسترسی کامل؛ باید محدود شود.
11. **آیا ACL روی VTY مفید است؟** بله برای محدود کردن مبدأ.
12. **آیا این سناریو اجرا شده است؟** خیر.

## واژه‌نامه و چک‌لیست

SSH: دسترسی رمزنگاری‌شده؛ RSA: الگوریتم کلید؛ VTY: خط دسترسی راه دور؛ Privilege: سطح دسترسی.

- [ ] Telnet را غیرفعال می‌کنم.
- [ ] کلید RSA را با Hostname و Domain می‌سازم.
- [ ] دسترسی VTY را با کاربر محلی و ACL محدود می‌کنم.
