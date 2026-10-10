# Bounded Experiment Plan

## Primary Claim

A human-aware, stability-aware, accessibility-aware multi-lift controller can
reduce failed pickups, unnecessary stops, and accessibility inequity while
maintaining or improving average waiting time compared with classical group
control and occupancy-only dispatching.

## Hypotheses

H1. Occupancy-aware dispatch reduces failed pickup rate versus collective and
nearest-car baselines.

H2. The integrated human-aware controller reduces average waiting time and 95th
percentile waiting time across mixed traffic patterns.

H3. Accessibility priority reduces special-needs passenger waiting time and
fairness disparity without a large penalty to the general population.

H4. Pressure-distribution stability and adaptive motion control reduce comfort
risk and jerk exposure, especially under high load and hand-carried-object
conditions.

H5. Interactive guidance reduces door crowding, repeated hall calls, and failed
boarding attempts when lifts are full or reserved for higher-priority passengers.

## Independent Variables

- Floors: 8, 16, 32
- Lifts: 2, 4, 8
- Population scale: 200, 800, 2000 synthetic occupants
- Traffic pattern: morning up-peak, lunch/interfloor, evening down-peak, mixed
- Accessibility share: 2%, 8%, 15%
- Carrying-object share: 5%, 20%, 40%
- Sensor noise: none, moderate, high
- Controller: collective, nearest_car, occupancy_aware, access_priority,
  stability_aware, human_aware, layered_access_stability, oracle_upper

## Dependent Metrics

- Mean waiting time
- 95th percentile waiting time
- Mean journey time
- Failed pickup rate
- Unnecessary stop rate
- Door crowding rate
- Energy proxy
- Lift utilisation imbalance
- Special-needs mean waiting time
- Fairness disparity between special-needs and general passengers
- Stability-risk exposure
- Jerk exposure
- Adaptive slowdowns
- Guidance compliance benefit

## Bounded Tiers

### Smoke

Purpose: Verify that the simulator, metrics, and analysis pipeline work.

- 1 building setting
- 2 traffic patterns
- 3 controllers
- 2 seeds

### Pilot

Purpose: Estimate effect direction and runtime.

- 2 building settings
- 4 traffic patterns
- 6 controllers
- 5 seeds

### Full

Purpose: Paper-grade factorial evaluation.

- 3 floor counts
- 3 lift counts
- 3 population scales
- 4 traffic patterns
- 3 accessibility shares
- 3 carrying shares
- 3 sensor-noise levels
- 7 controllers
- 12 seeds

Total full runs: 3 x 3 x 3 x 4 x 3 x 3 x 3 x 8 x 12 = 279,936 simulated
building-days.

## Branches If Something Does Not Work

1. If runtime is too high:
   - Keep all controllers.
   - Reduce seeds from 12 to 6.
   - Preserve factorial diversity.
   - Mark as `full_reduced`.

2. If the human-aware controller does not improve mean waiting time:
   - Do not retune endlessly.
   - Report trade-off result.
   - Analyse whether it improves failed pickups, accessibility fairness, and
     comfort.
   - Position the contribution as multi-objective human-aware control rather
     than pure speed optimisation.

3. If accessibility priority harms general waiting time substantially:
   - Run a bounded sensitivity branch with priority weights 0.5, 1.0, 1.5.
   - Select the Pareto-balanced setting.
   - Report the trade-off curve.

4. If pressure stability has weak effect:
   - Run a bounded high-instability branch using carrying-object share 40% and
     high sensor noise.
   - If still weak, keep stability as a secondary contribution and strengthen
     the paper around dispatch, fairness, and interaction.

5. If sensor noise breaks the integrated method:
   - Run robust filtering branch with exponential smoothing factors 0.2, 0.5,
     0.8.
   - Report degradation curves.

6. If no controller dominates:
   - Use Pareto analysis across waiting time, failed pickups, fairness, comfort,
     and energy proxy.
   - Claim balanced improvement rather than single-metric dominance.

## Stopping Rule

Run smoke, pilot, and either full or full_reduced. Stop. Do not perform
open-ended search. Only the three pre-declared sensitivity branches above are
allowed, and only if triggered by the pilot or full run.


