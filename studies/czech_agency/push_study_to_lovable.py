#!/usr/bin/env python3
"""Push Czech agency runs + analysis payloads to Antigone Lab (Lovable)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY_DIR = Path(__file__).resolve().parent

MAIN_RUN = STUDY_DIR / "logs" / "phase3_20260529T112210Z_77ea6d3b"
CONTROL_RUN = STUDY_DIR / "logs" / "phase3_20260529T125836Z_6570a5fc"

ANALYSIS_FILES = [
    STUDY_DIR / "output" / "agency_analysis.json",
    STUDY_DIR / "output_noq" / "agency_analysis.json",
    STUDY_DIR / "output" / "agency_comparison.json",
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    py = sys.executable
    build = STUDY_DIR / "build_agency_analysis.py"
    push_run = ROOT / "push_to_lovable.py"
    push_analysis = ROOT / "push_analysis_to_lovable.py"

    run([py, str(build), "--all"])

    for run_dir in (MAIN_RUN, CONTROL_RUN):
        run([py, str(push_run), str(run_dir)])

    for path in ANALYSIS_FILES:
        if not path.exists():
            raise SystemExit(f"Missing analysis file: {path}")
        run([py, str(push_analysis), str(path)])

    print("[ok] Czech agency: 2 runs + 3 analysis payloads pushed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
