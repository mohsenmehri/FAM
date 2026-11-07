#!/bin/bash
# FAM lab setup: builds the app image offline and starts HTTPS + the app.
# Usage:  sudo bash setup.sh <host-or-ip-you-use-in-the-browser>
# Example: sudo bash setup.sh 192.168.97.128
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
cd "$here"

if [ $# -ne 1 ]; then
    echo "usage: sudo bash setup.sh <host-or-ip-you-use-in-the-browser>" >&2
    exit 1
fi
ORIGIN="$1"

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: run this script with sudo." >&2
    exit 1
fi

echo "=== 1/6 prerequisite checks ==="
command -v docker >/dev/null || { echo "ERROR: docker is not installed."; exit 1; }
docker image inspect python:3.12-slim >/dev/null 2>&1 || {
    echo "ERROR: image python:3.12-slim is not loaded."; exit 1
}
docker image inspect nginx:alpine >/dev/null 2>&1 || {
    echo "ERROR: image nginx:alpine is not loaded."; exit 1
}

echo "=== 2/6 collect ssh client ==="
sh collect-ssh.sh

echo "=== 3/6 build app image (offline) ==="
printf 'FAM_PUBLIC_ORIGIN=https://%s\n' "$ORIGIN" > .env
docker compose build

echo "=== 4/6 lab TLS certificate ==="
mkdir -p certs data
if [ ! -f certs/fam.crt ]; then
    docker run --rm -v "$here/certs:/certs" fam-app:1.0 \
        python /app/gen_cert.py --out /certs --host fam-lab --origin "$ORIGIN"
else
    echo "certificate already exists; keeping it."
fi

echo "=== 5/6 first administrator ==="
if [ -s data/fam.sqlite3 ]; then
    echo "database already exists; bootstrap skipped."
else
    echo "Type a strong administrator password (12+ characters) when asked."
    docker compose run --rm --no-deps app \
        python /app/server/bootstrap_admin.py --db /data/fam.sqlite3 --origin "https://$ORIGIN"
fi

echo "=== 6/6 start ==="
docker compose up -d
sleep 3
docker compose ps

cat <<EOF

Done. Open  https://$ORIGIN  in the Windows browser.
If the browser warns about the certificate, choose Advanced -> Proceed
(this is the expected lab certificate, not a public one).
EOF
