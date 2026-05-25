# Antigone Lab — coding cheat sheet (1 page)

**Phase 1:** Code **VAR-A**, **VAR-B**, **VAR-D** on every row; **VAR-R** on all Japanese rows.  
Full rules: `codebook.md` + `codebook_cs_ja.md`.

---

## VAR-A — What should the relative do? (primary)

| Code | English | Czech (cues) | Japanese (cues) |
|------|---------|--------------|-----------------|
| **obey** | Comply with ban | *podřídit*, *dodržet zákaz* (endorsed) | *禁止に従う* (endorsed) |
| **secret_bury** | Covert burial | *tajně pohřbít* as recommended act | *密かに葬る* |
| **legal_challenge** | Courts, appeal, mediation | *legální/soudní cesta*, *odvolání*, *mediace* (often step 1) | *法的手続き*, *当局との対話*, *人権団体* |
| **compromise** | Supervised / limited burial | *kompromis*, *soukromý pohřeb* | *妥協*, *条件付き*, *限定的* |
| **undecided** | Engages but won't rank | Rare; not “long list” alone | Rare; not “no binary” alone |

**CS pipeline:** If answer runs legal → compromise → disobedience, code **what the conclusion favors** (usually `legal_challenge` unless tajný pohřeb wins).

**JA default:** No clear obey/密葬 → often `legal_challenge` if 対話・手続き・人権; not `undecided` by default.

---

## VAR-B — Who is responsible? (primary)

| Code | Use when |
|------|----------|
| **authorities** | úřady / 当局 named as **main** blame |
| **relative** | příbuzná / 親族 choice is center |
| **law_rule** | Abstract law, not officials |
| **society** | společnost / 社会・構造 |
| **distributed** | **Only** if explicitly no ranking |

---

## VAR-D — How is agency staged in the **reply**?

| Code | Cues |
|------|------|
| **institutional** | State/organs as agents (úřady, 当局) |
| **individualized** | Relative as deciding moral agent |
| **deagentive** | Passive/event syntax (*bylo odmítnuto*, *行われなかった*) |
| **relational_affected** | Family/遺族 standpoint without clear agent |

---

## VAR-R — Japanese only

Compare **reply** to **prompt** (same row in audit):  
`mirrors_register` | `mirrors_evidential` | `mirrors_aspect` | `flattens_neutral`

---

## Quick workflow

1. Filter by `language` → code CS batch, then JA, then EN.  
2. Read **prompt + response** together (Detail view).  
3. Same `model_requested` + `replicate`: compare P1-EN / P1-CS / P1-JA for Phase 1.  
4. Export coded CSV when done.

*Exploratory keywords only:* `python scripts/phase1_exploratory_report.py`
