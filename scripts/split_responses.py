"""Split responses into per-language preview files for coding."""

from __future__ import annotations

import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)

rows = [
    json.loads(line)
    for line in (run_dir / "responses.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
rows.sort(key=lambda r: (r["language"], r["model_requested"], r["replicate"]))

by_lang: dict[str, list[str]] = {"en": [], "cs": [], "ja": []}
for r in rows:
    header = f"\n=== {r['record_id']} | {r['language']} | {r['stimulus_id']} | {r['model_requested']} | r{r['replicate']} ==="
    by_lang[r["language"]].append(header)
    by_lang[r["language"]].append(r["response_text"].replace("\r", ""))

for lang, lines in by_lang.items():
    path = out_dir / f"_phase1_v2_{lang}.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path} ({len([l for l in lines if l.startswith('===')])} rows)")
