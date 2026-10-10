import csv
import math
import argparse
from collections import defaultdict
from pathlib import Path


DEFAULT_RESDIR = Path("results_full")
METRICS = [
    "mean_wait",
    "p95_wait",
    "failed_pickup_rate",
    "door_crowding_rate",
    "special_mean_wait",
    "jerk_exposure",
    "score",
]
CONTROLLERS = [
    "collective",
    "occupancy_aware",
    "access_priority",
    "stability_aware",
    "layered_access_stability",
    "human_aware",
    "oracle_upper",
]
LABELS = {
    "collective": "classical baseline",
    "occupancy_aware": "capacity sensing only",
    "access_priority": "accessibility-aware dispatch",
    "stability_aware": "synthetic stability exposure accounting",
    "layered_access_stability": "accessibility and stability rule configuration",
    "human_aware": "monolithic combined controller",
    "oracle_upper": "oracle-labelled reference, not a proven bound",
}


def building_class(row):
    floors = int(row["floors"])
    population = int(row["population"])
    lifts = int(row["lifts"])
    if floors <= 8 and population <= 200:
        return "small"
    if floors >= 32 or population >= 2000 or lifts >= 8:
        return "large"
    return "medium"


def grouped_mean(rows, keys):
    sums = defaultdict(lambda: {metric: 0.0 for metric in METRICS})
    counts = defaultdict(lambda: {metric: 0 for metric in METRICS})
    row_counts = defaultdict(int)
    for row in rows:
        key = tuple(row[k] for k in keys)
        row_counts[key] += 1
        for metric in METRICS:
            value = float(row[metric])
            if math.isfinite(value):
                sums[key][metric] += value
                counts[key][metric] += 1
    means = {}
    for key, values in sums.items():
        means[key] = {
            metric: values[metric] / counts[key][metric] if counts[key][metric] else float("nan")
            for metric in METRICS
        }
        means[key]["runs"] = row_counts[key]
    return means


