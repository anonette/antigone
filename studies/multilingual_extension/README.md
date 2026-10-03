# Multilingual extension (ISF five-language endorsement test)

A self-contained experiment that extends the Antigone protocol to the **exact confirmatory language set of the ISF resubmission** — Hebrew, English, Czech, Bulgarian, Serbian — and adds, within each language, a minimal-pair manipulation of **how the stimulus marks the authorities' account** (plain indicative vs each language's own reportative/nonconfirmative carrier). It is independent of the main Phase 1/2 cross-language design and of `studies/czech_agency/`: it does not modify `stimuli_phase2.yaml`, `run.py`, `recode.py`, or the global codebook. Everything lives under `studies/multilingual_extension/`.

## Why this exists

Phase 1 established the language-flip result in EN/CS/JA — two of which (JA) are outside the ISF confirmatory set. The ISF resubmission ("Grammar or Legal Culture?") builds its primary hypotheses on the **Endorsement Partition**: the grammatical means by which a writing voice marks what it vouches for versus what it merely reports — Bulgarian renarrative morphology against Serbian *navodno*, Czech reportative *měl* + infinitive, Hebrew *lekhora*, English reporting-verb selection. This study does two things at once:

1. **Replicates the language-flip result inside the project's own five languages**, including the BG/SR near-twin pair that carries ISF H1.
2. **Pilots the EPI coding channels on model output**: when a model restates the authorities' account, does it preserve, upgrade, or hedge the account's epistemic status — and by which of its output language's own means? This makes the study a direct mini-pilot of the ISF instrument (the `claim_marking_means` column is a one-proposition EPI), not just a replication.

It is a **motivating pilot, never confirmatory**: no real-corpus band is estimated from it, no ISF hypothesis is tested on it, and the anti-circularity architecture of the proposal (Phase A bands frozen before generation) is untouched — these are moral-dilemma responses, not judicial opinions.

## Hypotheses (descriptive, pre-stated)

> (1) The Phase 1 language effect on modal recommendation (`code_var_a`) reappears within HE/EN/CS/BG/SR. (2) In reportative cells, models **flatten**: `evidential_echo` ≈ 0 (per the passive-echo result) and `evidential_repair` > 0 — reported status silently upgraded to asserted fact, the spontaneous analogue of the ISF's "migration toward the English band". (3) Any grammar effect is larger in the no-question control than under the responsibility question (saturation transfer). (4) The distribution over `claim_marking_means` differs by language according to available means — BG can mark morphologically, SR only lexically: the first empirical look at the contrast ISF H1 is built on. (5) Model heterogeneity is qualitative (Claude vs Gemini in the Czech pilot); per-model curves throughout.

## Design — minimal pairs within language, parallels across languages

One dilemma (the Phase 1 burial-ban case). Per language, **only the marking of the authority-action sentence varies** between the two cells; everything else is identical. Across languages, prompts are semantic parallels (anchored on P1-EN/P1-CS verbatim for EN/CS).

| Language | `evid_condition: baseline` | `evid_condition: reportative` (the only change) | Carrier type |
|----------|----------------------------|--------------------------------------------------|--------------|
| EN | *the authorities have refused* | *the authorities have **reportedly** refused* | lexical adverb |
| CS | *úřady … odmítly* | *úřady **měly** … **odmítnout*** | reportative modal (ISF Czech carrier) |
| BG | *властите … отказаха* (aorist) | *властите … **отказали*** (renarrative, bare l-participle) | **morphological** (sole grammaticalized carrier in the set) |
| SR | *vlasti su odbile* | *vlasti su **navodno** odbile* | lexical adverb (the only one Serbian has — that asymmetry is the design) |
| HE | *הרשויות סירבו* | *הרשויות סירבו **לכאורה*** | legal lexeme (ISF Hebrew form list) |

**Crossed with the question manipulation** (the saturation control, per the Czech agency finding that asking drives a real 92%→72% gradient to a 92–100% ceiling):

- `ME-*` (stimuli.yaml): full closing — action question + responsibility question (Phase 1-comparable).
- `MN-*` (stimuli_noq.yaml): action question only — the **primary surface** for the spontaneous endorsement DVs.

No prompt names evidentiality, endorsement, neutrality, or any measured construct; the manipulation lives in stimulus grammar and is counterbalanced (B vs R), so calque is separable from stimulus echo — the same stimulus-grammar discipline the ISF design commits to.

**Split dependent variables:**

