# Phase 1 v2 — model × model × language analysis

Run: `phase1_20260525T135121Z_eab51040` · 54 ok responses · 6 models × 3 languages × 3 replicates · temperature = 0.

Source data: `output/phase1_v2_cross/*.csv`.

---

## 1. Language → action (VAR-A) — pooled across 6 models

| Language | obey | compromise | legal_challenge | secret_bury | undecided |
|----------|------|------------|------------------|-------------|------------|
| **EN** | — | **50%** | 17% | — | **33%** |
| **CS** | 6% | **50%** | **44%** | — | — |
| **JA** | — | 6% | **72%** | 6% | 17% |

- **JA pulls hardest toward legal_challenge** (法的手段, 当局との対話) — 13 of 18 replies.
- **EN hedges most** (33% undecided — gemini and llama mostly refuse to rank).
- **CS** is balanced: half compromise (negotiation with úřady), half legal_challenge (vyčerpat legální cesty first).
- **Secret burial endorsed exactly once** (qwen JA r3, 密葬倫理的に正当化される).

## 2. Language → responsibility (VAR-B)

| Language | authorities | deceased | distributed | relative |
|----------|-------------|----------|-------------|----------|
| **EN** | 72% | **17%** (claude only) | 11% | — |
| **CS** | **72%** | — | 28% | — |
| **JA** | 50% | — | 39% | **11%** (llama only) |

- Claude in EN puts "the terrorist bears primary responsibility" — unique to that model+language.
- Japanese has the most **distributed** blame (社会全体・親族・当局 listed without ranking).
- Llama is the only one that codes JA as **relative-responsible** ("結果の責任は親族にある" twice).

## 3. Language → agency in reply (VAR-D)

| Language | institutional | individualized |
|----------|---------------|----------------|
| **EN** | **100%** | — |
| **CS** | **100%** | — |
| **JA** | 89% | 11% (llama only) |

- Almost universal institutional staging: replies frame **authorities** as the actor and **the relative** as moral chooser only.
- Llama JA shifts to individualized when it loses the institutional thread.

---

## 4. Model fingerprint across languages (modal VAR-A per cell)

| Model | EN | CS | JA | Consistent? |
|-------|------|------|------|-------------|
| **claude-sonnet-4** | compromise | legal_challenge | legal_challenge | ✗ EN diverges |
| **gemini-2.0-flash** | undecided | legal_challenge | legal_challenge | ✗ EN diverges |
| **gpt-4o** | compromise | compromise | legal_challenge | ✗ JA diverges |
| **llama-3.3-70b** | undecided | legal_challenge | undecided | ✗ CS diverges |
| **mistral-large-2411** | compromise | compromise | compromise | **✓ stable** |
| **qwen-2.5-72b** | legal_challenge | compromise | legal_challenge | ✗ CS diverges |

**Headline finding:** 5 of 6 models change their modal recommendation **just because the prompt language changed**, with identical facts. Only **mistral-large** is language-invariant.

This is direct evidence that **language alone — not framing — already moves the moral verdict**, which is the Phase 1 hypothesis.

---

## 5. Pairwise model agreement on VAR-A (9 cells per pair)

| Pair | agree | comment |
|------|-------|---------|
| gpt-4o ↔ mistralL | **0.78** | most aligned |
| claude4 ↔ gpt-4o | 0.67 | "compromise-leaning" cluster |
| claude4 ↔ gemini2 | 0.67 | |
| gemini2 ↔ llama3.3 | 0.67 | "undecided-leaning" cluster |
| median pair | ~0.33 | low overall |
| llama3.3 ↔ mistralL | **0.00** | total disagreement |
| llama3.3 ↔ gpt-4o | 0.11 | |
| llama3.3 ↔ qwen2.5 | 0.11 | |

- Two informal clusters: `{gpt-4o, mistral, claude}` (compromise-leaning) vs `{gemini, llama}` (undecided-leaning).
- **Llama is the outlier on every comparison** — partly because its degraded loops make codes brittle.
- Even the top pair (gpt-4o ↔ mistralL) only agrees 78% — **model identity is a stronger predictor of the verdict than language**.

## 6. Pairwise agreement on VAR-D

VAR-D is nearly invariant (institutional ≥ 89% in every cell), so all pairs agree at ≥ 0.89. **The "institutional staging" default is shared across models.** What differs is whether the model then *recommends* action against the institution (legal_challenge) or seeks *with* it (compromise) or refuses (undecided).

