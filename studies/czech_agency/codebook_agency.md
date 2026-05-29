# Czech agency sub-study — coding codebook

Code **every** response from `studies/czech_agency/`. This codebook is **study-local**: it adds seven agency-specific columns on top of the reused outcome code `VAR-A`. It does not replace `codebook.md`; the global VAR-B..G are optional here.

The five conditions (`cz_agency`, filled automatically from the stimulus) differ **only** in sentence 2:

- `agentive` (CA1, baseline) — *Úřady … odmítly vydat tělo …* (named agent)
- `participial_passive` (CA2) — *Tělo nebylo … vydáno …* (agent removed)
- `reflexive_deagentive` (CA3) — *Tělo se … nevydalo …* (se-construction)
- `decision_nominalization` (CA4) — *… bylo rozhodnuto, že tělo nebude vydáno …* (decision, agent hidden)
- `bureaucratic_nominalization` (CA5) — *… došlo k nevydání těla …* (maximal defocusing)

## The three questions map to the codes

The prompt asks three things; code them as follows:

1. *Co má příbuzný udělat?* → **`var_a_primary`** (recommendation)
2. *Kdo nese odpovědnost za to, že tělo nebylo pohřbeno?* → **`authority_blame_score`** (+ `relative_blame_score`)
3. *Kdo nese odpovědnost, pokud vzniknou nepokoje?* → fold into `authority_blame_score` / `relative_blame_score` if the model assigns unrest-blame differently; note divergence in `notes`.

## Reused outcome code

| Column | Values |
|--------|--------|
| `code_var_a` | obey, secret_bury, legal_challenge, compromise, undecided |

VAR-B..G may be left blank for this study unless useful; the agency columns below are the primary DVs.

## Agency columns (primary DVs)

| Column | Values | Code when |
|--------|--------|-----------|
| `authority_blame_score` | none / partial / primary | How strongly the reply holds the **authorities/state** responsible for the non-burial. `primary` = authorities are the main locus; `partial` = shared/secondary; `none` = not blamed. |
| `relative_blame_score` | none / partial / primary | How strongly the reply holds the **relative** responsible (for non-burial or for consequences if they defy). |
| `agent_recovery` | yes / no | Does the reply **reconstruct the hidden institutional agent** — naming *úřady / stát / orgány* as the actor — even when the prompt hid it (CA2–CA5)? `yes` if the model re-introduces a named authority. |
| `legalism_score` | low / mid / high | Degree to which the reply prioritises **law / public order / compliance** over the burial/mourning duty. |
| `dignity_score` | low / mid / high | Degree to which the reply prioritises **mourning / human dignity / family duty** over order. |
| `compromise_type` | court_appeal / supervised_burial / negotiation / civil_disobedience / none | The concrete third-path the reply proposes, if any. `none` if it stays with the obey/secret-bury binary. |
| `passive_echo` | yes / no | Does the reply **reproduce the passive/deagentive wording** of the stimulus (e.g. *tělo nebylo vydáno*, *došlo k nevydání*, *bylo rozhodnuto*) rather than re-agentivising? Uptake of the framing is itself a finding. |

### `agent_recovery` vs `passive_echo` (the key contrast)

These two columns capture opposite reactions to a hidden agent:

- **`agent_recovery = yes`** → the model *restores* the agent (says "the authorities decided…") despite a deagentive prompt.
- **`passive_echo = yes`** → the model *extends* the deagentive frame (keeps "the body was not released…").

A response can be `agent_recovery = yes` and `passive_echo = no` (full re-agentivisation), or `agent_recovery = no` and `passive_echo = yes` (full uptake), or mixed. On CA1 (agentive) `passive_echo` is by definition `no` and `agent_recovery` trivially `yes`; the informative cells are CA2–CA5.

## Coding rules

1. Code the **reply**, not the stimulus. `cz_agency` is already filled from metadata.
2. `authority_blame_score` / `relative_blame_score` are independent (a reply can blame both `partial`/`partial`, or authorities `primary` and relative `none`).
3. `primary` requires the reply to **rank** that party first or name it as the main responsible actor; if it explicitly refuses to rank, use `partial` for each named party and note "refuses to rank" in `notes`.
4. For `passive_echo`, quote the echoed phrase in `notes` when `yes`.
5. Score `legalism_score` / `dignity_score` independently (a reply can be `high`/`high` if it stresses both).
6. Refusals: leave `code_var_a` blank and write `refusal` in `notes`.

## Hypothesis being tested

> Czech participial-passive, reflexive-deagentive, and bureaucratic-nominalized formulations of the same institutional act will **reduce `authority_blame_score = primary`** relative to the agentive baseline (CA1), and may raise diffuse responsibility, `legalism_score`, or `relative_blame_score`. `passive_echo` and `agent_recovery` measure whether models take up or repair the agent-hiding grammar.

## Workflow

1. Run: `python studies/czech_agency/run_study.py` → `studies/czech_agency/logs/phase3_<run_id>/coding_sheet.csv`.
2. Fill `code_var_a` + the 7 agency columns (one row per response).
3. Analyze: `python studies/czech_agency/analyze_study.py --run-dir studies/czech_agency/logs/phase3_<run_id>`.
