# RewardCompare

RewardCompare reviews a revised ZTO reward budget before a worker replaces an allocation. It verifies both saved reports with RewardReceipt, requires identical contributor IDs, exact weights, addresses and token capture, then reports each signed change in smallest token units. Largest-remainder allocation can give someone less when the total budget grows; this tool makes that visible.

Run from the repository root with Python 3.9+ (standard library only, no installation or network):

```sh
python3 -B line-3/tools/rewardcompare/rewardcompare.py demo
```

**Expected exit: 1, meaning review required.** This is a successful demonstration of a warning, not an input error. The included real Ethereum ZTO capture specifies 18 decimals. Six illustrative contributor labels have weights 1500, 1500, 900, 500, 500, 200. With budgets of 25 and 26 smallest ZTO units, allocations change from `[7,7,4,3,3,1]` to `[8,8,5,2,2,1]`. Contributors `d` and `e` each lose one unit even though the budget increases. No recipient addresses are invented. These tiny budgets deliberately expose rounding; they imply no reward promise.

For your own saved RewardSplit reports:

```sh
python3 -B line-3/tools/rewardcompare/rewardcompare.py compare \
  --before-request BEFORE_REQUEST.json --before-report BEFORE_REPORT.json \
  --after-request AFTER_REQUEST.json --after-report AFTER_REPORT.json \
  --metadata line-3/tools/rewardsplit/zto-mainnet.json
```

Create each report with RewardSplit's `allocate` command and the same metadata capture. Change only the budget; input order and equivalent weight notation (`"1"` / `"1.0"`) may differ. A changed ID, address, exact weight, missing contributor, changed token block, or tampered report is rejected. Proportional rescaling of all weights is intentionally rejected too: freeze the original weights for this narrowly scoped budget review.

Optional `--output PATH` creates a new workspace JSON file and refuses overwrites. File reads use the inherited workspace-only, duplicate-key-rejecting, 256-KiB JSON reader. Exits: **0** verified comparison without counter-directional changes, **1** verified comparison needing review (a loss with an increased budget, or gain with a decreased budget), **2** invalid input or I/O failure. All negative deltas are listed even when expected from a budget decrease. Unchanged budgets produce zero deltas. Canonical before/after receipts link the supplied requests, reports and metadata by SHA-256.

What happened here: the demo returned exit 1 and flagged exactly `d` and `e`; ten offline tests passed, including 250 seeded comparisons checking conservation and reverse deltas, uint256 precision, roster changes, report tampering, metadata changes, equivalent weights and the warning exit. The file-based CLI also produced the same verified warning, returned 0 for identical inputs, and rejected a tampered report with exit 2.

```sh
python3 -B line-3/tools/rewardcompare/selftest.py
```

This is a comparison of two complete allocations, **not a payment adjustment plan**: a negative delta is not an instruction to recover funds. Review does not establish work quality, recipient ownership, available balance, actual payments or authorization. Hashes are unsigned and the metadata is the inherited single-provider observation, not a fresh chain proof. The tool imports the existing sibling RewardReceipt and RewardSplit sources; keep the line's `tools/` tree together. Nothing accesses keys, signs, sends, pays or makes network requests.
