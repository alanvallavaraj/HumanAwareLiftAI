# Supplementary experiment records

The main manuscript contains a compact history table (Table A.1). The historical narrative dump has been removed from the typeset appendix because it contained superseded interpretations.

- Historical full CSV and code snapshot: `data/historical-results.csv.gz` and `data/historical-code-snapshot.tar.gz`.
- Historical controller means and group outcomes: `results/reviewer_analysis/controller_outcomes.csv`.
- Historical paired scenario intervals: `results/reviewer_analysis/paired_cluster_intervals.csv`.
- Partial-identification sensitivity: `results/reviewer_analysis/censoring_sensitivity.csv`; assumptions are not recovered passenger data.
- Event-recorded campaign: `results/censoring_validation/results.csv` and compressed per-case files under `passengers/`.
- Restricted-wait outcomes and intervals: `restricted_outcomes.csv` and `restricted_cluster_intervals.csv`.
- Restricted-horizon sensitivity: `restricted_horizon_sensitivity.csv` and `.json`, checking 600, 900 and 1,200 model time units.
- Event verification and cohort pairing: `verification.json`.
- Historical replay discrepancies: `archived_parity_differences.json` (783 of 3,888 comparisons).
- Event-file recovery: `event_recovery.json`; one replay, every aggregate unchanged.

The recorded campaign supports priority-group service benefits with costs to the general group. The restricted-horizon sensitivity preserves this conclusion at 600, 900 and 1,200 units. It does not establish overall superiority, physical ride-comfort improvement, sensing robustness or interface effectiveness. Noise invariance in historical waiting outcomes follows from the implementation. No further-experiment-is-unnecessary claim is made.

The event-recorded campaign ran locally and is separate from the original 279,936-run campaign. These datasets must not be pooled as independent replication.

## Completed corrected-model campaign

The separate 16,848-run extension, executed from frozen source identified by SHA-256 in `results/aei_extension/protocol.json`, tested component ablation, positive dwell and bonuses −1.4/−2.8/−4.2. All 22,998,183 passenger records were verified, all cases retained, and the event archive checksum is 2655703d6228cb0be8938716e70885f96931885ec16615cf5ddb2d582457db63. Detailed fixed contrasts and subgroup outcomes are in results/aei_extension; interpretation is in extension_report.md. No hardware or interface effects were tested.
