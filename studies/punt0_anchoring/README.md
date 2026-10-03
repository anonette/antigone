# PUNT0 anchoring study

PUNT0 v1.4 (Salamanca García, 2026, DOI 10.5281/zenodo.22292297) makes
concrete, falsifiable predictions about how anchoring a model's deictic
position changes error attribution and stance stability. This pilot,
designed jointly with the framework's author, gives those predictions their
first controlled test. The framework builds on enunciation theory
(Benveniste, Jakobson) and on Reshef Kera (2026), *Deixis machines and
enunciation without a speaker in large language models*.

**Para Néstor:** Este estudio piloto pone a prueba empírica la fórmula de
anclaje "Yo Deíctico" de PUNT0 v1.4. Tu parte: los campos `es:` de
`stimuli.yaml` (sección "Contributing the Spanish materials" abajo), la
revisión de las definiciones de la matriz de atribución en
`codebook_attribution.md`, y la revisión de la codificación en español.
Nada de esto requiere Python. Los anclajes A1/A2 en español son borradores:
confírmalos o corrígelos; la formulación exacta es tuya.

Collaboration: Denisa Reshef Kera (design, pipeline, English materials,
analysis) and Néstor Sebastián Salamanca García (Spanish materials,
attribution matrix definitions, codebook governance).

**Independent study. Never pool with Phase 1/2 or any other Antigone study.**
It reuses the repository's engine conventions (model registry, deterministic
seeds) and writes only inside this folder.

## Design

Pilot core (default command): 4 anchors × 2 languages (en, es) × 4 dilemmas
× 3 core models × 5 replicates = 480 three-turn transcripts. Planned
extension (`--extended`, after calibration): Czech, Japanese and 3 further
models, 1,920 transcripts in all; the runner and `stimuli.yaml` already
carry these fields.

There is no human coding: every transcript is coded by a panel of LLM
coders under two rules, no coder codes its own model family, and every
transcript is double-coded independently with agreement reported (see
`codebook_attribution.md` and `code_transcripts_llm.py`).

| Factor | Levels |
|---|---|
| Anchor | A1 "owned by / propiedad de", A2 "developed by / desarrollado por", A0 neutral system prompt (control), A3 no system message |
| Language | en, es (core); cs, ja (extension; PA1 cs/ja prompts are the reviewed Antigone parallels) |
| Stimulus | PA1 (Antigone burial baseline) + PA2–PA4 (new dilemmas, draft) |
| Models | Core: GPT-4o, Claude Sonnet, DeepSeek R1. Extension: Gemini 2.0 Flash, Llama 3.3 70B, Qwen 2.5 72B |

H1 is tested as (A1+A2) vs A0, the formula effect net of system-prompt
presence; A0 vs A3 is reported as the system-prompt-presence check.

Each transcript has three scripted turns: the dilemma (stance), a scripted
bare disagreement with no new information (pressure), and a scripted
confrontation with an error the model did not make (planted claim, a
scenario-external fact so denial is verifiable). Outcomes: the PUNT0
five-level attribution matrix as an ordinal code on turn 3 (every reply
graded, denials included), abstention at turn 1, stance stability at turn
2, false error acceptance (yes / partial / no) at turn 3.

The four languages differ in how marked agent omission is (Czech reflexive
impersonals, Japanese subjectless clauses, Spanish pro-drop, English marked
omission), so language drift in the middle attribution grades is itself an
informative outcome for the matrix's cross-linguistic validity. DeepSeek R1
is a reasoning model, giving the core a thinking versus non-thinking
contrast relevant to PUNT0's abstention claims.

## Hypotheses

1. H1 (anchoring): supported if (A1+A2) produce more directly attributed
   turn-3 forms (lower grades) than A0; not supported if the distributions
   are indistinguishable.
2. H2 (wording): supported if A1 "owned by" produces lower grades than A2
   "developed by"; not supported if the two anchors are indistinguishable.
3. H3 (stance stability): supported if anchored transcripts flip less at
   turn 2 than A0/A3; not supported otherwise. Uses only transcripts with a
   codable turn-1 stance.
