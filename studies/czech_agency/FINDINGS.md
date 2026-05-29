# Czech agency sub-study — pilot findings

> **Independent study.** This Czech-only minimal-pair study (grammatical agency as the variable) is **separate** from the cross-language Phase 1 baseline (`output/phase1_v2_cross/FINDINGS.md`, run `phase1_…`). Do not pool or compare their numbers; different design, stimuli, models-present, and temperature.

**Run:** `phase3_20260529T112210Z_77ea6d3b`
**Design:** one burial-ban dilemma, five Czech minimal-pair conditions varying **only** the grammar of the authority's action (sentence 2); 6 models x 5 replicates, temperature 0.3.
**Coded:** 125 responses (5 models x 5 conditions x 5 replicates). **qwen excluded** (its OpenRouter slug returns HTTP 400 for the `/completions` endpoint).
**Status:** PILOT. Prompts are `draft_needs_native`; coding is a rule-based first pass (`coder_id = auto-cursor-2026-05`) and needs human verification. Numbers are provisional.

## Conditions

- CA1 agentive (baseline): *Úřady ... odmítly vydat tělo rodině k pohřbu.*
- CA2 participial passive: *Tělo nebylo ... vydáno rodině k pohřbu.*
- CA3 reflexive deagentive: *Tělo se ... rodině k pohřbu nevydalo.*
- CA4 decision nominalization: *... bylo rozhodnuto, že tělo nebude vydáno ...*
- CA5 bureaucratic nominalization: *... došlo k nevydání těla rodině k pohřbu.*

## Headline result

**The agent-hiding manipulation did not reduce blame on the authorities.** Authority blame sits at ceiling in every condition — including the most defocused (nominalized) ones — with no meaningful gradient. Models reconstruct the deleted institutional agent and re-attribute primary responsibility to it regardless of surface grammar.

### Authority blamed as "primary" for the non-burial (verified coding)

| Condition | authority = primary | Δ vs agentive |
|-----------|---------------------|----------------|
| CA1 agentive | 92% | — |
| CA2 participial passive | 92% | 0.00 |
| CA3 reflexive deagentive | 100% | +0.08 |
| CA4 decision nominalization | 96% | +0.04 |
| CA5 bureaucratic nominalization | 92% | 0.00 |

The effect of the manipulation is essentially flat at ceiling: 92–100% across all five conditions. (An earlier first-pass coding showed a spurious 76→96% gradient; on verification this was a coding artifact — the rule had missed bare "Úřady nesou odpovědnost…" phrasings. Corrected, the picture is uniform near-ceiling.)

### Agent recovery (model re-names úřady / stát / orgán as the decision-maker)

| Condition | agent_recovery = yes |
|-----------|----------------------|
| CA1 | 96% |
| CA2 | 100% |
| CA3 | 100% |
| CA4 | 100% |
| CA5 | 100% |

Even when the prompt says only *"došlo k nevydání těla"* (no agent), the model supplies *"rozhodly úřady / stát / orgán"*.

### Passive echo (model repeats the agentless wording)

**0% in every condition.** No model extends the deagentive frame; all re-agentivise.

### Recommended action (VAR-A)

Compromise/negotiation dominates (68–84% per condition), with a little legal_challenge and some undecided. **No response endorsed obeying the ban or secret burial as the primary recommendation.** This mirrors Phase 1: models reroute the obey/defy binary into a negotiated third path.

## Interpretation

At temperature 0.3, these six (five usable) models behave as **agent-restorers**: Czech deagentive, reflexive, and nominalized grammar — which in human discourse defocuses the institutional actor — does **not** shift LLM responsibility attribution away from the authorities. The models treat the hidden decision as an institutional act and name the institution regardless of surface grammar. The Pergler-style "agency management" effect, robust in human language, appears **not to transfer** to these models' explicit blame assignment on this dilemma.

This is a clean, slightly counter-intuitive result that the controlled minimal-pair design was built to detect (and that the earlier cross-language Phase 2 cells, which confounded grammar with lexis/order/question wording, could not have isolated).

## Why this might happen (hypotheses, ranked)

These explain *why* the agent-hiding did not work. They are ordered by how strongly the current data support them, and each notes how to discriminate it.

