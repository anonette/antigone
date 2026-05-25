---
name: antigone-coding
description: >-
  Manual codebook coding and recode workflow for Antigone LLM study. Use when
  filling code_var_* columns, merging Lovable exports, validating codes against
  codebook.md, canonicalizing run logs, or analyzing coded Phase 1/2 results.
---

# Antigone manual coding agent

You help the researcher **code model responses** and **re-run analysis on coded data**, not collect new LLM runs.

## Read first

| Doc | Purpose |
|-----|---------|
| `codebook.md` | VAR-A–G, VAR-R definitions |
| `codebook_cs_ja.md` | Czech & Japanese coding rules |
| `CODING_CHEATSHEET.md` | One-page coder reference |

## Canonical data (one row per cell)

Runs may contain retry duplicates. Before coding:

```bash
python recode.py canonicalize --run-dir logs/phase1_20260525T081321Z_8b488b4a
```

This keeps **54** ok rows (scaled Phase 1), archives the full jsonl, rebuilds `coding_sheet.csv`.

## Coding workflow

1. **Code** in Lovable or edit `logs/phaseN_{run_id}/coding_sheet.csv`.
2. Required Phase 1: `code_var_a`, `code_var_b`; recommended: `code_var_c`, `code_var_d`; JA: `code_var_r`.
3. **Export** coded CSV from Lovable (`record_id` + code columns).
4. **Merge** into logs:

```bash
python recode.py merge --run-dir logs/phase1_20260525T081321Z_8b488b4a --from path/to/coded_export.csv
```

5. **Validate**:

```bash
python recode.py validate --run-dir logs/phase1_20260525T081321Z_8b488b4a
```

6. **Analyze** (heuristics + coded summary):

```bash
python recode.py analyze --run-dir logs/phase1_20260525T081321Z_8b488b4a
```

## Coding rules (enforce)

- Code **reply text**, not stimulus metadata (IV columns are already set).
- **Primary VAR-A** = dominant endorsed action; CS numbered pipelines → code the **conclusion**, not step 1 alone.
- **VAR-B `distributed`** only if the model explicitly refuses to rank blame.
- **VAR-R** on every Japanese row (Phase 1 and 2).
- Do not use English keywords on Czech/Japanese rows.

## When assisting coding

- Open `prompts_audit.csv` + `response_text` for the same `record_id`.
- For Phase 2, compare to `baseline_stimulus_id` (same model + replicate on P1).
- Suggest codes with **codebook enum labels only**.
- After batch coding, always run `merge` + `validate`.

## Outputs

- `output/coding_validation_{run}.csv` — per-row issues
- `output/coded_summary_{run}.csv` — counts by language × VAR-A × VAR-D
- `output/analysis_master.csv` — after `recode.py analyze`

## Do not

- Run `run.py` unless user asks for new collection
- Treat `heuristic_action` as manual VAR-A
- Commit `.env` or API keys
