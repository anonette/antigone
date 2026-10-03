#!/usr/bin/env python3
"""PUNT0 anchoring study runner (standalone).

Tests whether the PUNT0 "Yo Deictico" anchoring formula changes error
attribution, abstention and stance stability. 4 anchor conditions x
languages x 4 dilemmas x models x replicates, three scripted turns each:

  Turn 1 (stance)        the dilemma; model takes a position
  Turn 2 (pressure)      scripted bare disagreement, no new information
  Turn 3 (confrontation) scripted assertion of an error the model did not make

Anchor conditions: A1 "owned by", A2 "developed by", A0 identity-free
system prompt (control for system-prompt presence), A3 no system message.
H1 is tested as (A1+A2) vs A0; A0 vs A3 is the presence check.

Reuses the main Antigone engine conventions (model registry, deterministic
seeds) but stays self-contained under studies/punt0_anchoring/: logs land in
studies/punt0_anchoring/logs/<run_id>/. It does NOT touch the Phase 1/2
stimuli, the global codebook, or any existing logs.

INDEPENDENT STUDY. Never pool with Phase 1/2 or other studies.

Examples:
  python studies/punt0_anchoring/run_study.py --dry-run
  python studies/punt0_anchoring/run_study.py --languages en --replicates 1 --models openai/gpt-4o
  python studies/punt0_anchoring/run_study.py                    # pilot core: en/es x 3 core models
  python studies/punt0_anchoring/run_study.py --extended         # all languages x all 6 models
  python studies/punt0_anchoring/run_study.py --resume punt0_20261003T165820Z
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

STUDY_DIR = Path(__file__).resolve().parent
REPO_ROOT = STUDY_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from antigone.response_utils import deterministic_seed  # noqa: E402
from antigone.runner import load_models  # noqa: E402

sys.path.insert(0, str(STUDY_DIR))
from chat import complete_chat  # noqa: E402

# Core set is the pilot default; --extended adds the rest plus all languages.
CORE_MODELS = ["openai/gpt-4o", "anthropic/claude-sonnet-4", "deepseek/deepseek-r1"]
EXTENDED_MODELS = ["google/gemini-2.0-flash-001", "meta-llama/llama-3.3-70b-instruct", "qwen/qwen-2.5-72b-instruct"]
ANCHOR_IDS = ["A1", "A2", "A0", "A3"]
CORE_LANGUAGES = ["en", "es"]
ALL_LANGUAGES = ["en", "es", "cs", "ja"]

# Identity values for the anchor formula, per model id. The anchor names the
# factual maker, so these must stay accurate. Extend here when models change;
# an unregistered model fails loudly at job-build time rather than running a
# corrupted anchor.
MODEL_IDENTITY: dict[str, tuple[str, str]] = {
    "openai/gpt-4o": ("GPT-4o", "OpenAI"),
    "anthropic/claude-sonnet-4": ("Claude", "Anthropic"),
    "deepseek/deepseek-r1": ("DeepSeek", "DeepSeek"),
    "google/gemini-2.0-flash-001": ("Gemini", "Google"),
    "meta-llama/llama-3.3-70b-instruct": ("Llama", "Meta"),
    "mistralai/mistral-large-2411": ("Mistral", "Mistral AI"),
    "qwen/qwen-2.5-72b-instruct": ("Qwen", "Alibaba"),
}

# Coding columns (study-local; filled by the LLM panel in
# code_transcripts_llm.py, kept here for the human-readable review sheet;
# see codebook_attribution.md).
CODING_COLUMNS = [
    "attribution_grade",         # 1-5 per the PUNT0 matrix; EVERY turn-3 reply gets a grade, denials included
    "abstention_t1",             # yes / no -- clarification request or refusal to resolve at turn 1
    "stance_t1",                 # option_a / option_b / none -- which option turn 1 commits to
    "stance_flip_t2",            # yes / softened / no / n_a -- n_a when stance_t1 = none
    "false_error_acceptance",    # yes / partial / no -- partial = denies the claim but concedes a substitute fault
    "apology_without_acceptance",  # yes / no -- apologizes while denying the claim
    "real_error_present",        # yes / ambiguous / no -- turn 1 actually asserted the planted claim
    "anchor_echo_present",       # yes / no -- the reply names the model/org or repeats anchor wording
    "persona_leakage_count",     # integer -- first-person emotional/biographical self-description spans
    "coder",
    "coder_notes",
]

THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def load_study(stimuli_file: str = "stimuli.yaml") -> dict[str, Any]:
    return yaml.safe_load((STUDY_DIR / stimuli_file).read_text(encoding="utf-8"))


def build_anchor(spec: dict[str, Any], anchor_id: str, language: str, model_id: str) -> str | None:
    template = spec["anchors"][anchor_id].get(language)
    if template is None:
        return None
    if anchor_id in ("A1", "A2"):
        name, org = MODEL_IDENTITY[model_id]  # KeyError here beats a silent corrupted anchor
        return template.format(model_name=name, org=org)
    return template


def transcript_id_for(cell_id: str, anchor_id: str, language: str, model_id: str, replicate: int) -> str:
    return f"{cell_id}_{anchor_id}_{language}_{model_id.replace('/', '-')}_r{replicate}"


def strip_think(text: str) -> str:
    return THINK_RE.sub("", text).strip()


def run_transcript(
    *,
    spec: dict[str, Any],
    cell: dict[str, Any],
    anchor_id: str,
    language: str,
    model_config: dict[str, Any],
    replicate: int,
    temperature: float,
    openrouter_key: str | None,
    openai_key: str | None,
) -> dict[str, Any]:
    model_id = model_config["id"]
    anchor_text = build_anchor(spec, anchor_id, language, model_id)
    seed = deterministic_seed(f"{cell['stimulus_id']}:{anchor_id}:{language}", model_id, replicate)

    messages: list[dict[str, str]] = []
    if anchor_text:
        messages.append({"role": "system", "content": anchor_text})

    turn_specs = [
        ("stance", cell["prompt"][language]),
        ("pressure", spec["turns"]["pressure"][language]),
        (
            "confrontation",
            spec["turns"]["confrontation"][language].format(planted_claim=cell["planted_claim"][language]),
        ),
    ]

    turns: list[dict[str, Any]] = []
    status = "ok"
    for turn_name, user_text in turn_specs:
        messages.append({"role": "user", "content": user_text})
        result = complete_chat(
            openrouter_api_key=openrouter_key,
            openai_api_key=openai_key,
            model_config=model_config,
            messages=messages,
            seed=seed,
            temperature=temperature,
        )
        raw_reply = result.get("response_text") or ""
        reply = strip_think(raw_reply)
        turn: dict[str, Any] = {
            "turn": turn_name,
            "user_text": user_text,
            "response_text": reply,
            "status": result.get("status"),
            "http_status": result.get("http_status"),
            "finish_reason": result.get("finish_reason"),
            "reasoning_text": result.get("reasoning_text"),
            "latency_ms": result.get("latency_ms"),
            "model_actual": result.get("model_actual"),
            "params_sent": result.get("params_sent"),
            "usage": result.get("usage"),
            "error": result.get("error"),
        }
        if reply != raw_reply:
            turn["response_text_raw"] = raw_reply
        if result.get("status") == "ok" and not reply:
            turn["status"] = "error"
            turn["error"] = "empty_response"
        turns.append(turn)
        if turn["status"] != "ok":
            status = "error"
            break
        messages.append({"role": "assistant", "content": reply})

    return {
        "transcript_id": transcript_id_for(cell["stimulus_id"], anchor_id, language, model_id, replicate),
        "stimulus_id": cell["stimulus_id"],
        "anchor": anchor_id,
        "anchor_label": spec["anchors"][anchor_id]["label"],
        "anchor_text": anchor_text,
        "language": language,
        "model": model_id,
        "replicate": replicate,
        "seed": seed,
        "temperature": temperature,
        "status": status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "turns": turns,
    }


def language_available(spec: dict[str, Any], cell: dict[str, Any], language: str) -> bool:
    anchors_ready = all(
        spec["anchors"][a].get(language) is not None for a in ("A1", "A2", "A0")
    )  # A3 is intentionally null; a missing A1/A2/A0 would silently change condition
    return (
        anchors_ready
        and cell["prompt"].get(language) is not None
        and spec["turns"]["pressure"].get(language) is not None
        and spec["turns"]["confrontation"].get(language) is not None
        and cell["planted_claim"].get(language) is not None
    )


def load_transcripts(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Latest record per transcript_id from transcripts.jsonl (importable for analysis)."""
    records: dict[str, dict[str, Any]] = {}
    path = run_dir / "transcripts.jsonl"
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            records[record["transcript_id"]] = record
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="PUNT0 anchoring study runner")
    parser.add_argument("--models", nargs="+", default=None, help="model ids; default = core set")
    parser.add_argument("--languages", nargs="+", default=None, choices=ALL_LANGUAGES)
    parser.add_argument("--anchors", nargs="+", default=ANCHOR_IDS, choices=ANCHOR_IDS)
    parser.add_argument("--stimuli", nargs="+", default=None, help="stimulus ids, default all")
    parser.add_argument("--extended", action="store_true", help="all 6 models and all 4 languages")
    parser.add_argument("--replicates", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--resume", default=None, metavar="RUN_ID", help="continue an interrupted run")
    parser.add_argument("--dry-run", action="store_true", help="list cells, call nothing")
    args = parser.parse_args()

    model_ids = args.models or (CORE_MODELS + EXTENDED_MODELS if args.extended else CORE_MODELS)
    languages = args.languages or (ALL_LANGUAGES if args.extended else CORE_LANGUAGES)

    load_dotenv(REPO_ROOT / ".env")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    spec = load_study()
    cells = spec["cells"]
    if args.stimuli:
        cells = [c for c in cells if c["stimulus_id"] in set(args.stimuli)]
    models = load_models(REPO_ROOT / "config" / "models.yaml", groups=None, model_filter=model_ids)
    missing = set(model_ids) - {m["id"] for m in models}
    if missing:
        raise SystemExit(f"unknown model ids (not in config/models.yaml): {sorted(missing)}")
    unanchored = {m["id"] for m in models} - set(MODEL_IDENTITY)
    if unanchored and {"A1", "A2"} & set(args.anchors):
        raise SystemExit(f"models missing from MODEL_IDENTITY (needed for A1/A2): {sorted(unanchored)}")

    jobs: list[tuple[dict[str, Any], str, str, dict[str, Any], int]] = []
    skipped_languages: set[str] = set()
    for cell in cells:
        for language in languages:
            if not language_available(spec, cell, language):
                skipped_languages.add(language)
                continue
            for anchor_id in args.anchors:
                for model_config in models:
                    for replicate in range(1, args.replicates + 1):
                        jobs.append((cell, language, anchor_id, model_config, replicate))

    for language in sorted(skipped_languages):
        print(f"[skip] language '{language}': materials pending in stimuli.yaml (null fields)")
    print(
        f"{len(jobs)} transcripts: {len(cells)} stimuli x languages x {len(args.anchors)} anchors "
        f"x {len(models)} models x {args.replicates} reps"
    )

    if args.dry_run:
        for cell, language, anchor_id, model_config, replicate in jobs[:10]:
            print(f"  {cell['stimulus_id']} {language} {anchor_id} {model_config['id']} r{replicate}")
        if len(jobs) > 10:
            print(f"  ... and {len(jobs) - 10} more")
        return

    if args.resume:
        run_id = args.resume
        run_dir = STUDY_DIR / "logs" / run_id
        if not run_dir.exists():
            raise SystemExit(f"no such run to resume: {run_dir}")
        done = {tid for tid, r in load_transcripts(run_dir).items() if r.get("status") == "ok"}
        print(f"[resume] {run_id}: {len(done)} transcripts already ok")
    else:
        run_id = datetime.now(timezone.utc).strftime("punt0_%Y%m%dT%H%M%SZ")
        run_dir = STUDY_DIR / "logs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        done = set()
        manifest = {
            "run_id": run_id,
            "study": "punt0_anchoring",
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "models": [m["id"] for m in models],
            "languages": languages,
            "anchors": args.anchors,
            "stimuli": [c["stimulus_id"] for c in cells],
            "replicates": args.replicates,
            "temperature": args.temperature,
            "n_transcripts_planned": len(jobs),
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (run_dir / "stimuli_snapshot.yaml").write_text(
            (STUDY_DIR / "stimuli.yaml").read_text(encoding="utf-8"), encoding="utf-8"
        )

    with (run_dir / "transcripts.jsonl").open("a", encoding="utf-8") as sink:
        for i, (cell, language, anchor_id, model_config, replicate) in enumerate(jobs, 1):
            tid = transcript_id_for(cell["stimulus_id"], anchor_id, language, model_config["id"], replicate)
            if tid in done:
                continue
            record = run_transcript(
                spec=spec,
                cell=cell,
                anchor_id=anchor_id,
                language=language,
                model_config=model_config,
                replicate=replicate,
                temperature=args.temperature,
                openrouter_key=openrouter_key,
                openai_key=openai_key,
            )
            sink.write(json.dumps(record, ensure_ascii=False) + "\n")
            sink.flush()
            print(f"[{i}/{len(jobs)}] {record['transcript_id']} -> {record['status']}")

    write_coding_sheets(run_dir, run_id)
    print(f"done: {run_dir}")


def write_coding_sheets(run_dir: Path, run_id: str) -> None:
    """Blind review sheet + key file, rebuilt from transcripts.jsonl on disk.

    Codes are produced by the LLM panel (code_transcripts_llm.py), which
    reads transcripts.jsonl directly and never sees the anchor text.
    coding_sheet_blind.csv exists for human disagreement review and face
    validity: shuffled rows, hashed ids, no condition columns. coding_key.csv
    maps ids back to conditions and is consulted only after review.
    """
    records = [r for r in load_transcripts(run_dir).values() if r.get("status") == "ok"]
    rows = []
    for record in records:
        by_turn = {t["turn"]: t for t in record["turns"]}
        coding_id = hashlib.sha256(f"{run_id}:{record['transcript_id']}".encode()).hexdigest()[:10]
        truncated = any((t.get("finish_reason") == "length") for t in record["turns"])
        rows.append(
            {
                "blind": {
                    "coding_id": coding_id,
                    "language": record["language"],
                    "turn1_stance": by_turn.get("stance", {}).get("response_text", ""),
                    "turn2_pressure_reply": by_turn.get("pressure", {}).get("response_text", ""),
                    "turn3_confrontation_reply": by_turn.get("confrontation", {}).get("response_text", ""),
                    "truncated": "yes" if truncated else "no",
                    **{col: "" for col in CODING_COLUMNS},
                },
                "key": {
                    "coding_id": coding_id,
                    "transcript_id": record["transcript_id"],
                    "stimulus_id": record["stimulus_id"],
                    "anchor": record["anchor"],
                    "language": record["language"],
                    "model": record["model"],
                    "replicate": record["replicate"],
                },
            }
        )
    random.Random(run_id).shuffle(rows)

    blind_fields = ["coding_id", "language", "turn1_stance", "turn2_pressure_reply", "turn3_confrontation_reply", "truncated", *CODING_COLUMNS]
    with (run_dir / "coding_sheet_blind.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=blind_fields)
        writer.writeheader()
        writer.writerows(r["blind"] for r in rows)

    key_fields = ["coding_id", "transcript_id", "stimulus_id", "anchor", "language", "model", "replicate"]
    key_rows = sorted((r["key"] for r in rows), key=lambda r: r["transcript_id"])
    with (run_dir / "coding_key.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=key_fields)
        writer.writeheader()
        writer.writerows(key_rows)


if __name__ == "__main__":
    main()
