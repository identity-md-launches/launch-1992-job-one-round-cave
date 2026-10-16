#!/usr/bin/env python3
"""Offline multipleOf compatibility checks, retaining ApiDelta and BoundCheck findings."""
import argparse
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys

BOUND_PATH = Path(__file__).resolve().parents[1] / 'boundcheck' / 'boundcheck.py'
spec = importlib.util.spec_from_file_location('multiplecheck_bound', BOUND_PATH)
bound = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bound)
api = bound.api


def step(schema):
    """Positive rational step; absent means unrestricted numbers (None)."""
    if 'multipleOf' not in schema:
        return None
    value = schema['multipleOf']
    api.require(type(value) in (int, float), 'multipleOf must be a positive finite number')
    try:
        result = Fraction(str(value))
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        raise api.Invalid('multipleOf must be a positive finite number') from exc
    api.require(result > 0, 'multipleOf must be a positive finite number')
    return result


def integer_only(schema):
    value = schema.get('type')
    return value == 'integer' or value == ['integer']


def contained(source, target):
    """Is the additive lattice source a subset of target? None is unrestricted."""
    if target is None:
        return True
    if source is None:
        return False
    return (source / target).denominator == 1


class Analyzer(bound.Analyzer):
    def _schema(self, old, new, loc, direction):
        super()._schema(old, new, loc, direction)
        before, after = step(old), step(new)
        # On an unchanged integer-only domain, multiples of p/q among integers
        # are exactly multiples of p (p/q is already reduced by Fraction).
        if integer_only(old) and integer_only(new):
            before = Fraction(before.numerator) if before is not None else Fraction(1)
            after = Fraction(after.numerator) if after is not None else Fraction(1)
        source, target = (before, after) if direction == 'request' else (after, before)
        if not contained(source, target):
            self.emit('breaking', 'multiple_of_incompatible', loc + '/multipleOf',
                      'New request multiple excludes formerly accepted numeric values.'
                      if direction == 'request' else
                      'New response multiples can violate the old numeric contract.')


def compare(old, new):
    report = Analyzer(old, new).run()
    report['extension'] = 'multiplecheck-v1 (includes boundcheck-v1)'
    return report


def demo():
    old, digest = api.load(bound.BASE.with_name('imd-openapi.json'))
    old = copy.deepcopy(old)
    schema = old['paths']['/requests/quote']['post']['requestBody']['content']['application/json']['schema']
    schema.setdefault('properties', {})['batchSize'] = {'type': 'integer', 'multipleOf': 2}
    new = copy.deepcopy(old)
    new['paths']['/requests/quote']['post']['requestBody']['content']['application/json']['schema']['properties']['batchSize']['multipleOf'] = 3
    result = compare(old, new)
    result.update(capture_sha256=digest,
                  demo='Hypothetical batchSize change in the captured public IMD API. A formerly valid value 2 is rejected by the new multiple 3. No operation called.')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('demo')
    diff = commands.add_parser('compare')
    diff.add_argument('old')
    diff.add_argument('new')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            report = demo()
        else:
            old, old_hash = api.load(args.old)
            new, new_hash = api.load(args.new)
            report = compare(old, new)
            report.update(old_sha256=old_hash, new_sha256=new_hash)
        print(json.dumps(report, indent=2, allow_nan=False))
        return 0 if args.command == 'demo' else {
            'breaking': 1, 'review_required': 3, 'no_detected_breakage': 0}[report['status']]
    except (api.Invalid, OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print('multiplecheck: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
