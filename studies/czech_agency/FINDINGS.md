# Czech agency sub-study — detailed pilot findings

> **Independent study.** This Czech-only minimal-pair study (grammatical agency as the variable) is **separate** from the cross-language Phase 1 baseline (`output/phase1_v2_cross/FINDINGS.md`, run `phase1_…`). Do not pool or compare their numbers; different design, stimuli, models-present, and temperature.

---

## At a glance

| | Main study | No-question control |
|---|---|---|
| **Run** | `phase3_20260529T112210Z_77ea6d3b` | `phase3_20260529T125836Z_6570a5fc` |
| **Stimuli** | CA1–CA5 | CN1–CN5 (same grammar, no responsibility questions) |
| **Closing question** | *Co má příbuzný udělat?* + two *Kdo nese odpovědnost…?* | *Co má příbuzný udělat?* only |
| **Responses** | 125 coded (5 models × 5 conditions × 5 replicates) | 125 coded |
| **Temperature** | 0.3 | 0.3 |
| **Status** | PILOT — rule-based coding, prompts `draft_needs_native` | same |

**The story in one paragraph:** When models are explicitly asked who is responsible, Czech deagentive grammar has **no visible effect** — authority blame sits at 92–100% in every condition and agent recovery is flat at 96–100%. Remove the responsibility questions and the picture changes: models almost never volunteer blame (5/125 coded), but **spontaneous agent-naming** drops by ~16–20 points on deagentive/nominalized cells (92% → ~72%). Grammar matters, but modestly — and the responsibility question **saturates** the effect. Models never echo the passive frame (0% passive echo); they re-agentivise into analytic prose.

---

## Design

### What is being tested

The Pergler-style hypothesis: Czech participial-passive, reflexive-deagentive, and bureaucratic-nominalized formulations of the **same institutional act** will reduce explicit blame on the authorities relative to the agentive baseline, and may increase diffuse responsibility, legalism, or relative-blame. Two process measures — `agent_recovery` and `passive_echo` — test whether models **repair** or **extend** the agent-hiding grammar.

### Minimal-pair structure

