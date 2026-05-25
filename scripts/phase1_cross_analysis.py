"""Cross-tabulations for Phase 1: model x model, model x language, language x language."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


MODEL_SHORT = {
    "openai/gpt-4o": "gpt-4o",
    "anthropic/claude-sonnet-4": "claude4",
    "google/gemini-2.0-flash-001": "gemini2",
    "meta-llama/llama-3.3-70b-instruct": "llama3.3",
    "mistralai/mistral-large-2411": "mistralL",
    "qwen/qwen-2.5-72b-instruct": "qwen2.5",
}


def load_coding(run_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(run_dir / "coding_sheet.csv")
    # Drop accidental duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]
    df["model_short"] = df["model_requested"].map(MODEL_SHORT).fillna(df["model_requested"])
    return df


def pct_table(df: pd.DataFrame, index: str, column: str) -> pd.DataFrame:
    counts = df.groupby([index, column]).size().unstack(fill_value=0)
    pct = counts.div(counts.sum(axis=1), axis=0).round(3)
    pct.columns = [f"%{c}" for c in pct.columns]
    return counts.join(pct)


def language_by_var(df: pd.DataFrame, var: str) -> pd.DataFrame:
    return pct_table(df, "language", var)


def model_by_var(df: pd.DataFrame, var: str) -> pd.DataFrame:
    return pct_table(df, "model_short", var)


def model_by_lang_var(df: pd.DataFrame, var: str) -> pd.DataFrame:
    """rows = (model, language), columns = var counts + percent."""
    out = []
    for lang in sorted(df["language"].unique()):
        sub = df[df["language"] == lang]
        tab = pct_table(sub, "model_short", var)
        tab.insert(0, "language", lang)
        out.append(tab.reset_index())
    return pd.concat(out, ignore_index=True)


def within_model_lang_consistency(df: pd.DataFrame, var: str) -> pd.DataFrame:
    """For each (model, language), how many unique codes across 3 replicates?

    1 = perfectly consistent; 2-3 = unstable.
    """
    g = df.groupby(["model_short", "language"])[var].agg(
        n_unique=lambda s: s.nunique(dropna=True),
        modal=lambda s: s.mode(dropna=True).iloc[0] if not s.mode(dropna=True).empty else None,
        all_codes=lambda s: ",".join(sorted(set(c for c in s.dropna()))),
    )
    return g.reset_index()


def cross_language_within_model(df: pd.DataFrame, var: str) -> pd.DataFrame:
    """For each model, does the modal VAR-* differ across languages?"""
    modal_by_lang = (
        df.groupby(["model_short", "language"])[var]
        .agg(lambda s: s.mode(dropna=True).iloc[0] if not s.mode(dropna=True).empty else None)
        .unstack("language")
    )
    modal_by_lang["all_same"] = modal_by_lang.nunique(axis=1, dropna=True) == 1
    modal_by_lang["n_distinct"] = modal_by_lang.drop(columns=["all_same"]).nunique(axis=1, dropna=True)
    return modal_by_lang.reset_index()


def pairwise_model_agreement(df: pd.DataFrame, var: str) -> pd.DataFrame:
    """Compare each model pair across (stimulus, replicate) cells; rate of agreement."""
    pivot = df.pivot_table(
        index=["stimulus_id", "replicate"],
        columns="model_short",
        values=var,
        aggfunc="first",
    )
    models = list(pivot.columns)
    rows = []
    for i, m1 in enumerate(models):
        for m2 in models[i + 1 :]:
            both = pivot[[m1, m2]].dropna()
            if both.empty:
                continue
            agree = (both[m1] == both[m2]).mean()
            rows.append({"model_a": m1, "model_b": m2, "n": len(both), "agree_rate": round(float(agree), 3)})
    return pd.DataFrame(rows).sort_values("agree_rate", ascending=False)


def length_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Response length by model x language (proxy for elaborateness)."""
    g = df.groupby(["model_short", "language"])["response_char_len"].agg(
        median="median", mean="mean", min="min", max="max", n="count"
    )
    return g.round(0).reset_index()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--run-dir",
        type=Path,
        default=ROOT / "logs" / "phase1_20260525T135121Z_eab51040",
    )
    ap.add_argument("--out-dir", type=Path, default=ROOT / "output" / "phase1_v2_cross")
    args = ap.parse_args()

    df = load_coding(args.run_dir)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    targets = {
        "language_by_var_a": language_by_var(df, "code_var_a"),
        "language_by_var_b": language_by_var(df, "code_var_b"),
        "language_by_var_d": language_by_var(df, "code_var_d"),
        "language_by_var_r": language_by_var(df[df["language"] == "ja"], "code_var_r"),
        "model_by_var_a": model_by_var(df, "code_var_a"),
        "model_by_var_b": model_by_var(df, "code_var_b"),
        "model_by_var_d": model_by_var(df, "code_var_d"),
        "model_x_lang_var_a": model_by_lang_var(df, "code_var_a"),
        "model_x_lang_var_b": model_by_lang_var(df, "code_var_b"),
        "model_x_lang_var_d": model_by_lang_var(df, "code_var_d"),
        "replicate_stability_var_a": within_model_lang_consistency(df, "code_var_a"),
        "replicate_stability_var_d": within_model_lang_consistency(df, "code_var_d"),
        "cross_lang_var_a": cross_language_within_model(df, "code_var_a"),
        "cross_lang_var_d": cross_language_within_model(df, "code_var_d"),
        "pairwise_agreement_var_a": pairwise_model_agreement(df, "code_var_a"),
        "pairwise_agreement_var_d": pairwise_model_agreement(df, "code_var_d"),
        "response_length": length_summary(df),
    }

    for name, tab in targets.items():
        path = args.out_dir / f"{name}.csv"
        tab.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"  {name:32s}  ({len(tab):3d} rows)  -> {path.name}")


if __name__ == "__main__":
    main()
