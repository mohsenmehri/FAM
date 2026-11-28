#!/usr/bin/env bash
# Hardened FAM VM rollback script.
# Restores: Git checkout to PREV_BRANCH (if tip==PREV_SHA) or detached PREV_SHA,
#           SQLite DB (01-خام-پروژه/data/fam.sqlite3), .env, certs/, equipment_known_hosts,
#           and rebuilds/restarts Docker services.
# Post-backup writes to fam.sqlite3, .env, certs/, and equipment_known_hosts WILL BE LOST.
# Extra runtime files created under 01-خام-پروژه/data/ after backup are reported for manual review.
set -Eeuo pipefail

REPO_DIR="${FAM_REPO_DIR:-/opt/FAM}"
APP_DIR="${REPO_DIR}/01-خام-پروژه"
BACKUP_ROOT="${1:?Usage: rollback_vm.sh /path/to/fam-upgrade-TIMESTAMP}"

CURRENT_STEP="init"
SERVICE_STATE="UNKNOWN"

on_exit() {
  local rc=$?
  if [ "${rc}" -ne 0 ]; then
    echo "============================================================" >&2
    echo "ROLLBACK FAILED at step: ${CURRENT_STEP} (exit=${rc})" >&2
    echo "SERVICE_STATE=${SERVICE_STATE}" >&2
    echo "BACKUP_ROOT=${BACKUP_ROOT}" >&2
    echo "============================================================" >&2
  fi
}
trap on_exit EXIT

test -f "${BACKUP_ROOT}/metadata.txt"
# shellcheck disable=SC1091
source "${BACKUP_ROOT}/metadata.txt"

CURRENT_STEP="1-check-dirty-worktree"
echo "[1/6] بررسی تمیز بودن مخزن پیش از Rollback..."
cd "${REPO_DIR}"
if [ -n "$(git status --porcelain --untracked-files=normal)" ]; then
  echo "ERROR: مخزن دارای تغییرات محلی است؛ پیش از Rollback بررسی کنید." >&2
  git status --short >&2
  exit 1
fi

CURRENT_STEP="2-stop-docker-services"
SERVICE_STATE="STOP_FAILED_CHECK_DOCKER"
echo "[2/6] توقف سرویس‌ها و تأیید صفر بودن کانتینر در حال اجرا..."
cd "${APP_DIR}"
docker compose stop
if [ -n "$(docker compose ps -q --status running)" ]; then
  echo "ERROR: هنوز کانتینر در حال اجرا باقی مانده است." >&2
  exit 1
fi
SERVICE_STATE="STOPPED_ROLLING_BACK"

CURRENT_STEP="3-restore-sqlite-backup"
echo "[3/6] راستی‌آزمایی و بازیابی ایمن SQLite..."
if [ -f "${BACKUP_ROOT}/fam.sqlite3" ]; then
  (cd "${BACKUP_ROOT}" && sha256sum -c fam.sqlite3.sha256)
  rm -f "${APP_DIR}/data/fam.sqlite3-wal" "${APP_DIR}/data/fam.sqlite3-shm"
  python3 - "${BACKUP_ROOT}/fam.sqlite3" "${APP_DIR}/data/fam.sqlite3" <<'PY'
import sqlite3, sys
src = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True, timeout=30)
dst = sqlite3.connect(sys.argv[2])
try:
    with dst:
        src.backup(dst)
    chk = dst.execute("PRAGMA integrity_check;").fetchall()
    if chk != [("ok",)]:
        raise SystemExit(f"SQLite rollback integrity_check failed: {chk}")
    print("SQLite rollback + integrity_check: OK")
finally:
    dst.close()
    src.close()
PY
fi

CURRENT_STEP="4-restore-ignored-runtime-files"
echo "[4/6] بازیابی فایل‌های ignored پشتیبان‌گیری‌شده (.env / certs / equipment_known_hosts)..."
cp -a "${BACKUP_ROOT}/.env" "${APP_DIR}/.env"
rm -rf "${APP_DIR}/certs"
cp -a "${BACKUP_ROOT}/certs" "${APP_DIR}/certs"
if [ -f "${BACKUP_ROOT}/equipment_known_hosts" ]; then
  cp -a "${BACKUP_ROOT}/equipment_known_hosts" "${APP_DIR}/data/equipment_known_hosts"
fi

if [ -f "${BACKUP_ROOT}/data-inventory-before.txt" ]; then
  AFTER_INV="$(mktemp)"
  (cd "${APP_DIR}/data" && find . -maxdepth 3 | LC_ALL=C sort) > "${AFTER_INV}"
  EXTRA_FILES="$(comm -13 "${BACKUP_ROOT}/data-inventory-before.txt" "${AFTER_INV}" || true)"
  rm -f "${AFTER_INV}"
  if [ -n "${EXTRA_FILES}" ]; then
    echo "NOTICE: فایل‌های زیر پس از زمان پشتیبان در data/ ایجاد شده‌اند و به‌صورت خودکار حذف نشدند (بررسی دستی کنید):"
    echo "${EXTRA_FILES}"
  fi
fi

CURRENT_STEP="5-restore-git-revision"
echo "[5/6] بازگشت کد به PREV_SHA بدون بازنشانی بی‌صدای شاخه‌ها..."
cd "${REPO_DIR}"
if [ "${PREV_BRANCH}" != "HEAD" ] && git show-ref --verify --quiet "refs/heads/${PREV_BRANCH}" \
   && [ "$(git rev-parse "refs/heads/${PREV_BRANCH}")" = "${PREV_SHA}" ]; then
  git checkout "${PREV_BRANCH}"
else
  git checkout --detach "${PREV_SHA}"
fi
test "$(git rev-parse HEAD)" = "${PREV_SHA}"

CURRENT_STEP="6-rebuild-start-and-healthcheck"
echo "[6/6] بازسازی و راه‌اندازی نسخه قبلی..."
cd "${APP_DIR}"
docker compose build --pull=false app
docker compose up -d --force-recreate --wait
docker compose ps
docker compose exec -T app python -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8765/'); print('APP HTTP:', r.status)"
SERVICE_STATE="RUNNING_ROLLED_BACK"
echo "SERVICE_STATE=${SERVICE_STATE}"
echo "=== Rollback به ${PREV_SHA} با موفقیت کامل شد. ==="
