"""Run stateless simulation — log only, no analysis."""

from __future__ import annotations

import argparse
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from antigone.completion import complete
from antigone.openrouter import uses_openai_direct
from antigone.research_log import RunLogger
from antigone.response_utils import deterministic_seed
from antigone.stimuli import build_prompt_text, load_stimuli

ROOT = Path(__file__).resolve().parent.parent


def load_models(
    config_path: Path,
    *,
    groups: list[str] | None,
    model_filter: list[str] | None,
) -> list[dict[str, Any]]:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    models = data.get("models") or []
    if groups:
        models = [m for m in models if m.get("group") in groups]
    if model_filter:
        allowed = set(model_filter)
        models = [m for m in models if m["id"] in allowed]
    return models


def run(args: argparse.Namespace) -> int:
    load_dotenv(ROOT / ".env")
    import os

    openrouter_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")

    cells = load_stimuli(args.phase)
    if args.stimulus:
        allowed = set(args.stimulus)
        cells = [c for c in cells if c["stimulus_id"] in allowed]

    models = load_models(
        ROOT / "config" / "models.yaml",
        groups=args.group,
        model_filter=args.models,
    )
    if not models:
        raise SystemExit("No models selected — check config/models.yaml and filters")

    needs_openrouter = any(not uses_openai_direct(m) for m in models)
    needs_openai = any(uses_openai_direct(m) for m in models)
    if needs_openrouter and not openrouter_key:
        raise SystemExit("Set OPENROUTER_API_KEY in .env (required for non-OpenAI models)")
    if needs_openai and not openai_key:
        raise SystemExit("Set OPENAI_API_KEY in .env (required for openai/* models)")

    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    logger = RunLogger(ROOT, args.phase, run_id)

    run_config = {
        "temperature": args.temperature,
        "allow_fallbacks": False,
        "replicates": args.replicates,
        "timeout_s": args.timeout,
        "stimulus_filter": args.stimulus,
        "model_groups": args.group,
        "model_filter": args.models,
        "store_raw": args.store_raw,
    }

    logger.snapshot_stimuli(cells)
    logger.write_manifest(
        cells=cells,
        models=models,
        replicates=args.replicates,
        config=run_config,
        completed=False,
    )

    total = len(cells) * len(models) * args.replicates
    done = 0
    errors = 0
    skipped = 0

    print(f"Run ID: {run_id}")
    print(f"Run directory: {logger.run_dir}")
    print(f"Cells: {len(cells)} | Models: {len(models)} | Replicates: {args.replicates}")
    print(f"Total requests (max): {total}")
    openai_ids = [m["id"] for m in models if uses_openai_direct(m)]
    or_ids = [m["id"] for m in models if not uses_openai_direct(m)]
    print(f"Mode: stateless prompt-only, temperature={args.temperature}, no provider fallbacks")
    if openai_ids:
        print(f"  OpenAI direct: {', '.join(openai_ids)}")
    if or_ids:
        print(f"  OpenRouter: {', '.join(or_ids)}")
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
                    cell=cell,
                    model=model,
                    replicate=rep,
                    seed=seed,
                    prompt_text=prompt_text,
                    result=result,
                    store_raw=args.store_raw,
                )
                logger.append(record)
                done += 1

                if result.get("status") == "ok":
                    preview = (result.get("response_text") or "")[:80].replace("\n", " ")
                    try:
                        print(f"[ok] {cell['stimulus_id']} | {model_id} | r{rep} | {preview}...")
                    except UnicodeEncodeError:
                        print(f"[ok] {cell['stimulus_id']} | {model_id} | r{rep} | ({len(result.get('response_text') or '')} chars)")
                else:
                    errors += 1
                    print(f"[ERR] {cell['stimulus_id']} | {model_id} | r{rep} | HTTP {result.get('http_status')}")

    logger.export_flat_csv()
    logger.write_manifest(
        cells=cells,
        models=models,
        replicates=args.replicates,
        config=run_config,
        completed=True,
    )

    print()
    print(f"Finished: {done} requests, {errors} errors, {skipped} skipped (resume)")
    print(f"  responses.jsonl + responses_flat.csv + coding_sheet.csv")
    print(f"  manifest.json + prompts_audit.csv")
    print(f"  Legacy copy: {logger.legacy_jsonl_path}")

    if args.push_lovable:
        try:
            from antigone.lovable_ingest import push_run

            result = push_run(logger.run_dir)
            print(f"Lovable ingest: run_id={result['run_id']} count={result['count']}")
        except Exception as exc:
            print(f"Lovable ingest failed: {exc}")
            return 1

    return 1 if errors and args.fail_on_error else 0


def main() -> None:
    p = argparse.ArgumentParser(
        description="Stateless Antigone runner (OpenAI direct for openai/*, OpenRouter otherwise)"
    )
    p.add_argument("--phase", type=int, choices=[1, 2], required=True)
    p.add_argument("--replicates", type=int, default=3)
    p.add_argument("--group", action="append", help="Filter model group (repeatable)")
    p.add_argument("--models", nargs="+", help="Exact OpenRouter model IDs")
    p.add_argument("--stimulus", nargs="+", help="Only these stimulus_id values")
    p.add_argument("--run-id", help="Custom run id (directory name suffix)")
    p.add_argument("--resume", action="store_true", help="Skip completed ok rows in this run's logs")
    p.add_argument("--timeout", type=float, default=180.0)
    p.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature. 0.0 = deterministic (Phase 1 default); 0.3 recommended for Phase 2 to surface replicate variance.",
    )
    p.add_argument("--store-raw", action="store_true", help="Include full API JSON in jsonl (large)")
    p.add_argument("--fail-on-error", action="store_true", help="Exit 1 if any request failed")
    p.add_argument(
        "--push-lovable",
        action="store_true",
        help="After run completes, POST to Lovable ingest (needs ANTIGONE_INGEST_SECRET in .env)",
    )
    run(p.parse_args())


if __name__ == "__main__":
    main()
