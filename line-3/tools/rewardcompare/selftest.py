#!/usr/bin/env python3
"""Offline regression, property and CLI checks for budget comparisons."""
import copy
import contextlib
import io
import random
import unittest
import rewardcompare as rc


class CompareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = rc.rs.read_json(rc.rr.ROOT / 'zto-mainnet.json')
        cls.request = rc.rs.read_json(rc.rr.ROOT / 'example.json')

    def compare(self, before, after):
        return rc.compare(before, rc.rs.allocate(before, self.metadata),
                          after, rc.rs.allocate(after, self.metadata), self.metadata)

    def test_known_budget_paradox(self):
        result = rc.demo()
        self.assertEqual(result['budget_delta_units'], '1')
        self.assertEqual(result['contributors_moving_against_budget'], ['d', 'e'])
        self.assertEqual([r['before_units'] for r in result['allocations']],
                         ['7', '7', '4', '3', '3', '1'])
        self.assertEqual([r['after_units'] for r in result['allocations']],
                         ['8', '8', '5', '2', '2', '1'])
        self.assertTrue(result['review_required'])

    def test_same_budget_and_permutation(self):
        after = copy.deepcopy(self.request)
        after['contributors'].reverse()
        result = self.compare(self.request, after)
        self.assertFalse(result['review_required'])
        self.assertEqual(result['budget_delta_units'], '0')
        self.assertTrue(all(row['delta_units'] == '0' for row in result['allocations']))

    def test_equivalent_weight_notation(self):
        after = copy.deepcopy(self.request)
        after['contributors'][0]['weight'] += '.0'
        self.assertFalse(self.compare(self.request, after)['review_required'])

    def test_changed_roster_or_weights_rejected(self):
        for key, value in [('id', 'other'), ('weight', '2'),
                           ('address', self.metadata['address'])]:
            after = copy.deepcopy(self.request)
            after['contributors'][0][key] = value
            with self.subTest(key=key), self.assertRaises(rc.rs.Invalid):
                self.compare(self.request, after)
        after = copy.deepcopy(self.request)
        after['contributors'].pop()
        with self.assertRaises(rc.rs.Invalid):
            self.compare(self.request, after)

    def test_both_reports_verified(self):
        report = rc.rs.allocate(self.request, self.metadata)
        bad = copy.deepcopy(report)
        bad['allocations'][0]['units'] = '0'
        for before, after in [(report, bad), (bad, report)]:
            with self.assertRaises(rc.rs.Invalid):
                rc.compare(self.request, before, self.request, after, self.metadata)

    def test_capture_change_rejected(self):
        report = rc.rs.allocate(self.request, self.metadata)
        metadata = dict(self.metadata, block_number=self.metadata['block_number'] + 1)
        with self.assertRaises(rc.rs.Invalid):
            rc.compare(self.request, report, self.request, report, metadata)

    def test_added_payment_claim_rejected(self):
        report = rc.rs.allocate(self.request, self.metadata)
        with self.assertRaises(rc.rs.Invalid):
            rc.compare(self.request, dict(report, paid=True), self.request, report, self.metadata)

    def test_uint256_precision(self):
        before = dict(self.request, budget=rc.rs.display_units(rc.rs.UINT256_MAX - 1, 18))
        after = dict(self.request, budget=rc.rs.display_units(rc.rs.UINT256_MAX, 18))
        result = self.compare(before, after)
        self.assertEqual(result['budget_delta_units'], '1')
        self.assertEqual(result['allocation_delta_sum_units'], '1')

    def test_250_seeded_conservation_and_reverse(self):
        rng = random.Random(737)
        for _ in range(250):
            rows = [{'id': 'worker-' + str(i), 'weight': str(rng.randrange(1, 10000))}
                    for i in range(rng.randrange(1, 25))]
            before = {'budget': rc.rs.display_units(rng.randrange(1, 1000000), 18),
                      'contributors': rows}
            after = dict(before, budget=rc.rs.display_units(rng.randrange(1, 1000000), 18))
            forward = self.compare(before, after)
            reverse = self.compare(after, before)
            self.assertEqual(sum(int(r['delta_units']) for r in forward['allocations']),
                             int(forward['budget_delta_units']))
            self.assertEqual([int(r['delta_units']) for r in reverse['allocations']],
                             [-int(r['delta_units']) for r in forward['allocations']])
            self.assertEqual(forward['contributors_losing_units'], reverse['contributors_gaining_units'])

    def test_demo_cli_review_exit(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = rc.main(['demo'])
        self.assertEqual(code, 1)
        self.assertIn('"review_required": true', output.getvalue())


if __name__ == '__main__':
    unittest.main(verbosity=2)
