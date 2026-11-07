#!/bin/sh
exec /usr/local/fam-ssh/lib/ld-linux-x86-64.so.2 --library-path /usr/local/fam-ssh/lib /usr/local/fam-ssh/ssh "$@"
