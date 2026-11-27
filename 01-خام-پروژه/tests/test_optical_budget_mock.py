import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'academy-labs/optical_budget_mock.py'
spec = importlib.util.spec_from_file_location('optical_budget_mock', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class OpticalBudgetTests(unittest.TestCase):
    def test_budget_and_limits(self):
        self.assertEqual(m.calculate(-3, -15, [4, 1, 1], 3),
                         {'total_loss_db':6, 'predicted_rx_dbm':-9, 'available_margin_db':6, 'meets_margin':True})
        self.assertFalse(m.calculate(-3, -15, [4, 1, 1], 7)['meets_margin'])
        with self.assertRaises(ValueError): m.calculate(-3, -15, [], 3)
        with self.assertRaises(ValueError): m.calculate(-3, -15, [-1], 3)
