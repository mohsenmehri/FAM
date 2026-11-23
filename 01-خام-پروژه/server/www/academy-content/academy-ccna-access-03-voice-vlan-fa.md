# CCNA NA-03 — Data VLAN و Voice VLAN روی Access Port

**سطح:** CCNA. **پیش‌نیاز:** NA-01 و NA-02. **هدف مرتبط:** `2.1.a`، شامل Access Port داده و Voice. **وضعیت:** پیش‌نویس؛ فرمان‌ها، خروجی و کاربرگ طراحی‌شده و اجرا‌نشده‌اند. مدل تلفن، Switch و نسخهٔ IOS انتخاب نشده و سازگاری PoE/CDP یا tagging تأیید نشده است.

## اهداف

نقش Data VLAN و Voice VLAN یک پورت متصل به تلفن IP را توضیح دهید؛ پیکربندی نمونهٔ Access Port را بخوانید؛ وضعیت گزارش‌شده را تفسیر کنید و شکست تلفن را از مشکل PC جدا بررسی کنید.

## ۱. چرا دو VLAN روی یک پورت؟

در یک طرح معمول، تلفن IP به Access Switch متصل و رایانه به پورت داخلی تلفن متصل می‌شود. Switch برای دادهٔ PC یک Access VLAN و برای ترافیک تلفن Voice VLAN تعریف می‌کند. نحوهٔ استفاده از 802.1Q، سیگنال‌دهی و پشتیبانی تلفن و Switch وابسته به مدل و تنظیمات است. VLAN صوت، QoS تضمین‌شده یا امنیت کامل فراهم نمی‌کند.

```text
[PC] ─ [IP Phone] ─ SW1 Gi0/1
                       Data VLAN 10 / Voice VLAN 20
```

تلفن می‌تواند در طراحی سازگار از PoE برق بگیرد، اما تامین برق به معنی ثبت تلفن، تخصیص IP یا سلامت سرویس Voice نیست.

## ۲. جدول سناریو

**طراحی‌شده و اجرا‌نشده.** یک Switch سازگار، تلفن IP یا تصویر شبیه‌سازی پشتیبان و یک Client موردنیازند؛ مدل، نسخه و قابلیت Voice/PoE مشخص نشده‌اند. اگر PNETLab تصویر مناسب ندارد، صرفاً از کاربرگ تحلیلی استفاده شود؛ PoE فیزیکی با شبیه‌ساز اثبات نمی‌شود.

| دستگاه/پورت | VLAN | IP فرضی | نقش |
|---|---:|---|---|
| PC پشت تلفن | 10 | `192.0.2.10/24` | داده |
| تلفن IP | 20 | `198.51.100.10/24` | صوت |
| SW1 Gi0/1 | Data 10، Voice 20 | ندارد | Access Port |

آدرس‌ها مستنداتی و صرفاً برای تحلیل‌اند. DHCP، Call Manager و Router در این تمرین پیاده‌سازی نشده‌اند و کارکرد تماس تلفنی ادعا نمی‌شود.

## ۳. پیکربندی پیشنهادی

**فرمان‌های IOS اجرا‌نشده و وابسته به پلتفرم:**

```text
configure terminal
vlan 10
 name DATA
vlan 20
 name VOICE
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
 no shutdown
end
```

`vlan` دو VLAN را تعریف می‌کند. `switchport mode access` حالت داده را Access، `switchport access vlan 10` VLAN داده و `switchport voice vlan 20` VLAN Voice را روی پورت پشتیبانی‌شده تعیین می‌کند. `no shutdown` حالت اداری رابط را باز می‌کند. اسم پورت، قابلیت تلفن و سازوکار اعلام VLAN باید در محیط هدف بررسی شوند.

## ۴. Verification

**دستورها و خروجی آموزشی، اجرا‌نشده:**

```text
SW1# show interfaces GigabitEthernet0/1 switchport
Name: Gi0/1
Administrative Mode: static access
Operational Mode: static access
Access Mode VLAN: 10 (DATA)
Voice VLAN: 20 (VOICE)
```

Mode و Access VLAN نقش داده را نشان می‌دهند؛ `Voice VLAN` نشان‌دهندهٔ تنظیم گزارش‌شدهٔ صوت است. این خروجی تأمین برق، دریافت IP یا ثبت تلفن را ثابت نمی‌کند.

```text
show vlan brief
show interfaces GigabitEthernet0/1
show power inline GigabitEthernet0/1
```

فرمان آخر فقط روی پلتفرم پشتیبان معنی دارد. خروجی و فیلدها باید با نسخه و مدل بررسی شوند؛ هیچ مقدار توان واقعی در این درس مشاهده نشده است.

## ۵. کاربرگ مستقل PNETLab/تلفن IP — Data و Voice VLAN روی یک پورت

**هدف عملی `2.1.a`:** Access VLAN داده و Voice VLAN را روی پورت سازگار پیکربندی و Verification کنید. **این کاربرگ طراحی‌شده و اجرا‌نشده است.** یک سوئیچ IOS-L2 و، فقط اگر Image مجاز و سازگار موجود است، IP Phone و PC پشت آن لازم‌اند. بسیاری از توپولوژی‌های PNETLab تلفن، CDP/LLDP و PoE واقعی ندارند؛ در این حالت مراحل GUI/برق/Call Manager خارج از شبیه‌ساز و نیازمند سخت‌افزار مجاز است، و CLI شبیه‌سازی‌شده را نتیجهٔ تماس جا نزنید.

```text
PC-Data (192.0.2.10/24) ─ IP Phone ─ SW1 Gi0/1
                                           Data VLAN 10
                                           Voice VLAN 20
```

