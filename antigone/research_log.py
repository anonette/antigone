"""Research-oriented logging: manifest, stable schema, analysis-ready exports."""

from __future__ import annotations

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

LOG_SCHEMA_VERSION = 1

# Phase-2 cells map to same-language Phase-1 baseline for within-language comparison.
BASELINE_STIMULUS: dict[str, str] = {
    "E1": "P1-EN",
    "E2": "P1-EN",
    "E3": "P1-EN",
    "E4": "P1-EN",
    "E5": "P1-EN",
    "E6": "P1-EN",
    "E7": "P1-EN",
    "E8": "P1-EN",
    "C1": "P1-CS",
    "C2": "P1-CS",
    "C3": "P1-CS",
    "C4": "P1-CS",
    "C5": "P1-CS",
    "J1": "P1-JA",
    "J2": "P1-JA",
    "J3": "P1-JA",
    "J4": "P1-JA",
    "J5": "P1-JA",
    "J6": "P1-JA",
    "J7": "P1-JA",
    "J8": "P1-JA",
    "J9": "P1-JA",
    "P1-EN": "P1-EN",
    "P1-CS": "P1-CS",
    "P1-JA": "P1-JA",
}

IV_COLUMNS = [
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
]

CODING_COLUMNS = [
    "code_var_a",
    "code_var_b",
    "code_var_c",
    "code_var_d",
    "code_var_e",
    "code_var_f",
    "code_var_g",
    "code_var_r",
    "coder_id",
    "coded_at",
]

FLAT_COLUMNS = [
    "schema_version",
    "record_id",
    "run_id",
    "row_index",
    "timestamp_utc",
    "phase",
    "framing",
    "language",
    "stimulus_id",
    "baseline_stimulus_id",
    "translation_note",
    *IV_COLUMNS,
    "model_requested",
    "model_actual",
    "model_group",
    "model_thinking",
    "api_backend",
    "request_mode",
    "replicate",
    "seed",
    "cell_key",
    "prompt_char_len",
    "status",
    "http_status",
    "latency_ms",
    "error_message",
    "response_text",
    "reasoning_text",
    "response_char_len",
    "response_word_count",
    "has_reasoning",
    "tokens_prompt",
    "tokens_completion",
    "tokens_total",
    "tokens_reasoning",
    "finish_reason",
    "provider_response_id",
    *CODING_COLUMNS,
]


def _word_count(text: str | None) -> int:
    if not text or not str(text).strip():
        return 0
    return len(str(text).split())


def _flatten_usage(usage: Any) -> dict[str, int | None]:
    if not isinstance(usage, dict):
        return {
            "tokens_prompt": None,
            "tokens_completion": None,
            "tokens_total": None,
            "tokens_reasoning": None,
        }
    prompt = usage.get("prompt_tokens")
    completion = usage.get("completion_tokens")
    total = usage.get("total_tokens")
    reasoning = None
    details = usage.get("completion_tokens_details") or usage.get("output_tokens_details")
    if isinstance(details, dict):
        reasoning = details.get("reasoning_tokens")
    return {
        "tokens_prompt": prompt,
        "tokens_completion": completion,
        "tokens_total": total,
        "tokens_reasoning": reasoning,
    }


def baseline_for(stimulus_id: str) -> str:
    return BASELINE_STIMULUS.get(stimulus_id, stimulus_id)


def cell_key(stimulus_id: str, model_id: str, replicate: int) -> str:
    return f"{stimulus_id}|{model_id}|{replicate}"


