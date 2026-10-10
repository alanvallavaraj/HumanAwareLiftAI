# Ten-paper AEI structure and reference audit

Audit date: 7 October 2026. All ten selected items are original research articles in Advanced Engineering Informatics. Three address lifts directly; seven are methodological neighbours. This is a purposive comparison, not a systematic review or a claim that these are the ten newest journal articles. Eight appeared in 2024–2026; two older papers are retained for direct or foundational relevance.

## Access and evidence

DOIs, titles, authors and reference counts were verified using publisher-deposited Crossref metadata. Publisher abstracts, indexed introductions and available section previews were checked through ScienceDirect search results. Direct full-page retrieval returned access errors, and a KAIST author-hosted PDF timed out. Consequently, this report does not claim that ten complete PDFs were read. The section sequences below describe retrieved evidence, with missing details marked. Full-text appraisal remains necessary before submission.

Reference counts are bibliography entries, not citations received. A secondary listing reported 45 for Wang et al. (2025); the publisher preview and Crossref both reported 47. We retain 47. A secondary motion-paper listing reported 54 extracted references; Crossref and the publisher preview reported 68. We retain 68.

| Paper | Relevance | References | Workflow/validation checked | Structure evidence | Justification and implication |
| --- | --- | ---: | --- | --- | --- |
| [Smart dispatching and optimal elevator group control through real-time occupancy-aware deep learning of usage patterns](https://doi.org/10.1016/j.aei.2021.101286) (2021) | Direct lift comparator | 37 | Occupancy estimation, traffic recognition and dispatch model followed by simulation evaluation. | Related work precedes decision modelling and simulation. | Avoiding capacity-blind pickup decisions; Simio/MATLAB simulation. Occupancy-aware dispatch is prior art. |
| [Design of digital twin applications in automated storage yard scheduling](https://doi.org/10.1016/j.aei.2021.101477) (2022) | Related scheduling comparator | 38 | Resource framework, key technologies, uncertain-arrival case, sensitivity and comparison. | Explicit sequence: related work; framework; technologies; experiments/results; comparisons; conclusions. | Resource coordination evaluated through an ASC scheduling case and configuration sensitivity. Separate architecture from decision rules and test conditions. |
| [Traffic pattern-aware elevator dispatching via deep reinforcement learning](https://doi.org/10.1016/j.aei.2024.102497) (2024) | Direct lift comparator | 51 | SMDP formulation, unified D3QN training and empirical comparison of added techniques. | Preliminaries; SMDP; architecture/training; empirical results; conclusion. | Mixed-traffic dispatch and incremental technique contribution. Our rules do not reproduce this learned baseline. |
| [An information freshness-based digital twin model to support multi-level complementary dynamic scheduling in Shared Manufacturing](https://doi.org/10.1016/j.aei.2024.102525) (2024) | Related scheduling comparator | 34 | Multilevel scheduling model, information freshness, customer-oriented trigger and improved ABC. | Model, monitoring and solution method precede case-based evaluation; preview numbering is inconsistent. | Coordinated response to disturbances and bounded monitoring resources. Report what information actually affects decisions. |
| [Elevator priority scheduling with deep learning based image analytics for people with special needs](https://doi.org/10.1016/j.aei.2024.102794) (2024) | Direct lift comparator | 50 | Image analytics plus accessibility-priority scheduling, evaluated by simulation. | Related research; detailed methodology; simulation model/evaluation. | Service inequality for wheelchair users. Accessibility priority is established prior work. |
| [Adaptive exit choices of pedestrians during emergency evacuation: A study combining virtual experiments, survey and modelling](https://doi.org/10.1016/j.aei.2025.103302) (2025) | Related behavioural comparator | 71 | Virtual evacuation experiments, post-experiment survey, choice-model calibration and simulation. | Experimental method; experimental/survey results; model development/evaluation visible in preview. | Behavioural evidence supports exit-choice model assumptions. Interface-compliance claims need human evidence. |
| [A reinforcement learning from human feedback based method for task allocation of human robot collaboration assembly considering human preference](https://doi.org/10.1016/j.aei.2025.103497) (2025) | Related human/scheduling comparator | 47 | Multi-agent pre-training, preference reward construction and preference adaptation. | Task representation and RLHF framework, then comparative and ablation evaluation. | Human preference should influence allocation, alongside production objectives. Separate human service objectives from aggregate performance. |
| [Contexts Matter: Robot-Aware 3D human motion prediction for Agentic AI-empowered Human-Robot collaboration](https://doi.org/10.1016/j.aei.2025.103591) (2025) | Related human-state comparator | 68 | Measured motion/context collection, two-branch LSTM and comparison with context variants. | Related concepts; methodology; data collection; performance comparison. | Tests whether robot context contributes to prediction. A pressure-state claim similarly needs measured data. |
| [Integration of dynamic knowledge and LLM for adaptive human-robot collaborative assembly solution generation](https://doi.org/10.1016/j.aei.2025.103613) (2025) | Related human-context comparator | 62 | Knowledge modelling/evolution/enhancement and comparative collaborative-assembly case. | Workflow components and case comparison visible; complete numbered outline unavailable. | Changing contextual knowledge should improve solution generation. State the added mechanism and its tested contribution. |
| [A multi-layer dynamic production scheduling method for manufacturing systems with cloud-edge-end architecture](https://doi.org/10.1016/j.aei.2025.103961) (2026) | Related layered-scheduling comparator | 41 | Cloud-edge-end collaborative layered dynamic scheduling. | Section 2 related work; Section 3 layered process; complete evaluation details unavailable in retrieved preview. | Adaptation to complex tasks and unexpected events. Layered architecture does not alone demonstrate a new algorithm. |

## Reference-count comparison

Verified counts: 37, 38, 51, 34, 50, 71, 47, 68, 62, 41. Range 34–71; median 48.5; mean 49.9. Direct lift comparators have 37, 51 and 50 references. These observations are not a journal minimum or maximum.

A reasonable editorial target is around 45–55 relevant references for the intended interdisciplinary paper, provided the sources are actually used. The current draft cites 32 DOI-verified sources. Eight additional candidate lookups remained unresolved after a bounded anonymous retry and are omitted from the reference list. We have not padded the bibliography to reach a numerical target. Metadata verification of background entries must be followed by claim-specific reading.

## Structure adopted for our manuscript

1. Introduction: service problem, closest precedents, narrow gap, contributions.
2. Related work: dispatch, coordinated engineering representations and human state.
3. Problem representation and simulation model.
4. Controller design and interface proposal.
5. Experimental protocol and complete experiment history.
6. Results: principal comparison, adverse outcomes, module comparisons, noise and subgroups.
7. Discussion: mechanism, validity limits, engineering implications and bounded next validation.
8. Conclusions, data/code availability, author declarations and references.

The common argumentative sequence is adopted; exact headings are adapted to this study. No text, figures or numerical results have been copied from the comparator papers.

## Writing choices

British English; concrete descriptions; moderate claims; explicit explanation of negative results; no language implying measured pressure, trained AI, proven fairness or a tested voice/display interface. The user-facing title has been narrowed to match the implemented model. Natural writing is achieved by editing for clarity and flow, not by promising to evade AI detection.

## Publisher requirements

The official guide is https://www.sciencedirect.com/journal/advanced-engineering-informatics/publish/guide-for-authors. Highlights and declarations are included as draft material; mandatory length, graphical abstract, formatting and disclosure requirements need a final check against the current guide before submission.
