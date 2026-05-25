#!/usr/bin/env python3
"""Push a local run folder to Antigone Lab (Lovable ingest API)."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from antigone.lovable_ingest import push_analysis, push_catalog, push_run, resolve_run_dir

ROOT = Path(__file__).resolve().parent


def main() -> None:
    load_dotenv(ROOT / ".env")
    ap = argparse.ArgumentParser(description="POST a run to Lovable Antigone Lab ingest API")
    ap.add_argument("--phase", type=int, choices=[1, 2], help="Phase number (1 or 2)")
    ap.add_argument("--run-id", help="Run id suffix (e.g. 20260525T081321Z_8b488b4a)")
    ap.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="Run folder, e.g. logs/phase1_20260525T081321Z_8b488b4a",
    )
    ap.add_argument("--run-dir", type=Path, dest="run_dir_flag", help="Run folder (same as path)")
    ap.add_argument("--include-errors", action="store_true", help="Also push latest non-ok rows")
    ap.add_argument("--dry-run", action="store_true", help="Build payload only, no HTTP")
    ap.add_argument(
        "--with-catalog",
        action="store_true",
        help="Also push share/stimuli_reference.json after run upload",
    )
    ap.add_argument(
        "--with-analysis",
        action="store_true",
        help="Also push output/phase1_v2_cross/analysis_chart_data.json after run upload",
    )
    ap.add_argument("--url", help="Override LOVABLE_INGEST_URL")
    ap.add_argument(
        "--via",
        choices=["auto", "http", "supabase"],
        default="auto",
        help="auto: HTTP ingest if URL set, else Supabase; supabase: direct REST",
    )
    ap.add_argument(
        "--save-payload",
        type=Path,
        help="Write ingest JSON to this path (e.g. share/phase1_*_ingest.json)",
    )
    args = ap.parse_args()

    run_dir = args.run_dir_flag or args.path
    if run_dir is None and args.phase is not None and args.run_id:
        run_dir = resolve_run_dir(ROOT / "logs", args.phase, args.run_id)
    if run_dir is None:
        ap.error("Provide run_dir path or both --phase and --run-id")
    run_dir = run_dir.resolve()
    if not run_dir.is_dir():
        raise SystemExit(f"Run directory not found: {run_dir}")

    phase = args.phase
    run_id = args.run_id
    if phase is None or run_id is None:
        name = run_dir.name
        if name.startswith("phase1_"):
            phase, run_id = 1, name[len("phase1_") :]
        elif name.startswith("phase2_"):
            phase, run_id = 2, name[len("phase2_") :]
        else:
            phase = phase or 1
            run_id = run_id or run_dir.name
    payload_out = args.save_payload
    if payload_out is None and not args.dry_run:
        payload_out = ROOT / "share" / f"phase{phase}_{run_id}_ingest.json"

    result = push_run(
        run_dir,
        via=args.via,
        ingest_url=args.url,
        ok_only=not args.include_errors,
        dry_run=args.dry_run,
        save_payload=payload_out,
    )
    if result.get("dry_run"):
        print(f"[dry-run] would POST run_id={result['run_id']} records={result['count']}")
        print(f"  url: {result['url']}")
    else:
        print(f"[ok] via={result.get('via')} run_id={result['run_id']} count={result['count']}")
        if payload_out:
            print(f"  payload saved: {payload_out}")

    if args.with_catalog and not args.dry_run:
        catalog_path = ROOT / "share" / "stimuli_reference.json"
        try:
            cat = push_catalog(catalog_path, catalog_url=args.url)
            print(f"[ok] catalog pushed: cells={cat['cells']}")
        except RuntimeError as exc:
            print(f"[warn] catalog push failed: {exc}")

    if args.with_analysis and not args.dry_run:
        analysis_path = ROOT / "output" / "phase1_v2_cross" / "analysis_chart_data.json"
        try:
            ana = push_analysis(analysis_path, analysis_url=args.url)
            print(f"[ok] analysis pushed: run_id={ana.get('run_id')}")
        except RuntimeError as exc:
            print(f"[warn] analysis push failed: {exc}")


if __name__ == "__main__":
    main()