1. Recommendation (`code_var_a`) — the Phase 1 replication layer.
2. Endorsement channels (8 columns, [`codebook_endorsement.md`](codebook_endorsement.md)) — the mini-EPI layer, coded against one fixed target proposition: the authorities' refusal and its fear-of-unrest justification.

## Run matrix

Main: 10 cells (5 languages × 2 evid) × 6 models (`config/models.yaml` group `current_multilingual`) × 5 replicates = **300 calls**. Control (`stimuli_noq.yaml`): another **300**. Total **600** (≈ $5–10 via OpenRouter at observed response lengths; budget $25 with reruns).

Default **temperature 0.3** (Phase 1 finding #5: temperature 0 collapses/destabilises replicates on several providers). Known issue: qwen-2.5-72b returned HTTP 400 on the `/completions` endpoint in the Czech agency runs; keep it in the matrix, log errors, and report on 5 models if it fails again.

Japanese is **not** in the matrix (language-capacity rule: no confirmatory language without in-house reading capacity). A JA continuity cell can be added later by copying P1-JA, marked non-confirmatory.

## Commands

```bash
# Gate 0 check is built in: the runner REFUSES draft_needs_native cells.
# Collect main run (writes studies/multilingual_extension/logs/phase4_<run_id>/)
python studies/multilingual_extension/run_study.py

# Collect no-question control
python studies/multilingual_extension/run_study.py --stimuli-file stimuli_noq.yaml

# Subsets / overrides
python studies/multilingual_extension/run_study.py --replicates 3 --stimulus ME-BG-B ME-BG-R
python studies/multilingual_extension/run_study.py --models openai/gpt-4o anthropic/claude-sonnet-4

# EN-only smoke test before native sign-off (the ONLY sanctioned use of the bypass)
python studies/multilingual_extension/run_study.py --stimulus ME-EN-B ME-EN-R --replicates 1 --allow-draft-translations

# Code: fill code_var_a + the 8 endorsement columns in
#   studies/multilingual_extension/logs/phase4_<run_id>/coding_sheet.csv
# (header template: data/multilingual_extension_codes.template.csv)
```

## Files

```
studies/multilingual_extension/
├── README.md                 this file
├── stimuli.yaml              10 cells (ME-*), full question; bg/sr/he DRAFT, needs native review
├── stimuli_noq.yaml          10 cells (MN-*), action-only control; same draft status
├── codebook_endorsement.md   8 endorsement codes + closed form lists + gates
├── run_study.py              standalone runner (reuses the Antigone engine; enforces Gate 0)
├── data/
│   └── multilingual_extension_codes.template.csv   coding header template
├── logs/                     phase4_<run_id>/ run folders (created on run)
└── output/                   analysis CSVs + charts/ (created on analyze)
```

## NATIVE-SPEAKER REVIEW REQUIRED BEFORE COLLECTION

All Bulgarian, Serbian, and Hebrew strings, and the new Czech reportative cell, are marked `translation_status: draft_needs_native` and **must be checked by a native (or named native-equivalent) reviewer before running** — the runner enforces this. The 90/125-row recode in the Czech agency pilot, caught only by native reading, is the standing justification. Specific points each reviewer must resolve (also flagged per cell in the YAML):

- **Minimal-pair property:** within each language, the B and R cells differ *only* in the marking of the authority-action sentence(s) — no incidental lexical or register drift.
- **BG (critical):** the bare l-participles in ME/MN-BG-R (*починал, извършил, отказали*) must read as renarrative, not truncated perfect — this is exactly the third-person auxiliary-drop homography (Friedman: nonconfirmative marking, not obligatory evidentials). The reviewer also adjudicates whole-narration renarrative (drafted) vs sentence-2-only (tighter pair, higher ambiguity risk); the decision is recorded either way.
- **CS:** reportative vs deontic reading of *měly … odmítnout* inside the relative clause; fallback *údajně odmítly* if deontic reading intrudes.
- **SR:** scope of *navodno* (over the refusal, not the fear); ekavian Serbian lexical choices; produce the Cyrillic rendering for the archive (digraphia rule).
- **HE:** placement/register of *לכאורה*; fallback *על פי הדיווחים*.
- **Actor gender (known non-uniformity):** EN unmarked, CS feminine (*příbuzná*, kept verbatim from P1-CS for anchor continuity), BG epicene (*роднина*), SR masculine (*rođak*), HE masculine (*קרוב משפחה*). Documented as a limitation, not silently harmonized; a gender-balanced second wave is the fix if it matters.

Sign-off decisions are archived in `translations_review.md` (create at review), and `translation_status` is flipped to `reviewed` per cell — only then will the runner collect.
