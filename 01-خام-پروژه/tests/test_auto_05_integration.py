"""Behavior of the selected local serialization exercise; no devices or YAML parser."""
import html
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('auto05', ROOT / 'academy-labs/agent3/auto_05_lab.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class SerializationTests(unittest.TestCase):
    def test_json_valid_values_and_nested_duplicates(self):
        self.assertEqual(lab.parse_json_strict('{"x":[true,null,1]}'), {'x':[True,None,1]})
        self.assertEqual(lab.parse_json_strict('42'), 42)
        for text in ('NaN', 'Infinity', '-Infinity', '{"x":NaN}', '{"x":{"a":1,"a":2}}', '{"x":1,}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                lab.parse_json_strict(text)
        self.assertEqual(lab.parse_json_strict('{"a":1,"a":2}', reject_duplicate_keys=False), {'a':2})
        with self.assertRaises(ValueError):
            lab.parse_json_strict('NaN', reject_duplicate_keys=False)

    def test_model_and_xml_are_explicitly_limited(self):
        self.assertTrue(lab.detect_yaml_11_norway_trap('NO')['yaml_1_1_coerced_to_bool'])
        self.assertFalse(lab.detect_yaml_11_norway_trap('nO')['yaml_1_1_coerced_to_bool'])
        self.assertFalse(lab.detect_yaml_11_norway_trap('"NO"')['yaml_1_1_coerced_to_bool'])
        original = 'x"\\\n'
        self.assertEqual(json.loads(lab.detect_yaml_11_norway_trap(original)['safe_representation']), original)
        self.assertEqual(lab.parse_xml_with_namespace(lab.SAMPLE_NETCONF_XML), [{'name':'GigabitEthernet1','enabled':'true'}])
        self.assertEqual(lab.parse_xml_with_namespace('<interfaces><interface><name>x</name></interface></interfaces>'), [])

    def test_catalog_and_embedded_lab(self):
        bp = json.loads((ROOT / 'server/www/academy-assets/v5/blueprints/auto_05.json').read_text())
        source = (ROOT / 'academy-labs/agent3/auto_05_lab.py').read_text().rstrip('\n')
        self.assertIn(source, html.unescape(bp['stages']['lab']['html']))
        catalog = json.loads((ROOT / 'server/www/academy-assets/curriculum-catalog.json').read_text())
        items = [l for p in catalog['paths'] for c in p['courses'] for l in c['lessons'] if l['id']=='auto_05']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['prerequisites'], ['auto_02'])
        self.assertIn('بازبینی مستقل انسانی انجام نشده', bp['reviewStatus'])

if __name__ == '__main__': unittest.main()
