#!/usr/bin/env python3
"""
Manual codebook workflow: canonicalize logs, merge Lovable exports, validate, analyze.

Examples:
  python recode.py canonicalize --run-dir logs/phase1_20260525T081321Z_8b488b4a
  python recode.py merge --run-dir logs/phase1_... --from coded_export.csv
  python recode.py validate --run-dir logs/phase1_...
  python recode.py analyze --run-dir logs/phase1_...
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from antigone.canonical import canonicalize_run_dir
from antigone.coding_workflow import coded_summary, merge_coding_into_run, validation_report

OUTPUT = ROOT / "output"


def resolve_run_dir(args: argparse.Namespace) -> Path:
    if args.run_dir:
        return Path(args.run_dir).resolve()
    if args.phase and args.run_id:
        return ROOT / "logs" / f"phase{args.phase}_{args.run_id}"
    raise SystemExit("Provide --run-dir or --phase and --run-id")


def cmd_canonicalize(args: argparse.Namespace) -> None:
    run_dir = resolve_run_dir(args)
    n = canonicalize_run_dir(run_dir, archive=not args.no_archive)
    print(f"Canonicalized {run_dir.name}: {n} ok rows")
    if (run_dir / "responses_archive.jsonl").exists():
        print(f"  Archive: {run_dir / 'responses_archive.jsonl'}")


def cmd_merge(args: argparse.Namespace) -> None:
    run_dir = resolve_run_dir(args)
    from_path = Path(args.from_path).resolve()
    updated, total = merge_coding_into_run(run_dir, from_path)
    print(f"Merged {updated}/{total} patches from {from_path.name} into {run_dir.name}")
    from antigone.research_log import RunLogger

    parts = run_dir.name.split("_", 1)
    phase = int(parts[0].replace("phase", ""))
    run_id = parts[1]
    RunLogger(run_dir.parent, phase, run_id).export_flat_csv()
    # Slim sheet without multiline response_text (Excel-safe)
    import subprocess

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "rebuild_coding_sheet.py"), "--run-dir", str(run_dir)],
        check=True,
    )


def cmd_validate(args: argparse.Namespace) -> None:
    run_dir = resolve_run_dir(args)
    df = validation_report(run_dir)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    out = OUTPUT / f"coding_validation_{run_dir.name}.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    n_ok = int(df["complete"].sum()) if "complete" in df.columns else 0
    print(f"Validation: {n_ok}/{len(df)} complete -> {out}")
    incomplete = df[~df["complete"]] if "complete" in df.columns else df
    if not incomplete.empty and args.strict:
        raise SystemExit(f"{len(incomplete)} rows have codebook issues")


def cmd_analyze(args: argparse.Namespace) -> None:
    run_dir = resolve_run_dir(args)
    run_id = run_dir.name.split("_", 1)[-1]
    phase = int(run_dir.name.split("_")[0].replace("phase", ""))
    subprocess.run(
        [sys.executable, str(ROOT / "analyze.py"), "--phase", str(phase), "--run-id", run_id],
        check=True,
    )
    df = validation_report(run_dir)
    summary = coded_summary(df)
    if not summary.empty:
        path = OUTPUT / f"coded_summary_{run_dir.name}.csv"
        summary.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"Coded summary: {path}")
    else:
        print("No manual code_var_a filled yet — run merge after Lovable export.")


def main() -> None:
    p = argparse.ArgumentParser(description="Antigone manual coding workflow")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("canonicalize", help="One ok row per cell_key; refresh coding_sheet")
    c.add_argument("--run-dir", type=Path)
    c.add_argument("--phase", type=int, choices=[1, 2])
    c.add_argument("--run-id")
    c.add_argument("--no-archive", action="store_true")
    c.set_defaults(func=cmd_canonicalize)

    m = sub.add_parser("merge", help="Merge Lovable coded CSV into run logs")
    m.add_argument("--run-dir", type=Path)
    m.add_argument("--phase", type=int, choices=[1, 2])
    m.add_argument("--run-id")
    m.add_argument("--from", dest="from_path", required=True, help="Exported coded CSV")
    m.set_defaults(func=cmd_merge)

    v = sub.add_parser("validate", help="Check codebook values and required fields")
    v.add_argument("--run-dir", type=Path)
    v.add_argument("--phase", type=int, choices=[1, 2])
    v.add_argument("--run-id")
    v.add_argument("--strict", action="store_true")
    v.set_defaults(func=cmd_validate)

    a = sub.add_parser("analyze", help="analyze.py + coded summary if codes present")
    a.add_argument("--run-dir", type=Path)
    a.add_argument("--phase", type=int, choices=[1, 2])
    a.add_argument("--run-id")
    a.set_defaults(func=cmd_analyze)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