---

## 7. Replicate stability (3 reps at temp = 0)

For each (model, language) cell, how many distinct VAR-A codes appear across 3 replicates?

| Stable (1 unique) | Unstable (≥2 unique) |
|---|---|
| 14 cells | **4 cells** |

Unstable cells:

| Model | Language | Codes |
|-------|----------|-------|
| llama3.3 | cs | legal_challenge, **obey** |
| llama3.3 | ja | legal_challenge, undecided |
| mistral-large | ja | compromise, legal_challenge, undecided (3 distinct in 3 reps!) |
| qwen2.5 | ja | legal_challenge, secret_bury |

- Even at **temperature 0**, llama and mistral wobble across replicates — likely because of provider-side non-determinism on long generations.
- Mistral JA gave **3 different actions in 3 replicates** for the same prompt — strong instability.
- Claude/gpt-4o/gemini are perfectly stable across all 9 cells each.

---

## 8. Response length — model × language

Median response length (chars):

| | EN | CS | JA |
|--|----|----|----|
| **claude-sonnet-4** | 1,632 | 1,218 | **472** |
| **gemini-2.0-flash** | **4,520** | 3,384 | 1,298 |
| **gpt-4o** | 2,032 | 1,577 | 609 |
| **llama-3.3-70b** | 1,097* | **14,295†** | 5,414† |
| **mistral-large** | 2,777 | 1,794 | 866 |
| **qwen-2.5-72b** | 3,119 | 1,573 | 1,114 |

\* llama EN one rep blew up to 19,076 chars (the repeating "Have a great day!" loop).  
† llama CS/JA frequently looped into repeated paragraphs — visible as multi-thousand-char inflations.

Universal pattern: **EN > CS > JA** length. Japanese is consistently the most concise (Claude JA averages **472 chars** vs 1,632 in EN — ~3.5× shorter for the same content).

Caveat: Llama length is unreliable because of looping; treat as ≥ that floor of "actual" reasoning length.

---

## 9. Japanese register mirroring (VAR-R)

| flattens_neutral | mirrors_register | mirrors_evidential | mirrors_aspect |
|------------------|------------------|---------------------|-----------------|
| **18 / 18** | 0 | 0 | 0 |

**Every JA response flattens to neutral analyst Japanese** (である調 / 〜ます expository), regardless of the prompt being neutral baseline P1-JA. Models do not extend the prompt's stance into the reply.

This is the **flattening hypothesis** in its clearest form: even when given neutral input, no model picks up Japanese stance/evidential markers.

(More interesting result will come from Phase 2 J3/J4/J5/J9 — does anyone mirror 私たち家族 / ようだね / とのこと?)

---

## 10. Headline takeaways

1. **Language shifts the verdict in 5 of 6 models** — the most basic Phase 1 effect is real.
2. **Mistral-large is the language-invariant outlier** — compromise everywhere; lowest sensitivity to language.
3. **Models cluster into two camps**: compromise-leaners (gpt-4o, mistralL, claude) and undecided-leaners (gemini, llama). Qwen is the only model that endorses secret_bury (once).
4. **Institutional staging is shared** — VAR-D is institutional ≥ 89% across every cell; what differs is the **recommended action against institutions** (legal_challenge / compromise / refusal).
5. **JA flattens stance 100%** — no model picks up Japanese register markers. This is the baseline for Phase 2 framing tests.
6. **Llama is unstable** (looping, replicate divergence) — code with caution; consider dropping or rerunning.
7. **Claude EN is unique in blaming the deceased terrorist** as primary cause — no other model in any language does this.
8. **Response length: EN > CS > JA**, ~3-4× factor — Japanese replies are the most compact even at fixed prompts.

---

## Files

| | |
|---|---|
| `language_by_var_{a,b,d,r}.csv` | language-pooled counts and percentages |
| `model_by_var_{a,b,d}.csv` | model-pooled counts |
| `model_x_lang_var_{a,b,d}.csv` | 3-way model × language × code |
| `replicate_stability_var_{a,d}.csv` | within-cell variance across replicates |
| `cross_lang_var_{a,d}.csv` | per-model modal code across languages |
| `pairwise_agreement_var_{a,d}.csv` | model-pair agreement rates |
| `response_length.csv` | char-length descriptives |
| **`ANALYSIS_REPORT.md`** | this document |

Regenerate: `python scripts/phase1_cross_analysis.py`.
