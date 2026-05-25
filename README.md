# Antigone — stateless burial-dilemma LLM study

**Research question and operationalization:** see [RESEARCH.md](RESEARCH.md).  
**Stimulus catalog (Phase 1 & 2, EN/CS):** [STIMULI_REFERENCE.md](STIMULI_REFERENCE.md) · Lovable seed: [share/stimuli_reference.json](share/stimuli_reference.json)

Cross-language moral-dilemma simulation: **log first**, **analyze later**. Each API call is independent (no chat history, no memory, no provider fallbacks).

## Setup

```bash
cd c:\dev\antigone
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env:
#   OPENAI_API_KEY      — for openai/* models (direct api.openai.com)
#   OPENROUTER_API_KEY  — for all other models
```

## Phase 1 — open language baseline (run first)

```bash
python run.py --phase 1 --replicates 3
```

3 stimuli × N models × 3 replicates. Each run creates `logs/phase1_<run_id>/` with manifest, jsonl, flat CSV, and coding sheet (see `logs/README.md`).

## Phase 2 — framed variants (after Phase 1)

```bash
python run.py --phase 2 --replicates 3
```

## Stateless guarantees

| Property | Implementation |
|----------|----------------|
| No memory | One HTTP request per row; no prior messages sent |
| Prompt only | Scenario + two questions; no meta-instructions (no “answer in X”, refusal bans, action menus) |
| No roles (OpenRouter) | OpenRouter: `prompt` field only (not `messages`) |
| OpenAI direct | `openai/*` models → `api.openai.com` with **OPENAI_API_KEY**; single `user` message only |
| No provider fallback | OpenRouter: `"provider": {"allow_fallbacks": false}`; no OpenAI↔OpenRouter fallback |
| No model substitution | Requested model ID is fixed; errors are logged, not rerouted |
| Reproducibility | `temperature: 0` + deterministic `seed` per (stimulus, model, replicate) |
| Log before analysis | `run.py` never codes or plots; `analyze.py` reads logs only |

## Model selection

Edit `config/models.yaml`. Groups:

- `current_multilingual` — recent strong multilingual models
- `thinking` — reasoning models (stores `reasoning_text` when API returns it)
- `legacy` — older models for comparison

Run a subset:

```bash
python run.py --phase 1 --group current_multilingual --replicates 3
python run.py --phase 1 --group thinking --replicates 1
python run.py --phase 1 --models openai/gpt-4o anthropic/claude-3.5-sonnet
```

Resume an interrupted run (same log file, skip successful rows):

```bash
python run.py --phase 1 --run-id 20250525T120000Z_abc12345 --resume
```

## Logging (research-ready)

Each run writes **`logs/phase{N}_{run_id}/`**:

| File | Purpose |
|------|---------|
| `manifest.json` | Design matrix, config, stats, join hints |
| `responses.jsonl` | Canonical one-row-per-response |
| `responses_flat.csv` | Spreadsheet / R / pandas (no prompt body) |
| `coding_sheet.csv` | Responses + empty `code_var_*` for manual coding |
| `prompts_audit.csv` | Full prompts keyed by `record_id` |

Key fields: `record_id`, `cell_key`, `baseline_stimulus_id` (Phase 2 → P1 baseline), all IV columns, token counts, `has_reasoning`.

## Analysis (after logs exist)

```bash
python analyze.py
python analyze.py --phase 1 --run-id 20250525T120000Z_abc12345
```

Outputs under `output/`:

- `analysis_master.csv` — all successful rows, viz-ready
- `aggregate_by_cell.csv` — pre-aggregated means for charts
- `runs_index.csv` — all runs under `logs/`
- Heatmaps (model × stimulus), phase-1 language plots
- `heuristic_*` — exploratory only; use `coding_sheet.csv` for real VAR-A–G

## Translations (Czech & Japanese)

English source text lives in **`translations/master.yaml`**. Czech and Japanese are parallel prompts (not word-for-word calques where framing differs).

```bash
# Side-by-side CSV for native reviewers
python -m antigone.translations export

# Push master -> runnable stimuli (after edits)
python -m antigone.translations sync

python -m antigone.translations validate
```

See `translations/README.md`. Phase 2 now includes **C4, C5** (Czech) and finalized **J2–J9** (Japanese, mark `reviewed` in master when signed off).

## Sharing logs and charts with collaborators

Generate data locally first (`run.py` → `logs/`, `analyze.py` → `output/`), then zip and import into **Antigone Lab** (Lovable). Manual coding: **`recode.py`** and **`.cursor/skills/antigone-coding/`** (see `AGENTS.md`). The web app does not run collection automatically. See **[SHARING.md](SHARING.md)**. Lovable prompts: **[LOVABLE_PROMPT.md](LOVABLE_PROMPT.md)** + **[LOVABLE_DATA.md](LOVABLE_DATA.md)**.

## Design docs

- `DESIGN.md` — phases, variables
- `stimuli_phase1.yaml` / `stimuli_phase2.yaml`
- `translations/master.yaml` — EN / CS / JA source
- `codebook.md` — outcome coding
