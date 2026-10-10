# Bounded AEI extension protocol — 8 October 2026

*Editorial note, 10 October 2026: references to the execution platform were removed. The design, grid, outcomes, analysis and stopping rules are unchanged from the version fixed on 8 October 2026.*

## Design and stopping rule

108 structural scenarios: floor/car pairs (8,2), (16,4), (32,8); populations 200, 800, 2000; up-peak, down-peak, lunch and mixed traffic; priority shares 0.02, 0.08, 0.15. Carrying share is 0.20; arrivals occupy 3,600 model units, observation ends at 4,500. Twelve seeds (0–11). All policies share identical arrival cohorts. No performance-driven tuning, exclusions or additional scenarios.

Thirteen non-overlapping configurations yield exactly 16,848 runs:

- No dwell: occupancy-matched reference; dispatch-only; boarding-only; pickup-exception-only; full priority at -2.8; full priority at -1.4 and -4.2; direction-aware collective reference; distance-only nearest-car reference (9 configurations).
- Dwell: occupancy reference, full priority at -2.8, direction-aware reference and distance-only reference (4 configurations; 5,184 runs).

The reference in component ablations retains occupancy penalties and occupancy pickup gates. Each of the three priority mechanisms is a separate switch. Singleton effects and full-rule effects identify sufficiency; this five-arm design does not identify every interaction or establish that a component is necessary.

## Shared model revision

A served target is cleared when the stop is serviced; empty stale targets are cleared. The legacy simulator could retain served destination targets. This correction is applied to all extension configurations, including the no-dwell controls. Consequently the extension is a separate model version, not an exact replay of archived numbers. Dwell effects are compared within this new version.

Dispatch tie-breaking has its own counter-based pseudorandom draw keyed by seed, assignment time, calling floor and car ID, shared across policy variants. Unused synthetic stability/comfort accounting is excluded. Arrivals retain the existing generator. This removes dependence of dispatch jitter on irrelevant synthetic exposure draws and controller-specific random offsets. Car capacity remains thirteen persons; one-floor-per-unit travel and the original direction eligibility rules remain. No pressure sensing, physical jerk, predictive display or user-interface effect is evaluated.

## Dwell state model

A physical stop incurs five fixed door-service units, then one unit per alighting passenger followed by one unit per boarding passenger. Transfer events receive their actual completion times. Selected boarders are reserved from the hall queue; physical car occupancy changes only when each transfer completes. The car cannot move during service. Boarding selection uses capacity after planned alighting; physical capacity is checked at every transfer. People arriving after service selection wait for a later service cycle. The dispatch scoring formula does not gain a new busy-time penalty.

## Outcomes and uncertainty

Primary: mean run-level waiting restricted to 900 units, including all generated passengers; report all, priority and general groups. Every generated passenger has at least 900 units of follow-up. Zero-person groups are omitted only from that subgroup's average and identified in counts. Secondary: finite-horizon accrued waiting, boarding by 900, destination completion, group completion, physical stop count, distance and dwell occupancy. Scheduled transfers beyond the observation horizon remain unobserved.

Paired 108-scenario percentile bootstrap (2,000 draws, seed 20261008), retaining all twelve seeds jointly. Report subgroup benefit/cost, full versus matched reference, each singleton versus matched reference, dwell-minus-no-dwell changes and priority-minus-reference interactions with dwell. Report all three weights; no selection of a favourable weight. Intervals describe this fixed scenario design, not physical calibration uncertainty. Singleton effects do not decompose the full effect additively.

## Failure branches

1. Fail code invariants or matched arrivals: stop before full submission, repair the implementation and repeat only the failed development check.
2. Planned compute resources unavailable: preserve submission-ready code and report the blocker; label the execution environment accurately.
3. Process interruption: resume only absent cases from the immutable manifest. Preserve existing files; do not rerun based on outcome.
4. A case or verification fails: retain the failure and execute that identical case once after an identified technical repair. Otherwise stop and disclose.
5. Priority benefit or dwell robustness fails: report it; do not change weights, demand or the controller to obtain a favourable conclusion.
