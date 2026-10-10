# HumanAwareLiftAI

**Alan Immanuel Benjamin Vallavaraj — Lecturer, University of Westminster.**

[Reproduction instructions](REPRODUCING.md) · [LaTeX manuscript](paper/) · [Licensing](LICENSING.md)

The current manuscript is **Requirement-aware multi-lift dispatch: restricted waiting and accessibility trade-offs**, prepared for Advanced Engineering Informatics.

The study evaluates explicit priority, occupancy and direction rules in a synthetic multi-lift simulator. It does not implement learned control, physical pressure sensing, adaptive motion, waiting-time prediction or display/voice interaction.

## Current results

The primary evidence is the corrected matched-arrival campaign: 16,848 runs over 108 scenarios, twelve seeds and thirteen configurations, with all 22,998,183 passenger records verified. Every arriving passenger enters the 900-unit restricted mean waiting time.

- Priority-first boarding alone produces most of the priority benefit and of the general-passenger cost.
- With door and transfer delays, full priority reduces priority-request waiting from 340.66 to 132.51 model time units relative to an occupancy-matched reference; general-request waiting rises by 7.26 units (paired scenario interval 5.34 to 9.40).
- Overall capped waiting falls, but horizon-accrued waiting and overall completion do not change detectably.
- Against collective dispatch with delays, general-request waiting falls instead, so the baseline determines the apparent cost.
- Dispatch bonuses of −1.4, −2.8 and −4.2 give closely similar outcomes, and the trade-off holds at restricted horizons of 300, 600, 900 and 1,200 units.

The historical 279,936-run campaign is used only to show how completed-trip means behave: its 5.32% completed-trip advantage for a combined configuration coincides with unchanged general-request waiting and lower completion. Synthetic comfort bookkeeping is not a physical comfort measurement.

## Evidence and provenance

| Artifact | Purpose |
| --- | --- |
| [PDF](paper/manuscript.pdf) | Current manuscript |
| [Source and highlights](paper/) | Elsevier template, bibliography and highlights; `scripts/build_submission_package.py` builds the upload ZIP |
| [Corrected campaign](results/aei_extension/) | Protocol, per-run outcomes, paired intervals, horizon sensitivity and verification |
| [Historical reanalysis](results/reviewer_analysis/) | Group outcomes, clustered intervals and censoring sensitivity |
| [Legacy event campaign](results/censoring_validation/) | Superseded legacy-model event campaign, replay-parity records and mismatch diagnosis |
| [Data](data/) | Historical CSV, code snapshot and checksum-verified passenger-event archives |
| [Supplementary records](publishing/experiment_supplement.md) | Execution history and source boundaries |
| [Literature audit](publishing/aei_ten_paper_audit.md) | Journal comparator structures and reference counts |

**Replay parity.** The legacy movement rule resolves equidistant target floors through Python set iteration order, which differs between Python 3.9 and 3.11+. Under Python 3.9.6, all 3,888 replayed legacy cases reproduce the historical archive on all eighteen metrics; under Python 3.11–3.12 the same 3,105 match. The corrected campaign shares the movement rule and reproduces under Python 3.11+ (it ran on Python 3.12.1). See [REPRODUCING.md](REPRODUCING.md).

The archived release on Zenodo contains the code, all datasets and the reproduction scripts; the submitted manuscript is left out of the archive.

## Licence

Code is released under the [MIT licence](LICENSE) and data and results under [CC BY 4.0](LICENSE-DATA). The manuscript in `paper/` is not licensed for reuse. See [LICENSING.md](LICENSING.md) for the exact scope.
