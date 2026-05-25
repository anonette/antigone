#!/usr/bin/env python3
"""Push analysis chart data to Antigone Lab (Lovable analysis endpoint).

Default file: output/phase1_v2_cross/analysis_chart_data.json
Requires Lovable to implement POST /api/public/analysis.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from antigone.lovable_ingest import push_analysis


def main() -> None:
    load_dotenv(ROOT / ".env")
    ap = argparse.ArgumentParser(description="POST analysis chart data to Lovable")
    ap.add_argument(
        "analysis",
        nargs="?",
        type=Path,
        default=ROOT / "output" / "phase1_v2_cross" / "analysis_chart_data.json",
        help="Analysis JSON (default: output/phase1_v2_cross/analysis_chart_data.json)",
    )
    ap.add_argument("--url", help="Override Lovable base URL")
    ap.add_argument("--timeout", type=float, default=60.0)
    args = ap.parse_args()

    try:
        result = push_analysis(args.analysis.resolve(), analysis_url=args.url, timeout_s=args.timeout)
    except RuntimeError as exc:
        print(f"[fail] {exc}")
        print()
        print("Fallback: open Lovable chat and paste:")
        print("  Add Analysis page that loads the attached JSON as src/data/analysis_chart_data.json")
        print(f"  Then attach: {args.analysis.resolve()}")
        sys.exit(1)

    print(f"[ok] analysis pushed: run_id={result.get('run_id')}")
    print(f"  url: {result['analysis_url']}")


if __name__ == "__main__":
    main()