def pct_better(base, current, metric):
    return (base[metric] - current[metric]) / base[metric] * 100.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default=str(DEFAULT_RESDIR))
    args = parser.parse_args()
    resdir = Path(args.results_dir)

    with (resdir / "results.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        row["building_class"] = building_class(row)

    out = [
        "# Extra Validation Report",
        "",
        f"Dataset: `{resdir}/results.csv`",
        f"Total simulated building-days: {len(rows):,}",
        f"Controllers analysed: {len(set(row['controller'] for row in rows))}",
        "",
    ]

    by_controller = grouped_mean(rows, ["controller"])
    ordered = sorted(CONTROLLERS, key=lambda c: by_controller[(c,)]["score"])
    out.extend(
        [
            "## 1. Ablation / Module Contribution",
            "",
            "| controller | interpretation | mean_wait | door_crowding_rate | special_mean_wait | jerk_exposure | score |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for controller in ordered:
        row = by_controller[(controller,)]
        out.append(
            f"| {controller} | {LABELS[controller]} | {row['mean_wait']:.3f} | "
            f"{row['door_crowding_rate']:.4f} | {row['special_mean_wait']:.3f} | "
            f"{row['jerk_exposure']:.3f} | {row['score']:.3f} |"
        )

    base = by_controller[("collective",)]
    out.extend(
        [
            "",
            "### Improvements vs collective baseline",
            "",
            "| controller | mean_wait | door_crowding | special_wait | jerk_exposure | score |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for controller in [
        "occupancy_aware",
        "access_priority",
        "stability_aware",
        "layered_access_stability",
        "human_aware",
    ]:
        row = by_controller[(controller,)]
        out.append(
            f"| {controller} | {pct_better(base, row, 'mean_wait'):.2f}% | "
            f"{pct_better(base, row, 'door_crowding_rate'):.2f}% | "
            f"{pct_better(base, row, 'special_mean_wait'):.2f}% | "
            f"{pct_better(base, row, 'jerk_exposure'):.2f}% | "
            f"{pct_better(base, row, 'score'):.2f}% |"
        )
    out.extend(
        [
            "",
            "Interpretation: accessibility dispatch is the dominant scheduling contribution; "
            "stability control is the dominant comfort contribution. The layered controller "
            "preserves the accessibility benefit while reducing jerk exposure.",
            "",
            "## 2. Sensor-Noise Robustness",
            "",
            "| noise | controller | mean_wait | door_crowding_rate | special_mean_wait | jerk_exposure | score |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    by_noise = grouped_mean(rows, ["sensor_noise", "controller"])
    noise_levels = sorted(set(row["sensor_noise"] for row in rows), key=float)
    for noise in noise_levels:
        for controller in [
            "collective",
            "access_priority",
            "layered_access_stability",
            "human_aware",
            "stability_aware",
        ]:
            row = by_noise[(noise, controller)]
            out.append(
                f"| {float(noise):.2f} | {controller} | {row['mean_wait']:.3f} | "
                f"{row['door_crowding_rate']:.4f} | {row['special_mean_wait']:.3f} | "
                f"{row['jerk_exposure']:.3f} | {row['score']:.3f} |"
            )

    out.extend(
        [
            "",
            "### Robustness deltas from noise 0.00 to 0.18",
            "",
            "| controller | score_change_% | mean_wait_change_% | jerk_change_% |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for controller in [
        "access_priority",
        "layered_access_stability",
        "human_aware",
        "stability_aware",
    ]:
        low = by_noise[("0.0", controller)]
        high = by_noise[("0.18", controller)]
        out.append(
            f"| {controller} | {(high['score'] - low['score']) / low['score'] * 100:.2f}% | "
            f"{(high['mean_wait'] - low['mean_wait']) / low['mean_wait'] * 100:.2f}% | "
            f"{(high['jerk_exposure'] - low['jerk_exposure']) / low['jerk_exposure'] * 100:.2f}% |"
        )

    out.extend(
        [
            "",
            "## 3. Building / Population Scaling",
            "",
            "| building_class | controller | mean_wait | door_crowding_rate | special_mean_wait | jerk_exposure | score |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    by_scale = grouped_mean(rows, ["building_class", "controller"])
    for klass in ["small", "medium", "large"]:
        for controller in [
            "collective",
            "access_priority",
            "layered_access_stability",
            "human_aware",
            "stability_aware",
        ]:
            row = by_scale[(klass, controller)]
            out.append(
                f"| {klass} | {controller} | {row['mean_wait']:.3f} | "
                f"{row['door_crowding_rate']:.4f} | {row['special_mean_wait']:.3f} | "
                f"{row['jerk_exposure']:.3f} | {row['score']:.3f} |"
            )

    out.extend(
        [
            "",
            "### Layered controller improvement vs collective by building class",
            "",
            "| building_class | mean_wait | door_crowding | special_wait | jerk_exposure | score |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for klass in ["small", "medium", "large"]:
        base = by_scale[(klass, "collective")]
        row = by_scale[(klass, "layered_access_stability")]
        out.append(
            f"| {klass} | {pct_better(base, row, 'mean_wait'):.2f}% | "
            f"{pct_better(base, row, 'door_crowding_rate'):.2f}% | "
            f"{pct_better(base, row, 'special_mean_wait'):.2f}% | "
            f"{pct_better(base, row, 'jerk_exposure'):.2f}% | "
            f"{pct_better(base, row, 'score'):.2f}% |"
        )

    out.extend(["", "## Interpretation boundaries", "", "These are descriptive reanalyses of existing runs, not independent validation. The stability factor changes comfort accounting but not movement timing. Noise perturbs the synthetic stability signal only. Configurations differ in multiple rules, so comparisons are not clean causal ablations. Completion fractions and matched scenario uncertainty should accompany wait comparisons. See paper/manuscript.pdf and results/reproduction_check.json."])

    report = "\n".join(out) + "\n"
    report_path = resdir / "validation_report.md"
    report_path.write_text(report)
    print(report_path)
    print(report)


if __name__ == "__main__":
    main()

