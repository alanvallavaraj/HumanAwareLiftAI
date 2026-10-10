# Corrected-campaign experiment results — 8 October 2026

The requested priority ablation, door/dwell robustness and bonus sensitivity campaign completed 16,848 simulation cases. The executed source files are identified by SHA-256 in `results/aei_extension/protocol.json`. Verification reconstructed all 22,998,183 passenger records, confirmed 1,296 matched arrival cohorts across thirteen policies, and retained every case. There were no performance exclusions or outcome-driven additional runs.

## Priority-rule ablation

The reference retains occupancy penalties and pickup gates while disabling all three priority mechanisms. This controls the occupancy layer and makes the pickup exception meaningful. Each configuration has 1,296 runs.

| Configuration | All restricted wait | Priority restricted wait | General restricted wait |
|---|---:|---:|---:|
| Occupancy reference | 203.96 | 200.78 | 204.24 |
| Dispatch only | 203.90 | 200.76 | 204.19 |
| Boarding only | 196.81 | 35.65 | 210.50 |
| Pickup exception only | 203.80 | 200.54 | 204.09 |
| Full priority | 196.64 | 35.22 | 210.33 |

Boarding alone lowers priority waiting by 165.13 units (95% paired scenario interval −209.61 to −124.04) and raises general waiting by 6.26 (4.56 to 8.20). Full priority has closely similar effects: −165.55 (−209.95 to −124.46) and +6.08 (4.27 to 8.03). Dispatch alone adds little; the pickup exception alone has a small priority effect of −0.24 units (−0.48 to −0.06).

Boarding alone is sufficient for most of the observed allocation effect. The five-arm design does not prove necessity or identify every component interaction.

## Door/dwell robustness

The 5,184 positive-dwell cases use five fixed stop units and one unit per alighting or boarding passenger. Transfer completion changes physical occupancy and determines recorded timestamps; the car remains stationary during service.

| Configuration | All restricted wait | Priority restricted wait | General restricted wait | Completion % |
|---|---:|---:|---:|---:|
| Occupancy reference | 344.08 | 340.66 | 344.38 | 79.60 |
| Full priority | 335.40 | 132.51 | 351.64 | 79.63 |
| Collective | 357.14 | 353.40 | 357.48 | 78.30 |
| Distance-only nearest | 363.57 | 359.42 | 363.94 | 78.10 |

Relative to the occupancy-matched reference, priority waiting decreases 61.10%, a difference of −208.15 units (−247.76 to −170.90). General waiting increases +7.26 (5.34 to 9.40). Overall restricted waiting decreases −8.68 (−11.50 to −5.93), but horizon-accrued waiting differs by −0.84 (−2.51 to 0.78), and the total-completion interval includes zero. General completion falls 1.55 percentage points (−2.07 to −1.07).

Against collective dispatch, the full rule instead reduces general restricted waiting by −5.84 (−11.49 to −0.74), overall waiting by −21.74 (−26.81 to −16.82), and increases total completion by 1.33 percentage points (0.64 to 2.14). These combined-layer comparisons differ from the occupancy-controlled priority effect. They do not attribute the advantage specifically to priority.

The priority benefit and occupancy-matched general cost survive this specified dwell assumption. The assumption is not operationally calibrated, and this is not a dwell-parameter sweep.

## Priority bonus sensitivity

| Bonus | All restricted wait | Priority restricted wait | General restricted wait |
|---|---:|---:|---:|
| −1.4 | 196.72 | 35.28 | 210.42 |
| −2.8 | 196.64 | 35.22 | 210.33 |
| −4.2 | 196.61 | 35.12 | 210.30 |

Priority and general differences between each alternative and −2.8 have intervals spanning zero. These outcomes do not support a monotonic general-passenger penalty from increasing bonus magnitude. The dominant boarding mechanism remains enabled at all weights. Do not select −4.2 as a superior setting on these differences. The result is bounded sensitivity evidence, not equivalence or proof outside the tested range; sensitivity was tested without dwell.

## Interpretation and reproducibility

All waits above include every arriving passenger and are capped at 900 model units, fully observable over the common horizon. They are averages of run-level group means, not passenger-weighted pooled means. Completion is observed destination arrival by the finite observation horizon. Intervals are descriptive paired scenario bootstrap intervals (108 clusters, twelve seeds retained, 2,000 draws, seed 20261008), without multiplicity correction; they do not quantify real-building calibration uncertainty.

The extension clears served/stale targets and separates common counter-based dispatch randomness from unused synthetic comfort draws. These corrections were frozen before the full campaign and shared across all arms. This is a separate model version: do not interpret changes from older legacy means as dwell effects. The legacy campaign, its 783/3,888 replay discrepancies and its distinct results remain disclosed. No pressure hardware, measured jerk, thermal inference or accessible interface benefit was tested.

All three requested experiments are complete. No additional simulation was selected after viewing the results. These experiments strengthen mechanism attribution and model-assumption robustness, but do not by themselves establish the novelty or operational validation required for AEI acceptance.
