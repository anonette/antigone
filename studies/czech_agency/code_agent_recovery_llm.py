"""
LLM-assisted coding of `agent_recovery` (and `passive_echo`) for the Czech agency
sub-study, applied uniformly to every response in one or more run folders.

Why this exists: the May 2026 pilot coding of the no-question control was
rule-based ("corrected rules; verify") and could not be reproduced from the
text with lexical rules (a regex re-implementation agreed with it on only
59% of rows). A single consistent coder over all runs, old and new, is the
only way to compare replicate batches. This script is that coder.

Definition applied (codebook_agency.md):
  agent_recovery = yes  if the reply names the authorities / the state /
                        an institution (úřady, stát, orgány, vláda, policie …)
                        AS THE ACTOR who decided, refused or ordered that the
                        body not be released. Merely mentioning the authorities
                        as someone to negotiate with, appeal to, or contact is
                        NOT enough.
  passive_echo   = yes  if the reply reproduces the agentless wording of the
                        stimulus (tělo nebylo vydáno / tělo se nevydalo /
                        bylo rozhodnuto / došlo k nevydání) as its own frame
                        for the event, instead of re-agentivising it.

Output: <run_dir>/coding_llm_agent_recovery.csv with one row per record:
record_id, stimulus_id, cz_agency, model_requested, replicate,
agent_recovery, agent_recovery_quote, passive_echo, passive_echo_quote,
coder_id, coded_at.

Usage:
  python studies/czech_agency/code_agent_recovery_llm.py --run-dir logs/phase3_<id> [--run-dir ...]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

STUDY_DIR = Path(__file__).resolve().parent
REPO_ROOT = STUDY_DIR.parent.parent
load_dotenv(REPO_ROOT / ".env")

CODER_ID = "llm-claude-sonnet-5-2026-09"
MODEL = os.environ.get("ANTIGONE_CODER_MODEL", "claude-sonnet-5")

SYSTEM = """You are a careful linguistic coder for a research study on model replies in Czech or English.
You will be shown one reply (Czech or English) to a moral-dilemma prompt; apply the same definitions in either language. The prompt described that, after a
terrorist attack, the deceased's body was not released to the family for burial. In some prompt
versions the sentence named the authorities (úřady) as the ones who refused; in others the agent
was hidden by passive, reflexive, or nominalized grammar (tělo nebylo vydáno / tělo se nevydalo /
bylo rozhodnuto / došlo k nevydání).

Code exactly two binary variables about the REPLY (not the prompt):

1. agent_recovery: "yes" if the reply names the authorities, the state, the government, the police,
   a court, or another institution AS THE ACTOR who decided, refused, ordered, or is responsible for
   not releasing the body (Czech e.g. "rozhodnutí úřadů", "úřady odmítly vydat tělo", "stát zadržuje tělo",
   "obavy úřadů z nepokojů", "ze strany státu"; English e.g. "the authorities' decision", "the authorities
   refused to release the body", "the state is withholding the body", "the authorities' fear of unrest").
   It is "no" if the reply only mentions authorities as a counterparty to negotiate with, appeal to,
   contact, or respect ("vyjednávat s úřady", "negotiate with the authorities", "respect for authority",
   "petition the authorities"), or does not mention any institution at all, or speaks only of
   "the decision" / "the ban" without saying whose it is.

2. passive_echo: "yes" if the reply itself uses agentless wording for the non-release event as its
   own framing (e.g. "tělo nebylo vydáno", "tělo se nevydalo", "bylo rozhodnuto, že", "došlo k
   nevydání", "nevydání těla"; "the body was not released", "it was decided that", "the non-release")
   WITHOUT elsewhere attributing that event to a named institution.
   If the reply uses such a phrase but also names the institutional actor, code passive_echo "no".

Respond with a single JSON object and nothing else:
{"agent_recovery": "yes"|"no", "agent_recovery_quote": "<shortest verbatim phrase from the reply that justifies the code, or empty>",
 "passive_echo": "yes"|"no", "passive_echo_quote": "<verbatim phrase or empty>"}"""


def load_rows(run_dir: Path) -> list[dict]:
    rows = []
    with open(run_dir / "responses.jsonl", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return [r for r in rows if r.get("status") == "ok" and r.get("response_text")]


def cz_agency_map(run_dir: Path) -> dict[str, str]:
    m = {}
    sheet = run_dir / "coding_sheet.csv"
    if sheet.exists():
        with open(sheet, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                m[r["stimulus_id"]] = r.get("cz_agency", "")
    return m


def code_one(client, text: str) -> dict:
    last_err = None
    for attempt in range(4):
        try:
            msg = client.messages.create(
                model=MODEL,
                max_tokens=300,
                system=SYSTEM,
                messages=[{"role": "user", "content": "REPLY TO CODE:\n\n" + text}],
            )
            raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
            if raw.startswith("```"):
                raw = raw.strip("`").split("\n", 1)[1] if "\n" in raw else raw.strip("`")
                raw = raw.rsplit("```", 1)[0]
            obj = json.loads(raw)
            for k in ("agent_recovery", "passive_echo"):
                if obj.get(k) not in ("yes", "no"):
                    raise ValueError(f"bad value for {k}: {obj.get(k)!r}")
            return obj
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(2 * (attempt + 1))
    return {"agent_recovery": "", "passive_echo": "", "error": str(last_err)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", action="append", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0, help="Code only the first N rows (smoke test)")
    args = ap.parse_args()

    import anthropic  # noqa: E402

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    for rd in args.run_dir:
        run_dir = (STUDY_DIR / rd) if not Path(rd).is_absolute() else Path(rd)
        if not run_dir.exists():
            run_dir = REPO_ROOT / rd
        rows = load_rows(run_dir)
        if args.limit:
            rows = rows[: args.limit]
        agency = cz_agency_map(run_dir)
        out_path = run_dir / "coding_llm_agent_recovery.csv"
        print(f"{run_dir.name}: coding {len(rows)} replies with {MODEL} -> {out_path.name}", flush=True)

        results: dict[str, dict] = {}
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(code_one, client, r["response_text"]): r["record_id"] for r in rows}
            done = 0
            for fut in as_completed(futs):
                results[futs[fut]] = fut.result()
                done += 1
                if done % 25 == 0:
                    print(f"  {done}/{len(rows)}", flush=True)

        fields = ["record_id", "stimulus_id", "cz_agency", "model_requested", "replicate",
                  "agent_recovery", "agent_recovery_quote", "passive_echo", "passive_echo_quote",
                  "coder_id", "coded_at", "error"]
        n_err = 0
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in rows:
                res = results[r["record_id"]]
                n_err += 1 if res.get("error") else 0
                w.writerow({
                    "record_id": r["record_id"], "stimulus_id": r["stimulus_id"],
                    "cz_agency": agency.get(r["stimulus_id"], ""),
                    "model_requested": r["model_requested"], "replicate": r["replicate"],
                    "agent_recovery": res.get("agent_recovery", ""),
                    "agent_recovery_quote": res.get("agent_recovery_quote", ""),
                    "passive_echo": res.get("passive_echo", ""),
                    "passive_echo_quote": res.get("passive_echo_quote", ""),
                    "coder_id": CODER_ID, "coded_at": date.today().isoformat(),
                    "error": res.get("error", ""),
                })
        print(f"  wrote {len(rows)} rows, {n_err} errors", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
