# استقرار FAM Academy v2 روی VM — دستورات ترمینال

این دستورات **روی ترمینال VM** اجرا میشوند، نه در محیط Arena. فرض میشود کلید خصوصی GitHub روی VM موجود است و مسیر نصب FAM همان `~/FAM-Linux-Lab` است. شاخه `arena/5473d411-fam` ساخته و به GitHub push شده است؛ `main` بدون تغییر مانده و نباید checkout شود.

## متغیرها و پیشفرضها

```bash
BRANCH='arena/5473d411-fam'
REPO='git@github.com:mohsenmehri/FAM.git'
STAMP="$(date +%Y%m%d-%H%M%S)"
SRC="$HOME/FAM-v2-git-$STAMP"
DST="$HOME/FAM-Linux-Lab"          # اگر مسیر نصب فرق دارد فقط این را تغییر دهید
HOST='192.168.97.128'              # همان IP/نام میزبان که در مرورگر باز میکنید
KEY="$HOME/.ssh/id_ed25519"        # مسیر کلید خصوصی GitHub؛ در صورت نیاز تغییر دهید
```

اگر کلید خصوصی پیشفرض نیست، قبل از clone این خط را اجرا کنید:

```bash
export GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes"
ssh -T git@github.com
```

پیام `You've successfully authenticated` یعنی کلید درست است. خروجی کد `1` از `ssh -T` بهدلیل ندادن shell توسط GitHub طبیعی است.

## ۱. بررسی شاخه و دریافت کد از GitHub

```bash
git ls-remote "$REPO" "refs/heads/$BRANCH"
REMOTE_COMMIT="$(git ls-remote "$REPO" "refs/heads/$BRANCH" | cut -f1)"
git clone --branch "$BRANCH" --single-branch "$REPO" "$SRC"
git -C "$SRC" log -3 --oneline
test "$(git -C "$SRC" rev-parse HEAD)" = "$REMOTE_COMMIT" && echo 'clone HEAD matches remote branch'
test -f "$SRC/01-خام-پروژه/server/www/academy-content/v1/manifest.json"
test -f "$SRC/01-خام-پروژه/server/private_ui/academy.html"
```

## ۲. پشتیبانگیری از دادهها، گواهیها و تنظیمات فعلی

**هشدار:** `data/`، `certs/` و `.env` حذف نشوند. پایگاه داده و پیشرفت کاربران داخل `data/` است.

```bash
mkdir -p "$DST" "$DST/data" "$DST/certs"
BACKUP="$HOME/fam-backup-$STAMP"
mkdir -p "$BACKUP"
[ -d "$DST/data" ]  && cp -a "$DST/data"  "$BACKUP/"
[ -d "$DST/certs" ] && cp -a "$DST/certs" "$BACKUP/"
[ -f "$DST/.env" ]  && cp -a "$DST/.env"  "$BACKUP/"
echo "backup: $BACKUP"
```

## ۳. توقف سرویس قدیمی، بدون حذف Volume

```bash
if [ -f "$DST/docker-compose.yml" ]; then
    cd "$DST"
    sudo docker compose down
fi
```

از `docker compose down -v`، `rm -rf data certs`، `git reset --hard`، `git clean -fd` و `git checkout main` استفاده نکنید.

## ۴. کپی نسخه جدید روی همان نصب FAM

```bash
cp -a "$SRC/01-خام-پروژه/." "$DST/"
cd "$DST"
python3 -B tools/validate_academy_v2.py | tail -8
```

`cp -a` فایلهای برنامه/آکادمی را جایگزین و فایلهای v2 را اضافه میکند، ولی `data/`، `certs/` و `.env` موجود را چون در مبدأ نیستند حذف نمیکند.

## ۵. آمادهسازی Imageهای پایه Docker

`setup.sh` انتظار دارد `python:3.12-slim` و `nginx:alpine` روی VM باشند:

```bash
sudo docker image inspect python:3.12-slim >/dev/null 2>&1 && echo 'python:3.12-slim OK' || echo 'python:3.12-slim MISSING'
sudo docker image inspect nginx:alpine      >/dev/null 2>&1 && echo 'nginx:alpine OK'      || echo 'nginx:alpine MISSING'
```

اگر هرکدام `MISSING` بود، یکی از دو مسیر زیر را انتخاب کنید:

```bash
# حالت آفلاین: tar تصاویر پایه را از مسیر امن VM لود کنید
sudo docker load -i /path/to/fam-docker-images.tar

# یا اگر VM به Docker Hub دسترسی دارد
sudo docker pull python:3.12-slim
sudo docker pull nginx:alpine
```

**از `02-فایل-های-اجرایی/RUN-FAM.sh` استفاده نکنید**؛ آن اسکریپت Image ازپیشساخته `fam-app:delivery-20261123` را لود میکند و نسخه v2 را build نمیکند.

## ۶. نصب و اجرا

```bash
cd "$DST"
sudo bash setup.sh "$HOST"
```

