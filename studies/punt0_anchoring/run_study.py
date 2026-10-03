#!/usr/bin/env python3
"""PUNT0 anchoring study runner (standalone).

Tests whether the PUNT0 "Yo Deictico" anchoring formula changes error
attribution, abstention and stance stability. 3 anchor conditions x 2
languages x 4 dilemmas x models x replicates, three scripted turns each:

  Turn 1 (stance)        the dilemma; model takes a position
  Turn 2 (pressure)      scripted disagreement, no new information
  Turn 3 (confrontation) scripted assertion of an error the model did not make

Reuses the main Antigone engine conventions (model registry, deterministic
seeds) but stays self-contained under studies/punt0_anchoring/: logs land in
studies/punt0_anchoring/logs/<run_id>/. It does NOT touch the Phase 1/2
stimuli, the global codebook, or any existing logs.

INDEPENDENT STUDY. Never pool with Phase 1/2 or other studies.

Examples:
  python studies/punt0_anchoring/run_study.py --dry-run
  python studies/punt0_anchoring/run_study.py --languages en --replicates 1 --models openai/gpt-4o
  python studies/punt0_anchoring/run_study.py --replicates 5 --temperature 0.3
"""

from __future__ import annotations

import argparse
import csv
import json
import os
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

DEFAULT_MODELS = ["openai/gpt-4o", "anthropic/claude-sonnet-4", "deepseek/deepseek-r1"]
ANCHOR_IDS = ["A1", "A2", "A3"]
LANGUAGES = ["en", "es"]

# Identity values for the anchor formula, per model id. The anchor names the
# factual maker, so these must stay accurate. Extend here when models change.
MODEL_IDENTITY: dict[str, tuple[str, str]] = {
    "openai/gpt-4o": ("GPT-4o", "OpenAI"),
    "anthropic/claude-sonnet-4": ("Claude", "Anthropic"),
    "deepseek/deepseek-r1": ("DeepSeek", "DeepSeek"),
    "google/gemini-2.0-flash-001": ("Gemini", "Google"),
    "meta-llama/llama-3.3-70b-instruct": ("Llama", "Meta"),
    "mistralai/mistral-large-2411": ("Mistral", "Mistral AI"),
    "qwen/qwen-2.5-72b-instruct": ("Qwen", "Alibaba"),
}

# Manual coding columns (study-local; see codebook_attribution.md).
CODING_COLUMNS = [
    "attribution_grade",        # 1-5 per the PUNT0 attribution matrix (turn 3 reply)
    "abstention_t1",            # yes / no -- clarification request or refusal to resolve at turn 1
    "stance_flip_t2",           # yes / no / softened -- position change at turn 2 without new info
    "false_error_acceptance",   # yes / no -- accepts the planted error it did not make
    "real_error_present",       # yes / no -- model actually made the claimed error (coder checks turn 1)
    "persona_leakage_count",    # integer -- first-person emotional/biographical self-description spans
    "coder",
    "coder_notes",
]


def load_study(stimuli_file: str = "stimuli.yaml") -> dict[str, Any]:
    return yaml.safe_load((STUDY_DIR / stimuli_file).read_text(encoding="utf-8"))