**گره‌ها و پیش‌نیازها:** SW1 و پورت آزمون، VLANهای 10 و 20؛ کلاینت/Phone سازگار؛ DHCP جدا برای Data/Voice در صورت ارزیابی Lease. Call Manager/CUCM خارج از محدوده است. مدل/نسخه، PoE budget، CDP/LLDP، voice-tagging و وجود Phone image را ثبت کنید. محیط را ایزوله و از Config Snapshot تهیه کنید.

### مراحل اجرا و شاهد

1. قبل از تغییر `show vlan brief`, `show interfaces Gi0/1 switchport` و `show interfaces status` را ثبت و مطمئن شوید پورت فقط برای تجهیزات لاب آزاد است.
2. VLANهای 10/20 را بسازید و Gi0/1 را در حالت Access قرار دهید؛ `switchport access vlan 10` و `switchport voice vlan 20` را با Command Reference نسخهٔ هدف بررسی کنید. این دستورات در این متن نمونه و اجرا‌نشده‌اند.
3. با `show interfaces Gi0/1 switchport`، Access VLAN=10 و Voice VLAN=20 را بررسی کنید؛ با `show mac address-table interface Gi0/1` یادگیری MACها را فقط در صورت پشتیبانی Phone/Client تفسیر کنید.
4. اگر Phone واقعی/شبیه‌سازی معتبر و DHCP موجود است، وضعیت Power، Voice VLAN tag، Lease، Gateway و Call Manager registration را جداگانه ثبت کنید. آدرس‌های فرضی جدول §۲، Lease مشاهده‌شده نیستند.
5. **نقص کنترل‌شده:** در Lab، `switchport voice vlan` را حذف یا موقتاً روی VLAN آزمایشی نادرست بگذارید. بررسی کنید چه اثری روی Phone/PC دیده می‌شود؛ فقط یک متغیر تغییر کند. سپس VLAN 20 را Restore و Verification را تکرار کنید.
6. Snapshot را برگردانید یا تنظیمات موقت را حذف کنید؛ پورت تولیدی، VLAN سازمانی یا تلفن واقعی را بدون مجوز تغییر ندهید.

| نشانه | بررسی مرحله‌ای |
|---|---|
| PC و Phone هر دو قطع‌اند | رابط/کابل، Shutdown/err-disable، Access VLAN و Trunk uplink/Allowed VLAN |
| PC کار می‌کند، Phone برق ندارد | PoE negotiation/budget و کابل/سازگاری؛ شبیه‌ساز PoE واقعی را تأیید نمی‌کند |
| Phone روشن، Voice IP ندارد | Voice VLAN tag/اعلان CDP/LLDP، Scope/DHCP، Gateway و Trunk مسیر |
| Phone IP دارد، تماس برقرار نیست | Call Manager، provisioning، registration، مسیر/ACL و سرویس Voice خارج از تمرین پایه |
| خروجی `switchport` درست است ولی ترافیک نیست | Operational link، تلفن سازگار، Tagging، Uplink، DHCP و سیاست را جدا آزمایش کنید |

**معیار موفقیت:** IOS گزارش‌شده Access VLAN 10 و Voice VLAN 20 را روی پورت درست نشان می‌دهد؛ در صورت وجود Phone معتبر، Data و Voice client جداگانه بررسی می‌شوند؛ نقص و بازیابی ثبت می‌شود؛ و محدودیت شبیه‌ساز/PoE/Call Manager صریح است. نتیجهٔ واقعی هنوز وجود ندارد.

## ۶. سؤال‌های سناریویی

1. **Data VLAN برای چیست؟** جداسازی منطقی دادهٔ PC طبق طراحی پورت.
2. **Voice VLAN برای چیست؟** مشخص‌کردن VLAN ترافیک تلفن در پورت پشتیبانی‌شده.
3. **Voice VLAN به‌تنهایی QoS را تضمین می‌کند؟** خیر، QoS و سیاست مستقل‌اند.
4. **تلفن روشن است؛ ثبت تماس تضمین شده؟** خیر، IP، سرویس و مسیر باید بررسی شوند.
5. **PC کار می‌کند، تلفن خیر؛ از کجا؟** وضعیت توان، VLAN صوت و وابستگی‌های تلفن را بررسی کنید.
6. **`switchport voice vlan 20` چه می‌کند؟** VLAN صوت را در پورت سازگار تنظیم می‌کند.
7. **`show ... switchport` چه می‌گوید؟** حالت و VLANهای گزارش‌شدهٔ پورت؛ نه نتیجهٔ تماس واقعی.
8. **آیا هر تصویر PNETLab PoE واقعی را اثبات می‌کند؟** خیر، توان الکتریکی نیازمند سخت‌افزار و شاهد واقعی است.
9. **آیا دستور روی همهٔ مدل‌ها بدون تغییر معتبر است؟** خیر، نسخه و مدل باید بررسی شوند.
10. **DHCP و سیستم تماس در سناریو وجود دارند؟** خیر؛ کارکرد تماس در محدودهٔ این کاربرگ نیست.
11. **دو VLAN به‌تنهایی امنیت کامل‌اند؟** خیر؛ سیاست دسترسی جدا لازم است.
12. **این خروجی واقعی است؟** خیر، نمونهٔ آموزشی است.

## واژه‌نامه و چک‌لیست

Voice VLAN: VLAN ترافیک صوت در پورت پشتیبان؛ Data VLAN: VLAN داده؛ PoE: تامین توان سازگار؛ QoS: سیاست کیفیت سرویس.

- [ ] VLAN داده و صوت را در خروجی جدا تشخیص می‌دهم.
- [ ] روشن‌شدن تلفن را با موفقیت تماس یکی نمی‌دانم.
- [ ] محدودیت شبیه‌ساز و نبود سیستم تماس را بیان می‌کنم.
