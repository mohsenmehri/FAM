"""Test the educational mock only; this does not execute Terraform."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / "academy-labs" / "terraform_mock.py"
spec = importlib.util.spec_from_file_location("terraform_mock", PATH)
mock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mock)


class TerraformMockTests(unittest.TestCase):
    def test_refresh_and_plan_preserve_observed_and_state_inputs(self):
        previous = {"name": "lab", "vlan": 10}
        observed = {"name": "lab", "vlan": 20}
        desired = {"name": "lab", "vlan": 10}
        plan = mock.refresh_only_plan(previous, observed)
        self.assertEqual(previous["vlan"], 10)
        self.assertEqual(observed["vlan"], 20)
        refreshed = mock.refresh_only_apply(plan)
        self.assertEqual(refreshed["vlan"], 20)
        refreshed["vlan"] = 30
        self.assertEqual(observed["vlan"], 20)
        self.assertEqual(mock.normal_plan(desired, observed), {
            "vlan": {"observed": 20, "desired": 10},
        })
        self.assertEqual(mock.normal_plan(observed, observed), {})

    def test_example_runs_without_network(self):
        result = subprocess.run([sys.executable, str(PATH)], capture_output=True, text=True, check=True, timeout=5)
        self.assertIn("observed object unchanged: {'name': 'lab', 'vlan': 20}", result.stdout)
        self.assertIn("'desired': 10", result.stdout)


if __name__ == "__main__":
    unittest.main()
