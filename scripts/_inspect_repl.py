"""Quick: show first 150 chars of each Claude P1-CS replicate, both runs."""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

for run in ["phase1_20260525T081321Z_8b488b4a", "phase1_20260525T135121Z_eab51040"]:
    p = Path("logs") / run / "responses.jsonl"
    if not p.exists():
        continue
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    sel = [
        r
        for r in rows
        if r["language"] == "cs" and "claude" in r["model_requested"] and r.get("status") == "ok"
    ]
    sel.sort(key=lambda r: r["replicate"])
    print(f"\n=== {run} ===")
    for r in sel:
        print(f"r{r['replicate']}: {r['response_text'][:160].replace(chr(10), ' / ')}")
