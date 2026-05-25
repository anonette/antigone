#!/usr/bin/env python3
"""
Post-hoc analysis — run ONLY after logs exist.

Reads logs/ (run directories + legacy jsonl), writes output/ for visualization
and merges with manual coding columns.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from antigone.coding_heuristics import agency_heuristic, heuristic_action
from antigone.research_log import discover_log_sources, load_all_responses

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "logs"
OUTPUT = ROOT / "output"


def dedupe_latest_cell(rows: list[dict]) -> list[dict]:
    """Keep the newest row per cell_key (resume retries append duplicates)."""
    latest: dict[str, dict] = {}
    for row in rows:
        key = row.get("cell_key")
        if not key:
            continue
        prev = latest.get(key)
        if prev is None or row.get("timestamp_utc", "") >= prev.get("timestamp_utc", ""):
            latest[key] = row
    return list(latest.values()) if latest else rows


def rows_to_dataframe(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if "response_char_len" not in df.columns and "response_text" in df.columns:
        df["response_char_len"] = df["response_text"].fillna("").str.len()
    if "heuristic_action" not in df.columns:
        df["heuristic_action"] = df.apply(
            lambda r: heuristic_action(r.get("response_text"), r.get("language")),
            axis=1,
        )
    if "agency_heuristic" not in df.columns:
        df["agency_heuristic"] = df.apply(
            lambda r: agency_heuristic(r.get("response_text"), r.get("language")),
            axis=1,
        )
    return df


def plot_heatmap(
    df: pd.DataFrame,
    value_col: str,
    path: Path,
    title: str,
) -> None:
    if df.empty:
        return
    pivot = df.pivot_table(
        index="model_requested",
        columns="stimulus_id",
        values=value_col,
        aggfunc="mean",
    )
    fig, ax = plt.subplots(figsize=(max(8, pivot.shape[1] * 0.5), max(4, pivot.shape[0] * 0.4)))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels(pivot.index, fontsize=8)
    ax.set_title(title)
    plt.colorbar(im, ax=ax, label=value_col)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_language_comparison(df: pd.DataFrame, path: Path) -> None:
    p1 = df[(df["phase"] == 1) & (df["status"] == "ok")]
    if p1.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, col in zip(axes, ["response_char_len", "latency_ms"]):
        if col not in p1.columns:
            continue
        p1.boxplot(column=col, by="language", ax=ax)
        ax.set_title(col)
        ax.set_xlabel("language")
    fig.suptitle("Phase 1 — by language")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_baseline_shift(df: pd.DataFrame, path: Path) -> None:
    """Phase 2: mean response length vs baseline_stimulus_id match."""
    p2 = df[(df["phase"] == 2) & (df["status"] == "ok")].copy()
    if p2.empty or "baseline_stimulus_id" not in p2.columns:
        return
    p2["is_baseline_cell"] = p2["stimulus_id"] == p2["baseline_stimulus_id"]
    agg = (
        p2.groupby(["language", "stimulus_id", "is_baseline_cell"])["response_char_len"]
        .mean()
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(12, 5))
    for lang in agg["language"].dropna().unique():
        sub = agg[agg["language"] == lang]
        ax.plot(
            range(len(sub)),
            sub["response_char_len"],
            marker="o",
            label=str(lang),
            alpha=0.7,
        )
    ax.set_title("Phase 2 mean response length by cell (exploratory)")
    ax.set_ylabel("chars")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze Antigone logs for research viz")
    ap.add_argument("--logs", nargs="*", help="Specific run dirs or jsonl files")
    ap.add_argument("--phase", type=int, choices=[1, 2], help="Filter by phase")
    ap.add_argument("--run-id", help="Filter to one run (directory name contains this)")
    ap.add_argument("--out", type=Path, default=OUTPUT, help="Output directory")
    args = ap.parse_args()

    if args.logs:
        rows = []
        for p in args.logs:
            path = Path(p)
            jsonl = path / "responses.jsonl" if path.is_dir() else path
            with jsonl.open(encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rows.append(json.loads(line))
    else:
        rows = load_all_responses(LOGS, phase=args.phase)

    if args.run_id:
        rows = [r for r in rows if args.run_id in r.get("run_id", "")]

    rows = dedupe_latest_cell(rows)

    if not rows:
        raise SystemExit(f"No log rows in {LOGS}. Run run.py first.")

    df = rows_to_dataframe(rows)
    if args.phase is not None and "phase" in df.columns:
        df = df[df["phase"] == args.phase]

    args.out.mkdir(parents=True, exist_ok=True)
    ok = df[df["status"] == "ok"].copy()

    # --- Master analysis table (parquet if available, else csv) ---
    master_path = args.out / "analysis_master.csv"
    ok.to_csv(master_path, index=False)

    # --- Index of runs ---
    index_rows = []
    for src in discover_log_sources(LOGS):
        manifest = {}
        if src.get("manifest") and Path(src["manifest"]).exists():
            manifest = json.loads(Path(src["manifest"]).read_text(encoding="utf-8"))
        index_rows.append(
            {
                "run_id": src["run_id"],
                "type": src["type"],
                "path": str(src["path"]),
                "planned_n": manifest.get("design", {}).get("planned_requests"),
                "completed_ok": manifest.get("stats", {}).get("ok"),
                "errors": manifest.get("stats", {}).get("error"),
            }
        )
    pd.DataFrame(index_rows).to_csv(args.out / "runs_index.csv", index=False)

    # --- Aggregates for visualization ---
    if not ok.empty:
        by_cell = (
            ok.groupby(
                ["phase", "language", "model_requested", "model_group", "stimulus_id", "baseline_stimulus_id"],
                dropna=False,
            )
            .agg(
                n=("record_id", "count"),
                mean_chars=("response_char_len", "mean"),
                mean_latency_ms=("latency_ms", "mean"),
                mean_tokens=("tokens_total", "mean"),
                share_reasoning=("has_reasoning", "mean"),
            )
            .reset_index()
        )
        by_cell.to_csv(args.out / "aggregate_by_cell.csv", index=False)

        # Heuristic action counts (exploratory)
        if "heuristic_action" in ok.columns:
            pd.crosstab(
                [ok["model_group"], ok["model_requested"]],
                [ok["language"], ok["stimulus_id"], ok["heuristic_action"]],
            ).to_csv(args.out / "heuristic_action_counts.csv")

        # Phase 1: language × model
        p1 = ok[ok["phase"] == 1]
        if not p1.empty:
            plot_language_comparison(p1, args.out / "phase1_by_language.png")
            ct = pd.crosstab(p1["language"], p1["heuristic_action"], normalize="index")
            ct.to_csv(args.out / "phase1_heuristic_by_language.csv")
            fig, ax = plt.subplots(figsize=(8, 4))
            ct.plot(kind="bar", stacked=True, ax=ax)
            ax.set_title("Phase 1 — exploratory action keywords by language")
            ax.legend(bbox_to_anchor=(1.02, 1), fontsize=7)
            fig.tight_layout()
            fig.savefig(args.out / "phase1_heuristic_stacked.png", dpi=150)
            plt.close(fig)

        # Heatmaps: model × stimulus
        plot_heatmap(
            ok[ok["phase"] == 1],
            "response_char_len",
            args.out / "heatmap_p1_response_chars.png",
            "Phase 1 — mean response length (model × stimulus)",
        )
        plot_heatmap(
            ok[ok["phase"] == 2],
            "response_char_len",
            args.out / "heatmap_p2_response_chars.png",
            "Phase 2 — mean response length (model × stimulus)",
        )
        plot_baseline_shift(ok, args.out / "phase2_length_by_cell.png")

        # Model group comparison
        if "model_group" in ok.columns:
            fig, ax = plt.subplots(figsize=(10, 4))
            ok.groupby("model_group")["response_char_len"].mean().sort_values().plot(kind="barh", ax=ax)
            ax.set_xlabel("Mean response chars")
            ax.set_title("By model group (all phases in filter)")
            fig.tight_layout()
            fig.savefig(args.out / "mean_chars_by_model_group.png", dpi=150)
            plt.close(fig)

    err = df[df["status"] != "ok"]
    if not err.empty:
        err.to_csv(args.out / "errors.csv", index=False)

    print(f"Rows: {len(df)} total | {len(ok)} ok | {len(err)} errors")
    print(f"Output: {args.out.resolve()}")
    print(f"  analysis_master.csv — full ok rows for R/ggplot/pandas")
    print(f"  aggregate_by_cell.csv — pre-aggregated for charts")
    print(f"  runs_index.csv — all discovered runs")
    print(f"  coding: use logs/*/coding_sheet.csv (fill code_var_* columns)")


if __name__ == "__main__":
    main()
