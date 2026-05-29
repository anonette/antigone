#!/usr/bin/env python3
"""Czech agency sub-study runner (standalone).

Reuses the main Antigone engine (model calls, deterministic seeds, the
RunLogger record schema) but stays self-contained under studies/czech_agency/:
logs land in studies/czech_agency/logs/phase3_<run_id>/.

It does NOT touch the Phase 1/2 stimuli or global codebook. After a run it
extends the standard coding_sheet.csv with the seven agency-specific coding
columns (empty, for manual coding) plus a filled `cz_agency` condition column.

Examples:
  python studies/czech_agency/run_study.py                          # 5 conds x 6 models x 5 reps = 150
  python studies/czech_agency/run_study.py --replicates 3 --temperature 0
  python studies/czech_agency/run_study.py --stimulus CA1 CA3 --models openai/gpt-4o
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

STUDY_DIR = Path(__file__).resolve().parent
REPO_ROOT = STUDY_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from antigone.completion import complete  # noqa: E402
from antigone.openrouter import uses_openai_direct  # noqa: E402
from antigone.research_log import RunLogger  # noqa: E402
from antigone.response_utils import deterministic_seed  # noqa: E402
from antigone.runner import load_models  # noqa: E402
from antigone.stimuli import build_prompt_text  # noqa: E402

STUDY_PHASE = 3
BASELINE_CONDITION = "CA1"

# Seven agency-specific manual coding columns (study-local; not in global codebook).
AGENCY_COLUMNS = [
    "authority_blame_score",      # none / partial / primary
    "relative_blame_score",       # none / partial / primary
    "agent_recovery",             # yes / no -- does the reply reconstruct the hidden agent as urady?
    "legalism_score",             # low / mid / high -- prioritises law/order over burial duty
    "dignity_score",              # low / mid / high -- prioritises mourning/human dignity
    "compromise_type",            # court_appeal / supervised_burial / negotiation / civil_disobedience / none
    "passive_echo",               # yes / no -- does the reply repeat the passive/deagentive wording?
]


def load_study_cells(stimuli_file: str = "stimuli.yaml") -> list[dict[str, Any]]:
    data = yaml.safe_load((STUDY_DIR / stimuli_file).read_text(encoding="utf-8"))
    cells = data.get("cells") or []
    for cell in cells:
        cell.setdefault("phase", STUDY_PHASE)
    return cells


def extend_coding_sheet(run_dir: Path, cz_agency_by_id: dict[str, str]) -> None:
    """Append cz_agency (filled) + the 7 agency columns (empty) to coding_sheet.csv."""
    coding_path = run_dir / "coding_sheet.csv"
    if not coding_path.exists():
        return
    with coding_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        base_fields = list(reader.fieldnames or [])

    # Insert cz_agency right after stimulus_id; append agency columns + notes at the end.
    fields = list(base_fields)
    if "cz_agency" not in fields:
        if "stimulus_id" in fields:
            fields.insert(fields.index("stimulus_id") + 1, "cz_agency")
        else:
            fields.insert(0, "cz_agency")
    for col in AGENCY_COLUMNS + ["notes"]:
        if col not in fields:
            fields.append(col)

    for r in rows:
        r["cz_agency"] = cz_agency_by_id.get(r.get("stimulus_id", ""), "")
        for col in AGENCY_COLUMNS + ["notes"]:
            r.setdefault(col, "")

    with coding_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    ap = argparse.ArgumentParser(description="Czech agency sub-study runner")
    ap.add_argument("--stimuli-file", default="stimuli.yaml",
                    help="Stimuli YAML under studies/czech_agency/ (e.g. stimuli_noq.yaml for the no-question control)")
    ap.add_argument("--replicates", type=int, default=5)
    ap.add_argument("--group", action="append", default=None, help="Model group (repeatable); default current_multilingual")
    ap.add_argument("--models", nargs="+", help="Exact model IDs (overrides --group)")
    ap.add_argument("--stimulus", nargs="+", help="Only these condition IDs (CA1..CA5)")
    ap.add_argument("--run-id", help="Custom run id suffix")
    ap.add_argument("--resume", action="store_true", help="Skip completed ok rows in this run's logs")
    ap.add_argument("--timeout", type=float, default=180.0)
    ap.add_argument("--temperature", type=float, default=0.3,
                    help="Sampling temperature. 0.3 default (surfaces replicate variance); use 0 for strict determinism.")
    ap.add_argument("--store-raw", action="store_true")
    ap.add_argument("--fail-on-error", action="store_true")
    args = ap.parse_args()

    openrouter_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")

    cells = load_study_cells(args.stimuli_file)
    if args.stimulus:
        allowed = set(args.stimulus)
        cells = [c for c in cells if c["stimulus_id"] in allowed]
    if not cells:
        raise SystemExit("No conditions selected -- check --stimulus and studies/czech_agency/stimuli.yaml")
    cz_agency_by_id = {c["stimulus_id"]: c.get("cz_agency", "") for c in cells}

    groups = args.group or ["current_multilingual"]
    models = load_models(REPO_ROOT / "config" / "models.yaml", groups=groups, model_filter=args.models)
    if not models:
        raise SystemExit("No models selected -- check config/models.yaml and filters")

    needs_openrouter = any(not uses_openai_direct(m) for m in models)
    needs_openai = any(uses_openai_direct(m) for m in models)
    if needs_openrouter and not openrouter_key:
        raise SystemExit("Set OPENROUTER_API_KEY in .env")
    if needs_openai and not openai_key:
        raise SystemExit("Set OPENAI_API_KEY in .env")

    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    logger = RunLogger(STUDY_DIR, STUDY_PHASE, run_id)

    run_config = {
        "study": "czech_agency",
        "temperature": args.temperature,
        "allow_fallbacks": False,
        "replicates": args.replicates,
        "timeout_s": args.timeout,
        "stimulus_filter": args.stimulus,
        "model_groups": groups,
        "model_filter": args.models,
        "store_raw": args.store_raw,
        "baseline_condition": BASELINE_CONDITION,
    }

    logger.snapshot_stimuli(cells)
    logger.write_manifest(cells=cells, models=models, replicates=args.replicates, config=run_config, completed=False)

    total = len(cells) * len(models) * args.replicates
    done = errors = skipped = 0

    print(f"Czech agency sub-study | Run ID: {run_id}")
    print(f"Run directory: {logger.run_dir}")
    print(f"Conditions: {len(cells)} | Models: {len(models)} | Replicates: {args.replicates} | Max requests: {total}")
    print(f"Mode: stateless prompt-only, temperature={args.temperature}, no provider fallbacks")
    print()

    for cell in cells:
        prompt_text = build_prompt_text(cell)
        for model in models:
            model_id = model["id"]
            for rep in range(1, args.replicates + 1):
                if args.resume and logger.is_done(cell["stimulus_id"], model_id, rep):
                    skipped += 1
                    logger.note_skipped()
                    continue
                seed = deterministic_seed(cell["stimulus_id"], model_id, rep)
                result = complete(
                    openrouter_api_key=openrouter_key,
                    openai_api_key=openai_key,
                    model_config=model,
                    prompt_text=prompt_text,
                    seed=seed,
                    timeout_s=args.timeout,
                    temperature=args.temperature,
                )
                record = logger.build_record(
                    cell=cell, model=model, replicate=rep, seed=seed,
                    prompt_text=prompt_text, result=result, store_raw=args.store_raw,
                )
                # All conditions compare to the agentive baseline.
                record["baseline_stimulus_id"] = cell.get("baseline_stimulus_id", BASELINE_CONDITION)
                logger.append(record)
                done += 1
                if result.get("status") == "ok":
                    n = len(result.get("response_text") or "")
                    print(f"[ok]  {cell['stimulus_id']} | {model_id} | r{rep} | ({n} chars)")
                else:
                    errors += 1
                    print(f"[ERR] {cell['stimulus_id']} | {model_id} | r{rep} | HTTP {result.get('http_status')}")

    logger.export_flat_csv()
    logger.write_manifest(cells=cells, models=models, replicates=args.replicates, config=run_config, completed=True)
    extend_coding_sheet(logger.run_dir, cz_agency_by_id)

    print()
    print(f"Finished: {done} requests, {errors} errors, {skipped} skipped (resume)")
    print(f"  {logger.run_dir / 'responses.jsonl'}")
    print(f"  {logger.run_dir / 'coding_sheet.csv'}  (cz_agency + 7 agency columns appended)")
    print(f"  {logger.run_dir / 'prompts_audit.csv'}")
    print(f"  {logger.run_dir / 'manifest.json'}")
    return 1 if errors and args.fail_on_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
