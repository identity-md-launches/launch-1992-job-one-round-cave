# Optplan

Prove the shortest schedule for a small offline dependency graph. It complements
Workplan's fast greedy plan: Optplan enumerates every non-delay choice at task
completion events, so its result is exact rather than heuristic. Python 3.9+,
standard library only; it never executes task labels, uses a network, or reads
environment variables.

From the repository root:

```sh
python3 -B line-1/tools/optplan/optplan.py --demo --workers 2
```

Observed result: the five-task demonstration finishes at minute **11**, reports
`"proven_optimal": true`, and lists its worker schedule. The same graph needs
15 minutes with one worker.

Use the same `{"tasks": [...]}` JSON shape as Workplan with `--input`. Exact
search accepts at most 14 tasks and integer-minute estimates only; use Workplan
or Replan for larger graphs, fractional estimates, and progress snapshots.
Inputs are limited to an ordinary workspace-local file of 100 KB. The solver
does not promise a real-world deadline: estimates, worker availability, and the
nonpreemptive model remain caller assumptions.

Check it with:

```sh
python3 -B line-1/tools/optplan/optplan.py --self-test
```

The check covers two exact schedules, the single-worker bound, and both explicit
limits. It is a local observation, not a guarantee about supplied estimates.
