"""Offline administration: consistent live backup; explicit, checked restore.
Never copy an active .sqlite3 file with Explorer (the WAL may contain new writes).
Run with the service's Python environment. Backups contain sensitive data.
"""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from datetime import datetime, timezone
import uuid

try:
    from .account_policy import has_active_manager
except ImportError:
    from account_policy import has_active_manager

TABLES={'state','users','settings','sessions','receipts','audit','undo','attempts'}

def connect_read(path):
    path=Path(path).resolve()
    if not path.is_file():raise ValueError('Database does not exist: '+str(path))
    return sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=30)

def check(db):
    if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity check failed')
    tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not TABLES<=tables:raise ValueError('Not a FAM central backup')
    row=db.execute('SELECT payload FROM state WHERE id=1').fetchone()
    if not row or not isinstance(json.loads(row[0]),dict):raise ValueError('Missing workbook')
    try:
        if __package__:
            from .app import validate_state, Problem
        else:
            from app import validate_state, Problem
        validate_state(json.loads(row[0]))
    except Problem as e:raise ValueError('Invalid workbook in backup: '+e.message) from e
    if not has_active_manager(db):raise ValueError('No active administrator')

def backup(source,destination):
    destination=Path(destination).resolve()
    if destination.exists():raise ValueError('Refusing to overwrite an existing backup')
    destination.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='fam-backup-',suffix='.sqlite3',dir=destination.parent);os.close(fd)
    try:
        src=connect_read(source);dst=sqlite3.connect(name)
        try:src.backup(dst);check(dst)
        finally:src.close();dst.close()
        # Publish a complete file only after verification and SQLite close/checkpoint.
        os.replace(name,destination)
    finally:
        if os.path.exists(name):os.unlink(name)
    return destination

def restore(source,destination,server_stopped=False):
    if not server_stopped:raise ValueError('Stop ALL backend workers first; pass --server-stopped after verifying the port is closed')
    destination=Path(destination).resolve();source=Path(source).resolve()
    if source==destination:raise ValueError('Source and destination must differ')
    destination.parent.mkdir(parents=True,exist_ok=True)
    # Validate the source before touching the target; prepare a rotated copy.
    fd,name=tempfile.mkstemp(prefix='fam-restore-',suffix='.sqlite3',dir=destination.parent);os.close(fd)
    safety=None
    try:
        src=connect_read(source);prepared=sqlite3.connect(name)
        try:
            src.backup(prepared);check(prepared)
            prepared.execute('UPDATE state SET epoch=? WHERE id=1',(str(uuid.uuid4()),))
            for table in ('sessions','receipts','undo','attempts'):prepared.execute('DELETE FROM '+table)
            for table in ('equipment_used_tickets','equipment_leases'):
                if prepared.execute("SELECT 1 FROM sqlite_master WHERE name=?",(table,)).fetchone():prepared.execute('DELETE FROM '+table)
            prepared.commit()
        finally:src.close();prepared.close()
        if destination.exists():
            stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            safety=backup(destination,destination.with_name(destination.stem+'.before-restore.'+stamp+'.'+uuid.uuid4().hex[:6]+'.sqlite3'))
        src=connect_read(name);dst=sqlite3.connect(destination,timeout=30)
        try:
            # SQLite backup into the target, NOT file replacement over a live WAL.
            src.backup(dst);check(dst);dst.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        finally:src.close();dst.close()
    finally:
        if os.path.exists(name):os.unlink(name)
    return safety

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    b=sub.add_parser('backup');b.add_argument('--db',required=True);b.add_argument('--output',required=True)
    r=sub.add_parser('restore');r.add_argument('--input',required=True);r.add_argument('--db',required=True);r.add_argument('--server-stopped',action='store_true')
    args=parser.parse_args()
    try:
        if args.command=='backup':print('Verified backup:',backup(args.db,args.output))
        else:print('Restore complete. Sessions revoked; epoch rotated. Safety copy:',restore(args.input,args.db,args.server_stopped))
    except (ValueError,sqlite3.Error,OSError) as e:parser.exit(1,str(e)+'\n')

if __name__=='__main__':main()
