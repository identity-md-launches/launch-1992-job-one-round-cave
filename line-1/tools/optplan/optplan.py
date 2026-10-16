#!/usr/bin/env python3
"""Prove the shortest nonpreemptive schedule for a small dependency graph."""
import argparse
import functools
import importlib.util
import itertools
import json
from pathlib import Path
import sys


_spec = importlib.util.spec_from_file_location(
    "pepeolithic_workplan", Path(__file__).resolve().parent.parent / "workplan" / "workplan.py")
_workplan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_workplan)


def exact(data, workers=2):
    """Return an optimum schedule for at most 14 integer-minute tasks.

    The search considers every non-delay choice at each completion event.  With
    interchangeable workers, idling while a ready task and worker both exist is
    dominated, so this finite search contains an optimum.
    """
    _workplan.plan(data, workers)  # Existing strict graph and number validation.
    rows = data["tasks"]
    if len(rows) > 14:
        raise ValueError("exact search is limited to 14 tasks")
    if any(type(row["minutes"]) is not int for row in rows):
        raise ValueError("exact search requires integer minutes")
    names = sorted(row["id"] for row in rows)
    index = {name: i for i, name in enumerate(names)}
    duration = [next(row["minutes"] for row in rows if row["id"] == name) for name in names]
    needs = [sum(1 << index[x] for x in next(row.get("after", []) for row in rows if row["id"] == name))
             for name in names]
    all_done = (1 << len(names)) - 1

    @functools.lru_cache(maxsize=None)
    def solve(done, active):
        # active is sorted (task-index, remaining-minutes), one entry per busy worker.
        if done == all_done and not active:
            return 0, ()
        busy = {task for task, _ in active}
        ready = tuple(i for i in range(len(names))
                      if not (done >> i) & 1 and i not in busy and needs[i] & ~done == 0)
        slots = workers - len(active)
        if slots < 0:
            raise AssertionError("too many active tasks")
        count = min(slots, len(ready))
        # A non-delay schedule must fill every available slot while work is ready.
        choices = itertools.combinations(ready, count) if count else [()]
        best = None
        for chosen in choices:
            started = tuple(sorted(active + tuple((i, duration[i]) for i in chosen)))
            if not started:
                raise ValueError("dependency graph cannot make progress")
            step = min(remaining for _, remaining in started)
            finished = tuple(i for i, remaining in started if remaining == step)
            next_done = done
            next_active = []
            for task, remaining in started:
                if remaining == step:
                    next_done |= 1 << task
                else:
                    next_active.append((task, remaining - step))
            tail, _ = solve(next_done, tuple(next_active))
            candidate = (step + tail, chosen)
            if best is None or candidate < best:
                best = candidate
        return best

    optimum, _ = solve(0, ())
    # Replay the deterministic winning choices to make a useful worker-labelled schedule.
    done, active, now = 0, [], 0
    free = list(range(1, workers + 1))
    schedule = []
    while done != all_done or active:
        state = tuple(sorted((task, finish - now) for task, finish, _ in active))
        _, chosen = solve(done, state)
        for task, worker in zip(chosen, free[:len(chosen)]):
            finish = now + duration[task]
            active.append((task, finish, worker))
            schedule.append({"task": names[task], "worker": worker, "start": now, "finish": finish})
        if not active:
            raise AssertionError("replay stalled")
        now = min(finish for _, finish, _ in active)
        ended = [(task, worker) for task, finish, worker in active if finish == now]
        active = [(task, finish, worker) for task, finish, worker in active if finish != now]
        for task, _ in ended:
            done |= 1 << task
        free = sorted([worker for _, _, worker in active] + [worker for _, worker in ended])
        # Only workers absent from active are free.
        used = {worker for _, _, worker in active}
        free = [worker for worker in range(1, workers + 1) if worker not in used]
    return {"units": "minutes", "workers": workers, "method": "exhaustive non-delay event search",
            "task_limit": 14, "finish": optimum, "schedule": schedule,
            "states_examined": solve.cache_info().currsize, "proven_optimal": True}


def demo():
    return {"tasks": [
        {"id": "brief", "minutes": 2}, {"id": "build-a", "minutes": 5, "after": ["brief"]},
        {"id": "build-b", "minutes": 4, "after": ["brief"]}, {"id": "check", "minutes": 3, "after": ["build-a", "build-b"]},
        {"id": "handoff", "minutes": 1, "after": ["check"]}]}


def self_test():
    result = exact(demo(), 2)
    assert result["finish"] == 11 and result["proven_optimal"]
    assert exact(demo(), 1)["finish"] == 15
    tricky = {"tasks": [{"id": "a", "minutes": 3}, {"id": "b", "minutes": 3},
                         {"id": "c", "minutes": 2}, {"id": "d", "minutes": 2, "after": ["a"]}]}
    assert exact(tricky, 2)["finish"] == 5
    for bad in ({"tasks": [{"id": "a", "minutes": 1.5}]},
                {"tasks": [{"id": str(i), "minutes": 1} for i in range(15)]}):
        try: exact(bad, 2)
        except ValueError: pass
        else: raise AssertionError("invalid exact input accepted")
    print("PASS: optimum demos, worker bound, integer/task limits")


def read_input(filename):
    root, path = Path.cwd().resolve(), Path(filename).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("input must be an ordinary JSON file inside the workspace")
    raw = path.read_bytes()
    if len(raw) > 100000: raise ValueError("input exceeds 100 KB")
    return json.loads(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input"); source.add_argument("--demo", action="store_true"); source.add_argument("--self-test", action="store_true")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    try:
        if args.self_test: self_test(); return 0
        print(json.dumps(exact(demo() if args.demo else read_input(args.input), args.workers), indent=2))
        return 0
    except (ValueError, OSError, RecursionError, OverflowError) as exc:
        print("optplan: " + str(exc), file=sys.stderr); return 1


if __name__ == "__main__": sys.exit(main())
