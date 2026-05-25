"""Trilingual translation master: export for review, sync into stimuli YAML."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "translations" / "master.yaml"


def load_master() -> dict[str, Any]:
    return yaml.safe_load(MASTER.read_text(encoding="utf-8"))


def resolve_entry(entry: dict[str, Any], entries_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Merge inherited prompts from P1-EN etc."""
    if entry.get("inherits"):
        base = entries_by_id[entry["inherits"]]
        resolved = {**base, **entry}
        for lang in ("en", "cs", "ja"):
            if lang not in resolved and lang in base:
                resolved[lang] = base[lang]
        return resolved
    return entry


def build_resolved_entries() -> list[dict[str, Any]]:
    data = load_master()
    raw = data.get("entries") or []
    by_id = {e["stimulus_id"]: e for e in raw}
    resolved = []
    for entry in raw:
        e = resolve_entry(entry, by_id)
        resolved.append(e)
    return resolved


def export_csv(out_path: Path) -> None:
    """Side-by-side EN / CS / JA for translator review."""
    rows = []
    for e in build_resolved_entries():
        rows.append(
            {
                "stimulus_id": e["stimulus_id"],
                "phase": e.get("phase"),
                "framing_note": e.get("framing_note", ""),
                "en": (e.get("en") or {}).get("prompt", ""),
                "cs": (e.get("cs") or {}).get("prompt", ""),
                "ja": (e.get("ja") or {}).get("prompt", ""),
                "en_gloss": e.get("en_gloss", ""),
                "translation_status": str(e.get("translation_status", "")),
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "stimulus_id",
                "phase",
                "framing_note",
                "en",
                "cs",
                "ja",
                "en_gloss",
                "translation_status",
            ],
        )
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out_path} ({len(rows)} rows)")


def _lang_for_stimulus(stimulus_id: str) -> str | None:
    if stimulus_id.startswith("P1-") or stimulus_id.startswith("E"):
        if stimulus_id.endswith("-EN") or stimulus_id == "E1":
            return "en"
        if stimulus_id.endswith("-CS") or stimulus_id.startswith("C"):
            return "cs"
        if stimulus_id.endswith("-JA") or stimulus_id.startswith("J"):
            return "ja"
    if stimulus_id.startswith("C"):
        return "cs"
    if stimulus_id.startswith("J"):
        return "ja"
    if stimulus_id == "E1":
        return "en"
    return None


def _block_scalar(key: str, text: str, indent: int = 2) -> str:
    pad = " " * indent
    lines = text.strip().splitlines()
    out = [f"{pad}{key}: |"]
    for line in lines:
        out.append(f"{pad}  {line}" if line else pad + "  ")
    return "\n".join(out)


def _iv_fields(meta: dict[str, Any]) -> str:
    """Emit framing IV columns; null when not set in registry."""
    lines = []
    for key in (
        "EN-AG",
        "CZ-AG",
        "CZ-OB",
        "CZ-AF",
        "CZ-PR",
        "JP-V",
        "JP-A",
        "JP-E",
        "JP-H",
        "JP-S",
    ):
        val = meta.get(key)
        lines.append(f"  {key}: {val if val is not None else 'null'}")
    return "\n".join(lines)


def regenerate_stimuli(phase: int | None) -> None:
    """Rebuild stimuli_phase*.yaml from master + registry (readable block scalars)."""
    entries = {e["stimulus_id"]: e for e in build_resolved_entries()}
    registry = yaml.safe_load((ROOT / "config" / "stimuli_registry.yaml").read_text(encoding="utf-8"))

    phases = [phase] if phase else [1, 2]
    for ph in phases:
        reg_cells = registry.get(f"phase{ph}") or []
        header = {
            1: (
                "# Phase 1 — Open language baseline\n"
                "# Prompts: translations/master.yaml | Sync: python -m antigone.translations sync\n"
            ),
            2: (
                "# Phase 2 — Linguistic framing variants\n"
                "# Prompts: translations/master.yaml | Sync: python -m antigone.translations sync\n"
            ),
        }[ph]
        parts = [
            header.rstrip(),
            "",
            "schema_version: 1",
            f"phase: {ph}",
            f"framing: {'open' if ph == 1 else 'manipulated'}",
            "",
            "cells:",
        ]
        count = 0
        for meta in reg_cells:
            sid = meta["stimulus_id"]
            e = entries.get(sid)
            if not e:
                continue
            lang = meta["language"]
            block = e.get(lang) or {}
            prompt = (block.get("prompt") or "").strip()
            if not prompt:
                print(f"Warning: no {lang} prompt for {sid}")
                continue

            cell_lines = [
                f"- stimulus_id: {sid}",
                f"  phase: {ph}",
                f"  framing: {'open' if ph == 1 else 'manipulated'}",
                f"  language: {lang}",
                _iv_fields(meta),
                _block_scalar("prompt", prompt, indent=2),
            ]
            if e.get("translation_status"):
                cell_lines.append("  translation_status:")
                for k, v in e["translation_status"].items():
                    cell_lines.append(f"    {k}: {v}")
            if e.get("framing_note"):
                cell_lines.append(f"  translation_note: {e['framing_note']}")
            if meta.get("hypothesis_note"):
                cell_lines.append(f"  hypothesis_note: {meta['hypothesis_note']}")
            parts.extend(cell_lines)
            parts.append("")
            count += 1

        path = ROOT / f"stimuli_phase{ph}.yaml"
        path.write_text("\n".join(parts), encoding="utf-8")
        print(f"Regenerated {count} cells -> {path}")


def sync_stimuli(phase: int | None) -> None:
    """Rebuild runnable stimuli from translation master."""
    regenerate_stimuli(phase)


def validate() -> int:
    """Fail if PLACEHOLDER or missing cs/ja where required."""
    issues = []
    for e in build_resolved_entries():
        sid = e["stimulus_id"]
        lang = _lang_for_stimulus(sid)
        if lang == "cs":
            text = (e.get("cs") or {}).get("prompt", "")
        elif lang == "ja":
            text = (e.get("ja") or {}).get("prompt", "")
        else:
            continue
        if not text.strip():
            issues.append(f"{sid}: missing {lang} prompt")
        if "PLACEHOLDER" in text:
            issues.append(f"{sid}: contains PLACEHOLDER")

    # Also scan runnable stimuli
    for ph in (1, 2):
        path = ROOT / f"stimuli_phase{ph}.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for cell in data.get("cells") or []:
            p = cell.get("prompt") or ""
            if "PLACEHOLDER" in p:
                issues.append(f"{cell['stimulus_id']} in {path.name}: PLACEHOLDER in prompt")

    if issues:
        for i in issues:
            print(f"  - {i}")
        return 1
    print("Translation validation OK")
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description="Trilingual translation tools")
    sub = p.add_subparsers(dest="cmd", required=True)

    ex = sub.add_parser("export", help="CSV side-by-side for reviewers")
    ex.add_argument(
        "-o",
        "--output",
        type=Path,
        default=ROOT / "translations" / "review_sheet.csv",
    )

    sy = sub.add_parser("sync", help="Write master → stimuli_phase*.yaml")
    sy.add_argument("--phase", type=int, choices=[1, 2], help="Phase to sync (default: both)")

    sub.add_parser("validate", help="Check for placeholders and missing text")

    args = p.parse_args()
    if args.cmd == "export":
        export_csv(args.output)
    elif args.cmd == "sync":
        sync_stimuli(getattr(args, "phase", None))
    elif args.cmd == "validate":
        raise SystemExit(validate())


if __name__ == "__main__":
    main()
