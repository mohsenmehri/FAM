# FAM Academy v2 — verification report

- Generated: `2026-11-24T20:00:36+00:00`
- Overall: **PASS**
- Branch / HEAD: `arena/5473d411-fam` / `430b4212d1edd4a290c7da578c3372c604d983dd`
- Preview API used during tests: `http://127.0.0.1:45721` (ephemeral, stopped after tests)
- Browser visual automation: **not run** — Chromium/Playwright/Selenium are unavailable; a DOM-shim SPA flow test was run instead.

## Command results

| Check | Result | Details |
|---|---:|---|
| content validator | PASS | validator ok=True; checks=15; errors=0; lessons=10; sims=3; labs=2 |
| python unittest suite | PASS | Ran 49 tests; skipped=12 |
| node engine tests | PASS | node pass=8; fail=0 |
| node syntax checks | PASS | exit 0 |
| node SPA syntax check | PASS | exit 0 |
| SPA UI flow (file fixtures) | PASS | exit 0 |
| SPA UI flow (live preview HTTP API) | PASS | exit 0 |

## Exact command tails

### content validator

`/usr/bin/python3 -B /home/user/FAM/01-خام-پروژه/tools/validate_academy_v2.py --json` → exit `0`

```text
"exercises": 10,
    "references": 26,
    "manifestFiles": 37,
    "rootManifestEntries": 213,
    "rootManifestValid": 66,
    "rootManifestMissing": 143,
    "rootManifestMismatch": 4
  }
}
```

### python unittest suite

`/usr/bin/python3 -B -m unittest discover -s /home/user/FAM/01-خام-پروژه/tests -p test_*.py -v` → exit `0`

```text
test_rate_limit_isolates_clients_and_ignores_spoofed_xff_behind_trusted_proxy (test_app_api.FamProxyFixTests.test_rate_limit_isolates_clients_and_ignores_spoofed_xff_behind_trusted_proxy) ... skipped 'Flask is not installed in this Python environment'
test_trusted_proxy_uses_rightmost_hop_and_blocks_untrusted_peer_spoofing (test_app_api.FamProxyFixTests.test_trusted_proxy_uses_rightmost_hop_and_blocks_untrusted_peer_spoofing) ... skipped 'Flask is not installed in this Python environment'
test_allowlist_is_exact_ipv4_and_empty_by_default (test_equipment_probe_legacy_ssh.LegacySSHCompatibilityTests.test_allowlist_is_exact_ipv4_and_empty_by_default) ... ok
test_allowlist_rejects_hostnames_ipv6_and_public_ips (test_equipment_probe_legacy_ssh.LegacySSHCompatibilityTests.test_allowlist_rejects_hostnames_ipv6_and_public_ips) ... ok
test_legacy_algorithms_are_only_appended_when_explicitly_enabled (test_equipment_probe_legacy_ssh.LegacySSHCompatibilityTests.test_legacy_algorithms_are_only_appended_when_explicitly_enabled) ... ok

----------------------------------------------------------------------
Ran 49 tests in 0.895s

OK (skipped=12)
```

### node engine tests

`/usr/local/bin/node --test /home/user/FAM/01-خام-پروژه/tests/test_academy_v2_engine.test.mjs` → exit `0`

```text
1..8
# tests 8
# suites 0
# pass 8
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 163.837692
```

### node syntax checks

`/usr/local/bin/node --check /home/user/FAM/01-خام-پروژه/server/www/academy-assets/academy-engine.js` → exit `0`

```text
(no output)
```

### node SPA syntax check

`/usr/local/bin/node --check /home/user/FAM/01-خام-پروژه/server/www/academy-assets/academy-v2.js` → exit `0`

```text
(no output)
```

### SPA UI flow (file fixtures)

`/usr/local/bin/node --test /home/user/FAM/01-خام-پروژه/tests/test_academy_v2_ui.test.mjs` → exit `0`

```text
1..1
# tests 1
# suites 0
# pass 1
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 152.072991
```

### SPA UI flow (live preview HTTP API)

`/usr/local/bin/node --test /home/user/FAM/01-خام-پروژه/tests/test_academy_v2_ui.test.mjs` → exit `0`

```text
1..1
# tests 1
# suites 0
# pass 1
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 213.207132
```

## Git status snapshot

- `git status --short -uall` lines: 199
- Deleted legacy paths (` D`): 143
- Modified tracked paths (` M`): 4
- Untracked paths (`??`): 52

Full stdout/stderr of every command is in `reports/academy-v2-test-logs.txt`.

## Known, explicit limitations

- Browser visual/interactive rendering was not photographed or pixel-tested; no browser engine is installed.
- 18 of 23 courses are honest P1 roadmap entries; the presentation-ready vertical slice contains 5 connected live courses, 10 complete lessons, 3 simulations and 2 labs.
- Flask-dependent production route tests are skipped in this environment because Flask is absent; their v2 contract is checked statically and the equivalent read-only/quiz API is exercised over HTTP in the preview server.
- Root `MANIFEST.sha256` is unchanged. Its missing/mismatch counts reflect the 143 intentionally preserved deletions and tracked files modified during this rebuild, not manifest corruption.
