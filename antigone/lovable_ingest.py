"""Push a completed run to Antigone Lab (Lovable HTTP ingest or Supabase REST)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal

import httpx

DEFAULT_SUPABASE_URL = "https://ssxrezezuydvzzjdlktr.supabase.co"
DEFAULT_IMPORTS_TABLE = "antigone_imports"
PREVIEW_HOST_MARKER = "id-preview--"

RECORD_STRIP_KEYS = frozenset({"raw_response"})
ViaMode = Literal["auto", "http", "supabase"]


def ingest_run_id(manifest: dict[str, Any]) -> str:
    """Lovable upsert key: phase{N}_{run_id} (matches logs folder name)."""
    phase = manifest.get("phase")
    run_id = manifest.get("run_id", "")
    if phase is not None:
        return f"phase{phase}_{run_id}"
    return str(run_id)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def dedupe_latest_cell(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row.get("cell_key")
        if not key:
            continue
        prev = latest.get(key)
        if prev is None or row.get("timestamp_utc", "") >= prev.get("timestamp_utc", ""):
            latest[key] = row
    return list(latest.values())


def select_records_for_ingest(
    rows: list[dict[str, Any]],
    *,
    manifest: dict[str, Any],
    ok_only: bool = True,
) -> list[dict[str, Any]]:
    """Latest row per cell_key; optional filter to manifest models and ok status."""
    design = manifest.get("design") or {}
    allowed_models = set(design.get("models") or [])
    latest = dedupe_latest_cell(rows)
    out: list[dict[str, Any]] = []
    for row in latest:
        if allowed_models and row.get("model_requested") not in allowed_models:
            continue
        if ok_only:
            if row.get("status") != "ok":
                continue
            if not (row.get("response_text") or "").strip():
                continue
        out.append(sanitize_record(row))
    out.sort(key=lambda r: (r.get("stimulus_id", ""), r.get("model_requested", ""), r.get("replicate", 0)))
    return out


def sanitize_record(row: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in row.items() if k not in RECORD_STRIP_KEYS}


def build_run_meta(manifest: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    design = manifest.get("design") or {}
    stats = manifest.get("stats") or {}
    return {
        "run_id": ingest_run_id(manifest),
        "phase": manifest.get("phase"),
        "started_at": manifest.get("started_at_utc"),
        "completed_at": manifest.get("completed_at_utc"),
        "stimuli": design.get("stimuli") or [],
        "models": design.get("models") or [],
        "replicates": design.get("replicates"),
        "stats": {
            "ok": len(records),
            "error": stats.get("error", 0),
            "skipped": stats.get("skipped", 0),
            "total": len(records),
        },
    }


def default_ingest_candidates(project_id: str = "eb15caff-c2b0-41c2-8ad1-843acce73d3c") -> list[str]:
    """URLs to try in order (project → published id → preview)."""
    return [
        f"https://project--{project_id}.lovable.app/api/public/ingest",
        f"https://{project_id}.lovable.app/api/public/ingest",
        f"https://id-preview--{project_id}.lovable.app/api/public/ingest",
    ]


def resolve_ingest_urls(explicit: str | None = None, root: Path | None = None) -> list[str]:
    if explicit:
        return [_ingest_endpoint(explicit.rstrip("/"))]
    env = (os.environ.get("LOVABLE_INGEST_URL") or "").strip()
    urls: list[str] = []
    if env:
        urls.append(_ingest_endpoint(env.rstrip("/")))
    if root is None:
        root = Path(__file__).resolve().parent.parent
    url_file = root / "lovable_publish_url.txt"
    if url_file.exists():
        for line in url_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(_ingest_endpoint(line.rstrip("/")))
    for candidate in default_ingest_candidates():
        if candidate not in urls:
            urls.append(candidate)
    return urls


def resolve_ingest_url(explicit: str | None = None, root: Path | None = None) -> str:
    if explicit:
        return explicit.rstrip("/") + ("" if explicit.endswith("/ingest") else "")
    env = (os.environ.get("LOVABLE_INGEST_URL") or "").strip()
    if env:
        return env.rstrip("/")
    if root is None:
        root = Path(__file__).resolve().parent.parent
    url_file = root / "lovable_publish_url.txt"
    if url_file.exists():
        line = url_file.read_text(encoding="utf-8").strip().splitlines()[0].strip()
        if line:
            return line.rstrip("/")
    return ""


def _ingest_endpoint(base: str) -> str:
    base = base.rstrip("/")
    if base.endswith("/api/public/ingest"):
        return base
    return f"{base}/api/public/ingest"


def _catalog_endpoint(base: str) -> str:
    base = base.rstrip("/")
    if base.endswith("/api/public/catalog"):
        return base
    if base.endswith("/api/public/ingest"):
        base = base[: -len("/api/public/ingest")]
    return f"{base}/api/public/catalog"


def resolve_catalog_urls(explicit: str | None = None, root: Path | None = None) -> list[str]:
    return [_catalog_endpoint(u) for u in resolve_ingest_urls(explicit, root)]


def build_payload_from_run_dir(
    run_dir: Path,
    *,
    ok_only: bool = True,
) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.json"
    jsonl_path = run_dir / "responses.jsonl"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest: {manifest_path}")
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Missing responses: {jsonl_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = load_jsonl(jsonl_path)
    records = select_records_for_ingest(rows, manifest=manifest, ok_only=ok_only)
    canonical_run_id = ingest_run_id(manifest)
    for row in records:
        # Lovable joins on run.run_id; jsonl uses bare run_id without phase prefix.
        row["run_id"] = canonical_run_id
    if not records:
        raise ValueError("No records to ingest (check jsonl and filters)")
    if len(records) > 10_000:
        raise ValueError(f"Too many records ({len(records)}); max 10,000 per POST")

    return {"run": build_run_meta(manifest, records), "records": records}


def push_via_http(
    payload: dict[str, Any],
    *,
    ingest_url: str | list[str],
    secret: str,
    timeout_s: float,
) -> dict[str, Any]:
    urls = ingest_url if isinstance(ingest_url, list) else [ingest_url]
    headers = {"Content-Type": "application/json", "X-Antigone-Secret": secret}
    errors: list[str] = []
    with httpx.Client(timeout=timeout_s, follow_redirects=False) as client:
        for url in urls:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code in (301, 302, 303, 307, 308):
                errors.append(f"{url} → redirect {resp.status_code}")
                continue
            if resp.status_code == 401:
                raise RuntimeError("Ingest rejected (401): check ANTIGONE_INGEST_SECRET matches Lovable")
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "via": "http",
                    "ingest_url": url,
                    "ok": data.get("ok", True),
                    "run_id": data.get("run_id", payload["run"]["run_id"]),
                    "count": data.get("count", len(payload["records"])),
                }
            errors.append(f"{url} → HTTP {resp.status_code}")
    raise RuntimeError(
        "Ingest failed on all URLs. Publish in Lovable (top-right), then retry. "
        "Or use zip import / --via supabase. Tried:\n  " + "\n  ".join(errors)
    )


def push_via_supabase(
    payload: dict[str, Any],
    *,
    supabase_url: str | None = None,
    service_role: str | None = None,
    table: str | None = None,
    timeout_s: float = 120.0,
) -> dict[str, Any]:
    base = (supabase_url or os.environ.get("SUPABASE_URL") or DEFAULT_SUPABASE_URL).rstrip("/")
    key = service_role or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not key:
        raise RuntimeError(
            "Set SUPABASE_SERVICE_ROLE_KEY in .env "
            "(Lovable → Cloud → API → service_role; never commit)"
        )
    table_name = table or os.environ.get("SUPABASE_IMPORTS_TABLE") or DEFAULT_IMPORTS_TABLE
    row = {
        "run_id": payload["run"]["run_id"],
        "run": payload["run"],
        "records": payload["records"],
    }
    url = f"{base}/rest/v1/{table_name}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    with httpx.Client(timeout=timeout_s) as client:
        resp = client.post(url, headers=headers, json=row)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Supabase ingest failed HTTP {resp.status_code}: {resp.text[:500]}")
    return {
        "via": "supabase",
        "ok": True,
        "run_id": payload["run"]["run_id"],
        "count": len(payload["records"]),
    }


def push_catalog_via_http(
    catalog: dict[str, Any],
    *,
    urls: list[str],
    secret: str,
    timeout_s: float = 60.0,
) -> dict[str, Any]:
    """POST stimulus catalog to /api/public/catalog (Lovable must implement endpoint)."""
    headers = {"Content-Type": "application/json", "X-Antigone-Secret": secret}
    errors: list[str] = []
    with httpx.Client(timeout=timeout_s, follow_redirects=False) as client:
        for url in urls:
            resp = client.post(url, headers=headers, json=catalog)
            if resp.status_code in (301, 302, 303, 307, 308):
                errors.append(f"{url} -> redirect {resp.status_code}")
                continue
            if resp.status_code == 401:
                raise RuntimeError("Catalog rejected (401): check ANTIGONE_INGEST_SECRET matches Lovable")
            if resp.status_code == 404:
                errors.append(f"{url} -> 404 (Lovable has not implemented /api/public/catalog yet)")
                continue
            if resp.status_code == 200:
                data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                return {
                    "via": "http",
                    "ok": True,
                    "catalog_url": url,
                    "cells": len(catalog.get("cells") or []),
                    "response": data,
                }
            errors.append(f"{url} -> HTTP {resp.status_code}: {resp.text[:200]}")
    raise RuntimeError(
        "Catalog push failed on all URLs. Implement POST /api/public/catalog in Lovable, "
        "or upload share/stimuli_reference.json manually. Tried:\n  " + "\n  ".join(errors)
    )


def push_catalog(
    catalog_path: Path,
    *,
    catalog_url: str | None = None,
    secret: str | None = None,
    timeout_s: float = 60.0,
) -> dict[str, Any]:
    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog not found: {catalog_path}")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    secret = secret or os.environ.get("ANTIGONE_INGEST_SECRET")
    if not secret:
        raise RuntimeError("Set ANTIGONE_INGEST_SECRET in .env")
    urls = resolve_catalog_urls(catalog_url)
    return push_catalog_via_http(catalog, urls=urls, secret=secret, timeout_s=timeout_s)


def _analysis_endpoint(base: str) -> str:
    base = base.rstrip("/")
    if base.endswith("/api/public/analysis"):
        return base
    if base.endswith("/api/public/ingest"):
        base = base[: -len("/api/public/ingest")]
    if base.endswith("/api/public/catalog"):
        base = base[: -len("/api/public/catalog")]
    return f"{base}/api/public/analysis"


def resolve_analysis_urls(explicit: str | None = None, root: Path | None = None) -> list[str]:
    return [_analysis_endpoint(u) for u in resolve_ingest_urls(explicit, root)]


def push_analysis(
    analysis_path: Path,
    *,
    analysis_url: str | None = None,
    secret: str | None = None,
    timeout_s: float = 60.0,
) -> dict[str, Any]:
    """POST analysis chart data to /api/public/analysis (Lovable must implement)."""
    if not analysis_path.exists():
        raise FileNotFoundError(f"Analysis not found: {analysis_path}")
    payload = json.loads(analysis_path.read_text(encoding="utf-8"))
    secret = secret or os.environ.get("ANTIGONE_INGEST_SECRET")
    if not secret:
        raise RuntimeError("Set ANTIGONE_INGEST_SECRET in .env")
    urls = resolve_analysis_urls(analysis_url)
    headers = {"Content-Type": "application/json", "X-Antigone-Secret": secret}
    errors: list[str] = []
    with httpx.Client(timeout=timeout_s, follow_redirects=False) as client:
        for url in urls:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code in (301, 302, 303, 307, 308):
                errors.append(f"{url} -> redirect {resp.status_code}")
                continue
            if resp.status_code == 401:
                raise RuntimeError("Analysis rejected (401): check ANTIGONE_INGEST_SECRET")
            if resp.status_code == 404:
                errors.append(f"{url} -> 404 (Lovable has not implemented /api/public/analysis yet)")
                continue
            if resp.status_code == 200:
                data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                return {"via": "http", "ok": True, "analysis_url": url, "run_id": payload.get("run_id"), "response": data}
            errors.append(f"{url} -> HTTP {resp.status_code}: {resp.text[:200]}")
    raise RuntimeError(
        "Analysis push failed on all URLs. Implement POST /api/public/analysis in Lovable, "
        "or upload output/phase1_v2_cross/analysis_chart_data.json manually. Tried:\n  " + "\n  ".join(errors)
    )


def save_ingest_payload(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def push_run(
    run_dir: Path,
    *,
    via: ViaMode = "auto",
    ingest_url: str | None = None,
    secret: str | None = None,
    ok_only: bool = True,
    timeout_s: float = 120.0,
    dry_run: bool = False,
    save_payload: Path | None = None,
) -> dict[str, Any]:
    payload = build_payload_from_run_dir(run_dir, ok_only=ok_only)
    secret = secret or os.environ.get("ANTIGONE_INGEST_SECRET")

    if save_payload:
        save_ingest_payload(payload, save_payload)

    if dry_run:
        url = resolve_ingest_url(ingest_url) or "(not set)"
        return {
            "dry_run": True,
            "via": via,
            "url": url,
            "run_id": payload["run"]["run_id"],
            "count": len(payload["records"]),
        }

    if via in ("auto", "http"):
        if not secret:
            raise RuntimeError("Set ANTIGONE_INGEST_SECRET in .env")
        urls = resolve_ingest_urls(ingest_url)
        try:
            return push_via_http(payload, ingest_url=urls, secret=secret, timeout_s=timeout_s)
        except RuntimeError:
            if via == "http":
                raise

    if via in ("auto", "supabase"):
        return push_via_supabase(payload, timeout_s=timeout_s)

    raise RuntimeError(f"Unknown via mode: {via}")


def resolve_run_dir(logs_root: Path, phase: int, run_id: str) -> Path:
    run_dir = logs_root / f"phase{phase}_{run_id}"
    if not run_dir.is_dir():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    return run_dir
