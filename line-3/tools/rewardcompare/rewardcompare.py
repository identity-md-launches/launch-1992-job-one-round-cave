#!/usr/bin/env python3
"""Review exact allocation changes when only a ZTO/IMD budget changes. Offline."""

import argparse
import importlib.util
import json
from pathlib import Path
import sys


RECEIPT_PATH = Path(__file__).resolve().parents[1] / "rewardreceipt" / "rewardreceipt.py"
SPEC = importlib.util.spec_from_file_location("rewardreceipt", RECEIPT_PATH)
rr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rr)
rs = rr.rs


def compare(before_request, before_report, after_request, after_report, metadata):
    """Verify both reports; require fixed identities, addresses, and exact weights."""
    before_receipt = rr.verify(before_request, before_report, metadata)
    after_receipt = rr.verify(after_request, after_report, metadata)

    def roster(report):
        return [(row["id"], row["weight_fraction"], row.get("address"))
                for row in report["allocations"]]

    rs.require(roster(before_report) == roster(after_report),
               "budget comparison requires identical contributor IDs, exact weights and addresses")
    budget_delta = int(after_report["budget_units"]) - int(before_report["budget_units"])
    rows = []
    for before, after in zip(before_report["allocations"], after_report["allocations"]):
        delta = int(after["units"]) - int(before["units"])
        row = {"id": before["id"], "before_units": before["units"],
               "after_units": after["units"], "delta_units": str(delta)}
        if "address" in before:
            row["address"] = before["address"]
        rows.append(row)
    assert sum(int(row["delta_units"]) for row in rows) == budget_delta
    losses = [row["id"] for row in rows if int(row["delta_units"]) < 0]
    gains = [row["id"] for row in rows if int(row["delta_units"]) > 0]
    opposite = losses if budget_delta > 0 else gains if budget_delta < 0 else []
    return {
        "schema": "rewardcompare-v1",
        "token": before_report["token"],
        "before_budget_units": before_report["budget_units"],
        "after_budget_units": after_report["budget_units"],
        "budget_delta_units": str(budget_delta),
        "allocation_delta_sum_units": str(sum(int(row["delta_units"]) for row in rows)),
        "contributors_losing_units": losses,
        "contributors_gaining_units": gains,
        "contributors_moving_against_budget": opposite,
        "review_required": bool(opposite),
        "allocations": rows,
        "before_receipt": before_receipt,
        "after_receipt": after_receipt,
        "scope": "comparison of two complete allocations, not incremental payments or entitlement; no balance, identity, work or payment verified",
        "warning": "largest remainder is not budget-monotonic; review decreases before replacing an allocation",
    }


def demo():
    metadata = rs.read_json(rr.ROOT / "zto-mainnet.json")
    # Classic largest-remainder budget paradox, in real ZTO smallest units.
    # These are illustrative labels/weights, with no invented payees.
    contributors = [{"id": name, "weight": str(weight)} for name, weight in
                    zip("abcdef", (1500, 1500, 900, 500, 500, 200))]
    before = {"budget": rs.display_units(25, metadata["decimals"]),
              "contributors": contributors}
    after = dict(before, budget=rs.display_units(26, metadata["decimals"]))
    return compare(before, rs.allocate(before, metadata),
                   after, rs.allocate(after, metadata), metadata)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="offline ZTO example: a larger budget reduces two shares")
    check = sub.add_parser("compare", help="verify and compare two saved allocations")
    for side in ("before", "after"):
        check.add_argument("--" + side + "-request", required=True)
        check.add_argument("--" + side + "-report", required=True)
    check.add_argument("--metadata", default=str(rr.ROOT / "zto-mainnet.json"))
    check.add_argument("--output", help="new workspace JSON file; never overwrite")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            result = demo()
        else:
            result = compare(rs.read_json(args.before_request), rs.read_json(args.before_report),
                             rs.read_json(args.after_request), rs.read_json(args.after_report),
                             rs.read_json(args.metadata))
        rs.write_json(result, getattr(args, "output", None))
        # A valid comparison with counter-directional changes needs human review.
        return 1 if result["review_required"] else 0
    except (rs.Invalid, OSError, ValueError, OverflowError) as exc:
        message = str(exc) if isinstance(exc, rs.Invalid) else type(exc).__name__
        print("rewardcompare: " + message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
