from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product
import os
from pathlib import Path
from time import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from simulator import Scenario, simulate


CONTROLLERS = [
    "collective",
    "nearest_car",
    "occupancy_aware",
    "access_priority",
    "stability_aware",
    "human_aware",
    "layered_access_stability",
    "oracle_upper",
]


def tier_grid(tier: str):
    if tier == "smoke":
        return {
            "floors": [8],
            "lifts": [2],
            "population": [200],
            "traffic": ["up_peak", "mixed"],
            "special_share": [0.08],
            "carrying_share": [0.20],
            "sensor_noise": [0.05],
            "controllers": ["collective", "occupancy_aware", "human_aware"],
            "seeds": list(range(2)),
            "duration": 900,
        }
    if tier == "pilot":
        return {
            "floors": [8, 16],
            "lifts": [2, 4],
            "population": [200, 800],
            "traffic": ["up_peak", "down_peak", "lunch", "mixed"],
            "special_share": [0.02, 0.08],
            "carrying_share": [0.05, 0.20],
            "sensor_noise": [0.05, 0.15],
            "controllers": CONTROLLERS[:-1],
            "seeds": list(range(5)),
            "duration": 1800,
        }
    if tier == "full_reduced":
        grid = tier_grid("full")
        grid["seeds"] = list(range(6))
        return grid
    if tier == "layered_followup":
        grid = tier_grid("full_reduced")
        grid["controllers"] = ["layered_access_stability"]
        return grid
    if tier == "full":
        return {
            "floors": [8, 16, 32],
            "lifts": [2, 4, 8],
            "population": [200, 800, 2000],
            "traffic": ["up_peak", "down_peak", "lunch", "mixed"],
            "special_share": [0.02, 0.08, 0.15],
            "carrying_share": [0.05, 0.20, 0.40],
            "sensor_noise": [0.00, 0.08, 0.18],
            "controllers": CONTROLLERS,
            "seeds": list(range(12)),
            "duration": 3600,
        }
    if tier == "access_sensitivity":
        return {
            "floors": [16],
            "lifts": [4],
            "population": [800, 2000],
            "traffic": ["up_peak", "mixed"],
            "special_share": [0.08, 0.15],
            "carrying_share": [0.20],
            "sensor_noise": [0.08],
            "controllers": ["access_priority", "human_aware"],
            "seeds": list(range(8)),
            "duration": 3600,
        }
    if tier == "high_instability":
        return {
            "floors": [16, 32],
            "lifts": [4, 8],
            "population": [800, 2000],
            "traffic": ["up_peak", "mixed"],
            "special_share": [0.08],
            "carrying_share": [0.40],
            "sensor_noise": [0.18],
            "controllers": ["collective", "stability_aware", "human_aware"],
            "seeds": list(range(8)),
            "duration": 3600,
        }
    raise ValueError(f"Unknown tier: {tier}")


def iter_jobs(tier: str):
    g = tier_grid(tier)
    for floors, lifts, population, traffic, special, carrying, noise, controller, seed in product(
        g["floors"],
        g["lifts"],
        g["population"],
        g["traffic"],
        g["special_share"],
        g["carrying_share"],
        g["sensor_noise"],
        g["controllers"],
        g["seeds"],
    ):
        if lifts > floors:
            continue
        scenario = Scenario(
            floors=floors,
            lifts=lifts,
            population=population,
            traffic=traffic,
            special_share=special,
            carrying_share=carrying,
            sensor_noise=noise,
            duration=g["duration"],
        )
        yield scenario, controller, seed


def run_job(payload):
    tier, scenario, controller, seed = payload
    metrics = simulate(scenario, controller, seed)
    row = {
        "tier": tier,
        "seed": seed,
        "controller": controller,
        "floors": scenario.floors,
        "lifts": scenario.lifts,
        "population": scenario.population,
        "traffic": scenario.traffic,
        "special_share": scenario.special_share,
        "carrying_share": scenario.carrying_share,
        "sensor_noise": scenario.sensor_noise,
    }
    row.update(asdict(metrics))
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", default="smoke", choices=["smoke", "pilot", "full", "full_reduced", "layered_followup", "access_sensitivity", "high_instability"])
    parser.add_argument("--out", default="results")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=max(1, min(8, os.cpu_count() or 1)))
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    result_file = out / "results.csv"
    jobs = list(iter_jobs(args.tier))
    if args.limit:
        jobs = jobs[: args.limit]

    fieldnames = [
        "tier",
        "seed",
        "controller",
        "floors",
        "lifts",
        "population",
        "traffic",
        "special_share",
        "carrying_share",
        "sensor_noise",
        "completed",
        "generated",
        "mean_wait",
        "p95_wait",
        "mean_journey",
        "failed_pickup_rate",
        "unnecessary_stop_rate",
        "door_crowding_rate",
        "energy_proxy",
        "utilisation_imbalance",
        "special_mean_wait",
        "general_mean_wait",
        "fairness_disparity",
        "stability_risk",
        "jerk_exposure",
        "adaptive_slowdowns",
        "guidance_events",
        "score",
    ]

    started = time()
    with result_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        payloads = [(args.tier, scenario, controller, seed) for scenario, controller, seed in jobs]
        if args.workers == 1:
            for i, payload in enumerate(payloads, start=1):
                writer.writerow(run_job(payload))
                if i % 100 == 0:
                    elapsed = time() - started
                    print(f"{i}/{len(jobs)} runs complete in {elapsed:.1f}s", flush=True)
        else:
            completed = 0
            with ProcessPoolExecutor(max_workers=args.workers) as pool:
                futures = [pool.submit(run_job, payload) for payload in payloads]
                for future in as_completed(futures):
                    writer.writerow(future.result())
                    completed += 1
                    if completed % 100 == 0:
                        elapsed = time() - started
                        print(f"{completed}/{len(jobs)} runs complete in {elapsed:.1f}s using {args.workers} workers", flush=True)

    print(f"Wrote {len(jobs)} runs to {result_file}")


if __name__ == "__main__":
    main()

