#!/usr/bin/env python3
"""Analyze the Czech agency sub-study: each condition vs the CA1 agentive baseline.

Reads a run's coding_sheet.csv (after manual coding) and writes per-condition
tables + charts to studies/czech_agency/output/. Designed to degrade gracefully
when codes are not filled in yet (it still reports response counts and lengths).

Usage:
  python studies/czech_agency/analyze_study.py
  python studies/czech_agency/analyze_study.py --run-dir studies/czech_agency/logs/phase3_<run_id>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

STUDY_DIR = Path(__file__).resolve().parent

CONDITION_ORDER = [
    "agentive",
    "participial_passive",
    "reflexive_deagentive",
    "decision_nominalization",
    "bureaucratic_nominalization",
]
SCORE_ORDER = ["none", "partial", "primary"]
LEVEL_ORDER = ["low", "mid", "high"]
BASELINE = "agentive"


def latest_run_dir() -> Path:
    runs = sorted((STUDY_DIR / "logs").glob("phase3_*"))
    runs = [r for r in runs if r.is_dir()]
    if not runs:
        raise SystemExit("No runs found under studies/czech_agency/logs/. Run run_study.py first.")
    return runs[-1]


def share_table(df: pd.DataFrame, value_col: str, order: list[str] | None = None) -> pd.DataFrame:
    """Percent of responses per cz_agency condition for each value of value_col."""
    if value_col not in df.columns or df[value_col].dropna().empty:
        return pd.DataFrame()
    counts = (
        df.dropna(subset=[value_col])
        .assign(**{value_col: lambda d: d[value_col].astype(str).str.strip()})
        .groupby(["cz_agency", value_col])
        .size()
        .unstack(fill_value=0)
    )
    if order:
        counts = counts.reindex(columns=[c for c in order if c in counts.columns], fill_value=0)
    counts = counts.reindex(index=[c for c in CONDITION_ORDER if c in counts.index])
    pct = counts.div(counts.sum(axis=1).replace(0, 1), axis=0).round(3)
    pct.columns = [f"%{c}" for c in pct.columns]
    return counts.join(pct)


def yes_rate(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if col not in df.columns or df[col].dropna().empty:
        return pd.DataFrame()
    d = df.dropna(subset=[col]).copy()
    d[col] = d[col].astype(str).str.strip().str.lower()
    g = d.groupby("cz_agency")[col].agg(
        n="count",
        yes=lambda s: (s == "yes").sum(),
    )
    g["yes_rate"] = (g["yes"] / g["n"].replace(0, 1)).round(3)
    return g.reindex([c for c in CONDITION_ORDER if c in g.index])


def primary_blame_vs_baseline(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Share of `primary` for a blame column per condition, with delta vs baseline."""
    if col not in df.columns or df[col].dropna().empty:
        return pd.DataFrame()
    d = df.dropna(subset=[col]).copy()
    d[col] = d[col].astype(str).str.strip().str.lower()
    g = d.groupby("cz_agency")[col].agg(
        n="count",
        primary=lambda s: (s == "primary").sum(),
    )
    g["primary_rate"] = (g["primary"] / g["n"].replace(0, 1)).round(3)
    g = g.reindex([c for c in CONDITION_ORDER if c in g.index])
    base = g.loc[BASELINE, "primary_rate"] if BASELINE in g.index else float("nan")
    g["delta_vs_agentive"] = (g["primary_rate"] - base).round(3)
    return g


def bar_share(pct_table: pd.DataFrame, title: str, out: Path) -> None:
    if pct_table.empty:
        return
    pct_cols = [c for c in pct_table.columns if c.startswith("%")]
    if not pct_cols:
        return
    data = pct_table[pct_cols]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bottom = [0.0] * len(data)
    xs = range(len(data))
    for col in pct_cols:
        vals = data[col].tolist()
        ax.bar(list(xs), vals, bottom=bottom, label=col.lstrip("%"))
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_xticks(list(xs))
    ax.set_xticklabels(data.index, rotation=20, ha="right")
    ax.set_ylim(0, 1.02)
    ax.set_ylabel("share of responses")
    ax.set_title(title)
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)


