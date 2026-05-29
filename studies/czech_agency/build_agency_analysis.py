#!/usr/bin/env python3
"""Build a Lovable analysis payload for the Czech agency module.

Produces studies/czech_agency/output/agency_analysis.json in a shape the
existing POST /api/public/analysis endpoint can store (keyed by run_id, so it
lands as a separate row from the Phase 1 payload). Push with:

  python push_analysis_to_lovable.py studies/czech_agency/output/agency_analysis.json

Run after coding_sheet.csv has the agency columns filled. Degrades gracefully:
if codes are missing it still emits counts/lengths so the structure is visible.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

STUDY_DIR = Path(__file__).resolve().parent

CONDITION_ORDER = [
    "agentive",
    "participial_passive",
    "reflexive_deagentive",
    "decision_nominalization",
    "bureaucratic_nominalization",
]
BASELINE = "agentive"


def latest_run_dir() -> Path:
    runs = sorted((STUDY_DIR / "logs").glob("phase3_*"))
    runs = [r for r in runs if r.is_dir()]
    if not runs:
        raise SystemExit("No runs under studies/czech_agency/logs/. Run run_study.py first.")
    return runs[-1]


def counts(df: pd.DataFrame, col: str) -> list[dict]:
    if col not in df.columns or df[col].dropna().empty:
        return []
    d = df.dropna(subset=[col]).copy()
    d[col] = d[col].astype(str).str.strip()
    g = d.groupby(["cz_agency", col]).size().reset_index(name="n")
    return g.to_dict(orient="records")


def yes_rate(df: pd.DataFrame, col: str) -> list[dict]:
    if col not in df.columns or df[col].dropna().empty:
        return []
    d = df.dropna(subset=[col]).copy()
    d[col] = d[col].astype(str).str.strip().str.lower()
    out = []
    for cond in CONDITION_ORDER:
        sub = d[d["cz_agency"] == cond]
        if sub.empty:
            continue
        out.append({"cz_agency": cond, "n": int(len(sub)),
                    "yes_rate": round(float((sub[col] == "yes").mean()), 3)})
    return out


def primary_rate(df: pd.DataFrame, col: str) -> list[dict]:
    if col not in df.columns or df[col].dropna().empty:
        return []
    d = df.dropna(subset=[col]).copy()
    d[col] = d[col].astype(str).str.strip().str.lower()
    rate = {}
    out = []
    for cond in CONDITION_ORDER:
        sub = d[d["cz_agency"] == cond]
        if sub.empty:
            continue
        r = round(float((sub[col] == "primary").mean()), 3)
        rate[cond] = r
        out.append({"cz_agency": cond, "n": int(len(sub)), "primary_rate": r})
    base = rate.get(BASELINE)
    if base is not None:
        for row in out:
            row["delta_vs_agentive"] = round(row["primary_rate"] - base, 3)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=STUDY_DIR / "output" / "agency_analysis.json")
    args = ap.parse_args()

    run_dir = (args.run_dir or latest_run_dir()).resolve()
    coding_path = run_dir / "coding_sheet.csv"
    if not coding_path.exists():
        raise SystemExit(f"No coding_sheet.csv in {run_dir}")

    df = pd.read_csv(coding_path)
    df = df.loc[:, ~df.columns.duplicated()]
    if "cz_agency" not in df.columns:
        raise SystemExit("coding_sheet.csv has no cz_agency column -- produced by run_study.py?")

    n_coded = int(df["authority_blame_score"].notna().sum()) if "authority_blame_score" in df.columns else 0

    payload = {
        "schema_version": 1,
        "study": "czech_agency",
        "run_id": run_dir.name,  # e.g. phase3_<run_id>; separate analysis_payloads row
        "title": "Czech agency module -- responsibility attribution by agency construction",
        "subtitle": "One dilemma, only sentence 2 varies: agentive -> participial passive -> reflexive deagentive -> decision nominalization -> bureaucratic nominalization. Baseline = agentive (CA1).",
        "n": int(len(df)),
        "n_coded": n_coded,
        "conditions": CONDITION_ORDER,
        "baseline": BASELINE,
        "hypothesis": "Passive/deagentive/nominalized formulations reduce primary blame on the authorities vs the agentive baseline, and may raise diffuse responsibility, legalism, or relative-blame.",
        "by_condition": {
            "var_a": counts(df, "code_var_a"),
            "authority_blame": counts(df, "authority_blame_score"),
            "relative_blame": counts(df, "relative_blame_score"),
            "legalism": counts(df, "legalism_score"),
            "dignity": counts(df, "dignity_score"),
            "compromise_type": counts(df, "compromise_type"),
        },
        "rates": {
            "agent_recovery": yes_rate(df, "agent_recovery"),
            "passive_echo": yes_rate(df, "passive_echo"),
        },
        "primary_vs_baseline": {
            "authority_blame": primary_rate(df, "authority_blame_score"),
            "relative_blame": primary_rate(df, "relative_blame_score"),
        },
        "response_length_median": (
            df.groupby("cz_agency")["response_char_len"].median().round(0).reset_index().to_dict(orient="records")
            if "response_char_len" in df.columns else []
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}  (n={payload['n']}, coded={n_coded}, run_id={payload['run_id']})")
    if n_coded == 0:
        print("No agency codes yet -- payload has structure but empty distributions. Code first, then rebuild.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