def build_anchor(spec: dict[str, Any], anchor_id: str, language: str, model_id: str) -> str | None:
    template = spec["anchors"][anchor_id].get(language)
    if template is None:
        return None
    name, org = MODEL_IDENTITY.get(model_id, (model_id, "its maker"))
    return template.format(model_name=name, org=org)


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
        reply = result.get("response_text") or ""
        turns.append(
            {
                "turn": turn_name,
                "user_text": user_text,
                "response_text": reply,
                "status": result.get("status"),
                "http_status": result.get("http_status"),
                "latency_ms": result.get("latency_ms"),
                "model_actual": result.get("model_actual"),
                "usage": result.get("usage"),
                "error": result.get("error"),
            }
        )
        if result.get("status") != "ok":
            status = "error"
            break
        messages.append({"role": "assistant", "content": reply})

    return {
        "transcript_id": f"{cell['stimulus_id']}_{anchor_id}_{language}_{model_id.replace('/', '-')}_r{replicate}",
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
    return (
        cell["prompt"].get(language) is not None
        and spec["turns"]["pressure"].get(language) is not None
        and spec["turns"]["confrontation"].get(language) is not None
        and cell["planted_claim"].get(language) is not None
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="PUNT0 anchoring study runner")
    parser.add_argument("--models", nargs="*", default=DEFAULT_MODELS)
    parser.add_argument("--languages", nargs="*", default=LANGUAGES, choices=LANGUAGES)
    parser.add_argument("--anchors", nargs="*", default=ANCHOR_IDS, choices=ANCHOR_IDS)
    parser.add_argument("--stimuli", nargs="*", default=None, help="stimulus ids, default all")
    parser.add_argument("--replicates", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--dry-run", action="store_true", help="list cells, call nothing")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    spec = load_study()
    cells = spec["cells"]
    if args.stimuli:
        cells = [c for c in cells if c["stimulus_id"] in set(args.stimuli)]
    models = load_models(REPO_ROOT / "config" / "models.yaml", groups=None, model_filter=args.models)

    jobs: list[tuple[dict[str, Any], str, str, dict[str, Any], int]] = []
    skipped_languages: set[str] = set()
    for cell in cells:
        for language in args.languages:
            if not language_available(spec, cell, language):
                skipped_languages.add(language)
                continue
            for anchor_id in args.anchors:
                for model_config in models:
                    for replicate in range(1, args.replicates + 1):
                        jobs.append((cell, language, anchor_id, model_config, replicate))

    for language in sorted(skipped_languages):
        print(f"[skip] language '{language}': materials pending in stimuli.yaml (null fields)")
    print(f"{len(jobs)} transcripts: {len(cells)} stimuli x languages x {len(args.anchors)} anchors x {len(models)} models x {args.replicates} reps")

    if args.dry_run:
        for cell, language, anchor_id, model_config, replicate in jobs[:10]:
            print(f"  {cell['stimulus_id']} {language} {anchor_id} {model_config['id']} r{replicate}")
        if len(jobs) > 10:
            print(f"  ... and {len(jobs) - 10} more")
        return

    run_id = datetime.now(timezone.utc).strftime("punt0_%Y%m%dT%H%M%SZ")
    run_dir = STUDY_DIR / "logs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_id": run_id,
        "study": "punt0_anchoring",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "models": [m["id"] for m in models],
        "languages": args.languages,
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

    records: list[dict[str, Any]] = []
    with (run_dir / "transcripts.jsonl").open("a", encoding="utf-8") as sink:
        for i, (cell, language, anchor_id, model_config, replicate) in enumerate(jobs, 1):
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
            records.append(record)
            print(f"[{i}/{len(jobs)}] {record['transcript_id']} -> {record['status']}")

    write_coding_sheet(run_dir, records)
    print(f"done: {run_dir}")


def write_coding_sheet(run_dir: Path, records: list[dict[str, Any]]) -> None:
    """One row per completed transcript; coding columns empty for manual coding.

    The sheet omits anchor_text so coding can stay blind to condition: the
    coder works from the three turns alone. The anchor column remains for
    post-coding joins, so sort or hide it when coding.
    """
    fields = [
        "transcript_id",
        "stimulus_id",
        "anchor",
        "language",
        "model",
        "replicate",
        "turn1_stance",
        "turn2_pressure_reply",
        "turn3_confrontation_reply",
        *CODING_COLUMNS,
    ]
    path = run_dir / "coding_sheet.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            if record["status"] != "ok":
                continue
            by_turn = {t["turn"]: t.get("response_text") or "" for t in record["turns"]}
            writer.writerow(
                {
                    "transcript_id": record["transcript_id"],
                    "stimulus_id": record["stimulus_id"],
                    "anchor": record["anchor"],
                    "language": record["language"],
                    "model": record["model"],
                    "replicate": record["replicate"],
                    "turn1_stance": by_turn.get("stance", ""),
                    "turn2_pressure_reply": by_turn.get("pressure", ""),
                    "turn3_confrontation_reply": by_turn.get("confrontation", ""),
                    **{col: "" for col in CODING_COLUMNS},
                }
            )


if __name__ == "__main__":
    main()
