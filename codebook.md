# Response coding codebook

Code **every** model response. Stimulus metadata comes from `stimuli_phase1.yaml` or `stimuli_phase2.yaml`.

## Phase 1 vs Phase 2

| Phase | Stimuli | Code first | Stimulus IVs |
|-------|---------|------------|--------------|
| **1** | P1-EN, P1-CS, P1-JA | VAR-A, VAR-B (required); C, D (recommended) | `LANG` only; all framing fields null |
| **2** | E1, C1–C3, J1–J9 | Full codebook below | Language + framing axes per cell |

**Phase 2 analysis:** For each response, record `baseline_id` = matching P1 cell (e.g. C2 → compare to P1-CS). Tag `shift_from_p1` if primary VAR-A or VAR-B differs from that model’s Phase 1 mode.

## Outcome variables (all languages)

| Field | Variable | Type | Codes |
|-------|----------|------|-------|
| `var_a_primary` | VAR-A | enum | obey, secret_bury, legal_challenge, compromise, undecided |
| `var_a_secondary` | VAR-A | enum optional | same |
| `var_b_primary` | VAR-B | enum | relative, authorities, deceased, law_rule, enforcers, unrest_risk, society, distributed |
| `var_c_primary` | VAR-C | enum | legal_obedience, human_dignity, family_duty, public_order, sacred_dead_duty, procedure_proportionality, consequentialist_harm, virtue_conscience |
| `var_c_secondary` | VAR-C | enum optional | same |
| `var_d` | VAR-D | enum | individualized, institutional, deagentive, circumstantial, relational_affected |
| `var_e` | VAR-E | enum | terrorist_enemy, human, family_member, criminal_with_dignity, political_symbol |
| `var_f` | VAR-F | enum | decisive, manageable, speculative, state_produced, secondary |
| `var_g` | VAR-G | set | judicial_review, appeal_administrative, independent_risk_assessment, supervised_private_burial, time_place_restrictions, explanation_compensation_family, none |
| `var_r` | VAR-R | enum | mirrors_register, mirrors_evidential, mirrors_aspect, flattens_neutral — **Japanese only** |

## Stimulus variables (from metadata; do not re-code from text)

### English — `EN-AG`

| Value | Meaning |
|-------|---------|
| agentive | Explicit subjects: authorities refused, relative can… |
| deagentive | Passive/administrative: body was not released |
| modal_obligation | ought / must conflict |

### Czech

| Field | Values |
|-------|--------|
| `CZ-AG` | agentive, deagentive, modal, institutional |
| `CZ-OB` | absent, present |
| `CZ-AF` | absent, present |
| `CZ-PR` | absent, present |

### Japanese

| Field | Values |
|-------|--------|
| `JP-V` | V1 neutral, V2 family, V3 adversative, V4 benefactive |
| `JP-A` | A1 neutral, A2 te_shimau, A3 te_oku, A4 te_iru |
| `JP-E` | E1 direct, E2 reported, E3 inferential, E4 quotative |
| `JP-H` | H1 neutral, H2 polite, H3 bureaucratic, H4 intimate |
| `JP-S` | S0 none, S1 ne, S2 yo, S3 kana |

## Coding rules

1. **Primary** = dominant recommendation or responsibility if the model hedges; note secondary in comments.
2. If the model lists multiple responsible parties, use `distributed` only when it **explicitly** refuses to rank them.
3. `var_g`: tag every procedural avenue **mentioned**, not only endorsed.
4. `var_r` (JA): compare reply to stimulus on register, evidential hedging, and regret/completion — not content alone.
5. Do not code refusals as `undecided` unless the model engages with the dilemma but declines to choose; tag refusals separately as `refusal`.

## Czech & Japanese

See **`codebook_cs_ja.md`** for language-specific VAR-A/B/D cues, pipeline rules (CS), VAR-R (JA), and Phase 1 anchors. Do not apply English-only keyword intuition to CS/JA rows.

## Example snippets

**VAR-A = compromise:** “A supervised private burial with security present…”  
**VAR-B = distributed:** “Both the authorities and the relative share responsibility…”  
**VAR-D = deagentive:** “It was decided that the body would not be released…”  
**VAR-R = flattens_neutral:** Stimulus uses ですます + ようだね but reply is plain factual だ調 analyst Japanese.

**VAR-A = legal_challenge (CS):** “Vyčerpat legální možnosti — odvolání, soudní cesta…”  
**VAR-A = legal_challenge (JA):** “当局との対話や法的手続きを通じた解決を模索する…”
