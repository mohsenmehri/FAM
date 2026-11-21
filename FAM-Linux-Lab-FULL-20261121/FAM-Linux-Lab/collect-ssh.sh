#!/bin/sh
# Collect the host OpenSSH client together with its loader and libraries so
# the FAM app image can run equipment probes completely offline.  ssh runs
# through its own bundled loader, so the container's C library version does
# not matter.
# Run this on the Ubuntu lab VM before "docker compose build".
set -eu

here="$(cd "$(dirname "$0")" && pwd)"
out="$here/ssh-bundle"
rm -rf "$out"
mkdir -p "$out/lib"

ssh_path="$(command -v ssh || true)"
if [ -z "$ssh_path" ]; then
    echo "ERROR: no 'ssh' client found on this system." >&2
    exit 1
fi

cp "$ssh_path" "$out/ssh"
chmod 0755 "$out/ssh"

# Every shared library ssh links against, including the C library and the
# dynamic loader itself (their paths appear at the start of an ldd line).
ldd "$ssh_path" | while read -r line; do
    lib=$(printf '%s' "$line" | awk '{for (i=1;i<=NF;i++) if ($i ~ /^\//) {print $i; exit}}')
    [ -n "$lib" ] || continue
    cp -L "$lib" "$out/lib/" 2>/dev/null || true
done

# Name-service modules are opened at run time and do not appear in ldd.
# ssh is only ever given numeric device addresses, but the modules are
# bundled anyway so nothing is required from the container filesystem.
for f in /lib/x86_64-linux-gnu/libnss_*.so* /lib/x86_64-linux-gnu/libresolv.so*; do
    [ -e "$f" ] && cp -L "$f" "$out/lib/" 2>/dev/null || true
done

loader=$(ls "$out/lib"/ld-linux-x86-64.so.* 2>/dev/null | head -n1 || true)
if [ -z "$loader" ]; then
    echo "ERROR: dynamic loader was not collected." >&2
    exit 1
fi

# The wrapper always uses the in-container path (the image layout is fixed).
cat > "$out/run-ssh.sh" <<EOF
#!/bin/sh
exec /usr/local/fam-ssh/lib/$(basename "$loader") --library-path /usr/local/fam-ssh/lib /usr/local/fam-ssh/ssh "\$@"
EOF
chmod 0755 "$out/run-ssh.sh"

echo "ssh bundle written to $out"
ls "$out" "$out/lib" | head -40
