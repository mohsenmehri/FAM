"""Atomic cross-process SSH admission and one-use confirmation metadata.

Only digests/expiry/lease ownership are persisted, never credentials, raw IPs,
full tickets, commands, results or jobs. Leases outlive the 160s maximum replacement executor bound.
"""
from contextlib import contextmanager
import hashlib
import logging
import os
import secrets
import sqlite3
import time

LOGGER = logging.getLogger(__name__)
DEFAULT_MAX_CONCURRENT = 8
MIN_CONCURRENT = 1
MAX_CONCURRENT = 32


class AdmissionError(Exception):
    def __init__(self, code):
        self.code = code


def resolve_max_concurrent(raw=None, default=DEFAULT_MAX_CONCURRENT):
    """Parse FAM_EQUIPMENT_MAX_CONCURRENT safely within [1, 32]."""
    value = os.environ.get('FAM_EQUIPMENT_MAX_CONCURRENT') if raw is None else raw
    if value is None or (isinstance(value, str) and not value.strip()):
        return default
    if isinstance(value, bool):
        LOGGER.warning('Invalid FAM_EQUIPMENT_MAX_CONCURRENT boolean value; using default %d', default)
        return default
    try:
        parsed = int(value.strip(), 10) if isinstance(value, str) else int(value) if type(value) is int else None
    except ValueError:
        parsed = None
    if parsed is None:
        LOGGER.warning('Invalid FAM_EQUIPMENT_MAX_CONCURRENT=%r; using default %d', value, default)
        return default
    if parsed < MIN_CONCURRENT:
        LOGGER.warning('FAM_EQUIPMENT_MAX_CONCURRENT=%d below %d; using default %d', parsed, MIN_CONCURRENT, default)
        return default
    if parsed > MAX_CONCURRENT:
        LOGGER.warning('FAM_EQUIPMENT_MAX_CONCURRENT=%d above %d; clamping to %d', parsed, MAX_CONCURRENT, MAX_CONCURRENT)
        return MAX_CONCURRENT
    return parsed


class EquipmentGuard:
    def __init__(self, path, maximum=None):
        self.path = str(path)
        if maximum is None:
            self.maximum = resolve_max_concurrent()
        else:
            if type(maximum) is not int or not MIN_CONCURRENT <= maximum <= MAX_CONCURRENT:
                raise ValueError(f'maximum must be an integer between {MIN_CONCURRENT} and {MAX_CONCURRENT}')
            self.maximum = maximum
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS equipment_used_tickets(digest TEXT PRIMARY KEY,expires INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS equipment_leases(target TEXT PRIMARY KEY,owner TEXT NOT NULL,expires INTEGER NOT NULL);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.execute('PRAGMA busy_timeout=5000')
        try:
            with db:
                yield db
        finally:
            db.close()

    @contextmanager
    def admit(self, host, ticket=None):
        target = hashlib.sha256(host.encode('ascii')).hexdigest()
        owner = secrets.token_hex(16)
        now = int(time.time())
        try:
            with self.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                db.execute('DELETE FROM equipment_used_tickets WHERE expires<?', (now,))
                db.execute('DELETE FROM equipment_leases WHERE expires<?', (now,))
                if db.execute('SELECT 1 FROM equipment_leases WHERE target=?', (target,)).fetchone() or db.execute('SELECT COUNT(*) FROM equipment_leases').fetchone()[0] >= self.maximum:
                    raise AdmissionError('equipment_busy')
                if ticket is not None:
                    digest = hashlib.sha256(ticket.encode('ascii')).hexdigest()
                    if db.execute('SELECT 1 FROM equipment_used_tickets WHERE digest=?', (digest,)).fetchone():
                        raise AdmissionError('ticket_consumed')
                    db.execute('INSERT INTO equipment_used_tickets VALUES(?,?)', (digest, now + 600))
                db.execute('INSERT INTO equipment_leases VALUES(?,?,?)', (target, owner, now + 180))
        except sqlite3.Error:
            raise AdmissionError('equipment_busy') from None
        try:
            yield
        finally:
            # A crashed worker leaves only a bounded lease; never delete another
            # worker's lease. Device SSH is bounded and supervised independently.
            try:
                with self.connect() as db:
                    db.execute('DELETE FROM equipment_leases WHERE target=? AND owner=?', (target, owner))
            except sqlite3.Error:
                pass  # fail closed until expiry, not a retry of any device command