`setup.sh` بهترتیب Docker و Imageها را بررسی میکند، بسته SSH میزبان را جمعآوری میکند، `.env` را با `FAM_PUBLIC_ORIGIN=https://$HOST` مینویسد، `docker compose build` آفلاین را اجرا میکند، جفت گواهی/کلید TLS را میسازد یا تطابق آنها را بررسی میکند، فقط در نبود `data/fam.sqlite3` مدیر اول را میسازد و در نهایت `docker compose up -d` را اجرا میکند. اگر `.env` تنظیمات اضافهای داشت، پس از setup از نسخه پشتیبان دوباره اضافه کنید.

## ۷. بررسی سرویسها و لاگها

```bash
cd "$DST"
sudo docker compose ps
sudo docker compose logs --tail=80 app nginx
```

## ۸. ورود و تست HTTP آکادمی نسخهدار

چون `/api/*` و حتی `/academy-assets/*` پشت نشست FAM هستند، برای `curl` ابتدا لاگین کرده و Cookie/CSRF را نگه دارید. رمز در تاریخچه shell نوشته نمیشود:

```bash
COOKIE="/tmp/fam-v2-cookies-$STAMP"
read -rp 'FAM username: ' FAM_USER
read -rsp 'FAM password (not echoed): ' FAM_PW; echo

LOGIN_JSON="$(FAM_USER="$FAM_USER" FAM_PW="$FAM_PW" python3 -c 'import json,os; print(json.dumps({"username":os.environ["FAM_USER"],"password":os.environ["FAM_PW"]}))')"
LOGIN="$(curl -k -sS -c "$COOKIE" -H "Origin: https://$HOST" -H 'Content-Type: application/json' -d "$LOGIN_JSON" "https://$HOST/api/login")"
CSRF="$(printf '%s' "$LOGIN" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("csrf",""))')"
[ -n "$CSRF" ] || { echo "Login failed: $LOGIN"; exit 1; }
unset FAM_PW LOGIN_JSON

AUTH=(-k -sS -b "$COOKIE" -H "X-FAM-CSRF: $CSRF")
curl "${AUTH[@]}" "https://$HOST/api/academy/v2/health" | python3 -m json.tool
curl "${AUTH[@]}" "https://$HOST/api/academy/v2/catalog" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["contentVersion"], "paths",len(d["paths"]), "courses",len(d["courses"]), "lessons",len(d["lessons"]), "sims",len(d["simulations"]), "labs",len(d["labs"]))'

for P in \
  /academy-assets/academy-reference-ui.css \
  /academy-assets/academy-v2.css \
  /academy-assets/academy-v2.js \
  /academy-content/v1/manifest.json \
  /api/academy/v2/lesson/l01-osi-tcpip-encapsulation \
  /api/academy/v2/simulation/sim-arp-discovery \
  /api/academy/v2/lab/lab-vlan-trunk; do
    curl "${AUTH[@]}" -o /dev/null -w "$P -> %{http_code} %{content_type} %{size_download} bytes\n" "https://$HOST$P"
done

curl "${AUTH[@]}" "https://$HOST/academy" > "/tmp/fam-academy-$STAMP.html"
grep -E 'academy-reference-ui.css|academy-v2.css|academy-v2.js|id="fam-app"|famAcademyV2.progress.v1' "/tmp/fam-academy-$STAMP.html" | head
```

خروجی مورد انتظار کاتالوگ:

```text
2026.11.24-p0 paths 23 courses 23 lessons 10 sims 3 labs 2
```

وضعیت health در Runtime تولیدی `service:"flask"` است. مسیرهای بالا باید `200` بدهند.

## ۹. تمیزکاری و باز کردن UI

```bash
unset CSRF LOGIN
rm -f "$COOKIE" "/tmp/fam-academy-$STAMP.html"
echo "Open: https://$HOST  →  login  →  Academy"
```

گواهی آزمایشگاه self-signed است؛ هشدار مرورگر مورد انتظار است. بعد از لاگین، صفحه آکادمی را با `Ctrl+F5` رفرش کنید تا CSS/JS قدیمی از کش مرورگر پاک شود. مسیر مستقیم: `https://$HOST/academy`.

## عیبیابی سریع

```bash
cd "$DST"
sudo docker compose ps
sudo docker compose logs --tail=200 app nginx
sudo docker compose exec -T app python -c 'from pathlib import Path; print((Path("/app/server/www/academy-content/v1/manifest.json")).is_file(), (Path("/app/server/private_ui/academy.html")).is_file())'
```

اگر لاگین `403` داد، مقدار `HOST` و هدر `Origin` باید دقیقاً یکی باشند. اگر کاتالوگ `404` داد، بررسی کنید `server/www/academy-content/v1/` داخل `$DST` و داخل Image کپی شده باشد و `docker compose build` دوباره اجرا شود. هیچ `Secret`، رمز یا کلید خصوصی را داخل مخزن قرار ندهید.
