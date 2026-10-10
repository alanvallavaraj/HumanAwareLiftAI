# Reproduction instructions

Run commands from the repository root. Simulation is standard-library Python; analyses require NumPy and figures require Matplotlib. Every dataset used below is in this repository, so nothing is downloaded.

```sh
python3 -m pip install -r requirements-analysis.txt -r requirements-figures.txt
```

## Corrected matched-arrival campaign (primary evidence)

The corrected-model campaign executed 16,848 cases (108 scenarios, twelve seeds, thirteen configurations), including 5,184 cases with door and transfer delays, under Python 3.12.1 and NumPy 2.3.5. Its protocol is `protocols/aei_extension_20261008.md`. `results/aei_extension/protocol.json` records the SHA-256 of the executed source, and `src/aei_extension.py` and `src/simulator.py` in this repository are byte-identical to it. Every configuration shares matched arrivals. The target-clearing and random-stream corrections apply to all thirteen arms, so compare effects within this model version.

Restore the deposited passenger records and repeat the analysis without simulation:

```sh
python3 scripts/restore_aei_extension_events.py
python3 scripts/analyse_aei_extension.py --directory results/aei_extension
python3 scripts/make_aei_extension_figures.py --directory results/aei_extension
python3 scripts/analyse_extension_horizon_sensitivity.py
```

The restoration script joins the archive parts in `data/aei-extension-event-parts`, verifies the archive SHA-256 and restores 16,848 per-case files. The analysis re-verifies all 22,998,183 passenger rows and computes paired intervals from 2,000 bootstrap resamples of the 108 scenarios, keeping all twelve seeds together. All fixed contrasts are reported and no favourable weight is selected. The horizon analysis reads the event archive directly, recomputes restricted waiting at 300, 600 and 900 units for every arrival and at 1,200 units for the 93.81% of arrivals with at least 1,200 units of follow-up, checks every 900-unit contrast against `paired_intervals.csv`, and writes `results/aei_extension/horizon_sensitivity.csv`.

Exact replay of the corrected campaign requires Python 3.11 or later because it shares the legacy movement rule (see below): 30 of 30 sampled eight-floor runs reproduce the archived outputs under Python 3.11.15, against 13 of 30 under Python 3.9.6.

To execute a fresh campaign, use a new output directory:

```sh
python3 -m unittest discover -s tests -p test_aei_extension.py
python3 scripts/run_aei_extension.py --workers 8 --out results/fresh_aei_extension
python3 scripts/analyse_aei_extension.py --directory results/fresh_aei_extension
```

## Historical factorial campaign

```sh
python3 scripts/download_evidence.py
python3 scripts/verify_results.py
python3 scripts/check_execution.py
python3 scripts/reviewer_analysis.py
python3 scripts/make_figures.py
```

`download_evidence.py` decompresses `data/historical-results.csv.gz` into `data/full/` and verifies its SHA-256 (`7654ba08d904362a1f463d9816ed936c83338682571c83b637bb214a37fe740d`). These scripts reanalyse the archived runs; they do not rerun the campaign. The campaign's Python version was not recorded.

## Legacy event-recording campaign (superseded)

```sh
python3 scripts/download_passenger_events.py
python3 scripts/analyse_censoring_validation.py
python3 scripts/analyse_restricted_horizon_sensitivity.py
```

This campaign ran locally with eight workers under Python 3.12.14 and is superseded by the corrected campaign (manuscript Appendix B). Its aggregate CSV SHA-256 is `65a7dfb460515b20ac920729c50387de884167fad06aa4c7afd8ab8582efdd21`. The event analysis checks 5,184 cases, arrival-cohort matching in 1,296 blocks and 7,076,364 event rows. The legacy script `analyse_restricted_horizon_sensitivity.py` caps waits at 1,200 units for all arrivals, although arrivals after time 3,300 have less than 1,200 units of follow-up; the corrected-model analysis above handles this explicitly. To execute the campaign again, run `python3 scripts/run_censoring_validation.py --workers 8 --out results/new_event_run`.

## Historical replay parity

```sh
python3.9 scripts/replay_historical_parity.py
python3 scripts/diagnose_replay_mismatches.py
```

`data/historical-code-snapshot.tar.gz` holds the post-run source snapshot of the historical campaign. The legacy movement rule chooses a stationary car's nearest target with `min()` over a Python set, so equidistant targets are resolved by set iteration order, which differs between Python 3.9 and Python 3.11 or later. Replaying the snapshot under Python 3.9.6 reproduces all 3,888 legacy cases of the event campaign against the historical archive on all eighteen archived metrics (`results/censoring_validation/replay_parity_python39.json`). Under Python 3.11.15, as under Python 3.12.14, 3,105 match and 783 differ (`replay_parity_python311.json`). The differing cases are concentrated in eight-floor, two-car buildings and do not depend on configuration, priority share or seed (`replay_mismatch_diagnosis.json`). Use Python 3.9 to reproduce the historical archive exactly.

## Compile the manuscript

```sh
cd paper
latexmk -pdf -halt-on-error manuscript.tex
```

Build the upload archive with `python3 scripts/build_submission_package.py`. It writes `publishing/submission-source.zip` with the `.tex` files, bibliography, `.bbl`, class and style files, Highlights.txt and the four figures as separate PDFs, and the archive compiles as uploaded. The 32 original literature references retain verified DOI metadata; the restricted-mean reference (Royston and Parmar 2013, doi:10.1186/1471-2288-13-152) was added on 10 October 2026. The dataset reference cites the Zenodo archive of this repository.
