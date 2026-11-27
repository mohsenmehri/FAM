# پیش‌نویس اصلاح آزمایشگاه Terraform (`auto_12`)

**وضعیت:** طرح آموزشی برای ادغام؛ هنوز در رابط آکادمی قرار نگرفته و به‌معنای بازبینی کامل درس نیست. هیچ تجهیز یا provider شبکه‌ای در این تمرین استفاده نمی‌شود.

## هدف و پیش‌نیاز

تفاوت میان **پیکربندی مطلوب**، **state ذخیره‌شده** و **وضعیت مشاهده‌شده منبع**، و اثر refresh-only را توضیح دهید. برای بخش اول Python 3 کافی است. بخش اختیاری دوم به Terraform 1.4 یا جدیدتر و یک پوشه آزمایشی قابل نوشتن نیاز دارد. از پوشه پروژه یا state عملیاتی استفاده نکنید.

## بخش ۱: مدل Python Mock — نه Terraform

از ریشه مخزن:

```bash
python3 '01-خام-پروژه/academy-labs/terraform_mock.py'
```

سناریو: مقدار مطلوب و state قبلی VLAN برابر ۱۰ است اما در واقعیت فرضی به ۲۰ تغییر کرده است. برنامه فقط dictionaryهای حافظه Python را مقایسه می‌کند؛ هیچ شبکه، تجهیز، backend، Terraform یا provider واقعی وجود ندارد. این مدل همه جزئیات Terraform، خطای API یا هم‌زمانی را پیاده‌سازی نمی‌کند.

**بررسی:** خروجی پیشنهادی refresh و state پس از mock apply باید VLAN ۲۰ و خروجی normal plan باید `observed: 20` و `desired: 10` را نشان دهد. refresh-only واقعیت فرضی را به ۱۰ بازنمی‌گرداند. اگر مقدارها متفاوت‌اند، کد را از پوشه درست اجرا کنید و ترتیب سه متغیر ابتدای `main` را ببینید. تمرین: پس از تغییر desired به ۲۰ پیش‌بینی کنید normal plan چه می‌شود، سپس بررسی کنید.

## بخش ۲: Terraform واقعی، فقط منبع داخلی محلی

این بخش **Terraform واقعی** است، اما `terraform_data` منبع داخلی Terraform است و VLAN یا زیرساخت بیرونی نمی‌سازد؛ آزمون provider شبکه‌ای نیست. دستورات زیر فقط در یک پوشه موقت تازه، روی ماشین آزمایشی و با اطلاع از ایجاد فایل state اجرا شوند:

```bash
workdir="$(mktemp -d)" && cd "$workdir" || exit 1
cat > main.tf <<'HCL'
terraform {
  required_version = ">= 1.4.0"
}
resource "terraform_data" "example" {
  input = { name = "lab", vlan = 10 }
}
output "example" {
  value = terraform_data.example.output
}
HCL
terraform init
terraform plan
terraform apply
terraform plan
terraform output example
```

در `apply` فقط پس از خواندن طرح تأیید کنید. انتظار: نخستین plan ایجاد یک `terraform_data` را پیشنهاد کند؛ پس از apply موفق، plan بعدی معمولاً تغییر ندارد و output شامل `vlan = 10` است. نسخه Terraform و خطاهای محیط را بررسی کنید؛ موفقیت بدون اجرای واقعی ادعا نمی‌شود. برای پاک‌سازی، در همان پوشه `terraform destroy` را پس از خواندن طرح تأیید کنید؛ فایل‌های پوشه موقت را تنها پس از بررسی و اطمینان از مسیر پاک کنید. از آنجا که منبع داخلی واقعیت شبکه بیرونی ندارد، این بخش **آزمایش drift تجهیز واقعی نیست**.

## مفهوم و عیب‌یابی drift واقعی

Drift می‌تواند از تغییر منبع واقعی خارج از گردش کار Terraform به وجود آید. در شرایط معمول، `plan` وضعیت منبع را از provider بازخوانی می‌کند. `terraform plan -refresh-only` تغییر پیشنهادی state را برای بررسی نشان می‌دهد؛ `terraform apply -refresh-only` پس از تأیید state را با وضعیت مشاهده‌شده همگام می‌کند، نه اینکه منبع بیرونی را به پیکربندی برگرداند. برای بازگردانی، ابتدا طرح معمولی و اثر آن را با مجوز بررسی کنید. قابلیت refresh و lock و جزئیات خطا به provider و backend وابسته‌اند. در صورت خطای احراز هویت، API یا قفل، دستورات را موفق فرض نکنید؛ پیام خطا، سطح دسترسی و backend را بررسی کنید. هرگز state واقعی را برای آزمایش دستی ویرایش نکنید.

منابع: [Terraform: Manage resource drift](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift)، [terraform_data](https://developer.hashicorp.com/terraform/language/resources/terraform-data).