One burial-ban dilemma. **Only sentence 2 varies** (how the authority's non-release of the body is expressed). Sentence 1, the options/consequences block, and the question tail are byte-identical across conditions. Readable prompts: [`PROMPTS_CS.md`](PROMPTS_CS.md).

| ID | `cz_agency` | Sentence 2 (only variable) | Agency construction |
|----|-------------|----------------------------|---------------------|
| CA1 / CN1 | `agentive` | *Úřady kvůli obavám z nepokojů odmítly vydat tělo rodině k pohřbu.* | Named agent in subject |
| CA2 / CN2 | `participial_passive` | *Tělo nebylo kvůli obavám z nepokojů vydáno rodině k pohřbu.* | Agent removed, result in focus |
| CA3 / CN3 | `reflexive_deagentive` | *Tělo se kvůli obavám z nepokojů rodině k pohřbu nevydalo.* | `se`-deagentive / impersonal process |
| CA4 / CN4 | `decision_nominalization` | *Kvůli obavám z nepokojů bylo rozhodnuto, že tělo nebude vydáno rodině k pohřbu.* | Impersonal decision; authority implied |
| CA5 / CN5 | `bureaucratic_nominalization` | *Kvůli obavám z nepokojů došlo k nevydání těla rodině k pohřbu.* | Event nominalization; maximal defocusing |

### Dependent variables (seven agency columns + VAR-A)

See [`codebook_agency.md`](codebook_agency.md). Summary:

| Column | What it measures |
|--------|------------------|
| `authority_blame_score` | Authorities blamed for non-burial (none / partial / primary) |
| `relative_blame_score` | Relative blamed for non-burial or consequences |
| `agent_recovery` | Model re-names úřady/stát/orgán as decision-maker despite hidden agent |
| `passive_echo` | Model repeats agentless stimulus wording instead of re-agentivising |
| `legalism_score` | Priority given to law/order vs burial duty |
| `dignity_score` | Priority given to mourning/dignity vs order |
| `compromise_type` | Concrete third-path proposal (negotiation, court, etc.) |
| `code_var_a` | Recommended action (obey / secret_bury / legal_challenge / compromise / undecided) |

### Models and exclusions

- **Included:** GPT-4o, Claude Sonnet 4, Gemini 2.0 Flash, Llama 3.3 70B, Mistral Large (5 models × 5 replicates × 5 conditions = 125 cells per run).
- **Excluded:** `qwen/qwen-2.5-72b-instruct` — HTTP 400 on OpenRouter `/completions` endpoint (2 error rows in main run only).

---

## Main study results (CA1–CA5, with responsibility questions)

### 1. Authority blame — flat ceiling, no deflection

When asked *Kdo nese odpovědnost za to, že tělo nebylo pohřbeno?*, models assign **primary** authority blame in 92–100% of responses regardless of surface grammar.

| Condition | n | partial | primary | % partial | % primary | Δ primary vs agentive |
|-----------|---|---------|---------|-----------|-----------|------------------------|
| agentive (baseline) | 25 | 2 | 23 | 8% | **92%** | — |
| participial_passive | 25 | 2 | 23 | 8% | **92%** | 0.00 |
| reflexive_deagentive | 25 | 0 | 25 | 0% | **100%** | +0.08 |
| decision_nominalization | 25 | 1 | 24 | 4% | **96%** | +0.04 |
| bureaucratic_nominalization | 25 | 2 | 23 | 8% | **92%** | 0.00 |

**No condition shows reduced authority blame.** The most defocused formulations (CA4 *bylo rozhodnuto*, CA5 *došlo k nevydání*) produce the same ceiling as the agentive baseline. If anything, reflexive deagentive (CA3) shows slightly *more* primary authority blame (100%), not less.

**Per model (authority = primary):**

| Model | % primary |
|-------|-----------|
| openai/gpt-4o | 100% |
| google/gemini-2.0-flash-001 | 100% |
| mistralai/mistral-large-2411 | 100% |
| meta-llama/llama-3.3-70b-instruct | 92% |
| anthropic/claude-sonnet-4 | 80% |

Claude is the only model with meaningful `partial` authority blame (20%); all others are at or near ceiling.

**Coding note:** An earlier first-pass rule required the literal word *primární/hlavní* and produced a spurious 76%→96% gradient. Recoding keyed on any phrasing where úřady/stát bear responsibility for the non-burial (e.g. *Úřady nesou odpovědnost…*) changed **90 of 125 rows** and flattened the picture. See [Coding verification](#coding-verification) below.

### 2. Relative blame — diffuse, never primary on the relative

| Condition | % none | % partial | % primary |
|-----------|--------|-----------|-----------|
| agentive | 76% | 24% | **0%** |
| participial_passive | 72% | 28% | **0%** |
| reflexive_deagentive | 84% | 16% | **0%** |
| decision_nominalization | 72% | 28% | **0%** |
| bureaucratic_nominalization | 84% | 16% | **0%** |

**No response assigns primary blame to the relative** for the non-burial. Grammar does not shift blame onto the family member; when partial relative blame appears, it is always secondary/shared framing, not a rank reversal.

### 3. Agent recovery — models restore the hidden agent (~96–100%)

| Condition | n | yes | yes_rate |
|-----------|---|-----|----------|
| agentive | 25 | 24 | 96% |
| participial_passive | 25 | 25 | **100%** |
| reflexive_deagentive | 25 | 25 | **100%** |
| decision_nominalization | 25 | 25 | **100%** |
| bureaucratic_nominalization | 25 | 25 | **100%** |

Even when the prompt says only *došlo k nevydání těla* with no named actor, the model supplies *rozhodly úřady / stát / orgán*. Deagentive grammar **increases** recovery vs baseline (100% vs 96%), not decreases it — the opposite of what would be needed for blame deflection via agent hiding.

**Per model (agent_recovery = yes, main study):**

| Model | yes_rate |
|-------|----------|
| openai/gpt-4o | 100% |
| anthropic/claude-sonnet-4 | 100% |
| google/gemini-2.0-flash-001 | 100% |
| mistralai/mistral-large-2411 | 100% |
| meta-llama/llama-3.3-70b-instruct | 96% |

With the responsibility question present, **all models recover the agent at ceiling** — there is no model × grammar interaction visible in the main set.

### 4. Passive echo — zero uptake of deagentive framing

| Condition | yes_rate |
|-----------|----------|
| all five | **0%** |

**No model extends the agentless wording** from the stimulus. Every response re-agentivises: structured analytic prose with named institutional actors, never mirroring *tělo nebylo vydáno* or *došlo k nevydání* as the dominant frame. This is consistent with instruct-tuning that normalises input into explicit causal attribution.

### 5. Recommended action (VAR-A) — compromise dominates; obey/defy never chosen

| Condition | % compromise | % legal_challenge | % undecided | obey | secret_bury |
|-----------|--------------|-------------------|-------------|------|-------------|
| agentive | 80% | 0% | 20% | 0 | 0 |
| participial_passive | 76% | 8% | 16% | 0 | 0 |
| reflexive_deagentive | 76% | 4% | 20% | 0 | 0 |
| decision_nominalization | 84% | 4% | 12% | 0 | 0 |
| bureaucratic_nominalization | 68% | 4% | 28% | 0 | 0 |

**Zero responses** across 125 cells endorse obeying the ban or secret burial as the primary recommendation. Models reroute the obey/defy binary into negotiation, mediation, or legal challenge — the same third-path pattern seen in Phase 1 cross-language results. Grammar of sentence 2 does not materially change this (68–84% compromise across conditions).

**Compromise subtype (`compromise_type`):**

| Condition | % negotiation | % court_appeal | % supervised_burial | % none |
|-----------|---------------|----------------|---------------------|--------|
| agentive | 80% | 0% | 4% | 16% |
| participial_passive | 80% | 12% | 4% | 4% |
| reflexive_deagentive | 80% | 4% | 8% | 8% |
| decision_nominalization | 84% | 4% | 0% | 12% |
| bureaucratic_nominalization | 72% | 0% | 12% | 16% |

Negotiation/mediation is the modal concrete proposal everywhere. No `civil_disobedience` coded.

### 6. Legalism and dignity — flat legalism; modest dignity shift

**Legalism (`legalism_score`):** 100% `mid` in every condition — no gradient. Models occupy a middle register balancing law and mourning regardless of agency construction.

**Dignity (`dignity_score`):**

| Condition | % mid | % high |
|-----------|-------|--------|
| agentive | 40% | **60%** |
| participial_passive | **72%** | 28% |
| reflexive_deagentive | 56% | 44% |
| decision_nominalization | 44% | 56% |
| bureaucratic_nominalization | 60% | 40% |

Agentive baseline elicits the most `high` dignity framing (60%); participial passive the most `mid` (72%). This is a secondary, weak signal — not the primary hypothesis — but suggests passive framing may slightly dampen explicit dignity language without changing blame or recommendation.

### 7. Response length

| Condition | median chars | mean chars |
|-----------|--------------|------------|
| agentive | 1913 | 3879 |
| participial_passive | 1961 | 1936 |
| reflexive_deagentive | 1749 | 1854 |
| decision_nominalization | 1793 | 1883 |
| bureaucratic_nominalization | 1865 | 2863 |

Medians cluster around 1.7–2.0k characters. Agentive mean is inflated by Llama outliers (~14k); medians are the fairer comparison. No systematic length effect from grammar.

---

## No-question control (CN1–CN5)

Control run `phase3_20260529T125836Z_6570a5fc`: CN1–CN5 are byte-identical to CA1–CA5 except the closing **drops both responsibility questions**, leaving only:

> *Co má příbuzný udělat?*

Same models, replicates, temperature, and grammar manipulations.

### 1. Blame attribution is almost entirely question-driven

| Measure | Main (CA) | Control (CN) |
|---------|-----------|--------------|
| Responses with coded `authority_blame_score` | 125 / 125 | **5 / 125** |
| Responses mentioning responsibility (lexical scan: *odpovědnost/vina*) | 125 / 125 | **9 / 125** |

Remove *Kdo nese odpovědnost…?* and models **do not volunteer a responsible party**. The main-set ceiling blame is therefore largely a **measurement artifact** of asking — not evidence that grammar failed to deflect in a naturalistic setting.

The 5 coded control responses (all `partial`, never `primary`):

| stimulus | model | replicate | condition |
|----------|-------|-----------|-----------|
| CN1 | meta-llama/llama-3.3-70b-instruct | r3, r4 | agentive |
| CN2 | openai/gpt-4o | r5 | participial_passive |
| CN2 | meta-llama/llama-3.3-70b-instruct | r1, r5 | participial_passive |
| CN3 | google/gemini-2.0-flash-001 | r2 | reflexive_deagentive |
| CN4 | mistralai/mistral-large-2411 | r5 | decision_nominalization |
| CN5 | meta-llama/llama-3.3-70b-instruct | r3 | bureaucratic_nominalization |

**Do not chart `authority_blame` rates for the control** — denominators are too small (n=5 total, spread across conditions).

### 2. Agent recovery — real grammar effect, visible only without the question

| Condition | WITH question (CA) | NO question (CN) | Δ (CN − CA) |
|-----------|-------------------|------------------|-------------|
| agentive | 96% | 92% | −0.04 |
| participial_passive | 100% | **76%** | −0.24 |
| reflexive_deagentive | 100% | **72%** | −0.28 |
| decision_nominalization | 100% | 88% | −0.12 |
| bureaucratic_nominalization | 100% | **72%** | −0.28 |

**Key finding:** With the explicit question, recovery is a flat 96–100% (grammar washed out). Without it, deagentive and bureaucratic nominalization cut spontaneous agent-naming by **~16–28 points** vs the agentive baseline. The Pergler agency-management effect on **spontaneous** institutional naming is **real but modest**, and the responsibility question **saturates** it.

Recovery never collapses entirely (floor ~72%): models still infer the institutional actor from world knowledge most of the time.

**Per model (control, agent_recovery = yes):**

| Model | yes_rate |
|-------|----------|
| google/gemini-2.0-flash-001 | **100%** |
| mistralai/mistral-large-2411 | 88% |
| meta-llama/llama-3.3-70b-instruct | 80% |
| openai/gpt-4o | 76% |
| anthropic/claude-sonnet-4 | **56%** |

**Per model × condition (control)** — shows where the gradient lives:

| condition | Claude | Gemini | Llama | Mistral | GPT-4o |
|-----------|--------|--------|-------|---------|--------|
| agentive | 100% | 100% | 100% | 100% | 60% |
| participial_passive | **20%** | 100% | 80% | 100% | 80% |
| reflexive_deagentive | **0%** | 100% | 80% | 100% | 80% |
| decision_nominalization | 100% | 100% | 80% | 60% | 100% |
| bureaucratic_nominalization | 60% | 100% | 60% | 80% | 60% |

**Claude is the outlier:** it respects deagentive grammar most (0–20% recovery on CA2/CA3 equivalents), while **Gemini recovers the agent in 100% of control cells** regardless of grammar. The aggregate 92%→72% gradient is real at the population level but **model-heterogeneous** — a follow-up should report per-model curves, not only pooled rates.

### 3. Passive echo — still zero in control

| Condition | yes_rate |
|-----------|----------|
| all five | **0%** |

Even without responsibility questions, models do not mirror passive/deagentive input. They either name the agent or discuss what to do in agent-neutral procedural terms — but never extend *došlo k nevydání* as the dominant voice.

### 4. VAR-A in control — same compromise dominance

| Condition | % compromise | % legal_challenge | % undecided |
|-----------|--------------|-------------------|-------------|
| agentive | 80% | 4% | 16% |
| participial_passive | 88% | 8% | 4% |
| reflexive_deagentive | 76% | 4% | 20% |
| decision_nominalization | 76% | 8% | 16% |
| bureaucratic_nominalization | 68% | **20%** | 12% |

Removing responsibility questions does not unlock obey/secret_bury (still 0%). Bureaucratic nominalization shows the highest legal_challenge rate (20%) — a weak hint that maximally defocused grammar may nudge toward formal/legal paths, but n=25 per cell.

### 5. Response length (control)

Medians 1.35–1.55k chars — slightly shorter than main study (no responsibility section to write). No grammar effect on length.

---

## Synthesis: what the two runs together show

### Revised headline (main + control)

1. **Explicit blame assignment is question-driven.** Ask *kdo nese odpovědnost* → 92–100% primary authority blame in every grammar condition. Don't ask → 5/125 coded blame mentions. The strong "no deflection" main-set result is **mostly an effect of the measurement**, not proof that models would naturally exonerate the institution.

2. **Spontaneous agent-naming is grammar-sensitive — but only without the forcing question.** Czech deagentive/nominalized grammar reduces `agent_recovery` by ~16–28 points (92% → ~72% pooled). The effect is **real, modest, and masked** when responsibility is explicitly solicited.

3. **Models are agent-restorers, not passive echoers.** 0% passive echo in both runs. Instruct models rewrite deagentive input into agentive analytic prose (or procedural recommendation) rather than extending the institutional defocusing register.

4. **The institution rarely gets off the hook even when grammar helps.** Floor recovery ~72%; world knowledge (*body not released after attack → someone decided*) and RLHF normalisation keep úřady/stát in frame most of the time.

5. **Recommendations are grammar-insensitive.** Compromise/negotiation dominates (68–88%); obey and secret_bury are never primary. Same structural rerouting as Phase 1.

### Hypotheses ranked (with current evidence)

| # | Hypothesis | Evidence |
|---|------------|----------|
| **1** | The responsibility question re-agentivises the scene | **Supported.** Control shows 5/125 blame vs 125/125; agent_recovery gradient appears only without the question. |
| **2** | World knowledge overrides surface syntax | **Supported.** Recovery floor ~72% even on maximally defocused CN5; pragmatic inference fills the agent gap. |
| **3** | Instruct-tuning normalises into agentive analytic prose | **Supported.** passive_echo = 0% everywhere; typical output: *Primární odpovědnost nesou úřady, které rozhodly…* |
| **4** | Ceiling effect on explicit blame (no room to move down) | **Supported in main set** — 92–100% primary leaves no headroom; grammar cannot reduce what is already saturated. |

---

## Interpretation for the Pergler framework

In human Czech discourse, agency management (passivisation, `se`-constructions, nominalizations like *došlo k nevydání*) helps institutions **background the actor** and diffuse responsibility. This pilot asks whether the same grammatical tools work on LLMs.

**Answer (qualified):**

- **On explicit blame assignment:** No. When asked directly, models blame the authorities at ceiling regardless of grammar. The manipulation and the measurement pull in opposite directions.
- **On spontaneous agent reference:** Partly. Deagentive grammar reduces — but does not eliminate — unprompted naming of úřady/stát. The effect size is ~20 percentage points, not a qualitative shift in blame target.
- **On register uptake:** No. Models do not reproduce the bureaucratic/defocused voice; they repair it.

This is a clean result the minimal-pair design was built to detect. The earlier cross-language Phase 2 Czech cells (C1–C5) could not have isolated it because they varied lexis, order, and question wording simultaneously.

---

## Coding verification

Seven agency columns filled by rule-based first pass (`coder_id = auto-cursor-2026-05`), then spot-checked against response texts.

| Column | Robustness | Notes |
|--------|------------|-------|
| `agent_recovery` | High | Lexical presence of úřady/stát/orgán as actor; spot-checks agreed. |
| `passive_echo` | High | Presence of agentless stimulus phrasing; 0% everywhere. |
| `authority_blame_score` | Medium — **recoded** | First pass required *primární/hlavní*; missed bare *Úřady nesou odpovědnost…*. Corrected rule: authority named as bearer of responsibility for non-burial in any phrasing. **90/125 rows changed** on recode. |
| `relative_blame_score` | Medium | Recomputed with authority; 0% primary on relative across all conditions. |
| `code_var_a`, `compromise_type`, `legalism_score`, `dignity_score` | Low — first pass only | Most in need of independent human coding. |

The headline (recovery ~100% main / gradient control, authority ceiling, passive_echo 0%) is **robust to the authority_blame recode**. If anything, corrected coding makes the ceiling flatter and the story cleaner.

---

## Caveats before any claim

1. **Native review** of five Czech prompts still pending (`draft_needs_native`); confirm only agency construction differs.
2. **Human re-coding** needed for `authority_blame_score`, `relative_blame_score`, `compromise_type`, `legalism_score`, `dignity_score`.
3. **qwen excluded** — 5 models, not 6; main run has 2 qwen error rows.
4. **Temperature 0.3** — replication at temperature 0 would test sampling robustness of agent-restoration.
5. **Single dilemma, single language** — no claim beyond this scenario.
6. **Model heterogeneity** — pooled rates hide Claude (grammar-sensitive) vs Gemini (always recovers) split; report per-model in any paper.
7. **Pilot n** — 25 cells per condition; exploratory, not confirmatory.

---

## Files and regeneration

| Artifact | Path |
|----------|------|
| Stimuli (main) | `stimuli.yaml` |
| Stimuli (control) | `stimuli_noq.yaml` |
| Readable prompts | `PROMPTS_CS.md` |
| Codebook | `codebook_agency.md` |
| Main run | `logs/phase3_20260529T112210Z_77ea6d3b/` |
| Control run | `logs/phase3_20260529T125836Z_6570a5fc/` |
| Main tables + charts | `output/` |
| Control tables + charts | `output_noq/` |
| Lovable payload (main) | `output/agency_analysis.json` |
| Lovable payload (control) | `output_noq/agency_analysis.json` |
| Lovable payload (combined) | `output/agency_comparison.json` |

```bash
# Re-analyze
python studies/czech_agency/analyze_study.py --run-dir studies/czech_agency/logs/phase3_20260529T112210Z_77ea6d3b
python studies/czech_agency/analyze_study.py --run-dir studies/czech_agency/logs/phase3_20260529T125836Z_6570a5fc --out-dir studies/czech_agency/output_noq

# Rebuild Lovable payloads (main + control + combined with findings)
python studies/czech_agency/build_agency_analysis.py --all

# Push runs + all three analysis rows to Lovable
python studies/czech_agency/push_study_to_lovable.py
```

| Lovable payload | Path | run_id |
|-----------------|------|--------|
| Main study | `output/agency_analysis.json` | `phase3_20260529T112210Z_77ea6d3b` |
| Control | `output_noq/agency_analysis.json` | `phase3_20260529T125836Z_6570a5fc` |
| **Combined (charts + findings)** | `output/agency_comparison.json` | `czech_agency_combined` |
