# Paper Outline

## Working Title

Human-Aware Multi-Lift Group Optimisation Using Pressure-Distribution Sensing, Accessible Interaction and Adaptive Ride-Comfort Control

## Target Journal

Elsevier Advanced Engineering Informatics.

## Core Claim

A modular human-aware multi-lift optimisation framework can reduce full-lift door-crowding and special-needs waiting time while pressure/stability-aware control improves ride comfort with only a small scheduling trade-off.

## Proposed Contributions

1. A multi-lift group-control simulation framework incorporating occupancy, pressure/stability, accessibility and passenger interaction signals.
2. A modular accessibility-aware dispatch controller for prioritising passengers with special needs and reducing unproductive full-lift stops.
3. A pressure-distribution-inspired adaptive ride-comfort module for reducing jerk exposure under unstable load conditions.
4. A full factorial population-scaled evaluation over building size, lift count, traffic pattern, accessibility share, carrying-object share and sensor noise.
5. Validation through ablation, sensor-noise robustness and building-scaling analysis.

## Recommended Result Framing

Do not claim that a single monolithic AI controller dominates every metric.

Use this framing instead:

- `access_priority` is the strongest dispatch module.
- `layered_access_stability` is the proposed human-aware system because it adds ride-comfort benefits while retaining most accessibility and crowding benefits.
- The method is most useful in medium-to-large multi-lift buildings.

## Key Quantitative Claims

Compared with classical collective control, `layered_access_stability` achieved:

| Metric | Improvement |
| --- | ---: |
| Mean waiting time | 5.32% |
| Door crowding | 86.04% |
| Special-needs waiting time | 62.32% |
| Jerk exposure | 13.08% |
| Composite score | 2.99% |

## Limitations to State Honestly

- The current work is simulation-based.
- Pressure distribution and passenger state are modelled rather than measured from deployed hardware.
- Small buildings show weaker or negative mean-wait trade-offs, so the recommended deployment context is medium-to-large multi-lift buildings.
- Real deployment would require privacy-preserving sensing, lift controller integration and accessibility co-design.

## Next Manuscript Sections

1. Introduction
2. Related Work
3. System Architecture
4. Simulation and Controller Design
5. Experimental Design
6. Results
7. Validation and Ablation
8. Discussion
9. Limitations
10. Conclusion