def bar_rate(rate_table: pd.DataFrame, value_col: str, title: str, out: Path) -> None:
    if rate_table.empty or value_col not in rate_table.columns:
        return
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(range(len(rate_table)), rate_table[value_col].tolist())
    ax.set_xticks(range(len(rate_table)))
    ax.set_xticklabels(rate_table.index, rotation=20, ha="right")
    ax.set_ylim(0, 1.02)
    ax.set_ylabel(value_col)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=STUDY_DIR / "output")
    args = ap.parse_args()

    run_dir = (args.run_dir or latest_run_dir()).resolve()
    coding_path = run_dir / "coding_sheet.csv"
    if not coding_path.exists():
        raise SystemExit(f"No coding_sheet.csv in {run_dir}")

    df = pd.read_csv(coding_path)
    df = df.loc[:, ~df.columns.duplicated()]
    if "cz_agency" not in df.columns:
        raise SystemExit("coding_sheet.csv has no cz_agency column -- was it produced by run_study.py?")

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    charts = out_dir / "charts"
    charts.mkdir(parents=True, exist_ok=True)

    n_total = len(df)
    n_coded = int(df["authority_blame_score"].notna().sum()) if "authority_blame_score" in df.columns else 0
    print(f"Run: {run_dir.name} | responses: {n_total} | authority_blame coded: {n_coded}")

    # Always-available: counts and response length by condition.
    length = (
        df.groupby("cz_agency")["response_char_len"].agg(n="count", median="median", mean="mean").round(0)
        if "response_char_len" in df.columns
        else pd.DataFrame()
    )
    if not length.empty:
        length = length.reindex([c for c in CONDITION_ORDER if c in length.index])
        length.to_csv(out_dir / "response_length_by_condition.csv", encoding="utf-8-sig")

    tables = {
        "var_a_by_condition": share_table(df, "code_var_a"),
        "authority_blame_by_condition": share_table(df, "authority_blame_score", SCORE_ORDER),
        "relative_blame_by_condition": share_table(df, "relative_blame_score", SCORE_ORDER),
        "legalism_by_condition": share_table(df, "legalism_score", LEVEL_ORDER),
        "dignity_by_condition": share_table(df, "dignity_score", LEVEL_ORDER),
        "compromise_type_by_condition": share_table(df, "compromise_type"),
        "agent_recovery_rate": yes_rate(df, "agent_recovery"),
        "passive_echo_rate": yes_rate(df, "passive_echo"),
        "authority_primary_vs_agentive": primary_blame_vs_baseline(df, "authority_blame_score"),
        "relative_primary_vs_agentive": primary_blame_vs_baseline(df, "relative_blame_score"),
    }

    written = 0
    for name, tab in tables.items():
        if tab.empty:
            continue
        tab.to_csv(out_dir / f"{name}.csv", encoding="utf-8-sig")
        written += 1

    # Charts (only those with data)
    bar_share(tables["authority_blame_by_condition"], "Authority blame by condition (CA1=agentive baseline)",
              charts / "authority_blame_by_condition.png")
    bar_share(tables["var_a_by_condition"], "Recommendation (VAR-A) by condition", charts / "var_a_by_condition.png")
    bar_rate(tables["agent_recovery_rate"], "yes_rate", "Agent recovery rate by condition (re-names the hidden agent)",
             charts / "agent_recovery_rate.png")
    bar_rate(tables["passive_echo_rate"], "yes_rate", "Passive-echo rate by condition (repeats deagentive wording)",
             charts / "passive_echo_rate.png")

    print(f"Wrote {written} tables + charts to {out_dir}")
    if n_coded == 0:
        print("No agency codes filled yet -- only counts/length were computed. "
              "Fill code_var_a + agency columns in coding_sheet.csv, then re-run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
