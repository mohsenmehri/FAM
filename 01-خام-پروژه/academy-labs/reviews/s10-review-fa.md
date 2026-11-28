# s10 — VLAN و trunk؛ بازبینی نویسنده

۲۰۲۶-۱۱-۲۷. بررسی ۱۴ بخش، واژه‌نامه، نمونه‌ها، تمرین، ۱۲ سؤال و همه گزینه‌ها و کد، توسط نویسنده است؛ بازبینی مستقل انسانی نیست.

- [ساختار فریم 802.1Q سیسکو](https://www.cisco.com/c/en/us/support/docs/lan-switching/8021q/17056-741-4.html) اطلاعات tag و وابستگی trunk به تجهیزات را توضیح می‌دهد؛ نگاشت untagged/native و native tagging به پیکربندی و پلتفرم وابسته است. مدل از VID 0 و QinQ و voice VLAN پشتیبانی نمی‌کند.
- [Inter-VLAN روی Catalyst](https://www.cisco.com/c/en/us/support/docs/lan-switching/inter-vlan-routing/41260-189.html) نمونه SVI و مسیریابی بین VLANها را در پلتفرم/نسخه مشخص نشان می‌دهد. VLAN جایگزین ACL یا فایروال نیست و trunk بودن به‌تنهایی عبور VLAN را تضمین نمی‌کند.
- پاسخ‌ها و گزینه‌های ۱۲ سؤال به ترتیب تفکیک لایه ۲، access، trunk، allowed/STP، native فرضی، drop، mismatch، gateway، VID 0، امنیت، router-on-a-stick و محدودیت مدل بررسی شدند.
- `vlan_trunk_mock.py` فقط طبقه‌بندی و خروجی ساده در حافظه دارد؛ `tests/test_vlan_trunk_mock.py` native، tag، drop و access را می‌سنجد. اعتبارسنجی egress، STP، مسیریابی و فریم واقعی در مدل نیست. هیچ دستگاه یا شبکه‌ای اجرا نشده است.
