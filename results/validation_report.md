# Superseded historical validation report

This file is retained for provenance only. It is not the evidential basis for the current manuscript, **Requirement-aware multi-lift dispatch: restricted waiting and accessibility trade-offs**.

The earlier report analysed the 279,936-run historical aggregate table and used completed-trip waiting, synthetic crowding fields and synthetic stability/jerk bookkeeping. Those outputs are useful for reconstructing the project history, but they should not be used to claim:

- overall controller superiority;
- physical ride-comfort improvement;
- sensing robustness in a deployed lift system;
- disability, wheelchair use or instability inference;
- exact replay of the historical campaign.

The current manuscript uses the separate 5,184-run event-recorded campaign as the primary evidence. It evaluates all generated passengers with restricted waiting, reports priority and general passengers separately, and treats the result as a service-allocation trade-off. The event campaign shows that priority scheduling strongly reduces priority-request waiting, increases general-request waiting, and does not establish general waiting-time superiority.

For current evidence, use:

| File | Purpose |
| --- | --- |
| `results/censoring_validation/verification.json` | Event-recorded campaign verification and cohort matching |
| `results/censoring_validation/restricted_outcomes.csv` | Primary 900-unit restricted-wait outcomes |
| `results/censoring_validation/restricted_cluster_intervals.csv` | Paired scenario-bootstrap contrasts |
| `results/censoring_validation/restricted_horizon_sensitivity.csv` | 600/900/1200 restricted-horizon sensitivity |
| `publishing/experiment_supplement.md` | Current provenance summary |

The historical aggregate outputs remain part of the record, but the current paper deliberately avoids the older "human-aware system superiority" framing.
