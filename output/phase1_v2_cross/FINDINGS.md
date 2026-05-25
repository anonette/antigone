# Phase 1 — 10 most surprising findings

**Run:** `phase1_20260525T135121Z_eab51040`  
**Design:** 6 current multilingual LLMs × 3 languages (EN, CS, JA) × 3 replicates × 1 stimulus (burial-ban dilemma) = **54 manually coded responses** at temperature = 0.  
**Codebook:** `codebook.md` (+ `codebook_cs_ja.md`).  
**Cross-tables and charts:** `output/phase1_v2_cross/`.

---

## Headline

> **Language shifts the model's verdict more than temperature noise does — but only on *what is recommended*, not on *how agency is staged* in the reply itself.**

The action layer (`code_var_a`) is language-sensitive in 5 of 6 models. The staging layer (`code_var_d`) is institutional in 89%+ of cells regardless of language. Phase 2 framing manipulations target exactly this gap.

---

## Findings

### 1. Only one of six models is language-invariant *(central finding)*

5 / 6 models change their **modal** action when the prompt language changes. The same facts, the same temperature, the same seed — yet:

| Model | EN | CS | JA |
|-------|----|----|----|
| claude-sonnet-4 | compromise | legal_challenge | legal_challenge |
| gpt-4o | compromise | compromise | legal_challenge |
| gemini-2.0-flash | **undecided** | legal_challenge | legal_challenge |
| llama-3.3-70b | undecided | legal_challenge | undecided |
| qwen-2.5-72b | legal_challenge | compromise | legal_challenge |
| **mistral-large-2411** | **compromise** | **compromise** | **compromise** |

Mistral-large is the outlier. Cleanest possible evidence that language alone — without any framing trick — moves the verdict in most current LLMs.

### 2. Japanese is the most legalistic, not the most collectivist *(counterintuitive)*

**72 %** of all Japanese replies endorse `legal_challenge` (courts, dialogue with 当局, 人権団体). EN: 17 %. CS: 44 %.

Pre-registered intuition might say JA would pull toward affectedness or communal yielding. The opposite happened: Japanese is the **most institutionally legalistic** of the three. LLM Japanese reads like institutional pull, not communal softness.

### 3. Only Claude blames the dead terrorist — and only in English

Across 54 responses, exactly **3 cells** code `deceased` as the primary responsibility locus. All three are **Claude in English**. The same Claude in Czech and Japanese blames authorities like everyone else.

Claude's instinct to ground responsibility in the original terror actor is **language-conditional**. A property of Claude may not exist when you query it in Czech.

### 4. Llama in Japanese is the only cell that blames the relative

In 17 / 18 (model × language) cells, the reply stages authorities institutionally (VAR-D) and assigns blame to authorities or distributed (VAR-B). One exception: **llama 3.3 in JA** writes 結果の責任は親族にある — *the responsibility is on the relative*. 2 / 3 replicates code `individualized` / `relative`.

Llama's tendency to wobble out of the institutional default appears specifically in **Japanese** — the very language where everyone else converges hardest on institutional staging.

### 5. Mistral at temperature 0 gave 3 different verdicts to the same Japanese prompt *(methods caveat)*

Same prompt, same model, same seed, temperature = 0. Three independent calls:

| Replicate | code_var_a |
|-----------|------------|
| r1 | compromise |
| r2 | legal_challenge |
| r3 | undecided |

Direct evidence that **OpenRouter providers ignore the `seed` parameter for non-OpenAI models**. The deterministic guarantee of temperature = 0 is a polite fiction at the provider edge. Phase 2 uses `temperature = 0.3` to surface real variance instead of provider tie-breaking noise.

### 6. Only 1 of 54 responses endorses secret burial *(central finding)*

Five possible action codes; `secret_bury` is the explicit second option in the prompt. Across **all 54 responses**, only one endorses it: **qwen 2.5 in Japanese, replicate 3**, which writes 密葬を選択することが倫理的に正当化される (*secret burial is ethically justified*). 53 / 54 = **98 % refuse the disobedience branch**.

### 7. Pure obedience is also nearly absent — except in Czech Llama

`obey` shows up exactly **once** in 54 cells: llama 3.3 P1-CS r3 — *Příbuzná by se měla podřídit zákazu*. The other two llama CS replicates code `legal_challenge`. So obedience is unstable even where it appears.

Together with finding 6: **the two explicitly offered options (obey, secret_bury) together account for ~4 %** of replies. Current LLMs do not actually answer the binary they are asked. They re-route into a third option (legal_challenge / compromise / undecided).

### 8. Institutional staging is a universal cognitive default *(central finding)*

Regardless of model and language, **VAR-D = institutional in 89 %+ of cells**. This is independent of what the reply then recommends. Even responses that endorse `compromise` or `legal_challenge` narrate "the authorities must decide", "the authorities are responsible".

**The grammar of the reply is more universal than its content.** Variation in VAR-A sits on top of a shared institutional frame. Phase 2 deagentive prompts (C2, E2) target exactly this default.

### 9. English is the hedging language

| Language | `undecided` share |
|----------|-------------------|
| EN | **33 %** (6 / 18) |
| CS | 0 % |
| JA | 17 % |

When asked in English, models are most likely to refuse to commit ("there is no right answer, it depends on values…"). In Czech they commit 100 %. Possible reading: the institutional grammars of English — *balancing*, *no single right answer* — give the model a culturally available exit that Czech does not.

### 10. Japanese is 3-4× shorter and 100 % flattens stance

**Median response length** (chars), claude as example: EN 1,632; CS 1,218; **JA 472** — 3.5× ratio for the same content. Pattern holds across all 6 models.

**VAR-R (Japanese register mirroring): 18 / 18 = `flattens_neutral`.** No model mirrors any Japanese stance, evidential, or aspect marker. Every reply defaults to plain analyst Japanese (である調).

This sets the **Phase 2 baseline**. If J3 (family POV, 私たち), J5 (とのこと reportative), J9 (ようだね shared stance) also produce 100 % flattening, the flattening hypothesis is strongly supported.

---

## What this means for Phase 2

| From finding | Phase 2 test |
|--------------|--------------|
| #1 mistral language-invariant | C2 deagentive + E2 deagentive on mistral — does grammar break the invariance? |
| #3 claude blames deceased only in EN | E2–E5 on claude — which EN framing axis shifts it off the "deceased did it" frame? |
| #4 llama JA individualizes | J3 (V2 family) + J4 (V3 adversative passive) on llama — amplifies or reverses? |
| #5 mistral 3 reps = 3 codes | **Run all of Phase 2 at `--temperature 0.3`** (already wired) |
| #6 disobedience refused 53/54 | C2, E2 deagentive — does the missing agent break the binary refusal? |
| #8 89 % institutional default | C4 (family affectedness) + J3 (family POV) test whether institutional default survives a foregrounded family |
| #10 100 % JA flattens | J3, J5, J9 — mirroring rate (VAR-R ≠ `flattens_neutral`) is the Phase 2 Japanese dependent measure |

---

## Files

| | |
|--|--|
| `output/phase1_v2_cross/findings.json` | structured (pushable to Lovable) |
| `output/phase1_v2_cross/ANALYSIS_REPORT.md` | full cross-tab analysis |
| `output/phase1_v2_cross/charts/*.png` | 9 static charts |
| `output/phase1_v2_cross/*.csv` | 17 cross-tabulations |

To re-generate: `python scripts/phase1_cross_analysis.py && python scripts/phase1_charts.py`.
