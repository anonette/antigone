"""Rebuild coding_sheet.csv from canonical jsonl (no embedded response text).

Accepts optional --run-dir; defaults to the most recent phase1_* folder.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from antigone.research_log import CODING_COLUMNS, IV_COLUMNS


def _latest_phase1() -> Path:
    candidates = sorted((ROOT / "logs").glob("phase1_*"))
    candidates = [p for p in candidates if p.is_dir()]
    if not candidates:
        raise SystemExit("No phase1_* logs found")
    return candidates[-1]


parser = argparse.ArgumentParser()
parser.add_argument("--run-dir", type=Path, default=None)
args = parser.parse_args()
RUN = (args.run_dir or _latest_phase1()).resolve()
FIELDS = [
    "record_id",
    "cell_key",
    "run_id",
    "phase",
    "language",
    "stimulus_id",
    "baseline_stimulus_id",
    "model_requested",
    "model_group",
    "replicate",
    "translation_note",
    *IV_COLUMNS,
    "response_char_len",
    "response_word_count",
    *CODING_COLUMNS,
    "coder_id",
    "coded_at",
]

rows = [
    json.loads(line)
    for line in (RUN / "responses.jsonl").open(encoding="utf-8")
    if line.strip()
]
rows = [r for r in rows if r.get("status") == "ok"]

path = RUN / "coding_sheet.csv"
with path.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k) for k in FIELDS})

print(f"Wrote {len(rows)} rows to {path}")
