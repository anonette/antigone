# Lovable — data integration (paste with LOVABLE_PROMPT.md)

Use **LOVABLE_PROMPT.md** for UI, pages, and design. Paste **this file** for how data arrives and how sharing works.

---

## Data source (important)

This app does **not** call LLMs or run Python. All data is **uploaded by the researcher** from a local pipeline (`run.py` → `logs/`, `analyze.py` → `output/`).

There is **no** file watcher on the researcher’s machine. Optional **HTTP ingest** from `push_to_lovable.py` after `run.py` finishes.

---

## Push from Python (optional)

After a run completes locally, POST to the Lovable backend (realtime in app — no zip needed).

**`.env` (never commit):**

```env
ANTIGONE_INGEST_SECRET=<same value as Lovable backend secret>
LOVABLE_INGEST_URL=https://…/api/public/ingest
```

**Command:**

```bash
python push_to_lovable.py --phase 1 --run-id 20260525T081321Z_8b488b4a
```

Or: `python run.py --phase 1 … --push-lovable` at the end of collection.

**URL:** Prefer the stable project URL (works before/after Publish):

`https://project--<project-id>.lovable.app/api/public/ingest`

Also valid after Publish: `https://<project-id>.lovable.app/api/public/ingest`.  
Preview-only: `https://id-preview--<project-id>.lovable.app/api/public/ingest`.

**HTTP:**

- `POST` `LOVABLE_INGEST_URL`
- Header `X-Antigone-Secret: <ANTIGONE_INGEST_SECRET>`
- Body: `{ "run": { "run_id": "phase1_…", "phase", "started_at", …, "stats" }, "records": [ … ] }`
- `run.run_id` = `phase{N}_{run_id}` (upsert key; re-post replaces)
- **Every `records[].run_id` must equal `run.run_id`** (same string). If they differ, the UI shows 0 responses while `stats.ok` is correct.
- `run.started_at` / `run.completed_at` are ISO-8601 UTC strings (from `manifest.json` `*_utc` fields)
- `records` max 10,000; pipeline sends latest row per `cell_key`, ok + non-empty text only

Zip import below still works if you prefer not to push.

---

## Import flow

User clicks **Import run** and uploads either:

- a **zip** of one run folder, or  
- these files together:

| File | Required | Purpose |
|------|----------|---------|
| `responses.jsonl` | Yes | One JSON object per line — all model responses |
| `coding_sheet.csv` | Yes | Same rows + empty `code_var_*` columns to edit in the UI |
| `prompts_audit.csv` | Yes | Join on `record_id` for full `prompt_text` |
| `manifest.json` | Optional | Run metadata, stimulus list, stats |
| `charts/*.png` | Optional | Pre-made figures from `analyze.py` (static gallery page) |

**Run folder name pattern:** `phase1_20250525T120000Z_abc12345` or `phase2_…` — parse `phase` (1 or 2) from the folder name or `manifest.json`.

---

## Keys and joins

| Field | Use |
|-------|-----|
| `record_id` | Primary key (UUID) |
| `cell_key` | `{stimulus_id}\|{model_requested}\|{replicate}` |
| `baseline_stimulus_id` | Phase 2 baseline for comparison (C2→P1-CS, J4→P1-JA, E1→P1-EN) |

Merge `prompts_audit.csv` → responses on `record_id`.

**Phase 2 UI:** When `phase === 2`, show a **vs baseline** panel: same `model_requested`, same `replicate`, row where `stimulus_id === baseline_stimulus_id`.

---

## Languages

`language`: `en` | `cs` | `ja`

Accent colors (sparing): EN `#3D6B4F`, CS `#4A6FA5`, JA `#C45C3E`.

---

## Coding persistence

- Editable in UI: `code_var_a` … `code_var_g`, `code_var_r`, `coder_id`, `coded_at`, `notes`
- Store in **Supabase** keyed by `record_id`, and/or
- **Export coded CSV** for download
- Re-import: merge on `record_id`; newer codes overwrite

---

## Charts

1. **Interactive (in app):** Aggregate imported rows by `language`, `stimulus_id`, `model_group`, and coded `code_var_a` / `code_var_b` / `code_var_d` after user fills codes.
2. **Static (optional):** If zip contains `charts/*.png`, show a gallery page — do not require for MVP.

---

## Sharing access

| Method | Behavior |
|--------|----------|
| Zip file | Collaborator imports locally in their browser / your Supabase |
| Published Lovable URL | Team opens app |
| Read-only mode (optional) | Browse + charts, no coding edits |
| Editor mode | Full coding form |

---

## Technical

- Parse JSONL line-by-line; CSV with **UTF-8** (Czech + Japanese).
- Handle large `response_text` / `prompt_text` in scrollable panels.
- Empty `code_var_*` = uncoded.

---

## Do not build

- OpenRouter / OpenAI API
- Running or embedding `run.py` / `analyze.py`
- Auto-sync from disk
- Moral “correct answer” scoring

---

## Stimulus reference page (static seed)

Bundle or fetch **`share/stimuli_reference.json`** (regenerate: `python scripts/build_stimuli_reference.py`).  
Source of truth for labels/descriptions: **`stimuli_catalog.yaml`** · human doc: **`STIMULI_REFERENCE.md`**.

Page intro: *The burial-ban dilemma in language baselines and framing cells. Imported runs override seed text where available.*

### Optional: analysis push endpoint (`/api/public/analysis`)

To let `python push_analysis_to_lovable.py` (or `push_to_lovable.py --with-analysis`) refresh the analysis page data without manual upload, Lovable should expose:

- `POST <project>.lovable.app/api/public/analysis`
- Header `X-Antigone-Secret: <ANTIGONE_INGEST_SECRET>`
- Body = full JSON from `output/phase1_v2_cross/analysis_chart_data.json` (schema_version, run_id, by_language, by_model, by_model_language, modal_per_cell_var_a, response_length_median, replicate_stability_var_a)
- Behaviour: upsert single row in `analysis_payloads` table keyed by `run_id`; the Analysis page reads the latest row.
- Response: 200 `{ "ok": true, "run_id": "..." }`.

Pair with **static gallery**: if the imported zip includes `charts/*.png`, render them on a fallback "Static charts" tab.

### Optional: catalog push endpoint (`/api/public/catalog`)

To let `python push_catalog_to_lovable.py` (or `push_to_lovable.py --with-catalog`) refresh the catalog without manual upload, Lovable should expose:

- `POST <project>.lovable.app/api/public/catalog`
- Header `X-Antigone-Secret: <ANTIGONE_INGEST_SECRET>` (same secret as `/ingest`)
- Body = full `share/stimuli_reference.json` (schema_version, page, phase*_summary_*, cells[])
- Behaviour: upsert into Supabase table `stimuli_catalog` keyed by `stimulus_id`; replace `page` + `phase*_summary_*` rows or store in `catalog_meta`.
- Response: `{ "ok": true, "cells": N }`.

Until that endpoint exists, the script reports 404 and prints fallback instructions (drag `share/stimuli_reference.json` into the Lovable chat).

---

## MVP build order

1. Import + parse  
2. Browse + filters  
3. Detail (prompt \| response \| code)  
4. Export coded CSV  
5. Compare charts  
6. Optional: static PNG gallery, Supabase, read-only share link  

---

## Researcher workflow (for About page)

1. Run `python run.py --phase N` locally → `logs/phaseN_{run_id}/`  
2. Optional: `python analyze.py` → `output/*.png`  
3. Zip run folder (+ optional `charts/`) → **Import** in Antigone Lab  
4. Code → **Export** → paper / R  

See **SHARING.md** in the repo for zip commands.
