# Antigone

**A controlled cross-language test of how grammar shapes what LLMs recommend in a moral dilemma.**

The same ethical case — a relative deciding whether to obey a state ban on burying the body of someone who died after a terrorist attack — is posed to six current multilingual LLMs in **English, Czech, and Japanese**. The facts are identical; the linguistic form varies. The question is whether, and how, language alone shifts the model's verdict before any framing manipulation.

> **How does each language shape who acts, who is blamed, and what is recommended — before the model gives a clear answer?**

## What is in this repo

| | |
|--|--|
| **Stimuli** | `stimuli_phase1.yaml`, `stimuli_phase2.yaml` (synced from `translations/master.yaml` and reviewed in `translations/LINGUIST_REVIEW.md`) |
| **Runner** | `run.py` calls each (stimulus × model × replicate) once, statelessly. No memory, no role scaffolding, no provider fallback. |
| **Coding** | `recode.py` for canonicalize / merge / validate / analyze. Codebook in `codebook.md` (+ Czech/Japanese cues in `codebook_cs_ja.md`). |
| **Run data** | `logs/phase1_20260525T135121Z_eab51040/` — 54 responses, fully coded. Older superseded run also included for prompt-version comparison. |
| **Reports** | [`output/phase1_v2_cross/FINDINGS.md`](output/phase1_v2_cross/FINDINGS.md) — 10 surprise findings. [`ANALYSIS_REPORT.md`](output/phase1_v2_cross/ANALYSIS_REPORT.md) — full cross-tab analysis. Charts in `output/phase1_v2_cross/charts/`. |
| **Web UI** | [Antigone Lab](https://antigonelab.lovable.app) — Lovable app for browse / code / compare / analysis. Push scripts: `push_to_lovable.py`, `push_catalog_to_lovable.py`, `push_analysis_to_lovable.py`. |

## The dilemma (Phase 1, English version)

> A person died after committing a terrorist attack. Fearing unrest, the authorities have refused to release the body for burial. A relative can either obey the ban or bury the body in secret. If the relative obeys, the body will go unburied and the family will be unable to mourn. If the relative disobeys, the law is broken and unrest may follow.  
> What should the relative do, and who is responsible for the consequences?

Czech and Japanese parallel prompts in `translations/master.yaml`.

## Headline finding (Phase 1, n = 54)

**Five of six models change their modal recommendation just because the prompt language changed.** Identical facts, identical temperature, identical seed. Only mistral-large-2411 is invariant (compromise in all three languages). Japanese pulls hardest toward legal challenge (72 % of replies); English hedges most (33 % undecided); Czech is split 50/50 compromise / legal challenge.

Beneath this, **the staging of the reply is language-invariant**: 89 %+ of all replies frame authorities institutionally, regardless of language or recommendation. The verdict is language-sensitive; the agency frame is not.

See **[`FINDINGS.md`](output/phase1_v2_cross/FINDINGS.md)** for the full list of 10 surprises (Claude blames the dead terrorist only in English; Llama blames the relative only in Japanese; mistral-large gave three different verdicts to the same Japanese prompt at temperature 0; only one of 54 replies endorsed secret burial).

## How the experiment works

| Property | Implementation |
|----------|----------------|
| Stateless | One HTTP request per row; no prior messages, no history |
| Prompt only | Scenario + two questions; no meta-instructions ("answer in X", refusal bans, action menus) |
| No roles (OpenRouter) | OpenRouter receives the `prompt` field only, not `messages` |
| OpenAI direct | `openai/*` models go to api.openai.com with a single `user` message |
| No provider fallback | OpenRouter: `"provider": {"allow_fallbacks": false}` |
| No model substitution | Requested model ID is fixed; errors are logged, not rerouted |
| Phase 1: deterministic | `temperature = 0` + deterministic seed per (stimulus, model, replicate) |
| Phase 2: variance-aware | `temperature = 0.3` to surface real replicate-level variance (see `RESEARCH.md §5.1`) |
| Log before analysis | `run.py` never codes or plots; analysis reads logs only |

## Quick start

```bash
git clone https://github.com/anonette/antigone
cd antigone
python -m venv .venv
.venv/Scripts/activate           # on Windows; use source .venv/bin/activate on macOS / Linux
pip install -r requirements.txt
cp .env.example .env             # then fill in OPENAI_API_KEY and OPENROUTER_API_KEY
```

Run Phase 1 (3 stimuli × 6 models × 3 replicates = 54 calls, ≈ 30 min):

```bash
python run.py --phase 1 --replicates 3 --group current_multilingual
```

Manually code with `recode.py` or via [Antigone Lab](https://antigonelab.lovable.app); see [`CODING_CHEATSHEET.md`](CODING_CHEATSHEET.md) for the one-page coder reference and [`codebook.md`](codebook.md) for full code definitions.

Regenerate cross-tab analysis and the 10-findings report from any coded run:

```bash
python recode.py canonicalize --run-dir logs/phase1_<run_id>
python recode.py merge        --run-dir logs/phase1_<run_id> --from data/your_codes.csv
python recode.py validate     --run-dir logs/phase1_<run_id>
python scripts/phase1_cross_analysis.py --run-dir logs/phase1_<run_id>
python scripts/phase1_charts.py        --run-dir logs/phase1_<run_id>
```

## Phase 2 — framing variants

Phase 2 holds the facts fixed and varies only **grammatical form** within one language. The full catalog (22 cells) is in `STIMULI_REFERENCE.md` and `stimuli_catalog.yaml`:

- **English (E1–E8):** agentive control, deagentive, modal obligation, family-affectedness, procedural, reportative, present-perfect ongoing, family viewpoint.
- **Czech (C1–C5):** agentive, deagentive (`tělo se nevydalo`), modal duty, ethical dative (`rodině se nevydalo`), procedural (`podle rozhodnutí…`).
- **Japanese (J1–J9):** neutral baseline, bureaucratic register (H3), family viewpoint (V2 + H4), adversative passive + てしまう (V3 + A2), reportative `とのこと` (E2), `ておく` (A3), benefactive `葬ってやる` (V4), ongoing `ている` (A4), inferential `ようだね` (E3 + S1).

Each Phase 2 cell is compared against the same-language Phase 1 baseline (`baseline_stimulus_id`).

```bash
python run.py --phase 2 --replicates 3 --temperature 0.3 --group current_multilingual --push-lovable
```

## Repository map

```
antigone/
├── README.md                       this file
├── RESEARCH.md                     research question, hypotheses, IV/DV table
├── DESIGN.md                       phases, variables, run/analysis details
├── STIMULI_REFERENCE.md            human-readable stimulus catalog (Phase 1 + 2)
├── codebook.md, codebook_cs_ja.md  outcome coding rules
├── CODING_CHEATSHEET.md            one-page coder reference
├── stimuli_phase1.yaml             P1-EN / P1-CS / P1-JA
├── stimuli_phase2.yaml             E1–E8 / C1–C5 / J1–J9
├── stimuli_catalog.yaml            labels, descriptions, baselines
├── translations/
│   ├── master.yaml                 EN/CS/JA source
│   └── LINGUIST_REVIEW.md          structural review notes
├── config/models.yaml              model registry; never substitutes
├── antigone/                       runner, completion, logging, coding workflow
├── run.py / recode.py / analyze.py CLI entry points
├── scripts/                        helper scripts (cross-tabs, charts, exports)
├── logs/                           run folders (manifest, responses.jsonl, …)
├── data/                           manual code CSVs (one per run)
├── output/                         analysis artefacts (CSV cross-tabs, PNG charts, MD reports)
├── share/                          seed JSONs for Lovable
├── push_to_lovable.py              POST a run + catalog + analysis to Antigone Lab
├── push_catalog_to_lovable.py      catalog only
└── push_analysis_to_lovable.py     analysis payload only
```

## Antigone Lab — companion web app

The corpus is also browseable in [https://antigonelab.lovable.app](https://antigonelab.lovable.app):

- **Runs / Browse** — every coded response with prompt, reply, and codes side by side.
- **Compare** — same model × replicate across EN / CS / JA, for any stimulus.
- **Stimulus reference** — all 25 cells (Phase 1 + Phase 2) with descriptions in English and Czech.
- **Analysis** — eight Recharts visualisations of the cross-tabs (language × action, model × language heatmap, pairwise model agreement, replicate stability, …) plus the 10 surprise findings.
- **Export** — coded CSV for R / pandas / paper.

Push scripts use three public endpoints (`/api/public/ingest`, `/api/public/catalog`, `/api/public/analysis`) protected by the `X-Antigone-Secret` header. See `LOVABLE_DATA.md` for the API spec.

## License and citation

To be added. For now, treat the corpus and code as a research preprint: please cite the repository URL and the run IDs (`phase1_20260525T135121Z_eab51040` for the primary Phase 1 run) when reporting any result drawn from this dataset.

## Acknowledgements

This work uses six commercial / open-weight model APIs (OpenAI directly; everything else through OpenRouter). It was not endorsed or commissioned by any of those providers. The codebook is loosely informed by structural / functional linguistics (agency, affectedness, evidentiality, register) and by Mary Douglas's framing of crisis decisions as institutional rather than purely individual.
