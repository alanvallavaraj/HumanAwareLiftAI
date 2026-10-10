"""Restricted-wait horizon sensitivity for the corrected model.

Reads the checksum-verified passenger-event archive directly from
data/aei-extension-event-parts (no extraction to disk) and recomputes
run-level restricted waits at several horizons.

Horizons of 300, 600 and 900 units are fully observed for every arrival:
arrivals end at 3,599 and observation ends at 4,500. A 1,200-unit horizon is
fully observed only for arrivals with at least 1,200 units of follow-up, so it
is reported on that subset and labelled accordingly.

The bootstrap reproduces scripts/analyse_aei_extension.py exactly (108
scenario blocks with all twelve seeds, 2,000 multinomial draws, seed
20261008), and every 900-unit contrast is checked against
results/aei_extension/paired_intervals.csv before results are written.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import tarfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results/aei_extension"
GROUPS = ("all", "priority", "general")
FULL = (300, 600, 900)
FOLLOWUP = 1200
CONFIGS = ("occupancy_reference", "full_priority", "collective",
           "dwell_occupancy_reference", "dwell_full_priority", "dwell_collective")
CONTRASTS = (
    ("zero dwell", "full_priority", "occupancy_reference", "ablation_or_weight", "full_priority vs occupancy_reference"),
    ("zero dwell", "full_priority", "collective", "reference_comparison", "full_priority vs collective"),
    ("dwell", "dwell_full_priority", "dwell_occupancy_reference", "dwell_priority_effect", "dwell full_priority vs occupancy_reference"),
    ("dwell", "dwell_full_priority", "dwell_collective", "dwell_priority_effect", "dwell full_priority vs collective"),
)
HORIZON_LABELS = [str(h) for h in FULL] + [f"{FOLLOWUP} (arrivals with >= {FOLLOWUP} follow-up)"]
METRICS = [f"{g}_{h}" for h in [*FULL, FOLLOWUP] for g in GROUPS]


def load_archive() -> bytes:
    manifest = json.loads((OUT_DIR / "archive_manifest.json").read_text())
    data = b"".join(p.read_bytes() for p in sorted((ROOT / "data/aei-extension-event-parts").glob("part-*")))
    if hashlib.sha256(data).hexdigest() != manifest["sha256"]:
        raise SystemExit("Event archive checksum mismatch")
    return data


def run_means(stream) -> tuple[dict, dict]:
    reader = csv.reader(io.TextIOWrapper(stream, encoding="utf-8", newline=""))
    header = next(reader)
    ia, ib, io_, ip = (header.index(c) for c in ("arrival_time", "boarded_time", "observation_end", "priority_requested"))
    sums = {m: 0.0 for m in METRICS}
    counts = {m: 0 for m in METRICS}
    followup = {"all": [0, 0]}
    for q in reader:
        at = int(q[ia])
        end = int(q[io_])
        w = (int(q[ib]) if q[ib] else end) - at
        group = "priority" if q[ip] == "1" else "general"
        long_followup = end - at >= FOLLOWUP
        followup["all"][0] += long_followup
        followup["all"][1] += 1
        for g in ("all", group):
            for h in FULL:
                sums[f"{g}_{h}"] += min(w, h)
                counts[f"{g}_{h}"] += 1
            if long_followup:
                sums[f"{g}_{FOLLOWUP}"] += min(w, FOLLOWUP)
                counts[f"{g}_{FOLLOWUP}"] += 1
    means = {m: (sums[m] / counts[m] if counts[m] else math.nan) for m in METRICS}
    return means, followup


def main() -> None:
    rows = {}
    with (OUT_DIR / "results.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r["configuration"] in CONFIGS:
                rows[(int(r["case_index"]), r["configuration"], int(r["seed"]))] = r

    blocks: dict = {}
    seen = 0
    followup_total = [0, 0]
    with tarfile.open(fileobj=io.BytesIO(load_archive()), mode="r:xz") as archive:
        for member in archive:
            name = Path(member.name).stem  # e.g. 017-full_priority-03
            case, *middle, seed = name.split("-")
            config = "-".join(middle)
            if config not in CONFIGS:
                continue
            means, followup = run_means(archive.extractfile(member))
            k = (int(case), config, int(seed))
            reference = rows[k]
            for g in GROUPS:
                stored = float(reference[f"{g}_restricted_wait_900"])
                if not (math.isnan(stored) and math.isnan(means[f"{g}_900"])):
                    assert math.isclose(stored, means[f"{g}_900"], rel_tol=1e-12, abs_tol=1e-12), (k, g)
            followup_total[0] += followup["all"][0]
            followup_total[1] += followup["all"][1]
            mat = blocks.setdefault((int(case), config), np.zeros((len(METRICS), 2)))
            for i, m in enumerate(METRICS):
                if math.isfinite(means[m]):
                    mat[i] += [means[m], 1]
            seen += 1
    if seen != len(CONFIGS) * 1296:
        raise SystemExit(f"Expected {len(CONFIGS) * 1296} event files, read {seen}")

    keys = sorted({c for c, _ in blocks})
    K = len(keys)
    weights = np.random.default_rng(20261008).multinomial(K, np.full(K, 1 / K), size=2000)
    means, samples = {}, {}
    for config in CONFIGS:
        mat = np.array([blocks[k, config] for k in keys])
        z = mat.sum(axis=0)
        boot = np.einsum("bk,kmn->bmn", weights, mat)
        means[config] = z[:, 0] / z[:, 1]
        samples[config] = boot[:, :, 0] / boot[:, :, 1]

    published = {(r["contrast"], r["metric"]): r for r in csv.DictReader((OUT_DIR / "paired_intervals.csv").open())}
    output = []
    for dwell, a, b, _family, label in CONTRASTS:
        diff = means[a] - means[b]
        lo, hi = np.quantile(samples[a] - samples[b], [0.025, 0.975], axis=0)
        for i, m in enumerate(METRICS):
            group, horizon = m.rsplit("_", 1)
            if horizon == "900":
                ref = published[(label, f"{group}_restricted_wait_900")]
                for x, y in ((diff[i], ref["difference"]), (lo[i], ref["ci_low"]), (hi[i], ref["ci_high"])):
                    assert math.isclose(x, float(y), rel_tol=1e-9, abs_tol=1e-9), (label, m, x, y)
            output.append({
                "dwell": dwell,
                "contrast": f"{a} vs {b}",
                "horizon": horizon if int(horizon) in FULL else HORIZON_LABELS[-1],
                "group": group,
                "treatment_mean": float(means[a][i]),
                "reference_mean": float(means[b][i]),
                "difference": float(diff[i]),
                "ci_low": float(lo[i]),
                "ci_high": float(hi[i]),
            })

    with (OUT_DIR / "horizon_sensitivity.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(output[0]))
        w.writeheader()
        w.writerows(output)
    report = {
        "event_files_read": seen,
        "configurations": list(CONFIGS),
        "horizons_fully_observed_for_all_arrivals": list(FULL),
        "followup_horizon": FOLLOWUP,
        "share_of_arrivals_with_followup_horizon": followup_total[0] / followup_total[1],
        "bootstrap": "108 scenario blocks, all twelve seeds jointly, 2,000 multinomial draws, seed 20261008, percentile 95% intervals",
        "check": "Every 900-unit run mean matched results.csv to 1e-12, and every 900-unit contrast matched paired_intervals.csv to 1e-9.",
        "contrasts": output,
    }
    (OUT_DIR / "horizon_sensitivity.json").write_text(json.dumps(report, indent=2) + "\n")
    for r in output:
        print(f"{r['contrast']:<52} {r['horizon']:<40} {r['group']:<9} {r['difference']:9.2f} [{r['ci_low']:8.2f}, {r['ci_high']:8.2f}]")
    print("share with >=1200 follow-up:", round(report["share_of_arrivals_with_followup_horizon"], 4))


if __name__ == "__main__":
    main()
