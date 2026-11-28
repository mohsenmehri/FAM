#!/usr/bin/env bash
# Hardened FAM VM deploy script (never uses `git checkout -B`, never ignores `docker compose stop`,
# never copies live SQLite without safe sqlite3.Connection.backup + PRAGMA integrity_check).
set -Eeuo pipefail

REPO_DIR="${FAM_REPO_DIR:-/opt/FAM}"
APP_DIR="${REPO_DIR}/01-خام-پروژه"
TARGET_BRANCH="${FAM_TARGET_BRANCH:-arena/941b9e62-fam}"
TARGET_SHA="${FAM_TARGET_SHA:?Set FAM_TARGET_SHA to the exact 40-char commit SHA to deploy}"
BACKUP_BASE="${FAM_BACKUP_BASE:-/var/backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_ROOT="${BACKUP_BASE}/fam-upgrade-${STAMP}"
DB_HOST_PATH="${APP_DIR}/data/fam.sqlite3"

CURRENT_STEP="init"
SERVICE_STATE="UNKNOWN"
BACKUP_VERIFIED="0"

on_exit() {
  local rc=$?
  if [ "${rc}" -ne 0 ]; then
    echo "============================================================" >&2
    echo "DEPLOY FAILED at step: ${CURRENT_STEP} (exit=${rc})" >&2
    echo "SERVICE_STATE=${SERVICE_STATE}" >&2
    if [ "${BACKUP_VERIFIED}" = "1" ]; then
      echo "VERIFIED_BACKUP=${BACKUP_ROOT}" >&2
      echo "ROLLBACK_CMD=FAM_REPO_DIR=\"${REPO_DIR}\" \"${APP_DIR}/tools/rollback_vm.sh\" \"${BACKUP_ROOT}\"" >&2
    else
      echo "VERIFIED_BACKUP=NONE (failure occurred before backup completed)" >&2
    fi
    echo "============================================================" >&2
  fi
}
trap on_exit EXIT

CURRENT_STEP="1-preflight-repo"
SERVICE_STATE="RUNNING_UNCHANGED"
echo "[1/10] بررسی مسیر مخزن و ثبت وضعیت فعلی..."
test -d "${REPO_DIR}/.git"
test -f "${APP_DIR}/docker-compose.yml"
cd "${REPO_DIR}"
PREV_SHA="$(git rev-parse HEAD)"
PREV_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "PREV_BRANCH=${PREV_BRANCH}  PREV_SHA=${PREV_SHA}"

CURRENT_STEP="2-check-dirty-worktree"
echo "[2/10] بررسی تغییرات tracked و فایل‌های untracked..."
if [ -n "$(git status --porcelain --untracked-files=normal)" ]; then
  echo "ERROR: تغییرات tracked یا فایل‌های untracked کنترل‌نشده وجود دارد:" >&2
  git status --short >&2
  exit 1
fi

CURRENT_STEP="3-fetch-target-sha"
echo "[3/10] دریافت SHA هدف از origin بدون تغییر شاخه‌های محلی..."
git fetch --prune origin "${TARGET_BRANCH}"
FETCHED_SHA="$(git rev-parse FETCH_HEAD)"
if [ "${FETCHED_SHA}" != "${TARGET_SHA}" ]; then
  echo "ERROR: SHA دریافت‌شده (${FETCHED_SHA}) با SHA مورد انتظار (${TARGET_SHA}) برابر نیست!" >&2
  exit 1
fi

CURRENT_STEP="4-check-local-commits-and-branch-divergence"
echo "[4/10] بررسی کمیت‌های محلی پوش‌نشده و عدم واگرایی شاخه..."
if [ -n "$(git rev-list "${PREV_SHA}" --not --remotes=origin)" ]; then
  echo "ERROR: شاخه فعلی (${PREV_BRANCH} @ ${PREV_SHA}) دارای کمیت محلی پوش‌نشده است. عملیات متوقف شد:" >&2
  git log --oneline "${PREV_SHA}" --not --remotes=origin >&2
  exit 1
fi
if git show-ref --verify --quiet "refs/heads/${TARGET_BRANCH}"; then
  LOCAL_TARGET_SHA="$(git rev-parse "refs/heads/${TARGET_BRANCH}")"
  if ! git merge-base --is-ancestor "${LOCAL_TARGET_SHA}" "${TARGET_SHA}"; then
    echo "ERROR: شاخه محلی ${TARGET_BRANCH} (${LOCAL_TARGET_SHA}) جد مستقیم ${TARGET_SHA} نیست و دارای کمیت واگراست. بدون مداخله دستی بازنشانی نمی‌شود." >&2
    git log --oneline "${TARGET_SHA}..${LOCAL_TARGET_SHA}" >&2
    exit 1
  fi
fi

CURRENT_STEP="5-check-ignored-runtime-files"
echo "[5/10] بررسی وجود فایل‌های محلی ignored (.env / certs / data)..."
test -f "${APP_DIR}/.env"
test -d "${APP_DIR}/certs"
test -d "${APP_DIR}/data"

