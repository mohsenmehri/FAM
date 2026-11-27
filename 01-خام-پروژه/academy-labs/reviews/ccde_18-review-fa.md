# شواهد بازبینی معنایی `ccde_18` — مطالعه موردی ۱: شرکت جهانی Pars-Global

تاریخ: ۲۰۲۶-۱۱-۲۷. **وضعیت بازبینی:** بازبینی معنایی توسط نویسنده (ایجنت)؛ **بازبینی مستقل انسانی انجام نشده است.**

- همه ۱۴ بخش، ۱۵ واژه، ۱۲ پرسش و اعتبارسنج `01-خام-پروژه/academy-labs/agent3/ccde_18_lab.py` بررسی و اجرا شدند.
- هیچ زیرساخت بین‌المللی واقعی متصل نشده است.

## بازبینی فنی و معنایی مرحله ۲ (۲۰۲۶-۱۱-۲۷)

- وضعیت بازبینی: همچنان **بازبینی نویسنده (author-agent-self-review-not-independent)** است و **بازبینی مستقل انسانی انجام نشده است**.
- مسئله ۱: بیان سقف ~۵ms برای Synchronous Replication به عنوان قاعده عمومی + نادیده گرفتن تفاوت مسیر مستقیم (~50ms) با مسیر واقعی (~95–130ms). منبع: مستندات VMware vSAN Stretched Cluster (≤5ms) و VMware vMSC / NetApp MetroCluster / Dell Metro Node (≤10ms). اصلاح در بخش‌های ۳، ۵، ۱۱، ۱۳، پرسش ۱ و اسکریپت `ccde_18_lab.py`.
- مسئله ۲: نشت واژه اسپانیایی `inicialmente` در بخش ۵. اصلاح به فارسی معیار و افزودن نگهبان خودکار در `test_agent3_content.py`.
- مسئله ۳: بیان مطلق کاهش ۷۵٪ Egress، ادعای غیرواقعی تأخیر <10ms برای همه ۱۰۰ شعبه سه‌قاره‌ای و عدد تضمینی ۹۵٪ PCI. اصلاح به صورت شرط‌دار (وابسته به ارائه‌دهنده/منطقه، فاصله جغرافیایی شعب و تأیید QSA).
- آزمون مرتبط: `test_agent3_content.py` (`test_technical_audit_regressions` + اجرای زنده `ccde_18_lab.py` شامل هر دو حالت رد Sync+L2 و قبولی Async+L3).

