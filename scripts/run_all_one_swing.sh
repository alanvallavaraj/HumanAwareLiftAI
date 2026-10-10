#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

WORKERS="${WORKERS:-8}"

python3 scripts/run_experiments.py --tier smoke --out results_smoke --workers "$WORKERS"
python3 scripts/analyse_results.py --results results_smoke/results.csv --out results_smoke

python3 scripts/run_experiments.py --tier pilot --out results_pilot --workers "$WORKERS"
python3 scripts/analyse_results.py --results results_pilot/results.csv --out results_pilot

python3 scripts/run_experiments.py --tier full --out results_full --workers "$WORKERS"
python3 scripts/analyse_results.py --results results_full/results.csv --out results_full

python3 scripts/validation_analysis.py

echo "All bounded tiers completed."

