import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
import equipment_probe as probe  # noqa: E402


class LegacySSHCompatibilityTests(unittest.TestCase):
    def test_allowlist_is_exact_ipv4_and_empty_by_default(self):
        with patch.dict(os.environ, {probe.LEGACY_SSH_HOSTS_ENV: ""}):
            self.assertEqual(probe.legacy_ssh_hosts(), frozenset())
        self.assertEqual(
            probe.legacy_ssh_hosts("10.4.86.2, 10.2.15.2"),
            frozenset({"10.4.86.2", "10.2.15.2"}),
        )

    def test_allowlist_rejects_hostnames_ipv6_and_public_ips(self):
        for value in ("switch.example", "2001:db8::1", "8.8.8.8", "10.4.86.2,"):
            with self.subTest(value=value), self.assertRaises(probe.ProbeError):
                probe.legacy_ssh_hosts(value)

    def test_legacy_algorithms_are_only_appended_when_explicitly_enabled(self):
        modern = probe.ssh_arguments(
            "/usr/local/bin/ssh", "10.4.86.3", "probe", "/data/known_hosts", "yes"
        )
        legacy = probe.ssh_arguments(
            "/usr/local/bin/ssh", "10.4.86.2", "probe", "/data/known_hosts", "yes",
            legacy_compatibility=True,
        )
        modern_options = [modern[i + 1] for i, value in enumerate(modern[:-1]) if value == "-o"]
        legacy_options = [legacy[i + 1] for i, value in enumerate(legacy[:-1]) if value == "-o"]
        self.assertNotIn(probe.LEGACY_KEX_OPTION, modern_options)
        self.assertNotIn(probe.LEGACY_HOST_KEY_OPTION, modern_options)
        self.assertIn(probe.LEGACY_KEX_OPTION, legacy_options)
        self.assertIn(probe.LEGACY_HOST_KEY_OPTION, legacy_options)
        self.assertIn("StrictHostKeyChecking=yes", legacy_options)
        self.assertIn(probe.LEGACY_CIPHER_OPTION, legacy_options)


if __name__ == "__main__":
    unittest.main()