class RunLogger:
    """One run → one directory with manifest, jsonl, and flat CSV."""

    def __init__(self, root: Path, phase: int, run_id: str) -> None:
        self.root = root
        self.phase = phase
        self.run_id = run_id
        self.run_dir = root / "logs" / f"phase{phase}_{run_id}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.run_dir / "responses.jsonl"
        self.csv_path = self.run_dir / "responses_flat.csv"
        self.manifest_path = self.run_dir / "manifest.json"
        self._row_index = 0
        self._stats = {"ok": 0, "error": 0, "skipped": 0}
        self._started = datetime.now(timezone.utc).isoformat()

    @property
    def legacy_jsonl_path(self) -> Path:
        """Flat path for backward compatibility."""
        return self.root / "logs" / f"phase{self.phase}_{self.run_id}.jsonl"

    def write_manifest(
        self,
        *,
        cells: list[dict[str, Any]],
        models: list[dict[str, Any]],
        replicates: int,
        config: dict[str, Any],
        completed: bool = False,
    ) -> None:
        manifest = {
            "schema_version": LOG_SCHEMA_VERSION,
            "run_id": self.run_id,
            "phase": self.phase,
            "started_at_utc": self._started,
            "completed_at_utc": datetime.now(timezone.utc).isoformat() if completed else None,
            "config": config,
            "design": {
                "stimuli": [c["stimulus_id"] for c in cells],
                "languages": sorted({c.get("language") for c in cells if c.get("language")}),
                "models": [m["id"] for m in models],
                "model_groups": sorted({m.get("group") for m in models if m.get("group")}),
                "replicates": replicates,
                "planned_requests": len(cells) * len(models) * replicates,
            },
            "stats": dict(self._stats),
            "files": {
                "responses_jsonl": str(self.jsonl_path.relative_to(self.root)),
                "responses_csv": str(self.csv_path.relative_to(self.root)),
                "legacy_jsonl": str(self.legacy_jsonl_path.relative_to(self.root)),
                "stimuli_snapshot": "stimuli_snapshot.yaml",
            },
            "analysis_hints": {
                "primary_keys": ["record_id", "cell_key"],
                "compare_baseline": "Join on model_requested, replicate, baseline_stimulus_id vs stimulus_id",
                "coding_columns": CODING_COLUMNS,
                "iv_columns": IV_COLUMNS,
            },
        }
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def snapshot_stimuli(self, cells: list[dict[str, Any]]) -> None:
        path = self.run_dir / "stimuli_snapshot.yaml"
        path.write_text(
            yaml.dump({"cells": cells}, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def is_done(self, stimulus_id: str, model_id: str, replicate: int) -> bool:
        for path in (self.jsonl_path, self.legacy_jsonl_path):
            if not path.exists():
                continue
            with path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if (
                        row.get("stimulus_id") == stimulus_id
                        and row.get("model_requested") == model_id
                        and row.get("replicate") == replicate
                        and row.get("status") == "ok"
                        and (row.get("response_text") or "").strip()
                    ):
                        return True
        return False

    def build_record(
        self,
        *,
        cell: dict[str, Any],
        model: dict[str, Any],
        replicate: int,
        seed: int,
        prompt_text: str,
        result: dict[str, Any],
        store_raw: bool = False,
    ) -> dict[str, Any]:
        self._row_index += 1
        stimulus_id = cell["stimulus_id"]
        model_id = model["id"]
        response_text = result.get("response_text")
        reasoning_text = result.get("reasoning_text")
        usage = _flatten_usage(result.get("usage"))

        record: dict[str, Any] = {
            "schema_version": LOG_SCHEMA_VERSION,
            "record_id": str(uuid.uuid4()),
            "run_id": self.run_id,
            "row_index": self._row_index,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "phase": cell.get("phase"),
            "framing": cell.get("framing"),
            "language": cell.get("language"),
            "stimulus_id": stimulus_id,
            "baseline_stimulus_id": baseline_for(stimulus_id),
            "translation_note": cell.get("translation_note"),
            "model_requested": model_id,
            "model_actual": result.get("model_actual"),
            "model_group": model.get("group"),
            "model_thinking": bool(model.get("thinking")),
            "api_backend": result.get("api_backend"),
            "request_mode": result.get("request_mode"),
            "replicate": replicate,
            "seed": seed,
            "cell_key": cell_key(stimulus_id, model_id, replicate),
            "prompt_char_len": len(prompt_text),
            "prompt_text": prompt_text,
            "status": result.get("status"),
            "http_status": result.get("http_status"),
            "latency_ms": result.get("latency_ms"),
            "error_message": result.get("error") if result.get("status") != "ok" else None,
            "response_text": response_text,
            "reasoning_text": reasoning_text,
            "response_char_len": len(response_text or ""),
            "response_word_count": _word_count(response_text),
            "has_reasoning": bool(reasoning_text and str(reasoning_text).strip()),
            "finish_reason": result.get("finish_reason"),
            "provider_response_id": result.get("openrouter_id") or result.get("openai_id"),
            **{col: cell.get(col) for col in IV_COLUMNS},
            **{col: None for col in CODING_COLUMNS},
            **usage,
        }
        if store_raw:
            record["raw_response"] = result.get("raw_response")
        return record

    def append(self, record: dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False) + "\n"
        for path in (self.jsonl_path, self.legacy_jsonl_path):
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(line)
        if record.get("status") == "ok":
            self._stats["ok"] += 1
        else:
            self._stats["error"] += 1

    def note_skipped(self, n: int = 1) -> None:
        self._stats["skipped"] += n

    def export_flat_csv(self) -> None:
        """Rebuild flat CSV from jsonl (no prompt_text by default for size)."""
        rows: list[dict[str, Any]] = []
        if not self.jsonl_path.exists():
            return
        with self.jsonl_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        if not rows:
            return

        export_cols = [c for c in FLAT_COLUMNS if c != "prompt_text"]
        # Include prompt_text in separate file for audit
        audit_path = self.run_dir / "prompts_audit.csv"
        with audit_path.open("w", encoding="utf-8-sig", newline="") as af:
            aw = csv.DictWriter(af, fieldnames=["record_id", "cell_key", "stimulus_id", "prompt_text"])
            aw.writeheader()
            for r in rows:
                aw.writerow(
                    {
                        "record_id": r.get("record_id"),
                        "cell_key": r.get("cell_key"),
                        "stimulus_id": r.get("stimulus_id"),
                        "prompt_text": r.get("prompt_text", ""),
                    }
                )

        with self.csv_path.open("w", encoding="utf-8-sig", newline="") as cf:
            writer = csv.DictWriter(cf, fieldnames=export_cols, extrasaction="ignore")
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k) for k in export_cols})

        coding_path = self.run_dir / "coding_sheet.csv"
        coding_fields = [
            "record_id",
            "cell_key",
            "run_id",
            "phase",
            "language",
            "stimulus_id",
            "baseline_stimulus_id",
            "model_requested",
            "model_group",
            "replicate",
            "translation_note",
            *IV_COLUMNS,
            "response_char_len",
            "response_word_count",
            *CODING_COLUMNS,
            "coder_id",
            "coded_at",
        ]
        with coding_path.open("w", encoding="utf-8-sig", newline="") as cf:
            writer = csv.DictWriter(cf, fieldnames=coding_fields, extrasaction="ignore")
            writer.writeheader()
            for r in rows:
                if r.get("status") != "ok":
                    continue
                writer.writerow({k: r.get(k) for k in coding_fields})


