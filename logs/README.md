# Log layout (research)

Each run creates a **directory**:

```
logs/phase1_20250525T120000Z_a1b2c3d4/
  manifest.json          # run config, design matrix, stats, analysis hints
  responses.jsonl        # one JSON object per line (canonical)
  responses_flat.csv     # flat columns for Excel/R (no full prompt)
  coding_sheet.csv       # responses + empty code_var_* columns
  prompts_audit.csv      # record_id, cell_key, full prompt text
  stimuli_snapshot.yaml  # exact stimuli used
```

A **legacy** flat file is also written for older tooling:

```
logs/phase1_20250525T120000Z_a1b2c3d4.jsonl
```

## Primary keys

| Field | Use |
|-------|-----|
| `record_id` | Unique row; join coding to responses |
| `cell_key` | `{stimulus_id}\|{model}\|{replicate}` |
| `baseline_stimulus_id` | Phase 2 → compare to P1-CS / P1-JA / P1-EN |

## Coding workflow

1. Canonicalize (drops retry duplicates): `python recode.py canonicalize --run-dir logs/phaseN_{run_id}/`
2. Code in `coding_sheet.csv` or Lovable; merge export: `python recode.py merge --from coded.csv`
3. Validate: `python recode.py validate --run-dir ...`
4. Analyze: `python recode.py analyze --run-dir ...`

See `codebook.md`, `codebook_cs_ja.md`, and `.cursor/skills/antigone-coding/`.

## Analysis

```bash
python analyze.py
python analyze.py --phase 1 --run-id 20250525T120000Z_a1b2c3d4
```

Outputs under `output/`: `analysis_master.csv`, `aggregate_by_cell.csv`, heatmaps.

## Schema version

`schema_version: 1` on each jsonl row. See `antigone/research_log.py` for column list.
