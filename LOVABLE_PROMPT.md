# Lovable prompt — Antigone research interface

1. Copy everything below the line into Lovable as your **main project prompt**.  
2. Also paste **LOVABLE_DATA.md** (data import, sharing, no API) in the same chat or as a follow-up.

See **SHARING.md** for the researcher workflow (local run → zip → upload).

---

## Prompt (copy from here)

Build a web app called **Antigone Lab** — a research review tool for a multilingual burial-dilemma study: browse **prompt ↔ response ↔ manual codes**, compare **Phase 1 language baselines** vs **Phase 2 framed cells**, and export coded CSV. This is an academic coding and sharing workspace, not a chat interface and not a generic dashboard.

### Research context (for UI copy and structure)

The study presents the same burial-ban dilemma (terror attack → body withheld → relative: obey or secret bury) in **English, Czech, and Japanese**, with grammatical framing variants (Czech: agentive / deagentive / modal / affectedness / procedure; Japanese: viewpoint, aspect, evidential, register).

**UI copy (use these; avoid theatre/chat metaphors):**

- **Subtitle:** *Institutional grammars of responsibility*
- **Home intro (one sentence):** *Compare how English, Czech, and Japanese prompts shape model answers and coded responsibility (Phase 1 baselines; Phase 2 framing variants).*
- **Footer (optional):** *How does each language shape who acts, who is blamed, and what is recommended — before the model gives a clear answer?*
- **About:** *Antigone Lab is a coding and review tool for the Antigone corpus. It does not call LLMs. Import a run folder, code with the project codebook, export CSV for analysis.*

---

### Visual design

- **Tone:** Quiet academic tool (archive + lab notebook), not startup marketing.
- **Palette:** Off-white background `#F7F6F3`, ink text `#1A1A1A`, muted borders `#D8D4CC`.
- **Accents:** Czech cells `#4A6FA5`, Japanese `#C45C3E`, English `#3D6B4F` — used sparingly as left border chips on cards.
- **Typography:** Serif for headings (e.g. Source Serif 4 or Lora), sans for data tables (IBM Plex Sans or similar).
- **Layout:** Wide reading pane for responses; collapsible metadata sidebar; no clutter, no gradients, no emoji.

---

### Data model (implement exactly — user uploads files)

Support **file upload** on first use (no live API to OpenRouter in v1). Parse and store in browser or Supabase if available.

**1. Run** (from `manifest.json` or inferred from folder name `phase1_20250525T120000Z_abc12345`)

- `run_id`, `phase` (1|2), `started_at`, `completed_at`
- `stimuli[]`, `models[]`, `replicates`, `stats` (ok/error/skipped)

**2. Response** (from `responses.jsonl` or `responses_flat.csv` + merge `coding_sheet.csv`)

Primary key: `record_id`

Fields to index and filter:

- Identity: `run_id`, `cell_key`, `stimulus_id`, `baseline_stimulus_id`, `phase`, `framing`, `language` (en|cs|ja)
- Model: `model_requested`, `model_group`, `model_thinking`, `api_backend`, `replicate`, `seed`
- IV metadata: `EN-AG`, `CZ-AG`, `CZ-OB`, `CZ-AF`, `CZ-PR`, `JP-V`, `JP-A`, `JP-E`, `JP-H`, `JP-S`, `translation_note`
- Text: `prompt_text` (from `prompts_audit.csv` join), `response_text`, `reasoning_text` (optional)
- Metrics: `response_char_len`, `response_word_count`, `latency_ms`, `tokens_prompt`, `tokens_completion`, `has_reasoning`, `status`
- **Manual coding** (editable in UI): `code_var_a`, `code_var_b`, `code_var_c`, `code_var_d`, `code_var_e`, `code_var_f`, `code_var_g`, `code_var_r`, `coder_id`, `coded_at`, `notes`

**3. Codebook enums** (dropdown labels in coder UI)

