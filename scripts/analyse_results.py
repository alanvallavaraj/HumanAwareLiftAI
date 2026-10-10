from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


LOWER_IS_BETTER = [
    "mean_wait",
    "p95_wait",
    "mean_journey",
    "failed_pickup_rate",
    "unnecessary_stop_rate",
    "door_crowding_rate",
    "energy_proxy",
    "utilisation_imbalance",
    "special_mean_wait",
    "fairness_disparity",
    "stability_risk",
    "jerk_exposure",
    "score",
]


def read_rows(path: Path):
    with path.open() as f:
        for row in csv.DictReader(f):
            out = {}
            for k, v in row.items():
                if k in {"tier", "controller", "traffic"}:
                    out[k] = v
                elif k:
                    try:
                        out[k] = float(v)
                    except ValueError:
                        out[k] = v
            yield out


def group_summary(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["controller"]].append(row)
    summary = {}
    for controller, items in grouped.items():
        summary[controller] = {metric: mean([r[metric] for r in items if r[metric] == r[metric]]) for metric in LOWER_IS_BETTER}
        summary[controller]["runs"] = len(items)
    return summary


def pairwise_win_rates(rows, reference="human_aware"):
    by_case = defaultdict(dict)
    case_keys = ["seed", "floors", "lifts", "population", "traffic", "special_share", "carrying_share", "sensor_noise"]
    for row in rows:
        key = tuple(row[k] for k in case_keys)
        by_case[key][row["controller"]] = row
    wins = defaultdict(lambda: defaultdict(int))
    totals = defaultdict(int)
    for controllers in by_case.values():
        if reference not in controllers:
            continue
        ref = controllers[reference]
        for other, row in controllers.items():
            if other == reference:
                continue
            totals[other] += 1
            for metric in LOWER_IS_BETTER:
                if ref[metric] == ref[metric] and row[metric] == row[metric] and ref[metric] < row[metric]:
                    wins[other][metric] += 1
    rates = {}
    for other, total in totals.items():
        rates[other] = {metric: wins[other][metric] / total for metric in LOWER_IS_BETTER}
        rates[other]["matched_cases"] = total
    return rates


def write_markdown(summary, wins, out: Path):
    lines = []
    lines.append("# Experiment Results Summary\n")
    lines.append("## Controller Means\n")
    header = ["controller", "runs"] + LOWER_IS_BETTER
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    for controller, metrics in sorted(summary.items(), key=lambda kv: kv[1]["score"]):
        row = [controller, str(metrics["runs"])] + [f"{metrics[m]:.4f}" for m in LOWER_IS_BETTER]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("\n## Human-Aware Pairwise Win Rates\n")
    lines.append("| baseline | matched_cases | " + " | ".join(LOWER_IS_BETTER) + " |")
    lines.append("| --- | --- | " + " | ".join(["---"] * len(LOWER_IS_BETTER)) + " |")
    for baseline, metrics in sorted(wins.items()):
        row = [baseline, str(metrics["matched_cases"])] + [f"{metrics[m]:.3f}" for m in LOWER_IS_BETTER]
        lines.append("| " + " | ".join(row) + " |")
    out.joinpath("summary.md").write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True)
    parser.add_argument("--out", default="results")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = list(read_rows(Path(args.results)))
    summary = group_summary(rows)
    wins = pairwise_win_rates(rows)
    write_markdown(summary, wins, out)
    print(out.joinpath("summary.md"))


if __name__ == "__main__":
    main()


