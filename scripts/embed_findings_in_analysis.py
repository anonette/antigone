"""Merge findings.json into analysis_chart_data.json so it pushes via /api/public/analysis."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CROSS = ROOT / "output" / "phase1_v2_cross"

analysis = json.loads((CROSS / "analysis_chart_data.json").read_text(encoding="utf-8"))
findings = json.loads((CROSS / "findings.json").read_text(encoding="utf-8"))

analysis["findings"] = findings

out = CROSS / "analysis_chart_data.json"
out.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {out} (now includes findings: {len(findings.get('findings', []))})")