- VAR-A: obey, secret_bury, legal_challenge, compromise, undecided
- VAR-B: relative, authorities, deceased, law_rule, enforcers, unrest_risk, society, distributed
- VAR-C: legal_obedience, human_dignity, family_duty, public_order, sacred_dead_duty, procedure_proportionality, consequentialist_harm, virtue_conscience
- VAR-D: individualized, institutional, deagentive, circumstantial, relational_affected
- VAR-E: terrorist_enemy, human, family_member, criminal_with_dignity, political_symbol
- VAR-F: decisive, manageable, speculative, state_produced, secondary
- VAR-G: multi-select — appeal, supervised_burial, judicial_review, etc.
- VAR-R (ja only): mirrors_register, mirrors_evidential, mirrors_aspect, flattens_neutral

**4. Derived flags** (compute on load)

- `shift_from_baseline`: true if Phase 2 and (code_var_a or code_var_b) differs from same model+replicate at `baseline_stimulus_id`
- `agency_match`: prompt deagentive (CZ-AG=deagentive) AND code_var_d=deagentive → “mirroring”; deagentive prompt + individualized VAR-D → “restoration”
- `coding_complete`: all required code_var_a, code_var_b, code_var_d filled

---

### Pages and features

#### 1. Home / Runs

- List imported runs with phase badge, date, n responses, % coded.
- Button: **Import run** — upload zip or multiple files: `responses.jsonl`, `coding_sheet.csv`, `prompts_audit.csv`, `manifest.json` (optional).
- Quick stats row: total responses, languages, models.

#### 2. Browse (main workhorse)

**Filter bar (sticky):** phase, language, stimulus_id, model_group, model, coding status (uncoded/partial/complete), VAR-A, VAR-B, VAR-D, text search in response.

**Results:** card list or dense table toggle.

Each card shows:

- Stimulus chip (e.g. C2 · deagentive) + language color bar
- Model + replicate
- First 2 lines of response (expandable)
- Coding pills if set (VAR-A, VAR-B, VAR-D)
- Badge: “≠ baseline” if shift_from_baseline

Click → **Detail drawer or full page**

#### 3. Response detail (interpretation view)

Three columns on desktop (stack on mobile):

| Column | Content |
|--------|---------|
| **Prompt** | Full `prompt_text`; highlight IV-relevant phrases if metadata present (e.g. “se nevydalo” for C2) |
| **Response** | Full `response_text`; separate tab for `reasoning_text` if present; char count |
| **Code** | Form with codebook dropdowns + free `notes`; save per record; show `coder_id` + timestamp |

Below: **Compare to baseline** panel — if Phase 2, load sibling response(s) with same `model_requested`, `replicate`, `baseline_stimulus_id` side-by-side (prompt + response + codes). Label: “P1-CS baseline vs C2 deagentive”.

Navigation: prev/next within current filter (keyboard ← →).

#### 4. Code (batch coding mode)

- Queue of uncoded rows; one screen = one response; same coding form; progress bar “47 / 312 coded”.
- Optional: hide model name until after coding (blind coding toggle) — store preference in localStorage.

#### 5. Compare (analysis)

Pre-built comparison views (charts with Recharts or similar):

- **Phase 1:** stacked bar VAR-A or VAR-B by language (aggregated across models or faceted by model_group).
- **Phase 2 Czech:** C1 vs C2 vs C3 vs C4 vs C5 — VAR-D distribution (mirroring vs restoration).
- **Phase 2 Japanese:** J1 vs J3 vs J4 vs J5 — VAR-R flattening rate.
- **Heatmap:** model (rows) × stimulus_id (cols), cell color = modal VAR-B or mean response length.
- **Baseline shift table:** % of rows where code_var_a or code_var_b changed vs baseline_stimulus_id.

All charts respect global filters.

#### 6. Stimuli reference

Read-only reference page. **Seed data:** load `share/stimuli_reference.json` from the repo (or equivalent embedded copy) — 18 cells with `label`, `description_en`, `description_cs`, `baseline_stimulus_id`, `framing_axes`, `prompt_text`.