def discover_log_sources(logs_root: Path) -> list[dict[str, Any]]:
    """Find all run directories and legacy flat jsonl files."""
    sources: list[dict[str, Any]] = []
    if not logs_root.exists():
        return sources

    for path in sorted(logs_root.iterdir()):
        if path.is_dir() and (path / "responses.jsonl").exists():
            sources.append(
                {
                    "type": "run_dir",
                    "path": path,
                    "jsonl": path / "responses.jsonl",
                    "manifest": path / "manifest.json",
                    "run_id": path.name,
                }
            )

    for path in sorted(logs_root.glob("phase*.jsonl")):
        if path.is_file():
            sources.append(
                {
                    "type": "legacy_jsonl",
                    "path": path,
                    "jsonl": path,
                    "manifest": None,
                    "run_id": path.stem,
                }
            )
    return sources


def load_all_responses(logs_root: Path, *, phase: int | None = None) -> list[dict[str, Any]]:
    """Load responses; dedupe by record_id (legacy flat jsonl duplicates run-dir jsonl)."""
    by_id: dict[str, dict[str, Any]] = {}
    for src in discover_log_sources(logs_root):
        if phase is not None and f"phase{phase}_" not in src["run_id"]:
            continue
        with src["jsonl"].open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                rid = row.get("record_id")
                if rid:
                    by_id[rid] = row
                else:
                    by_id[f"__noid_{len(by_id)}"] = row
    return list(by_id.values())
