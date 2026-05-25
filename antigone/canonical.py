"""Canonical run logs: one ok row per cell_key (latest timestamp)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from antigone.research_log import RunLogger


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def latest_per_cell(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row.get("cell_key")
        if not key:
            continue
        prev = latest.get(key)
        if prev is None or row.get("timestamp_utc", "") >= prev.get("timestamp_utc", ""):
            latest[key] = row
    return latest


def canonical_rows(
    rows: list[dict[str, Any]],
    *,
    manifest: dict[str, Any] | None = None,
    ok_only: bool = True,
) -> list[dict[str, Any]]:
    design = (manifest or {}).get("design") or {}
    allowed_models = set(design.get("models") or [])
    latest = latest_per_cell(rows)
    out: list[dict[str, Any]] = []
    for row in latest.values():
        if allowed_models and row.get("model_requested") not in allowed_models:
            continue
        if ok_only:
            if row.get("status") != "ok":
                continue
            if not (row.get("response_text") or "").strip():
                continue
        out.append(row)
    out.sort(
        key=lambda r: (
            r.get("stimulus_id", ""),
            r.get("model_requested", ""),
            r.get("replicate", 0),
        )
    )
    return out


def canonicalize_run_dir(run_dir: Path, *, archive: bool = True) -> int:
    """Replace responses.jsonl with canonical rows; refresh CSV exports."""
    run_dir = run_dir.resolve()
    jsonl_path = run_dir / "responses.jsonl"
    if not jsonl_path.exists():
        raise FileNotFoundError(jsonl_path)

    manifest_path = run_dir / "manifest.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {}
    )
    all_rows = load_jsonl(jsonl_path)
    canon = canonical_rows(all_rows, manifest=manifest, ok_only=True)
    if not canon:
        raise ValueError(f"No canonical ok rows in {run_dir}")

    if archive and len(all_rows) > len(canon):
        archive_path = run_dir / "responses_archive.jsonl"
        shutil.copy2(jsonl_path, archive_path)

    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in canon:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Drop legacy flat duplicate at logs root
    legacy = run_dir.parent / f"{run_dir.name}.jsonl"
    if legacy.exists():
        legacy.unlink()

    # Rebuild flat exports from canonical jsonl
    parts = run_dir.name.split("_", 1)
    phase = int(parts[0].replace("phase", "")) if parts[0].startswith("phase") else 1
    run_id = parts[1] if len(parts) > 1 else run_dir.name
    logger = RunLogger(run_dir.parent, phase, run_id)
    logger.export_flat_csv()

    return len(canon)