CURRENT_STEP="6-stop-docker-services"
SERVICE_STATE="STOP_FAILED_CHECK_DOCKER"
echo "[6/10] توقف سرویس‌های Docker و تأیید صفر بودن کانتینر در حال اجرا..."
cd "${APP_DIR}"
docker compose stop
RUNNING_AFTER_STOP="$(docker compose ps -q --status running)"
if [ -n "${RUNNING_AFTER_STOP}" ]; then
  echo "ERROR: پس از docker compose stop هنوز کانتینر در حال اجرا وجود دارد: ${RUNNING_AFTER_STOP}" >&2
  exit 1
fi
SERVICE_STATE="STOPPED_NO_CHANGES_YET"
echo "تأیید شد: صفر کانتینر در حال اجرا."

CURRENT_STEP="7-safe-sqlite-and-runtime-backup"
echo "[7/10] پشتیبان‌گیری ایمن SQLite + فایل‌های محلی ignored + راستی‌آزمایی integrity_check..."
install -d -m 0700 "${BACKUP_ROOT}"
cat > "${BACKUP_ROOT}/metadata.txt" <<EOF
STAMP=${STAMP}
PREV_BRANCH=${PREV_BRANCH}
PREV_SHA=${PREV_SHA}
TARGET_BRANCH=${TARGET_BRANCH}
TARGET_SHA=${TARGET_SHA}
EOF

(cd "${APP_DIR}/data" && find . -maxdepth 3 | LC_ALL=C sort) > "${BACKUP_ROOT}/data-inventory-before.txt"

if [ -f "${DB_HOST_PATH}" ]; then
  python3 - "${DB_HOST_PATH}" "${BACKUP_ROOT}/fam.sqlite3" <<'PY'
import sqlite3, sys
src_path, dst_path = sys.argv[1], sys.argv[2]
src = sqlite3.connect(f"file:{src_path}?mode=ro", uri=True, timeout=30)
dst = sqlite3.connect(dst_path)
try:
    with dst:
        src.backup(dst)
    chk = dst.execute("PRAGMA integrity_check;").fetchall()
    if chk != [("ok",)]:
        raise SystemExit(f"SQLite backup integrity_check failed: {chk}")
    print("SQLite safe backup + integrity_check: OK")
finally:
    dst.close()
    src.close()
PY
  (cd "${BACKUP_ROOT}" && sha256sum fam.sqlite3 > fam.sqlite3.sha256 && sha256sum -c fam.sqlite3.sha256)
else
  echo "WARNING: فایل ${DB_HOST_PATH} وجود نداشت (نصب تازه)."
fi

cp -a "${APP_DIR}/.env" "${BACKUP_ROOT}/.env"
cp -a "${APP_DIR}/certs" "${BACKUP_ROOT}/certs"
if [ -f "${APP_DIR}/data/equipment_known_hosts" ]; then
  cp -a "${APP_DIR}/data/equipment_known_hosts" "${BACKUP_ROOT}/equipment_known_hosts"
fi
chmod -R go-rwx "${BACKUP_ROOT}"
BACKUP_VERIFIED="1"

CURRENT_STEP="8-safe-git-update"
SERVICE_STATE="STOPPED_CODE_UPDATED_NEEDS_ROLLBACK_OR_RETRY"
echo "[8/10] انتقال امن شاخه (تنها fast-forward یا ایجاد جدید با -b، هرگز -B)..."
cd "${REPO_DIR}"
if git show-ref --verify --quiet "refs/heads/${TARGET_BRANCH}"; then
  git checkout "${TARGET_BRANCH}"
  git merge --ff-only "${TARGET_SHA}"
else
  git checkout -b "${TARGET_BRANCH}" "${TARGET_SHA}"
fi
test "$(git rev-parse HEAD)" = "${TARGET_SHA}"

CURRENT_STEP="9-verify-manifest-and-ignored-files"
echo "[9/10] راستی‌آزمایی MANIFEST.sha256 و سلامت فایل‌های ignored پس از checkout..."
cd "${APP_DIR}"
sha256sum -c MANIFEST.sha256 >/dev/null
test -f "${APP_DIR}/.env"
test -d "${APP_DIR}/certs"
test -d "${APP_DIR}/data"

CURRENT_STEP="10a-build-image"
echo "[10/10] ساخت ایمیج و راه‌اندازی سرویس‌ها + بررسی سلامت..."
docker compose build --pull=false app
CURRENT_STEP="10b-start-services"
docker compose up -d --force-recreate --wait
SERVICE_STATE="RUNNING_UNHEALTHY_NEEDS_ROLLBACK_OR_INSPECTION"
CURRENT_STEP="10c-healthcheck"
docker compose ps
docker compose exec -T app python -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8765/'); print('APP HTTP:', r.status)"
SERVICE_STATE="RUNNING_UPGRADED"
echo "SERVICE_STATE=${SERVICE_STATE}"
echo "=== استقرار ${TARGET_SHA} کامل شد. مسیر پشتیبان معتبر: ${BACKUP_ROOT} ==="
