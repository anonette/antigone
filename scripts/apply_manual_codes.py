"""Apply hand-coded Phase 1 values and merge into run logs."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from recode import cmd_merge  # noqa: E402
import argparse

# Populated by coding pass — record_id -> codebook fields
CODES: dict[str, dict[str, str]] = {}


def main() -> None:
    codes_path = ROOT / "data" / "phase1_manual_codes.csv"
    if not codes_path.exists():
        raise SystemExit(f"Missing {codes_path}")
    with codes_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rid = row["record_id"]
            CODES[rid] = {k: v for k, v in row.items() if k != "record_id" and v.strip()}

    out = ROOT / "output" / "phase1_manual_codes_export.csv"
    fields = [
        "record_id",
        "code_var_a",
        "code_var_b",
        "code_var_c",
        "code_var_d",
        "code_var_e",
        "code_var_f",
        "code_var_g",
        "code_var_r",
        "coder_id",
        "coded_at",
    ]
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for rid, codes in sorted(CODES.items()):
            w.writerow({"record_id": rid, **codes})

    class Args:
        run_dir = ROOT / "logs" / "phase1_20260525T081321Z_8b488b4a"
        from_path = out
        phase = run_id = None

    from antigone.coding_workflow import merge_coding_into_run

    updated, total = merge_coding_into_run(Args.run_dir, Args.from_path)
    print(f"Merged {updated}/{total} rows")


if __name__ == "__main__":
    main()
