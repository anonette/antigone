"""Compact per-row dump for manual coding (record_id, lang, model, stim, replicate, preview)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("logs/phase1_20260525T135121Z_eab51040")
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output/_phase1_v2_preview.txt")
jsonl = run_dir / "responses.jsonl"

rows = [json.loads(line) for line in jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
rows.sort(key=lambda r: (r["language"], r["model_requested"], r["replicate"]))

lines: list[str] = []
for r in rows:
    lines.append(
        f"\n=== {r['record_id']} | {r['language']} | {r['stimulus_id']} | {r['model_requested']} | r{r['replicate']} ==="
    )
    lines.append(r["response_text"].replace("\r", ""))

out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {out_path} ({len(rows)} rows)")
