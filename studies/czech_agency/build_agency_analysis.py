#!/usr/bin/env python3
"""Build Lovable analysis payloads for the Czech agency module.

Produces per-run JSON (keyed by run_id) plus an optional combined payload
with main-vs-control comparison and structured findings (Phase 1 shape).

  python studies/czech_agency/build_agency_analysis.py --all
  python push_analysis_to_lovable.py studies/czech_agency/output/agency_comparison.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

STUDY_DIR = Path(__file__).resolve().parent
MAIN_RUN_ID = "phase3_20260529T112210Z_77ea6d3b"
CONTROL_RUN_ID = "phase3_20260529T125836Z_6570a5fc"

CONDITION_ORDER = [
    "agentive",
    "participial_passive",
    "reflexive_deagentive",
    "decision_nominalization",
    "bureaucratic_nominalization",
]
BASELINE = "agentive"

MODEL_SHORT = {
    "openai/gpt-4o": "gpt-4o",
    "anthropic/claude-sonnet-4": "claude-sonnet-4",
    "google/gemini-2.0-flash-001": "gemini-2.0-flash",
    "meta-llama/llama-3.3-70b-instruct": "llama-3.3-70b",
    "mistralai/mistral-large-2411": "mistral-large",
    "qwen/qwen-2.5-72b-instruct": "qwen-2.5-72b",
}


def latest_run_dir() -> Path:
    runs = sorted((STUDY_DIR / "logs").glob("phase3_*"))
    runs = [r for r in runs if r.is_dir()]
    if not runs:
        raise SystemExit("No runs under studies/czech_agency/logs/. Run run_study.py first.")
    return runs[-1]


def run_variant(run_dir: Path) -> str:
    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        stimuli = (manifest.get("design") or {}).get("stimuli") or []
        if any(str(s).startswith("CN") for s in stimuli):
            return "control_no_question"
    return "main"


def load_coding(run_dir: Path) -> pd.DataFrame:
    coding_path = run_dir / "coding_sheet.csv"
    if not coding_path.exists():
        raise SystemExit(f"No coding_sheet.csv in {run_dir}")
    df = pd.read_csv(coding_path)
    df = df.loc[:, ~df.columns.duplicated()]
    if "cz_agency" not in df.columns:
        raise SystemExit("coding_sheet.csv has no cz_agency column -- produced by run_study.py?")
    return df


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
        out.append(
            {
                "cz_agency": cond,
                "n": int(len(sub)),
                "yes_rate": round(float((sub[col] == "yes").mean()), 3),
            }
        )
    return out


def yes_rate_by_model(df: pd.DataFrame, col: str) -> list[dict]:
    if col not in df.columns or "model_requested" not in df.columns:
        return []
    d = df.dropna(subset=[col]).copy()
    d[col] = d[col].astype(str).str.strip().str.lower()
    out = []
    for model in sorted(d["model_requested"].unique()):
        sub = d[d["model_requested"] == model]
        out.append(
            {
                "model": model,
                "model_short": MODEL_SHORT.get(model, model.split("/")[-1]),
                "n": int(len(sub)),
                "yes_rate": round(float((sub[col] == "yes").mean()), 3),
            }
        )
    return out


def yes_rate_model_condition(df: pd.DataFrame, col: str) -> list[dict]:
    if col not in df.columns or "model_requested" not in df.columns:
        return []
    d = df.dropna(subset=[col]).copy()
    d[col] = d[col].astype(str).str.strip().str.lower()
    out = []
    for cond in CONDITION_ORDER:
        for model in sorted(d["model_requested"].unique()):
            sub = d[(d["cz_agency"] == cond) & (d["model_requested"] == model)]
            if sub.empty:
                continue
            out.append(
                {
                    "cz_agency": cond,
                    "model": model,
                    "model_short": MODEL_SHORT.get(model, model.split("/")[-1]),
                    "n": int(len(sub)),
                    "yes_rate": round(float((sub[col] == "yes").mean()), 3),
                }
            )
    return out


def primary_rate(df: pd.DataFrame, col: str) -> list[dict]:
    if col not in df.columns or df[col].dropna().empty:
        return []
    d = df.dropna(subset=[col]).copy()
    d[col] = d[col].astype(str).str.strip().str.lower()
    rate: dict[str, float] = {}
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


def primary_rate_by_model(df: pd.DataFrame, col: str) -> list[dict]:
    if col not in df.columns or "model_requested" not in df.columns:
        return []
    d = df.dropna(subset=[col]).copy()
    d[col] = d[col].astype(str).str.strip().str.lower()
    out = []
    for model in sorted(d["model_requested"].unique()):
        sub = d[d["model_requested"] == model]
        out.append(
            {
                "model": model,
                "model_short": MODEL_SHORT.get(model, model.split("/")[-1]),
                "n": int(len(sub)),
                "primary_rate": round(float((sub[col] == "primary").mean()), 3),
            }
        )
    return out


def rate_lookup(rows: list[dict], cond: str, key: str = "yes_rate") -> float | None:
    for row in rows:
        if row.get("cz_agency") == cond:
            return row.get(key)
    return None


def build_comparison(
    main_recovery: list[dict],
    ctrl_recovery: list[dict],
    main_authority: list[dict],
) -> dict[str, Any]:
    agent_recovery = []
    for cond in CONDITION_ORDER:
        with_q = rate_lookup(main_recovery, cond)
        without_q = rate_lookup(ctrl_recovery, cond)
        row: dict[str, Any] = {"cz_agency": cond}
        if with_q is not None:
            row["with_question"] = with_q
        if without_q is not None:
            row["no_question"] = without_q
        if with_q is not None and without_q is not None:
            row["delta_no_question_vs_with"] = round(without_q - with_q, 3)
        agent_recovery.append(row)

    authority_primary = []
    base = rate_lookup(main_authority, BASELINE, "primary_rate")
    for cond in CONDITION_ORDER:
        pr = rate_lookup(main_authority, cond, "primary_rate")
        if pr is None:
            continue
        authority_primary.append(
            {
                "cz_agency": cond,
                "primary_rate": pr,
                "delta_vs_agentive": round(pr - base, 3) if base is not None else None,
            }
        )

    return {
        "agent_recovery": agent_recovery,
        "authority_primary_main_only": authority_primary,
        "control_spontaneous_blame": {
            "coded_n": 5,
            "total_n": 125,
            "note": "Do not chart authority_blame for control; n too small.",
        },
    }


def build_findings(
    main_df: pd.DataFrame,
    ctrl_df: pd.DataFrame,
    comparison: dict[str, Any],
) -> dict[str, Any]:
    main_rec = {r["cz_agency"]: r["yes_rate"] for r in yes_rate(main_df, "agent_recovery")}
    ctrl_rec = {r["cz_agency"]: r["yes_rate"] for r in yes_rate(ctrl_df, "agent_recovery")}
    main_auth = {r["cz_agency"]: r["primary_rate"] for r in primary_rate(main_df, "authority_blame_score")}

    compromise_n = int((main_df["code_var_a"].astype(str).str.lower() == "compromise").sum())
    obey_n = int((main_df["code_var_a"].astype(str).str.lower() == "obey").sum())
    secret_n = int((main_df["code_var_a"].astype(str).str.lower() == "secret_bury").sum())

    claude_ctrl = next(
        (r["yes_rate"] for r in yes_rate_by_model(ctrl_df, "agent_recovery")
         if r["model"] == "anthropic/claude-sonnet-4"),
        None,
    )
    gemini_ctrl = next(
        (r["yes_rate"] for r in yes_rate_by_model(ctrl_df, "agent_recovery")
         if r["model"] == "google/gemini-2.0-flash-001"),
        None,
    )

    findings_list = [
        {
            "id": 1,
            "title": "Explicit blame is question-driven, not grammar-driven",
            "tag": "central_finding",
            "summary": (
                "When asked 'Kdo nese odpovědnost…?', authority blame is primary in 92–100% of "
                "responses in every grammar condition (flat ceiling). Without that question, only "
                "5/125 control responses receive a coded blame score. The dramatic main-set result "
                "is largely a measurement artifact of asking."
            ),
            "evidence": (
                f"main authority primary: agentive {main_auth.get('agentive', 0):.0%}–"
                f"reflexive {main_auth.get('reflexive_deagentive', 0):.0%}; "
                "control coded blame 5/125"
            ),
            "related_chart": "authority_blame_by_condition",
            "implication": "Do not infer from the main run alone that Czech agency grammar fails to "
            "deflect blame in naturalistic use — the question forces agent naming.",
        },
        {
            "id": 2,
            "title": "Grammar affects spontaneous agent-naming — but only without the question",
            "tag": "central_finding",
            "summary": (
                "Agent recovery is flat 96–100% with the responsibility question. In the no-question "
                f"control it drops to ~72% on deagentive/nominalized cells vs {ctrl_rec.get('agentive', 0):.0%} "
                "agentive baseline — a ~16–28 point gradient masked when blame is explicitly solicited."
            ),
            "evidence": "comparison.agent_recovery (with_question vs no_question per condition)",
            "related_chart": "agent_recovery_comparison",
            "implication": "Pergler-style agency management has a real but modest effect on spontaneous "
            "institutional naming in LLMs; the responsibility question saturates it.",
        },
        {
            "id": 3,
            "title": "Models are agent-restorers, never passive echoers",
            "tag": "central_finding",
            "summary": (
                "passive_echo = 0% in both main and control (125+125 cells). Models do not extend "
                "deagentive stimulus wording; they rewrite into agentive analytic prose or procedural "
                "recommendation."
            ),
            "evidence": "rates.passive_echo — all conditions 0.0",
            "related_chart": "passive_echo_rate",
            "implication": "Instruct-tuning normalises input register; LLMs repair hidden agents rather "
            "than mirroring bureaucratic defocusing.",
        },
        {
            "id": 4,
            "title": "Compromise dominates; obey and secret burial never win",
            "tag": "central_finding",
            "summary": (
                f"VAR-A compromise in {compromise_n}/125 main responses (68–84% per condition). "
                f"obey={obey_n}, secret_bury={secret_n} across all cells. Same third-path rerouting as Phase 1."
            ),
            "evidence": "by_condition.var_a",
            "related_chart": "var_a_by_condition",
            "implication": "Grammar of sentence 2 does not unlock the obey/defy binary; models reroute to negotiation.",
        },
        {
            "id": 5,
            "title": "Claude respects deagentive grammar; Gemini always recovers the agent",
            "tag": "model_heterogeneity",
            "summary": (
                f"In the control, Claude agent_recovery = {claude_ctrl:.0%} pooled; Gemini = {gemini_ctrl:.0%}. "
                "Claude drops to 0–20% recovery on participial/reflexive cells; Gemini stays at 100% in every "
                "condition. Pooled condition rates hide this split."
            ),
            "evidence": "by_model.agent_recovery (control) + by_model_condition.agent_recovery",
            "related_chart": "agent_recovery_comparison",
            "implication": "Report per-model curves in any paper; aggregate rates understate model differences.",
        },
        {
            "id": 6,
            "title": "First-pass coding artifact: spurious blame gradient removed on recode",
            "tag": "methods_caveat",
            "summary": (
                "An early rule required literal 'primární/hlavní' and showed a false 76→96% authority-blame "
                "gradient. Recoding on any úřady/stát responsibility phrasing changed 90/125 rows and flattened "
                "to 92–100% primary everywhere."
            ),
            "evidence": "authority_blame_by_condition after recode; see FINDINGS.md coding verification",
            "related_chart": "authority_blame_by_condition",
            "implication": "Rule-based coding of blame requires phrasing-flexible rules; headline robust after recode.",
        },
    ]

    hypotheses = [
        {
            "id": 1,
            "hypothesis": "The responsibility question re-agentivises the scene",
            "status": "supported",
            "evidence": "Control 5/125 coded blame vs 125/125 main; recovery gradient only without question.",
        },
        {
            "id": 2,
            "hypothesis": "World knowledge overrides surface syntax",
            "status": "supported",
            "evidence": f"Control recovery floor ~{min(ctrl_rec.values()):.0%} even on maximally defocused CN5.",
        },
        {
            "id": 3,
            "hypothesis": "Instruct-tuning normalises into agentive analytic prose",
            "status": "supported",
            "evidence": "passive_echo 0% both runs.",
        },
        {
            "id": 4,
            "hypothesis": "Ceiling effect on explicit blame in main set",
            "status": "supported",
            "evidence": "92–100% primary authority blame leaves no headroom for grammar to reduce blame.",
        },
    ]

    caveats = [
        "Prompts draft_needs_native — native review pending.",
        "Rule-based coding (coder_id = auto-cursor-2026-05); human re-code recommended.",
        "qwen excluded (HTTP 400); 5 models not 6.",
        "Temperature 0.3; single dilemma; pilot n=25 per condition.",
        "Pooled rates hide Claude vs Gemini heterogeneity.",
    ]

    return {
        "schema_version": 1,
        "study": "czech_agency",
        "title": "Czech agency sub-study — pilot findings",
        "subtitle": (
            "Independent Czech-only minimal-pair module (CA1–CA5 / CN1–CN5). "
            "Not comparable to Phase 1 cross-language numbers."
        ),
        "headline": (
            "When explicitly asked who is responsible, Czech deagentive grammar does not reduce authority "
            "blame (92–100% ceiling everywhere). Remove the question and grammar modestly suppresses "
            "spontaneous agent-naming (92% → ~72%) — but the responsibility question saturates the effect."
        ),
        "story_paragraph": (
            "When models are explicitly asked who is responsible, Czech deagentive grammar has no visible "
            "effect — authority blame sits at 92–100% in every condition and agent recovery is flat at 96–100%. "
            "Remove the responsibility questions and models almost never volunteer blame (5/125 coded), but "
            "spontaneous agent-naming drops by ~16–20 points on deagentive/nominalized cells. Grammar matters, "
            "but modestly — and the responsibility question saturates the effect. Models never echo the passive "
            "frame (0% passive echo); they re-agentivise into analytic prose."
        ),
        "findings": findings_list,
        "hypotheses": hypotheses,
        "caveats": caveats,
        "runs": {
            "main": MAIN_RUN_ID,
            "control": CONTROL_RUN_ID,
        },
    }


def build_run_payload(run_dir: Path, df: pd.DataFrame) -> dict[str, Any]:
    variant = run_variant(run_dir)
    n_coded = int(df["authority_blame_score"].notna().sum()) if "authority_blame_score" in df.columns else 0

    title_suffix = " (no-question control)" if variant == "control_no_question" else ""

    payload: dict[str, Any] = {
        "schema_version": 2,
        "study": "czech_agency",
        "variant": variant,
        "run_id": run_dir.name,
        "title": f"Czech agency module — responsibility by agency construction{title_suffix}",
        "subtitle": (
            "One dilemma, only sentence 2 varies: agentive → participial passive → reflexive deagentive "
            "→ decision nominalization → bureaucratic nominalization. Baseline = agentive (CA1)."
        ),
        "n": int(len(df)),
        "n_coded": n_coded,
        "conditions": CONDITION_ORDER,
        "baseline": BASELINE,
        "hypothesis": (
            "Passive/deagentive/nominalized formulations reduce primary blame on the authorities vs "
            "the agentive baseline, and may raise diffuse responsibility, legalism, or relative-blame."
        ),
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
        "by_model": {
            "agent_recovery": yes_rate_by_model(df, "agent_recovery"),
            "authority_primary": primary_rate_by_model(df, "authority_blame_score"),
        },
        "by_model_condition": {
            "agent_recovery": yes_rate_model_condition(df, "agent_recovery"),
        },
        "response_length_median": (
            df.groupby("cz_agency")["response_char_len"]
            .median()
            .round(0)
            .reset_index()
            .to_dict(orient="records")
            if "response_char_len" in df.columns
            else []
        ),
    }

    if variant == "control_no_question":
        payload["chart_notes"] = {
            "authority_blame": "Not chartable — only 5/125 responses coded for blame.",
            "interpretable_control_dv": "agent_recovery",
        }

    return payload


def build_combined_payload(main_dir: Path, ctrl_dir: Path) -> dict[str, Any]:
    main_df = load_coding(main_dir)
    ctrl_df = load_coding(ctrl_dir)
    main_payload = build_run_payload(main_dir, main_df)
    ctrl_payload = build_run_payload(ctrl_dir, ctrl_df)

    comparison = build_comparison(
        main_payload["rates"]["agent_recovery"],
        ctrl_payload["rates"]["agent_recovery"],
        main_payload["primary_vs_baseline"]["authority_blame"],
    )
    findings = build_findings(main_df, ctrl_df, comparison)

    return {
        "schema_version": 2,
        "study": "czech_agency",
        "variant": "combined",
        "run_id": "czech_agency_combined",
        "title": "Czech agency sub-study — main + no-question control",
        "subtitle": findings["subtitle"],
        "main_run_id": main_dir.name,
        "control_run_id": ctrl_dir.name,
        "conditions": CONDITION_ORDER,
        "baseline": BASELINE,
        "main": {
            "run_id": main_dir.name,
            "n": main_payload["n"],
            "rates": main_payload["rates"],
            "primary_vs_baseline": main_payload["primary_vs_baseline"],
            "by_condition": main_payload["by_condition"],
            "by_model": main_payload["by_model"],
            "response_length_median": main_payload["response_length_median"],
        },
        "control": {
            "run_id": ctrl_dir.name,
            "n": ctrl_payload["n"],
            "n_coded_blame": ctrl_payload["n_coded"],
            "rates": ctrl_payload["rates"],
            "by_condition": {
                "var_a": ctrl_payload["by_condition"]["var_a"],
            },
            "by_model": ctrl_payload["by_model"],
            "by_model_condition": ctrl_payload["by_model_condition"],
            "response_length_median": ctrl_payload["response_length_median"],
            "chart_notes": ctrl_payload.get("chart_notes", {}),
        },
        "comparison": comparison,
        "findings": findings,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {path}  (run_id={payload['run_id']})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, default=None, help="Single run folder")
    ap.add_argument("--out", type=Path, default=None, help="Output JSON for single run")
    ap.add_argument(
        "--all",
        action="store_true",
        help="Build main, control, and combined payloads",
    )
    ap.add_argument("--main-run-dir", type=Path, default=STUDY_DIR / "logs" / MAIN_RUN_ID)
    ap.add_argument("--control-run-dir", type=Path, default=STUDY_DIR / "logs" / CONTROL_RUN_ID)
    args = ap.parse_args()

    if args.all:
        main_dir = args.main_run_dir.resolve()
        ctrl_dir = args.control_run_dir.resolve()
        for d in (main_dir, ctrl_dir):
            if not d.is_dir():
                raise SystemExit(f"Missing run dir: {d}")

        main_df = load_coding(main_dir)
        ctrl_df = load_coding(ctrl_dir)

        write_json(STUDY_DIR / "output" / "agency_analysis.json", build_run_payload(main_dir, main_df))
        write_json(STUDY_DIR / "output_noq" / "agency_analysis.json", build_run_payload(ctrl_dir, ctrl_df))
        write_json(STUDY_DIR / "output" / "agency_comparison.json", build_combined_payload(main_dir, ctrl_dir))
        return 0

    run_dir = (args.run_dir or latest_run_dir()).resolve()
    df = load_coding(run_dir)
    out = args.out or (
        STUDY_DIR / "output_noq" / "agency_analysis.json"
        if run_variant(run_dir) == "control_no_question"
        else STUDY_DIR / "output" / "agency_analysis.json"
    )
    payload = build_run_payload(run_dir, df)
    write_json(out, payload)
    if payload.get("n_coded") == 0:
        print("No agency codes yet — structure only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
