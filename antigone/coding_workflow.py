"""Manual codebook merge, validate, and coded analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd

from antigone.canonical import canonical_rows, load_jsonl
from antigone.codebook_schema import (
    ALLOWED,
    CODING_COLUMNS,
    META_COLUMNS,
    RECOMMENDED_PHASE1,
    REQUIRED_PHASE1,
    REQUIRED_PHASE1_JA,
)
ROOT = Path(__file__).resolve().parent.parent


def _empty(val: Any) -> bool:
    if val is None:
        return True
    return not str(val).strip()


def _split_var_g(val: Any) -> list[str]:
    if _empty(val):
        return []
    return [p.strip() for p in str(val).split(",") if p.strip()]


def validate_row(row: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    lang = row.get("language")
    phase = row.get("phase")

    for col, allowed in ALLOWED.items():
        if allowed is None:
            continue
        val = row.get(col)
        if _empty(val):
            if col in REQUIRED_PHASE1 and phase == 1:
                issues.append(f"missing {col}")
            if col in REQUIRED_PHASE1_JA and lang == "ja" and phase == 1:
                issues.append(f"missing {col} (ja)")
            continue
        if col == "code_var_g":
            for tag in _split_var_g(val):
                if tag not in allowed:
                    issues.append(f"invalid {col} tag: {tag}")
        elif str(val).strip() not in allowed:
            issues.append(f"invalid {col}: {val}")
    return issues


def load_coded_import(path: Path) -> dict[str, dict[str, str]]:
    """record_id -> coding fields from Lovable export or partial CSV."""
    by_id: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row.get("record_id")
            if not rid:
                continue
            patch = {}
            for col in [*CODING_COLUMNS, *META_COLUMNS]:
                if col in row and not _empty(row.get(col)):
                    patch[col] = str(row[col]).strip()
            if patch:
                by_id[rid] = patch
    return by_id


def merge_coding_into_run(run_dir: Path, coded_csv: Path) -> tuple[int, int]:
    """Apply coded import to responses.jsonl and coding_sheet.csv."""
    run_dir = run_dir.resolve()
    jsonl_path = run_dir / "responses.jsonl"
    rows = load_jsonl(jsonl_path)
    patches = load_coded_import(coded_csv)
    updated = 0
    for row in rows:
        rid = row.get("record_id")
        if rid not in patches:
            continue
        row.update(patches[rid])
        updated += 1

    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    coding_path = run_dir / "coding_sheet.csv"
    if coding_path.exists():
        sheet = pd.read_csv(coding_path, encoding="utf-8-sig", dtype=str)
        for col in [*CODING_COLUMNS, *META_COLUMNS]:
            if col in sheet.columns:
                sheet[col] = sheet[col].fillna("").astype(str).replace("nan", "")
        for idx, row in sheet.iterrows():
            rid = row.get("record_id")
            if rid in patches:
                for k, v in patches[rid].items():
                    if k in sheet.columns:
                        sheet.at[idx, k] = v
        sheet.to_csv(coding_path, index=False, encoding="utf-8-sig")

    return updated, len(patches)


def validation_report(run_dir: Path) -> pd.DataFrame:
    manifest = {}
    mp = run_dir / "manifest.json"
    if mp.exists():
        manifest = json.loads(mp.read_text(encoding="utf-8"))
    rows = canonical_rows(load_jsonl(run_dir / "responses.jsonl"), manifest=manifest)
    records = []
    for row in rows:
        issues = validate_row(row)
        records.append(
            {
                "record_id": row.get("record_id"),
                "cell_key": row.get("cell_key"),
                "language": row.get("language"),
                "stimulus_id": row.get("stimulus_id"),
                "model_requested": row.get("model_requested"),
                "replicate": row.get("replicate"),
                "issues": "; ".join(issues) if issues else "",
                "complete": len(issues) == 0,
                **{c: row.get(c) for c in CODING_COLUMNS},
            }
        )
    return pd.DataFrame(records)


def coded_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate manual codes (ok rows with code_var_a filled)."""
    coded = df[df["code_var_a"].notna() & (df["code_var_a"].astype(str).str.strip() != "")]
    if coded.empty:
        return pd.DataFrame()
    return (
        coded.groupby(["language", "code_var_a", "code_var_d"], dropna=False)
        .size()
        .reset_index(name="n")
    )
