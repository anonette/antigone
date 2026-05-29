# Czech agency sub-study — pilot findings

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

**The agent-hiding manipulation did not reduce blame on the authorities.** Models reconstruct the deleted institutional agent and re-attribute primary responsibility to it, even in the most defocused (nominalized) conditions.

### Authority blamed as "primary" for the non-burial

| Condition | authority = primary | Δ vs agentive |
|-----------|---------------------|----------------|
| CA1 agentive | 76% | — |
| CA2 participial passive | 72% | −0.04 |
| CA3 reflexive deagentive | 88% | +0.12 |
| CA4 decision nominalization | **96%** | **+0.20** |
| CA5 bureaucratic nominalization | 80% | +0.04 |

If anything, the more bureaucratic the framing, the *more* the authorities are blamed (CA4 highest).

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
