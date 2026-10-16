"""Offline regressions including finite lattice enumeration as an independent oracle."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import multiplecheck as m


def document(schema, response=False):
    media = {'application/json': {'schema': schema}}
    op = {'responses': {'200': {'description': 'ok', 'content': media if response else {}}}}
    if not response:
        op['requestBody'] = {'content': media}
    return {'openapi': '3.1.0', 'paths': {'/items': {'post': op}}}


def findings(old, new, response=False):
    return [f for f in m.compare(document(old, response), document(new, response))['findings']
            if f['code'] == 'multiple_of_incompatible']


class Tests(unittest.TestCase):
    def test_request_tightening_and_relaxation(self):
        self.assertTrue(findings({'multipleOf': 2}, {'multipleOf': 4}))
        self.assertFalse(findings({'multipleOf': 4}, {'multipleOf': 2}))

    def test_response_variance(self):
        self.assertFalse(findings({'multipleOf': 2}, {'multipleOf': 4}, True))
        self.assertTrue(findings({'multipleOf': 4}, {'multipleOf': 2}, True))

    def test_incomparable_steps(self):
        self.assertTrue(findings({'multipleOf': 2}, {'multipleOf': 3}))
        self.assertTrue(findings({'multipleOf': 3}, {'multipleOf': 2}))

    def test_decimal_no_float_modulo(self):
        self.assertFalse(findings({'multipleOf': 0.3}, {'multipleOf': 0.1}))
        self.assertTrue(findings({'multipleOf': 0.1}, {'multipleOf': 0.3}))
        self.assertFalse(findings({'multipleOf': 0.000003}, {'multipleOf': 0.000001}))

    def test_added_and_removed(self):
        self.assertTrue(findings({}, {'multipleOf': 1}))
        self.assertFalse(findings({'multipleOf': 1}, {}))
        self.assertTrue(findings({'multipleOf': 1}, {}, True))
        self.assertFalse(findings({}, {'multipleOf': 1}, True))

    def test_integer_normalization(self):
        for typ in ('integer', ['integer']):
            self.assertFalse(findings({'type': typ}, {'type': typ, 'multipleOf': 0.5}))
            self.assertFalse(findings({'type': typ, 'multipleOf': 3}, {'type': typ, 'multipleOf': 1.5}))
            self.assertTrue(findings({'type': typ}, {'type': typ, 'multipleOf': 1.5}))
            self.assertTrue(findings({'type': typ, 'multipleOf': 3}, {'type': typ}, True))

    def test_number_not_normalized(self):
        self.assertTrue(findings({'type': 'number'}, {'type': 'number', 'multipleOf': 0.5}))

    def test_equal_and_openapi30(self):
        old, new = document({'multipleOf': 0.1}), document({'multipleOf': 0.1})
        old['openapi'] = new['openapi'] = '3.0.3'
        self.assertEqual(m.compare(old, new)['findings'], [])

    def test_bad_multiple(self):
        for value in (0, -1, True, '2', None, [], {}, float('inf'), float('nan')):
            with self.subTest(value=value), self.assertRaises((m.api.Invalid, ValueError)):
                findings({}, {'multipleOf': value})

    def test_preserves_base_and_bound(self):
        result = m.compare(document({'multipleOf': 2, 'maximum': 10, 'pattern': 'a'}),
                           document({'multipleOf': 3, 'maximum': 5, 'pattern': 'b'}))
        codes = {f['code'] for f in result['findings']}
        self.assertTrue({'multiple_of_incompatible', 'numeric_bound_incompatible', 'schema_constraint_changed'} <= codes)

    def test_relaxation_still_review(self):
        self.assertEqual(m.compare(document({'multipleOf': 4}), document({'multipleOf': 2}))['status'], 'review_required')

    def test_nested_reference_and_recursion(self):
        old = document({'$ref': '#/components/schemas/N'})
        old['components'] = {'schemas': {'N': {'properties': {
            'next': {'$ref': '#/components/schemas/N'}, 'batch/~': {'multipleOf': 2}}}}}
        new = copy.deepcopy(old)
        new['components']['schemas']['N']['properties']['batch/~']['multipleOf'] = 3
        result = m.compare(old, new)
        hits = [f for f in result['findings'] if f['code'] == 'multiple_of_incompatible']
        self.assertEqual(len(hits), 1)
        self.assertIn('batch~1~0', hits[0]['location'])

    def test_finite_lattice_oracle(self):
        # Enumerate actual accepted decimal-grid values, independent of ratio test.
        values = [Fraction(i, 100) for i in range(-1000, 1001)]
        steps = [0.1, 0.2, 0.25, 0.3, 0.5, 1, 1.5, 2, 3, 4]
        for a in steps:
            for b in steps:
                accepted_a = {x for x in values if (x / Fraction(str(a))).denominator == 1}
                accepted_b = {x for x in values if (x / Fraction(str(b))).denominator == 1}
                for response in (False, True):
                    expected = not (accepted_b <= accepted_a if response else accepted_a <= accepted_b)
                    self.assertEqual(bool(findings({'multipleOf': a}, {'multipleOf': b}, response)), expected)

    def test_integer_oracle(self):
        for a in (None, 0.25, 0.5, 1, 1.5, 2.5, 3, 4):
            for b in (None, 0.25, 0.5, 1, 1.5, 2.5, 3, 4):
                def schema(v):
                    return dict(type='integer', **({} if v is None else {'multipleOf': v}))
                def accepted(v):
                    return {i for i in range(-60, 61) if v is None or (Fraction(i) / Fraction(str(v))).denominator == 1}
                self.assertEqual(bool(findings(schema(a), schema(b))), not accepted(a) <= accepted(b))

    def test_capture_and_demo(self):
        obj, _ = m.api.load(m.bound.BASE.with_name('imd-openapi.json'))
        self.assertEqual(m.compare(obj, obj)['operations_compared'], 5)
        self.assertEqual(m.compare(obj, obj)['findings'], [])
        self.assertEqual(m.demo()['counts']['breaking'], 1)

    def test_cli(self):
        root = Path('test/scratch')
        root.mkdir(parents=True, exist_ok=True)
        script = str(Path(__file__).with_name('multiplecheck.py'))
        with tempfile.TemporaryDirectory(dir=root) as folder:
            old, new = Path(folder) / 'old.json', Path(folder) / 'new.json'
            old.write_text(json.dumps(document({'multipleOf': 2})))
            for schema, code in (({'multipleOf': 2}, 0), ({'multipleOf': 3}, 1),
                                 ({'multipleOf': 1}, 3), ({'multipleOf': 0}, 2)):
                new.write_text(json.dumps(document(schema)))
                result = subprocess.run([sys.executable, '-B', script, 'compare', str(old), str(new)],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, code, result.stderr)
                if code != 2:
                    json.loads(result.stdout)
            new.write_text('{"openapi":"3.1.0","paths":{},"paths":{}}')
            result = subprocess.run([sys.executable, '-B', script, 'compare', str(old), str(new)],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