1. **The responsibility question re-agentivises the scene (most likely; partly methodological).** The prompt explicitly asks *"Kdo nese odpovědnost za to, že tělo nebylo pohřbeno?"* — which demands that the model name a responsible party. Deagentive grammar backgrounds the agent in sentence 2, but a direct "who is responsible?" question forces it back to the foreground. The manipulation and the measurement pull against each other. **Test:** a no-question control (free-form prompt without the explicit responsibility questions). If `agent_recovery` stays ~100%, the effect is genuine model behaviour; if it falls, the question was doing the work.

2. **World knowledge overrides surface syntax.** After a terrorist attack, "the body was not released" has one pragmatically available agent — the authorities. The model fills the gap from world knowledge regardless of voice. Agency management *defocuses* a known agent; it does not delete the inference, and a system asked "who decided?" re-surfaces it. On this reading the models are doing competent pragmatic inference, not being fooled.

3. **Instruct-tuning normalises terse/passive input into agentive analytic prose.** RLHF assistants rewrite whatever register they receive into structured exposition ("Primární odpovědnost nesou úřady, které rozhodly…"). This is the likely cause of `passive_echo = 0%`: they do not mirror the input voice, they re-render it.

4. **Ceiling effect, not a gradient.** Corrected coding shows authority blame at 92–100% in every condition, so there is no room for the grammar to move it down — and it does not. Even *"bylo rozhodnuto"* and *"došlo k nevydání"* (which give the model the least agentive cue) still produce ~92–96% primary authority blame. The deagentive surface does not change the model's institutional attribution at all.

**If the no-question control still shows ~100% recovery**, the substantive claim is: current instruct LLMs are *agent-restorers* — Czech agency-management grammar does not buy the institution the blame-deflection it buys in human discourse, because the models resolve responsibility from world knowledge and a normalising output style, and explicit-responsibility framing amplifies that.

## Coding verification (rule-based first pass)

The seven agency columns were filled by a rule-based first pass (`coder_id = auto-cursor-2026-05`) and then re-checked against the response texts. Verification notes:

- `agent_recovery` and `passive_echo` are lexically robust (presence/absence of a named institutional agent vs agentless echo); manual spot-checks across conditions agreed with the rule.
- `authority_blame_score`: **recoded after verification.** The first pass required the literal word "primární/hlavní" and so mis-labelled bare "Úřady nesou odpovědnost za to, že tělo nebylo pohřbeno" as `partial`. The corrected rule keys on the authority being named as the bearer of responsibility for the non-burial in any phrasing. Result: 92–100% `primary` across all conditions (a flat ceiling, not the spurious 76→96% gradient the first pass showed). 90 of 125 rows changed on recode.
- `relative_blame_score` was recomputed alongside (none / partial / primary by explicit exoneration vs shared-blame phrasing). `compromise_type`, `legalism_score`, `dignity_score` and `code_var_a` remain **first-pass** and are the columns most in need of independent human coding.

The headline (agent recovery ~100%, authority blame at ceiling, no deflection, passive_echo 0%) is robust to the recode; if anything the corrected coding makes it cleaner.

## Caveats before any claim

1. **Native review** of the five Czech prompts (still draft); confirm the only systematic difference is the agency construction.
2. **Human re-coding** of `authority_blame_score`, `relative_blame_score`, `compromise_type` (current codes are a rule-based first pass).
3. **qwen** missing (endpoint incompatibility) — 5 models, not 6.
4. **Temperature 0.3**; a temperature-0 replication would test whether the agent-restoration is sampling-robust.
5. Single dilemma, single language — no claim beyond this scenario.

## Files

- Stimuli: `stimuli.yaml` · readable: `PROMPTS_CS.md`
- Codebook: `codebook_agency.md`
- Run: `logs/phase3_20260529T112210Z_77ea6d3b/` (responses, coding_sheet, prompts_audit, manifest)
- Tables + charts: `output/` (`authority_blame_by_condition.csv`, `agent_recovery_rate.csv`, `passive_echo_rate.csv`, `authority_primary_vs_agentive.csv`, `var_a_by_condition.csv`, `charts/`)
- Lovable payload: `output/agency_analysis.json` (run_id `phase3_20260529T112210Z_77ea6d3b`)

Regenerate: `python studies/czech_agency/analyze_study.py --run-dir logs/phase3_20260529T112210Z_77ea6d3b` and `python studies/czech_agency/build_agency_analysis.py --run-dir ...`.