**Page header (verbatim):**

- Title: **Stimulus reference**
- Subtitle: *Institutional grammars of responsibility*
- Intro (EN): *The burial-ban dilemma in language baselines and framing cells. Imported runs override seed text where available.*
- Toggle or tabs: **EN** / **CS** for section summaries and per-cell `description_*`

**Layout:**

1. **Phase 1** section — intro from `phase1_summary_en` / `phase1_summary_cs`; cards for P1-EN, P1-CS, P1-JA.
2. **Phase 2** section — intro from `phase2_summary_*`; subsections **Czech (C1–C5)**, **Japanese (J1–J9)**, **English (E1)**.
3. Each card (collapsible): `stimulus_id`, `label`, language chip, `framing_axes`, `baseline_stimulus_id` / “Compare to: P1-CS”, descriptions, full `prompt_text`.
4. If user has **imported a run**: for any `stimulus_id` present in `prompts_audit.csv`, show banner *“Showing text from imported run”* and prefer that prompt over seed `prompt_text`.
5. Empty Phase 2 collection: still show seed cards; badge *“Not collected yet”* if no rows in DB for that stimulus.

Do not hide Phase 2 cells just because only Phase 1 is imported — researchers need the catalog before collection.

#### 7. Share / Export

- **Export coded dataset** → CSV download (all fields + codes).
- **Export share bundle** → JSON zip: coded responses + manifest + codebook legend.
- **Share link** (if Supabase): read-only view for collaborators — Browse + Detail + Compare only, no edit. Optional password.
- **Print-friendly** response detail (PDF via browser print CSS).

#### 8. About / Methods

Short static page using the **UI copy** bullets above, plus coding rules, what VAR-D “agency performance” means, and a link placeholder for paper/repo. Do not use “staging theatre”, “chat partner”, or “deixis machine” in the UI.

---

### Technical requirements

- React + TypeScript + Tailwind.
- Robust CSV and JSONL parsing (Papa Parse or similar); handle UTF-8 Czech and Japanese.
- Persist coding edits: Supabase table `responses` keyed by `record_id` OR download updated CSV if no backend.
- All state recoverable after refresh if using Supabase; else warn “export before leaving”.
- Empty states with clear import instructions listing expected filenames.
- No authentication required for v1 unless Share link needs it.
- Mobile: readable response text; coding form usable.

---

### Copy strings (use verbatim where noted)

- App title: **Antigone Lab**
- Subtitle: *Institutional grammars of responsibility*
- Footer: *How does each language shape who acts, who is blamed, and what is recommended — before the model gives a clear answer?*
- Import CTA: **Import a run folder**
- Empty browse: *No runs yet. Import responses.jsonl and coding_sheet.csv from logs/phaseN_runid/*
- Coding save toast: *Codes saved for {record_id}*
- Baseline panel title: *Same model · same replicate · language baseline*

---

### Do not build

- OpenRouter / LLM API calls
- Running Python scripts
- Generic “AI chat” interface
- Moral “correct answer” scoring or leaderboard
- Heavy social features (comments OK on a record as `notes` only)

---

### Success criteria

A researcher can: (1) import one run in under a minute, (2) read prompt and response together for C2 vs P1-CS, (3) code VAR-A/B/D with dropdowns, (4) see whether Czech deagentive prompts yield deagentive or individualized VAR-D in charts, (5) export coded CSV for R or paper, (6) send a collaborator a read-only link to review interpretations.

Build MVP in this order: Import → Browse → Detail + Coding → Compare charts → Export.

---

## Optional follow-up prompts for Lovable (after MVP)

1. *Add Supabase auth: researcher login, shared read-only project per run_id.*

2. *Add blind coding mode and inter-coder agreement view when two coder_id values exist for same record_id.*

3. *Add side-by-side trilingual view: same facts, P1-EN | P1-CS | P1-JA prompts only, no responses.*

4. *Embed static heatmap images from output/ folder as fallback when charts have few rows.*
