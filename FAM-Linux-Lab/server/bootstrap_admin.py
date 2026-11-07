"""Private one-time bootstrap prompt; never a password argv/file or DB reset."""
import argparse
import getpass
import os
from pathlib import Path
import sqlite3
import sys
from contextlib import closing


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',required=True);parser.add_argument('--origin',required=True)
    args=parser.parse_args();path=Path(args.db).resolve()
    if path.exists() and path.stat().st_size:
        with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)) as db:
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='state'").fetchone() and db.execute('SELECT 1 FROM state').fetchone():
                print('Existing database preserved; bootstrap skipped.');return
            if db.execute("SELECT 1 FROM sqlite_master WHERE type='table'").fetchone():
                raise SystemExit('Existing incomplete database: restore a verified backup; no reset performed.')
    try:minimum=min(128,max(4,int(os.environ.get('FAM_PASSWORD_MIN_LENGTH','12') or 12)))
    except ValueError:minimum=12
    secret=os.environ.get('FAM_INITIAL_PASSWORD')
    if secret is None:
        if not sys.stdin.isatty():raise SystemExit('Secure interactive console required for bootstrap; no plaintext fallback.')
        secret=getpass.getpass('New FAM administrator password (%d+ characters): '%minimum)
        if secret!=getpass.getpass('Repeat new administrator password: '):raise SystemExit('Passwords do not match.')
    if len(secret)<minimum or len(secret)>128:raise SystemExit('Bootstrap password must have %d to 128 characters.'%minimum)
    os.environ['FAM_INITIAL_PASSWORD']=secret
    try:
        if __package__:from .app import create_app
        else:from app import create_app
        create_app({'DB_PATH':str(path),'PUBLIC_ORIGIN':args.origin})
    finally:os.environ.pop('FAM_INITIAL_PASSWORD',None)
    print('Private bootstrap complete; no password was written to configuration.')


if __name__=='__main__':main()
