"""Characterise the historical replay discrepancies (Appendix B).

Compares the three legacy configurations replayed in the event-recording
campaign (results/censoring_validation/results.csv) with their archived
counterparts in the historical campaign (data/historical-results.csv.gz), and
reports where the 783 recorded mismatches fall and how
large they are. No simulation is run.

Usage:
  python scripts/diagnose_replay_mismatches.py
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY_FIELDS = ("controller", "seed", "floors", "lifts", "population", "traffic",
              "special_share", "carrying_share", "sensor_noise")
METRICS = ("generated", "completed", "mean_wait", "p95_wait", "special_mean_wait",
           "general_mean_wait", "mean_journey", "failed_pickup_rate",
           "unnecessary_stop_rate", "door_crowding_rate")
FACTORS = ("controller", "floors", "lifts", "population", "traffic", "special_share", "seed")


def key(row: dict) -> tuple:
    return (row["controller"], int(row["seed"]), int(row["floors"]), int(row["lifts"]),
            int(row["population"]), row["traffic"], round(float(row["special_share"]), 6),
            round(float(row["carrying_share"]), 6), round(float(row["sensor_noise"]), 6))


def value(text: str) -> float:
    try:
        return float(text)
    except ValueError:
        return math.nan


def same(a: float, b: float) -> bool:
    if math.isnan(a) and math.isnan(b):
        return True
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--historical", default=str(ROOT / "data/historical-results.csv.gz"))
    parser.add_argument("--out", default=str(ROOT / "results/censoring_validation/replay_mismatch_diagnosis.json"))
    args = parser.parse_args()

    replay = [r for r in csv.DictReader((ROOT / "results/censoring_validation/results.csv").open())
              if r["controller"] != "distance_only_nearest"]
    wanted = {key(r) for r in replay}
    archived = {}
    with gzip.open(args.historical, "rt", newline="") as stream:
        for row in csv.DictReader(stream):
            k = key(row)
            if k in wanted:
                archived[k] = row
    missing = wanted - set(archived)
    if missing:
        raise SystemExit(f"{len(missing)} replayed cases have no archived counterpart")

    recorded = {(int(d["case_index"]), d["controller"], int(d["seed"]))
                for d in json.loads((ROOT / "results/censoring_validation/archived_parity_differences.json").read_text())}

    cases = []
    for r in replay:
        a = archived[key(r)]
        diffs = {}
        for m in METRICS:
            x, y = value(r[m]), value(a[m])
            if not same(x, y):
                diffs[m] = {"replay": x, "archived": y, "difference": x - y,
                            "relative": (x - y) / y if y not in (0.0,) and not math.isnan(y) else math.nan}
        cases.append({"case_index": int(r["case_index"]), **{f: r[f] for f in FACTORS},
                      "mismatch": bool(diffs), "diffs": diffs})

    found = {(c["case_index"], c["controller"], int(c["seed"])) for c in cases if c["mismatch"]}
    by_factor = {}
    for f in FACTORS:
        total, bad = Counter(), Counter()
        for c in cases:
            total[c[f]] += 1
            bad[c[f]] += c["mismatch"]
        by_factor[f] = {str(level): {"cases": total[level], "mismatches": bad[level],
                                     "rate": bad[level] / total[level]} for level in sorted(total, key=str)}

    metric_counts = Counter(m for c in cases for m in c["diffs"])
    magnitudes = defaultdict(list)
    for c in cases:
        for m, d in c["diffs"].items():
            magnitudes[m].append(abs(d["difference"]))
    summary_magnitude = {}
    for m, values in magnitudes.items():
        values.sort()
        summary_magnitude[m] = {"n": len(values), "median_abs_difference": values[len(values) // 2],
                                "max_abs_difference": values[-1]}
    count_changed = sum(1 for c in cases if "generated" in c["diffs"])
    completed_changed = sum(1 for c in cases if "completed" in c["diffs"])

    # Does a mismatch in one controller co-occur with mismatches in the others
    # for the same scenario and seed (a shared arrival or movement difference),
    # or is it controller-specific (a decision-rule or random-stream difference)?
    per_block = defaultdict(set)
    for c in cases:
        if c["mismatch"]:
            per_block[(c["case_index"], c["seed"])].add(c["controller"])
    block_pattern = Counter(len(v) for v in per_block.values())

    # Mean signed difference in mean_wait by controller, to see whether the
    # discrepancy favours any configuration.
    signed = defaultdict(list)
    for c in cases:
        d = c["diffs"].get("mean_wait")
        signed[c["controller"]].append(d["difference"] if d else 0.0)
    signed_mean = {k: sum(v) / len(v) for k, v in signed.items()}

    report = {
        "replayed_cases": len(cases),
        "mismatched_cases": len(found),
        "matches_recorded_list": found == recorded,
        "generated_count_changed": count_changed,
        "completed_count_changed": completed_changed,
        "metrics_differing": dict(metric_counts.most_common()),
        "magnitude": summary_magnitude,
        "controllers_mismatched_per_scenario_seed": {str(k): v for k, v in sorted(block_pattern.items())},
        "mean_signed_mean_wait_difference_by_controller": signed_mean,
        "by_factor": by_factor,
    }
    out = Path(args.out)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "by_factor"}, indent=2))
    for f in FACTORS:
        print(f, {k: round(v["rate"], 3) for k, v in by_factor[f].items()})


if __name__ == "__main__":
    main()
