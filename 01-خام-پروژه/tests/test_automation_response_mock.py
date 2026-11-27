import importlib.util
import json
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'academy-labs/automation_response_mock.py'
spec = importlib.util.spec_from_file_location('automation_response_mock', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class AutomationResponseTests(unittest.TestCase):
    def test_json_data_and_rejection(self):
        body = json.dumps({'ietf-interfaces:interfaces': {'interface': [{'name':'Ethernet1','enabled':True}]}})
        self.assertEqual(m.parse_interfaces(200, body), [('Ethernet1', True)])
        with self.assertRaises(ValueError): m.parse_interfaces(401, body)
        with self.assertRaises(ValueError): m.parse_interfaces(200, body.replace('true', '"true"'))
        with self.assertRaises(ValueError): m.parse_interfaces(200, 'not json')
        with self.assertRaises(KeyError): m.parse_interfaces(200, '{}')
