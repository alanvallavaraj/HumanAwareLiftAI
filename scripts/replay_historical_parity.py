"""Replay the 3,888 legacy cases with the archived post-run code snapshot.

Run this with the Python interpreter whose behaviour you want to test, e.g.

  python3.9 scripts/replay_historical_parity.py

The legacy movement rule chooses the nearest target floor with min() over a
Python set. When two target floors are equidistant, the choice depends on set
iteration order, which differs between Python 3.9 and Python 3.11 or later.
This script reports how many replayed cases match the archived historical
outputs under the running interpreter. Compatible with Python 3.9+.
"""
import argparse
import csv
import gzip
import json
import math
import os
import sys
import tarfile
import tempfile
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ("generated", "completed", "mean_wait", "p95_wait", "mean_journey", "failed_pickup_rate",
           "unnecessary_stop_rate", "door_crowding_rate", "special_mean_wait", "general_mean_wait",
           "energy_proxy", "utilisation_imbalance", "fairness_disparity", "stability_risk",
           "jerk_exposure", "adaptive_slowdowns", "guidance_events", "score")


def key(r):
    return (r["controller"], int(r["seed"]), int(r["floors"]), int(r["lifts"]), int(r["population"]),
            r["traffic"], round(float(r["special_share"]), 6), round(float(r["carrying_share"]), 6),
            round(float(r["sensor_noise"]), 6))


def init(snapshot):
    sys.path.insert(0, snapshot)


def run(row):
    from dataclasses import asdict
    from simulator import Scenario, simulate
    s = Scenario(int(row["floors"]), int(row["lifts"]), int(row["population"]), row["traffic"],
                 float(row["special_share"]), float(row["carrying_share"]), float(row["sensor_noise"]))
    return key(row), asdict(simulate(s, row["controller"], int(row["seed"])))


def same(a, b):
    a, b = float(a), float(b)
    if math.isnan(a) and math.isnan(b):
        return True
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--historical", default=str(ROOT / "data/historical-results.csv.gz"))
    p.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    p.add_argument("--out", default=None)
    a = p.parse_args()
    version = "%d.%d.%d" % sys.version_info[:3]
    out = Path(a.out or ROOT / ("results/censoring_validation/replay_parity_python%d%d.json" % sys.version_info[:2]))

    replay = [r for r in csv.DictReader((ROOT / "results/censoring_validation/results.csv").open())
              if r["controller"] != "distance_only_nearest"]
    wanted = {key(r) for r in replay}
    archived = {}
    with gzip.open(a.historical, "rt", newline="") as stream:
        for r in csv.DictReader(stream):
            k = key(r)
            if k in wanted:
                archived[k] = r

    snapshot = tempfile.mkdtemp(prefix="lift-snapshot-")
    with tarfile.open(ROOT / "data/historical-code-snapshot.tar.gz") as t:
        for m in t.getmembers():
            if m.isfile() and m.name.endswith(".py") and "/" not in m.name.strip("./"):
                t.extract(m, snapshot)
    snapshot_py = os.path.join(snapshot, "simulator.py")
    if not os.path.exists(snapshot_py):
        raise SystemExit("simulator.py not found in snapshot archive")

    with Pool(a.workers, initializer=init, initargs=(snapshot,)) as pool:
        results = pool.map(run, replay, chunksize=8)

    matched = 0
    differing = []
    for k, metrics in results:
        arch = archived[k]
        bad = [m for m in METRICS if not same(metrics[m], arch[m])]
        if bad:
            differing.append({"key": list(k), "metrics": bad})
        else:
            matched += 1
    report = {"python": version, "replayed": len(results), "matching_archive": matched,
              "not_matching_archive": len(differing), "metrics_compared": list(METRICS),
              "tolerance": "relative and absolute 1e-12", "differences": differing[:50]}
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "differences"}, indent=2))


if __name__ == "__main__":
    main()
