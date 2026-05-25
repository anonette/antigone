import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = [
    json.loads(line)
    for line in (ROOT / "logs/phase1_20260525T081321Z_8b488b4a/responses.jsonl").open(encoding="utf-8")
    if line.strip()
]
out = ROOT / "output" / "coding_queue"
out.mkdir(parents=True, exist_ok=True)
for r in rows:
    (out / f"{r['record_id']}.txt").write_text(
        f"record_id: {r['record_id']}\n"
        f"cell: {r['cell_key']}\n"
        f"model: {r['model_requested']}\n"
        f"replicate: {r['replicate']}\n\n"
        f"PROMPT:\n{r.get('prompt_text', '')}\n\n"
        f"RESPONSE:\n{r.get('response_text', '')}\n",
        encoding="utf-8",
    )
print(len(list(out.glob("*.txt"))))