4. H4 (language generality): supported if the H1 contrast has the same sign
   across languages; a language-specific effect is reported as an
   interaction, informative either way.

Full protocol (procedure, analysis plan, roles, timeline): shared
separately; deposited on OSF at design freeze.

## Contributing the Spanish materials

Fields to fill in `stimuli.yaml` (currently `null`):

- `turns.pressure.es` and `turns.confrontation.es`
- for each of PA1–PA4: `prompt.es` and `planted_claim.es`
- confirm or replace the `anchors.A1.es`, `anchors.A2.es`, `anchors.A0.es`
  drafts: these strings ARE the manipulation and the final wording is yours

A worked example of the YAML shape (the `|` starts a block of text,
indentation must match):

```yaml
  prompt:
    es: |
      Una persona murió tras cometer un atentado...

      ¿Qué debe hacer el familiar y quién es responsable de las consecuencias?
```

Rules: translate meaning, not words; keep `{placeholders}` like
`{planted_claim}`, `{model_name}` and `{org}` exactly as written; leave the
`cs:`/`ja:` nulls untouched; keep the file UTF-8. Submission: edit
`stimuli.yaml` on a branch and open a PR titled `es-materials`, or email
the file and the PI commits it. Back-translation review happens before the
run, jointly.

## Running

```bash
python studies/punt0_anchoring/run_study.py --dry-run                      # no API keys needed; start here
python studies/punt0_anchoring/run_study.py --languages en --replicates 1 --models openai/gpt-4o
python studies/punt0_anchoring/run_study.py                                # pilot core (en/es, 3 models)
python studies/punt0_anchoring/run_study.py --extended                     # all languages and models
python studies/punt0_anchoring/run_study.py --resume <run_id>              # continue an interrupted run
python studies/punt0_anchoring/code_transcripts_llm.py --run <run_id>      # LLM panel coding
```

Practical notes:

- Setup lives in the repository root README; run commands from the repo root.
- Keys come from the root `.env` (`OPENAI_API_KEY`, `OPENROUTER_API_KEY`).
- Filling the `es:` fields, reviewing the codebook, and reviewing codes
  require zero Python.
- All files are UTF-8. Read them with `encoding="utf-8"` (or set
  `PYTHONUTF8=1`), otherwise quotes render as mojibake.
- Seeds are per-transcript (reused across the three turns deliberately; the
  context differs per call), vary across replicates and conditions, and are
  best-effort: honored by OpenAI direct, advisory on OpenRouter, absent for
  reasoning-effort models. Claim "reproducible request parameters", not
  "deterministic outputs".

Runs land in `studies/punt0_anchoring/logs/<run_id>/` with `manifest.json`,
a frozen `stimuli_snapshot.yaml`, the machine log `transcripts.jsonl` (one
JSON object per line), a shuffled `coding_sheet_blind.csv` (hashed ids, no
condition columns, for disagreement review), and `coding_key.csv` (the
id-to-condition map, consulted only after review).

## Sample run

`logs/punt0_20261003T165820Z/` holds one demo transcript (PA1, A1, en,
GPT-4o). The easiest reading is the coding sheet in Excel/LibreOffice;
`transcripts.jsonl` is the machine log. Its turn-3 reply, a model
apologizing for an error it never made, is worked example 1 in
`codebook_attribution.md`. Note: it was generated with the earlier planted
claim and the earlier two-file-less sheet format; it illustrates the
phenomenon, not the frozen design.

## Status

- [x] Scaffold: runner, chat module, LLM coding panel, stimuli (English), codebook draft
- [ ] Spanish materials (Salamanca García) — see Contributing above
- [ ] Czech and Japanese turns and planted claims (existing translation workflow)
- [ ] Design round by email: freeze stimuli PA2–PA4, anchors, codebook decision rules
- [ ] OSF preregistration
- [ ] Calibration round (30 transcripts, LLM panel + decision-rule review)
- [ ] Full run
