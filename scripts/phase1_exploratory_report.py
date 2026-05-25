"""Exploratory Phase 1 report: language × model (keyword heuristics only)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analyze import dedupe_latest_cell, rows_to_dataframe
from antigone.research_log import load_all_responses


def load_phase1_ok(*, run_id: str | None = None) -> list[dict]:
    rows = load_all_responses(ROOT / "logs", phase=1)
    if run_id:
        rows = [r for r in rows if run_id in r.get("run_id", "")]
    rows = dedupe_latest_cell(rows)
    return [r for r in rows if r.get("status") == "ok" and (r.get("response_text") or "").strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", help="Only this run (substring match)")
    ap.add_argument(
        "--all",
        action="store_true",
        help="All Phase 1 runs in logs/ (default; dedupe by cell_key)",
    )
    args = ap.parse_args()

    records = load_phase1_ok(run_id=args.run_id)
    df = rows_to_dataframe(records)
    df["chars"] = df["response_text"].str.len()
    out_dir = ROOT / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    for (lang,), g in df.groupby(["language"]):
        n = len(g)
        for col in ["heuristic_action", "agency_heuristic"]:
            for val, c in g[col].value_counts().items():
                summary_rows.append(
                    {
                        "dimension": col,
                        "language": lang,
                        "category": val,
                        "count": int(c),
                        "pct": round(100 * c / n, 1),
                    }
                )
    pd.DataFrame(summary_rows).to_csv(
        out_dir / "phase1_exploratory_summary.csv", index=False
    )
    df[
        [
            "record_id",
            "language",
            "model_requested",
            "replicate",
            "stimulus_id",
            "heuristic_action",
            "agency_heuristic",
            "response_char_len",
        ]
    ].to_csv(out_dir / "phase1_exploratory_by_cell.csv", index=False)

    runs = sorted(df["run_id"].unique()) if "run_id" in df.columns else []
    print(f"N = {len(df)} cells | runs: {', '.join(runs) or '(none)'}\n")
    print("=== Decision (VAR-A proxy) by language — row % ===")
    print(pd.crosstab(df["language"], df["heuristic_action"], normalize="index").round(2))
    print()
    print("=== Agency (VAR-D proxy) by language — row % ===")
    print(pd.crosstab(df["language"], df["agency_heuristic"], normalize="index").round(2))
    print(f"\nWrote {out_dir / 'phase1_exploratory_summary.csv'}")
    print(f"Wrote {out_dir / 'phase1_exploratory_by_cell.csv'}")


if __name__ == "__main__":
    main()
