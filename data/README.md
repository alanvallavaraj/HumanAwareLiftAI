Retained data, all synthetic simulation outputs (CC BY 4.0; see ../LICENSING.md):

- `historical-results.csv.gz`: the 279,936-row historical campaign (compressed SHA-256 fece0e4c…e3e4d; uncompressed 7654ba08…e740d). `scripts/download_evidence.py` decompresses and verifies it into `data/full/`, which git ignores.
- `passenger-event-parts/`: the legacy event-recording campaign's passenger records, split into parts; `scripts/download_passenger_events.py` joins and verifies them.
- `aei-extension-event-parts/`: all 22,998,183 passenger records of the corrected campaign; `scripts/restore_aei_extension_events.py` joins and verifies them.
- `historical-code-snapshot.tar.gz`: the post-run source snapshot of the historical campaign (simulator, runner and analysis script), used by `scripts/replay_historical_parity.py`.

See ../REPRODUCING.md for the full workflow.
