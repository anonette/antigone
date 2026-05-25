"""Load stimulus YAML registries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_stimuli(phase: int, *, merge_reference: bool = True) -> list[dict[str, Any]]:
    path = ROOT / f"stimuli_phase{phase}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    cells = data.get("cells") or []
    if merge_reference:
        from antigone.stimuli_catalog import merge_catalog

        cells = [merge_catalog(cell) for cell in cells]
    for cell in cells:
        cell["phase"] = phase
    return cells


def build_prompt_text(cell: dict[str, Any]) -> str:
    """Single plain-text prompt: scenario + questions only; no separate instructions."""
    return (cell.get("prompt") or "").strip()
