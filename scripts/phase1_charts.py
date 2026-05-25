"""Render charts for Phase 1 v2 cross-analysis (PNG + JSON for Lovable)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

VAR_A_ORDER = ["obey", "secret_bury", "legal_challenge", "compromise", "undecided"]
VAR_B_ORDER = ["authorities", "deceased", "law_rule", "relative", "society", "distributed"]
VAR_D_ORDER = ["institutional", "individualized", "deagentive", "relational_affected", "circumstantial"]

# Colour-blind safe Okabe-Ito subset + extras
COLOURS = {
    "obey": "#999999",
    "compromise": "#56B4E9",
    "legal_challenge": "#009E73",
    "secret_bury": "#D55E00",
    "undecided": "#F0E442",
    "authorities": "#0072B2",
    "deceased": "#CC79A7",
    "distributed": "#E69F00",
    "law_rule": "#999999",
    "relative": "#D55E00",
    "society": "#56B4E9",
    "institutional": "#0072B2",
    "individualized": "#D55E00",
    "deagentive": "#999999",
    "relational_affected": "#CC79A7",
    "circumstantial": "#F0E442",
}

LANG_COLOR = {"en": "#3D6B4F", "cs": "#4A6FA5", "ja": "#C45C3E"}

MODEL_ORDER = ["gpt-4o", "claude4", "gemini2", "llama3.3", "mistralL", "qwen2.5"]
LANG_ORDER = ["en", "cs", "ja"]


def stacked_pct(ax, df: pd.DataFrame, value_order: list[str], title: str, ylabel: str) -> None:
    """df has integer counts, index = group, columns = codes."""
    df = df.reindex(columns=[c for c in value_order if c in df.columns], fill_value=0)
    df_pct = df.div(df.sum(axis=1), axis=0).fillna(0)
    bottom = np.zeros(len(df_pct))
    xs = np.arange(len(df_pct))
    for code in df_pct.columns:
        ax.bar(xs, df_pct[code], bottom=bottom, label=code, color=COLOURS.get(code, "#666666"))
        for i, v in enumerate(df_pct[code]):
            if v >= 0.05:
                ax.text(xs[i], bottom[i] + v / 2, f"{int(v * 100)}%", ha="center", va="center",
                        fontsize=8, color="black")
        bottom += df_pct[code].values
    ax.set_xticks(xs)
    ax.set_xticklabels(df_pct.index, rotation=0)
    ax.set_ylim(0, 1.02)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8, frameon=False)


def chart_language_var_a(df: pd.DataFrame, out: Path) -> None:
    counts = df.groupby(["language", "code_var_a"]).size().unstack(fill_value=0).reindex(LANG_ORDER)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    stacked_pct(ax, counts, VAR_A_ORDER, "VAR-A by language (Phase 1, pooled 6 models × 3 reps)", "Share of responses")
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)


def chart_language_var_b(df: pd.DataFrame, out: Path) -> None:
    counts = df.groupby(["language", "code_var_b"]).size().unstack(fill_value=0).reindex(LANG_ORDER)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    stacked_pct(ax, counts, VAR_B_ORDER, "VAR-B (responsibility) by language", "Share of responses")
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)


def chart_language_var_d(df: pd.DataFrame, out: Path) -> None:
    counts = df.groupby(["language", "code_var_d"]).size().unstack(fill_value=0).reindex(LANG_ORDER)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    stacked_pct(ax, counts, VAR_D_ORDER, "VAR-D (agency in reply) by language", "Share of responses")
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)


def chart_model_var_a_by_lang(df: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    for ax, lang in zip(axes, LANG_ORDER):
        sub = df[df["language"] == lang]
        counts = (
            sub.groupby(["model_short", "code_var_a"]).size().unstack(fill_value=0).reindex(MODEL_ORDER, fill_value=0)
        )
        stacked_pct(ax, counts, VAR_A_ORDER, f"VAR-A · {lang.upper()}", "")
        if ax is axes[0]:
            ax.set_ylabel("Share of replicates (n=3)")
    fig.suptitle("VAR-A by model × language (each cell: 3 replicates)", y=1.02)
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)


def chart_modal_heatmap(df: pd.DataFrame, var: str, out: Path) -> None:
    pivot = (
        df.groupby(["model_short", "language"])[var]
        .agg(lambda s: s.mode(dropna=True).iloc[0] if not s.mode(dropna=True).empty else None)
        .unstack("language")
        .reindex(index=MODEL_ORDER, columns=LANG_ORDER)
    )
    codes = sorted({v for v in pivot.values.ravel() if isinstance(v, str)})
    code_to_id = {c: i for i, c in enumerate(codes)}
    arr = np.full(pivot.shape, np.nan)
    for i, m in enumerate(pivot.index):
        for j, c in enumerate(pivot.columns):
            v = pivot.loc[m, c]
            if isinstance(v, str):
                arr[i, j] = code_to_id[v]

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    cmap = plt.get_cmap("Set2", len(codes))
    im = ax.imshow(arr, cmap=cmap, aspect="auto", vmin=-0.5, vmax=len(codes) - 0.5)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([c.upper() for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            v = pivot.iat[i, j]
            if isinstance(v, str):
                ax.text(j, i, v, ha="center", va="center", fontsize=9, color="black",
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.6, lw=0))
    cbar = fig.colorbar(im, ax=ax, ticks=range(len(codes)))
    cbar.ax.set_yticklabels(codes)
    ax.set_title(f"Modal {var} per (model × language) — does the verdict shift?")
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)


def chart_pair_agreement(df: pd.DataFrame, var: str, out: Path) -> None:
    pivot = df.pivot_table(
        index=["stimulus_id", "replicate"], columns="model_short", values=var, aggfunc="first"
    )
    models = MODEL_ORDER
    mat = np.full((len(models), len(models)), np.nan)
    for i, m1 in enumerate(models):
        for j, m2 in enumerate(models):
            if m1 not in pivot.columns or m2 not in pivot.columns:
                continue
            if i == j:
                mat[i, j] = 1.0
                continue
            both = pivot[[m1, m2]].dropna()
            if both.empty:
                continue
            mat[i, j] = (both[m1] == both[m2]).mean()
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(mat, cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, rotation=30, ha="right")
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models)
    for i in range(len(models)):
        for j in range(len(models)):
            v = mat[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        color="black" if v > 0.4 else "white", fontsize=9)
    fig.colorbar(im, ax=ax, label="agreement rate")
    ax.set_title(f"Pairwise model agreement on {var} (across 9 cells = 3 langs × 3 reps)")
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)


def chart_replicate_stability(df: pd.DataFrame, out: Path) -> None:
    g = df.groupby(["model_short", "language"])["code_var_a"].agg(
        n_unique=lambda s: s.nunique(dropna=True)
    ).reset_index()
    pivot = g.pivot(index="model_short", columns="language", values="n_unique").reindex(MODEL_ORDER)[LANG_ORDER]
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    im = ax.imshow(pivot.values, cmap="RdYlGn_r", vmin=1, vmax=3)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([c.upper() for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = int(pivot.iat[i, j])
            ax.text(j, i, str(v), ha="center", va="center", color="black", fontsize=11, fontweight="bold")
    fig.colorbar(im, ax=ax, label="distinct VAR-A codes / 3 replicates", ticks=[1, 2, 3])
    ax.set_title("Replicate stability (temperature = 0; 1 = stable, 3 = chaotic)")
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)


def chart_response_length(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    width = 0.25
    xs = np.arange(len(MODEL_ORDER))
    for k, lang in enumerate(LANG_ORDER):
        meds = []
        for m in MODEL_ORDER:
            sub = df[(df["language"] == lang) & (df["model_short"] == m)]
            meds.append(sub["response_char_len"].median() if not sub.empty else 0)
        ax.bar(xs + (k - 1) * width, meds, width, label=lang.upper(), color=LANG_COLOR[lang])
    ax.set_xticks(xs)
    ax.set_xticklabels(MODEL_ORDER)
    ax.set_ylabel("Median response length (chars)")
    ax.set_title("Response length — model × language (median over 3 replicates)")
    ax.legend(title="Language", frameon=False)
    ax.set_yscale("log")
    fig.tight_layout()
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)


def export_chart_data_json(df: pd.DataFrame, out: Path) -> None:
    """For Lovable Recharts: pre-aggregated counts as JSON."""

    def grp_counts(group_cols: list[str], code_col: str) -> list[dict]:
        sub = df.groupby([*group_cols, code_col]).size().reset_index(name="n")
        return sub.to_dict(orient="records")

    payload = {
        "schema_version": 1,
        "run_id": df["run_id"].iloc[0] if not df.empty else None,
        "n": int(len(df)),
        "languages": sorted(df["language"].unique().tolist()),
        "models": MODEL_ORDER,
        "model_label_map": {
            "gpt-4o": "openai/gpt-4o",
            "claude4": "anthropic/claude-sonnet-4",
            "gemini2": "google/gemini-2.0-flash-001",
            "llama3.3": "meta-llama/llama-3.3-70b-instruct",
            "mistralL": "mistralai/mistral-large-2411",
            "qwen2.5": "qwen/qwen-2.5-72b-instruct",
        },
        "by_language": {
            "var_a": grp_counts(["language"], "code_var_a"),
            "var_b": grp_counts(["language"], "code_var_b"),
            "var_d": grp_counts(["language"], "code_var_d"),
            "var_r_ja": grp_counts(
                ["language"], "code_var_r"
            )
            if (df["language"] == "ja").any()
            else [],
        },
        "by_model": {
            "var_a": grp_counts(["model_short"], "code_var_a"),
        },
        "by_model_language": {
            "var_a": grp_counts(["model_short", "language"], "code_var_a"),
            "var_b": grp_counts(["model_short", "language"], "code_var_b"),
            "var_d": grp_counts(["model_short", "language"], "code_var_d"),
        },
        "modal_per_cell_var_a": df.groupby(["model_short", "language"])["code_var_a"]
        .agg(lambda s: s.mode(dropna=True).iloc[0] if not s.mode(dropna=True).empty else None)
        .reset_index()
        .to_dict(orient="records"),
        "response_length_median": df.groupby(["model_short", "language"])["response_char_len"]
        .median()
        .reset_index()
        .to_dict(orient="records"),
        "replicate_stability_var_a": df.groupby(["model_short", "language"])["code_var_a"]
        .agg(n_unique=lambda s: s.nunique(dropna=True))
        .reset_index()
        .to_dict(orient="records"),
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


MODEL_SHORT = {
    "openai/gpt-4o": "gpt-4o",
    "anthropic/claude-sonnet-4": "claude4",
    "google/gemini-2.0-flash-001": "gemini2",
    "meta-llama/llama-3.3-70b-instruct": "llama3.3",
    "mistralai/mistral-large-2411": "mistralL",
    "qwen/qwen-2.5-72b-instruct": "qwen2.5",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--run-dir",
        type=Path,
        default=ROOT / "logs" / "phase1_20260525T135121Z_eab51040",
    )
    ap.add_argument("--out-dir", type=Path, default=ROOT / "output" / "phase1_v2_cross" / "charts")
    args = ap.parse_args()

    df = pd.read_csv(args.run_dir / "coding_sheet.csv")
    df = df.loc[:, ~df.columns.duplicated()]
    df["model_short"] = df["model_requested"].map(MODEL_SHORT).fillna(df["model_requested"])

    args.out_dir.mkdir(parents=True, exist_ok=True)

    chart_language_var_a(df, args.out_dir / "01_var_a_by_language.png")
    chart_language_var_b(df, args.out_dir / "02_var_b_by_language.png")
    chart_language_var_d(df, args.out_dir / "03_var_d_by_language.png")
    chart_model_var_a_by_lang(df, args.out_dir / "04_var_a_model_x_language.png")
    chart_modal_heatmap(df, "code_var_a", args.out_dir / "05_modal_var_a_heatmap.png")
    chart_modal_heatmap(df, "code_var_b", args.out_dir / "06_modal_var_b_heatmap.png")
    chart_pair_agreement(df, "code_var_a", args.out_dir / "07_pairwise_agreement_var_a.png")
    chart_replicate_stability(df, args.out_dir / "08_replicate_stability_var_a.png")
    chart_response_length(df, args.out_dir / "09_response_length.png")

    json_path = args.out_dir.parent / "analysis_chart_data.json"
    export_chart_data_json(df, json_path)

    print(f"Charts: {args.out_dir}")
    print(f"Lovable seed: {json_path}")


if __name__ == "__main__":
    main()
