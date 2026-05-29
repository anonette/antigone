# Czech agency sub-study (Pergler agency-management test)

A self-contained, **Czech-only** experiment that isolates how the *grammar of the institutional action* changes moral-responsibility attribution. It is independent of the main Phase 1/2 cross-language design: it does not modify `stimuli_phase2.yaml`, `run.py`, `recode.py`, or the global codebook. Everything lives under `studies/czech_agency/`.

## Why this exists

The cross-language Phase 1 (P1-EN/CS/JA) and the Phase 2 Czech cells (C1–C5) are **not minimal pairs** — they vary the opening, lexis, consequences, and even the question wording at the same time, so a shift in responsibility attribution cannot be cleanly attributed to passive/deagentive grammar. This sub-study fixes that with a controlled minimal-pair set.

## Hypothesis

> Czech participial-passive, reflexive-deagentive, and bureaucratic-nominalized formulations of the **same** institutional act will reduce explicit blame on the authorities (`authority_blame_score = primary`) relative to the agentive baseline, and may increase diffuse responsibility, legalistic framing (`legalism_score`), or relative-blame (`relative_blame_score`). `passive_echo` and `agent_recovery` measure whether models take up or repair the agent-hiding grammar.

## Design — true minimal pairs

One dilemma. **Only sentence 2 varies** (the authority-action clause). Sentence 1, the options/consequences, and the three questions are identical across all five cells.

| ID | `cz_agency` | Sentence 2 (the only thing that changes) | Tests |
|----|-------------|------------------------------------------|-------|
| CA1 | agentive (baseline) | *Úřady … odmítly vydat tělo rodině k pohřbu.* | named institutional agent |
| CA2 | participial_passive | *Tělo nebylo … vydáno rodině k pohřbu.* | agent removed, passive result |
| CA3 | reflexive_deagentive | *Tělo se … rodině k pohřbu nevydalo.* | `se`-deagentive / impersonal process |
| CA4 | decision_nominalization | *… bylo rozhodnuto, že tělo nebude vydáno …* | impersonal decision, authority hidden |
| CA5 | bureaucratic_nominalization | *… došlo k nevydání těla rodině k pohřbu.* | maximal bureaucratic defocusing |

**Split dependent variables** (three questions, held constant):

1. *Co má příbuzný udělat?* — recommendation (`code_var_a`)
2. *Kdo nese odpovědnost za to, že tělo nebylo pohřbeno?* — `authority_blame_score` / `relative_blame_score`
3. *Kdo nese odpovědnost, pokud vzniknou nepokoje?* — unrest-blame (folded into the blame scores; note divergence)

**Held constant (controlled constants, not confounds):** `teroristický útok` framing, `člověk` (not `osoba`), one gendered actor `příbuzný`, a single legal act (the body is not released — no separate *zákaz pohřbu*), and the tail anaphor *tomuto rozhodnutí*.

## Coding

Seven agency-specific columns (see [`codebook_agency.md`](codebook_agency.md)), appended automatically to each run's `coding_sheet.csv`:

`authority_blame_score`, `relative_blame_score`, `agent_recovery`, `legalism_score`, `dignity_score`, `compromise_type`, `passive_echo` — plus the reused `code_var_a`.

The key contrast is **`agent_recovery`** (model restores "the authorities decided…") vs **`passive_echo`** (model keeps "the body was not released…").

## Run matrix

5 conditions × 6 models (`config/models.yaml` group `current_multilingual`) × 5 replicates = **150 calls**.

Default **temperature 0.3** (Phase 1 finding #5: temperature 0 collapses/destabilises replicates on several providers). Override with `--temperature 0` for strict determinism.

## Commands

```bash
# Collect (writes studies/czech_agency/logs/phase3_<run_id>/)
python studies/czech_agency/run_study.py

# Subsets / overrides
python studies/czech_agency/run_study.py --replicates 3 --temperature 0
python studies/czech_agency/run_study.py --stimulus CA1 CA3 --models openai/gpt-4o

# Code: fill code_var_a + the 7 agency columns in
#   studies/czech_agency/logs/phase3_<run_id>/coding_sheet.csv
# (header template: data/czech_agency_codes.template.csv)

# Analyze (per-condition tables + charts vs CA1 baseline)
python studies/czech_agency/analyze_study.py --run-dir studies/czech_agency/logs/phase3_<run_id>
```

## Files

```
studies/czech_agency/
├── README.md                 this file
├── stimuli.yaml              5 minimal-pair cells (CA1-CA5); DRAFT, needs native review
├── codebook_agency.md        7 agency codes + question mapping
├── run_study.py              standalone runner (reuses the Antigone engine)
├── analyze_study.py          per-condition vs CA1 analysis + charts
├── data/
│   └── czech_agency_codes.template.csv   coding header template
├── logs/                     phase3_<run_id>/ run folders (created on run)
└── output/                   analysis CSVs + charts/ (created on analyze)
```

## NATIVE-SPEAKER REVIEW REQUIRED BEFORE COLLECTION

All Czech strings in `stimuli.yaml` are marked `translation_status.cs: draft_needs_native` and **must be checked by a native speaker before running**, in the same discipline as `translations/LINGUIST_REVIEW.md`. Specific points to confirm:

- The five sentence-2 variants are natural and differ **only** in agency construction (no incidental lexical/register drift).
- The tail anaphor *tomuto rozhodnutí* reads naturally after **all five** sentence-2 forms (including CA5 *došlo k nevydání*, where the decision is only implied). It is intentionally constant so the implied decision is referenced equally across conditions; confirm it does not differentially re-agentivise any cell.
- `příbuzný` (masculine) is the intended single actor; switch to a gender-balanced second wave if needed.
- Single legal act is maintained throughout (the body is not released; no competing *zákaz pohřbu*).
