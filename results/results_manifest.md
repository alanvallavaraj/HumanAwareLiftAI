# Results manifest

| File | Description |
| --- | --- |
| `results/aei_extension/` | Corrected campaign (primary evidence): protocol, per-run outcomes, paired intervals, horizon sensitivity and verification |
| `results/full_controller_means.csv` | Controller means from the 279,936-run historical campaign |
| `results/reviewer_analysis/` | Historical group outcomes, clustered intervals and censoring sensitivity |
| `results/censoring_validation/` | Superseded legacy event-recording campaign, replay-parity records and mismatch diagnosis |
| `results/validation_report.md` | Superseded historical descriptive report retained to prevent accidental reuse of older overclaims |
| `docs/experiment_plan.md` | Bounded experimental design and stopping rule |
| `scripts/run_experiments.py` | Historical experiment runner |
| `scripts/analyse_results.py` | Historical summary-table generator |
| `scripts/validation_analysis.py` | Superseded historical validation generator; not used for the current manuscript claim |

## Historical raw data

| Item | Value |
| --- | --- |
| File | `data/historical-results.csv.gz` (decompressed by `scripts/download_evidence.py`) |
| Rows | 279,936 |
| Uncompressed size | 84 MB |
| Uncompressed SHA-256 | `7654ba08d904362a1f463d9816ed936c83338682571c83b637bb214a37fe740d` |
| Runtime | 2 h 09 min |
