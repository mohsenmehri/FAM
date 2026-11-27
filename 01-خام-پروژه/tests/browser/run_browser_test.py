"""Serve a disposable TESTING app and run real Chromium; not production TLS/nginx.

Requires FAM_CHROMIUM_PATH and Node-resolvable puppeteer-core (e.g. NODE_PATH).
"""
import os
import socket
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from flask import send_from_directory
from werkzeug.serving import make_server

PACKAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGE / 'server'))
import app  # noqa: E402

def main():
    if not os.environ.get('FAM_CHROMIUM_PATH'):
        raise SystemExit('Set FAM_CHROMIUM_PATH to a compatible Chromium executable.')
    with tempfile.TemporaryDirectory() as td:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        origin = f'http://127.0.0.1:{port}'
        os.environ['FAM_INITIAL_PASSWORD'] = 'TestAdminPassword!2026'
        application = app.create_app({'TESTING': True, 'COOKIE_SECURE': False,
                                      'DB_PATH': td + '/test.sqlite3', 'PUBLIC_ORIGIN': origin})
        # Production nginx serves these two files; mirror that here for the UI login.
        for filename in ('login.css', 'login.js'):
            application.add_url_rule('/' + filename, endpoint='test_' + filename,
                                     view_func=lambda name=filename: send_from_directory(PACKAGE / 'server/www', name))
        server = make_server('127.0.0.1', port, application, threaded=True)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            env = {**os.environ, 'FAM_TEST_URL': origin,
                   'FAM_OFFLINE_FILE': str(PACKAGE.parent / 'FAM-Academy-Offline.html')}
            subprocess.run(['node', str(Path(__file__).with_name('browser.test.cjs'))], env=env, timeout=120, check=True)
        finally:
            server.shutdown()
            thread.join()


if __name__ == '__main__':
    main()