## بازبینی فنی فاز ۴ (2026-11-27 — پاسخ به بازبینی همتای Agent 2 در `agent3-intake-c7351d1-fa.md`)
- **ایرادها:** (۱) معرفی اقامت داده EU و پین کردن SASE PoP به شکل ممنوعیت مطلق GDPR و القای کفایت اقامت جغرافیایی برای انطباق کامل؛ (۲) تناقض داخلی `ccde_18_lab.py` (چاپ پیام ثابت `exceeds ... Async required` حتی هنگام `sync_feasible_for_profile == True`، درهم‌آمیزی سیاست L2 Stretch با قید فیزیکی، و تقلیل انطباق به یک بولین `gdpr_eu_data_local`)؛ (۳) ادعای مطلق «صفر قطعی / Zero-Downtime» و تضمین «۳۰٪+ OpEx»؛ (۴) حذف `
` پایانی در HTML آزمایشگاه.
- **منبع معتبر:** [EDPB — International Data Transfers (GDPR Chapter V, Arts. 44–49)](https://www.edpb.europa.eu/sme/be-compliant/international-data-transfers_en)، PCI-DSS v4.0 (Req 4 & QSA scope validation)، مستندات VMware vSAN (≤5ms) / NetApp MetroCluster / VMware vMSC (≤10ms).
- **اصلاح انجام‌شده:** بازنویسی بخش‌های ۲، ۳، ۴ (SVG)، ۵، ۶، ۷، ۸، ۱۰، ۱۱، ۱۲، ۱۳، ۱۴، واژه‌نامه و پرسش‌های ۳، ۷ و ۹ برای تفکیک صریح **سیاست شرکتی اقامت داده EU** از چارچوب انتقال مشروط فصل ۵ GDPR (Adequacy/SCC+TIA) و تصریح عدم کفایت کنترل شبکه‌ای برای انطباق کامل؛ شرط‌دار کردن «کمینه‌سازی قطعی» و هدف «~۳۰٪ OpEx»؛ بازنویسی کامل `ccde_18_lab.py` با پیام پویا (از جمله سناریوی مترو ۱۵۰km)، تفکیک `replication_ok` از `l2_stretch_policy_ok` و مدل ساختاریافته انطباق؛ تطابق دقیق بایت‌به‌بایت HTML با `
` پایانی.
- **تست مرتبط:** `test_phase4_ccde_18_ccde_19_dynamic_labs_and_regressions` و `test_blueprints_schema_svg_quiz_lab_and_review_integrity` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** آزمایشگاه همچنان اعتبارسنج محلی Python 3 بدون اتصال به دیتاسنتر واقعی یا ارزیابی حقوقی DPO/QSA است و بازبینی نهایی انسانی مستقل انجام نشده است.

## بازبینی فنی فاز ۶ (2026-11-27 — رفع کامل یافته‌های `agent-intake-837fad64-fa.md` روی `ccde_18` و ممیزی مرزی درس‌های باقی‌مانده)
- **ایراد:** ۱) پذیرش فاصله منفی و چاپ پیام متناقض `supported` برای `storage_replication='not-a-real-mode'`؛ ۲) اشاره به انتخاب GSLB بدون ورودی/بررسی GSLB و نبود بررسی RPO؛ ۳) اجبار برچسب مبنای انتقال هنگام نبود انتقال خارج از EEA و نبود disclaimer فرض بودن بولین‌های انطباق؛ ۴) ناهماهنگی ~70ms آزمایشگاه با ~95-130ms متن و ادعاهای قطعی در Q9، Q10، Q11 و بخش‌های ۵، ۷، ۸، ۹ و ۱۲.
- **منبع معتبر:** گزارش بازبینی همتای Agent 2 (`agent-intake-837fad64-fa.md`)، [EDPB — International Data Transfers (GDPR Chapter V)](https://www.edpb.europa.eu/sme/be-compliant/international-data-transfers_en)، PCI-DSS v4.0 (Req 4 & QSA scope)، مستندات VMware vSAN (≤5ms) / MetroCluster / vMSC (≤10ms).
- **اصلاح انجام‌شده:** بازنویسی کامل `ccde_18_lab.py` با اعتبارسنجی فاصله مثبت متناهی، رد صریح mode نامعتبر، مدل‌سازی صریح `gslb_enabled` و `target_rpo_minutes`، تفکیک شفاف مدل فرضی تأخیر (50ms / 70ms / ~105ms در بازه ~95-130ms)، تفکیک سیاست اقامت EU از وضعیت انتقال خارج EEA و تضمین فصل ۵ + disclaimer فرض بودن بولین‌ها؛ اصلاح Q9، Q10، Q11 و بخش‌های ۳، ۵، ۷، ۸، ۹، ۱۲ و ۱۳ در `ccde_18.json`.
- **تست مرتبط:** `test_phase6_ccde_18_remediation_and_remaining_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** اعتبارسنج محلی Python 3؛ اعداد تأخیر و هزینه صرفاً فرضی هستند و بولین‌های انطباق جایگزین DPO/QSA نیستند؛ بازبینی مستقل انجام نشده است.

## بازبینی فنی فاز ۷ (2026-11-27 — اعتبارسنجی سخت‌گیرانه نوع `bool` و مرزهای ورودی)
- **ایراد:** استفاده از `bool()` روی ورودی‌های بولی (`gslb_enabled` و ۵ فیلد بولی دیگر) باعث تبدیل رشته `"False"` به `True` می‌شد؛ همچنین نیاز بود صریح‌تر ثبت شود که سازگاری فرضی RPO در مدل اثبات تحقق واقعی RPO نیست.
- **منبع معتبر:** Python Data Model (truthiness of non-empty `str`) و اصول مهندسی RPO/DR (وابستگی RPO واقعی به پهنای باند WAN، نرخ تغییر داده و آزمون زنده DR).
- **اصلاح انجام‌شده:** اعمال `_require_bool` سخت‌گیرانه روی هر ۶ فیلد بولی (`dci_l2_stretched`، `gslb_enabled`، `micro_sgt_enabled`، `eu_residency_policy_enforced`، `eu_personal_data_transferred_outside_eea`، `encryption_in_transit_assumed`) با رد `"False"`، `"True"`، `0`، `1` و `None`؛ اعتبارسنجی `str` روی فیلدهای رشته‌ای؛ افزودن `rpo_scope_note` صریح در خروجی و متن آزمایشگاه.
- **تست مرتبط:** `test_phase7_strict_boolean_typing_and_remaining_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** اعتبارسنج محلی Python 3؛ جایگزین اندازه‌گیری واقعی RPO/RTT یا تأیید حقوقی DPO/QSA نیست و بازبینی مستقل انجام نشده است.

## بازبینی فنی فاز ۸A (2026-11-27)
- **ایراد:** یافته Agent 2 در `agent-intake-a4d38ca2-fa.md`: پیام موفقیت ثابت `4 Macro VRFs` حتی برای `macro_vrfs` برابر `3`، `5` یا `6` چاپ می‌شد؛ همچنین پوشش تست `''`، `[]` و `{}` روی ورودی‌های بولی لازم بود.
- **منبع معتبر:** گزارش intake ایجنت دوم (`agent-intake-a4d38ca2-fa.md`) و Python Data Model.
- **اصلاح انجام‌شده:** پویاسازی پیام به `{macro_vrfs} Macro VRFs` و افزودن زیرتست‌های `''`، `[]` و `{}` روی هر ۶ ورودی بولی.
- **تست مرتبط:** `test_phase8a_ccde18_dynamic_vrf_and_specialist_core_labs` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** اعتبارسنج محلی Python 3؛ بازبینی نویسنده (نه مستقل) و جایگزین تست زنده DR یا DPO/QSA نیست.

## بازبینی فنی فاز ۹ (2026-11-27 — پاسخ به `AGENT-HANDOFF-fa.md` @ `53871318`)
- **ایراد:** تعمیم نام پروفایل `vmware_vmsc_netapp_metrocluster=10ms` و مقایسه `<=` به‌جای مرز دقیق سند محصول؛ و پرتاب `OverflowError` به‌جای `ValueError` روی عدد صحیح بسیار بزرگ (`10**500`) در `math.isfinite`.
- **منابع معتبر:** [NetApp vMSC with SnapMirror active sync](https://docs.netapp.com/us-en/netapp-solutions-virtualization/vmware/vmw-vmsc-with-smas.html) (`< 10 ms` اکید) و [NetApp ONTAP Select MetroCluster SDS](https://docs.netapp.com/us-en/ontap-select/concept_ha_config.html) (`<= 5 ms` RTT و `<= 5 ms` jitter).
- **اصلاح انجام‌شده:** جایگزینی با سه پروفایل دقیق و مستند (`vmware_vsan_stretched`, `netapp_vmsc_snapmirror_active_sync` با `< 10.0`, `netapp_ontap_select_metrocluster_sds` با `<= 5.0`)، تبدیل `OverflowError` به `ValueError` و هم‌ترازی متن `ccde_18.json` (بخش و Q1).
- **تست مرتبط:** `test_phase9_agent_handoff_ccde18_and_auto20_fixes` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** اعتبارسنج محلی Python 3؛ بازبینی نویسنده (نه مستقل) و منتظر بازبینی مستقل Agent 2 روی کل متن و ۱۲ سؤال.

## بازبینی فنی فاز ۱۰A (2026-11-27 — پاسخ به `AGENT-HANDOFF-fa.md` @ `f4e3ab1f`)
- **ایراد:** پروفایل `netapp_ontap_select_metrocluster_sds` شرط `<= 5 ms jitter` را در متن ذکر می‌کرد بدون آنکه `assumed_jitter_ms` ورودی/اعتبارسنجی شود و تنها با RTT مناسب عبارت انطباق با jitter را گزارش می‌داد.
- **منبع معتبر:** `AGENT-HANDOFF-fa.md` (@ `f4e3ab1f`) و [NetApp ONTAP Select MetroCluster SDS](https://docs.netapp.com/us-en/ontap-select/concept_ha_config.html).
- **اصلاح انجام‌شده:** افزودن `max_jitter_ms` در پروفایل‌ها و اعتبارسنجی صریح و **fail-closed** برای `assumed_jitter_ms` (غیاب یا `None` یا `> 5.0 ms` مانع پذیرش sync می‌شود؛ پروفایل‌های بدون مدل jitter صریحاً اعلام می‌کنند jitter مدل نشده است).
- **تست مرتبط:** `test_phase10a_handoff_f4e3ab1f_ccde18_jitter_and_auto20_zscore` در `01-خام-پروژه/tests/test_agent3_content.py`.
- **محدودیت:** اعتبارسنج محلی Python 3؛ بازبینی نویسنده (نه مستقل) و منتظر بازبینی مستقل Agent 2.
