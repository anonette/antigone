"""Load stimulus reference catalog and merge into runnable cells."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "stimuli_catalog.yaml"


def load_catalog() -> dict[str, Any]:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"Missing {CATALOG_PATH}")
    return yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))


def catalog_cells() -> dict[str, dict[str, Any]]:
    data = load_catalog()
    return dict(data.get("cells") or {})


def merge_catalog(cell: dict[str, Any]) -> dict[str, Any]:
    """Attach label, descriptions, baseline from catalog when stimulus_id matches."""
    meta = catalog_cells().get(cell.get("stimulus_id", ""))
    if not meta:
        return cell
    out = dict(cell)
    for key in (
        "label",
        "description_en",
        "description_cs",
        "baseline_stimulus_id",
        "compare_to",
        "framing_axes",
        "framing_summary",
    ):
        if key in meta and meta[key] is not None:
            out[key] = meta[key]
    return out


def build_reference_json(*, include_prompts: bool = True) -> dict[str, Any]:
    from antigone.stimuli import build_prompt_text, load_stimuli

    catalog = load_catalog()
    cells_out: list[dict[str, Any]] = []
    for phase in (1, 2):
        for cell in load_stimuli(phase):
            sid = cell["stimulus_id"]
            meta = dict(catalog_cells().get(sid, {}))
            entry: dict[str, Any] = {
                "stimulus_id": sid,
                "phase": cell.get("phase"),
                "language": cell.get("language"),
                "framing": cell.get("framing"),
                "label": meta.get("label", sid),
                "description_en": meta.get("description_en", ""),
                "description_cs": meta.get("description_cs", ""),
                "baseline_stimulus_id": meta.get("baseline_stimulus_id", sid),
                "compare_to": meta.get("compare_to"),
                "framing_axes": meta.get("framing_axes"),
                "translation_note": cell.get("translation_note"),
                "hypothesis_note": cell.get("hypothesis_note"),
                "IV": {k: cell.get(k) for k in IV_COLUMNS if cell.get(k) is not None},
            }
            if include_prompts:
                entry["prompt_text"] = build_prompt_text(cell)
            cells_out.append(entry)

    page = dict(catalog.get("page") or {})
    return {
        "schema_version": catalog.get("schema_version", 1),
        "page": page,
        "phase1_summary_en": catalog.get("phase1_summary_en", "").strip(),
        "phase1_summary_cs": catalog.get("phase1_summary_cs", "").strip(),
        "phase2_summary_en": catalog.get("phase2_summary_en", "").strip(),
        "phase2_summary_cs": catalog.get("phase2_summary_cs", "").strip(),
        "cells": cells_out,
    }


IV_COLUMNS = (
    "EN-AG",
    "EN-OB",
    "EN-AF",
    "EN-PR",
    "EN-E",
    "EN-A",
    "EN-V",
    "CZ-AG",
    "CZ-OB",
    "CZ-AF",
    "CZ-PR",
    "JP-V",
    "JP-A",
    "JP-E",
    "JP-H",
    "JP-S",
)


def write_reference_json(path: Path) -> Path:
    payload = build_reference_json()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
