"""Reanalyse event records at alternative restricted-wait horizons.

This script requires the event-recorded campaign outputs, including
results/censoring_validation/results.csv and the compressed per-case
passenger files under results/censoring_validation/passengers/.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

HORIZONS = (600, 900, 1200)
GROUPS = ("all", "priority", "general")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default="results/censoring_validation")
    parser.add_argument("--out", default="results/censoring_validation/restricted_horizon_sensitivity.csv")
    args = parser.parse_args()

    root = Path(args.directory)
    with (root / "results.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 5184:
        raise SystemExit(f"Expected 5,184 rows, found {len(rows)}")

    paired = defaultdict(set)
    metrics = [f"{group}_restricted_wait_{horizon}" for horizon in HORIZONS for group in GROUPS]
    blocks = {}

    for row in rows:
        case_index = int(row["case_index"])
        seed = row["seed"]
        controller = row["controller"]
        paired[(case_index, seed)].add(row["arrival_sha256"])

        event_file = root / "passengers" / f"{case_index:05d}-{controller}-{seed}.csv.gz"
        sums = {metric: 0.0 for metric in metrics}
        counts = {metric: 0 for metric in metrics}

        with gzip.open(event_file, "rt", newline="") as f:
            for passenger in csv.DictReader(f):
                group = "priority" if passenger["priority_requested"] == "1" else "general"
                wait = float(passenger["observed_wait"])
                for horizon in HORIZONS:
                    capped = min(wait, horizon)
                    for metric_group in ("all", group):
                        metric = f"{metric_group}_restricted_wait_{horizon}"
                        sums[metric] += capped
                        counts[metric] += 1

        z = blocks.setdefault((case_index, controller), np.zeros((len(metrics), 2)))
        for i, metric in enumerate(metrics):
            if counts[metric]:
                z[i] += [sums[metric] / counts[metric], 1]

    if len(paired) != 1296 or any(len(v) != 1 for v in paired.values()):
        raise SystemExit("Arrival cohorts are not matched across controllers.")

    controllers = sorted({row["controller"] for row in rows})
    weights = np.random.default_rng(20261008).multinomial(108, np.full(108, 1 / 108), size=2000)
    estimates = {}
    boot = {}

    for controller in controllers:
        mat = np.array([blocks[(case_index, controller)] for case_index in range(108)])
        summed = mat.sum(axis=0)
        estimates[controller] = {
            metric: float(summed[i, 0] / summed[i, 1])
            for i, metric in enumerate(metrics)
        }
        boot_summed = np.einsum("bk,kmn->bmn", weights, mat)
        boot[controller] = boot_summed[:, :, 0] / boot_summed[:, :, 1]

    output_rows = []
    for horizon in HORIZONS:
        for group in GROUPS:
            metric = f"{group}_restricted_wait_{horizon}"
            i = metrics.index(metric)
            diff_samples = boot["access_priority"][:, i] - boot["collective"][:, i]
            lo, hi = np.quantile(diff_samples, [0.025, 0.975])
            output_rows.append({
                "horizon": horizon,
                "metric": group,
                "priority_rule": estimates["access_priority"][metric],
                "direction_aware_reference": estimates["collective"][metric],
                "difference": estimates["access_priority"][metric] - estimates["collective"][metric],
                "ci_low": float(lo),
                "ci_high": float(hi),
            })

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    out_path.with_suffix(".json").write_text(json.dumps({
        "runs": len(rows),
        "matched_arrival_blocks": len(paired),
        "bootstrap_replicates": 2000,
        "bootstrap_seed": 20261008,
        "contrasts": output_rows,
    }, indent=2) + "\n")
    print(json.dumps(output_rows, indent=2))


if __name__ == "__main__":
    main()
