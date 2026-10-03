# Kripke reference sub-study: Gödel and Jonah cases across models and languages

> **Independent study.** Adapts the experimental design of Machery, Mallon, Nichols and Stich (2004), "Semantics, cross-cultural style" (*Cognition* 92, B1–B12), to large language models. It shares the Antigone engine (stateless calls, deterministic seeds, RunLogger schema) but nothing else: different vignettes, different dependent variable, different codebook. Never pool its numbers with Phase 1, the Czech agency study, or the multilingual extension.

## 1. Why this study

Machery et al. gave Kripke's Gödel case to undergraduates in New Jersey and Hong Kong and asked whom a speaker refers to when a proper name's associated description turns out to fit someone else. The two groups answered differently: most Americans gave the causal-historical answer (the name stays with the person it was originally attached to), most Hong Kong participants the descriptivist answer (the name goes to whoever fits the description). The finding launched experimental philosophy of reference and has been replicated, contested, and refined for twenty years.

Three features of that literature make it a natural instrument for the deixis programme:

1. **The human data confounded language and culture.** The 2004 Hong Kong participants read the vignettes in English. Lam (2010) ran them in Cantonese and did not find the effect; Sytsma, Livengood, Sato and Oguchi (2015) ran them in Japanese and did. Whether the effect lives in the language of the vignette or in the culture of the reader was never cleanly separated in humans. With a model, language of the prompt can be varied while everything else is held fixed, and "culture" becomes the model's training distribution, which is itself a variable across models.
2. **Reference is the mildest form of the deixis question.** A proper name has a description or a causal chain to anchor it. Deictic words have neither. If models already split on how a name is anchored, the Antigone results on who "the authorities" are, and on who "I" is, sit on a documented continuum rather than standing alone.
3. **The probe is forced-choice.** Unlike the burial dilemma, the dependent variable is a two-way answer that needs almost no coding. This makes it the cheapest cross-language, cross-model design in the repository and a good calibration study for the others.

## 2. Research questions and hypotheses

**RQ1 (language).** Does the language of the vignette shift a model's reference judgment, holding the model constant?
H1: Yes. Prompt language changes the descriptivist share for at least some models, replicating the Phase 1 pattern (language alone moves the verdict) on a different task.

**RQ2 (model).** Do models differ in their default reference theory, holding language constant?
H2: Yes, and the differences are larger than the language effect, as in the Czech agency study.

**RQ3 (Machery replication).** Do models trained predominantly on English text give the causal-historical answer in English, and does the descriptivist share rise in languages of the cultures where humans gave descriptivist answers (Japanese; Chinese if added)?
H3 (weak): Any model × language cell that departs from the near-unanimous causal-historical answer of Western philosophers is evidence that the "Kripkean intuition" is not a fixed property of the case. H3 (strong, exploratory): the descriptivist share is higher in Japanese and Chinese prompts than in English prompts for the same model.

**RQ4 (question format).** Does the effect survive the two format corrections from the later literature?
Sytsma and Livengood (2011) showed the original question is ambiguous between the narrator's and the speaker's perspective; Machery, Olivola and de Blanc (2009) reran it as a truth-value judgment. H4: the format shifts the absolute descriptivist share but not the language and model differences.

**RQ5 (deixis, Phase 2).** Does moving the question into first person ("When I use the name...") change the answer? This is the bridge to the LLMsDeixis framings and is run only after RQ1–RQ4 are stable.

## 3. Design

### 3.1 Factors

| Factor | Levels | Notes |
|---|---|---|
| Case | Gödel, Jonah | Machery et al.'s two probes. Gödel tests a description that fits someone else; Jonah tests a description that fits nobody. |
| Name variant | Western, local | The 2004 study used culturally neutral versions for Hong Kong (Tsu Ch'ung Chih, Chan Wai Man). We keep one Western and one locally plausible name per language so name familiarity is separable from language. |
| Language | en, cs, ja (+ zh-Hant, he optional) | en and cs anchor to the rest of the repository; ja is the language of the 2015 replication; zh-Hant is the original Hong Kong population; he mirrors the ISF language set. |
| Question format | reference (original), speaker-intent (Sytsma and Livengood), truth-value (Machery et al. 2009) | Three framings of the same probe. |
| Model | `current_multilingual` group | Gemini 2.0 Flash and Mistral Large 2411 no longer resolve on OpenRouter (404, 2026-09-07); replace in `config/models.yaml` before running. |
| Replicate | 10 | Temperature 0.7. The dependent variable is a proportion per cell, the model analogue of a population intuition, so replicates are the sample. Temperature 0 would collapse the cell to one vote and is used only for a determinism-labelled robustness run. |

Full matrix: 2 cases × 2 names × 3 formats × 3 languages = 36 cells per model. With 6 models and 10 replicates that is 2,160 calls. Responses are short, so the cost is on the order of 5 to 10 dollars.

### 3.2 Stimulus discipline

- Vignette text is a faithful rendering of Machery et al. 2004 (Appendix), with the name substituted per variant. Nothing else changes between name variants.
- Across languages, prompts are semantic parallels; all non-English cells start as `draft_needs_native` and the runner refuses them until a native speaker signs off (Gate 0, same rule as the multilingual extension).
- The prompt contains only the vignette and the question. No system prompt, no answer-format instruction beyond the two lettered options, no request to justify. Models often justify anyway; that text is coded, not solicited.
- Option order is counterbalanced: each cell exists in an A-first and a B-first version, so a position bias cannot masquerade as a theory of reference. This doubles the matrix; run the counterbalanced pair with half the replicates each.

### 3.3 Dependent variables

Primary: `ref_choice` ∈ {descriptivist, causal_historical, refuses, both, unclear}, parsed from the lettered answer and checked against the justification. Secondary (codebook_reference.md): `justification_type`, `hedging`, `response_language`, `mentions_theory` (whether the model names Kripke, descriptivism, or the thought experiment, which would indicate recall of the philosophy literature rather than a judgment).

### 3.4 Analysis plan

Per cell: descriptivist share with a Wilson interval. Then a logistic model of `ref_choice` on language, model, case, name variant, format, and the language × model interaction, with replicate as the unit. Report effect sizes as differences in descriptivist share, in percentage points, exactly as the Czech agency chart does. Human reference points from the literature go on the same axis: Machery et al. 2004 (Gödel case: about 58 percent causal-historical for Americans, about 32 percent for Hong Kong participants), Sytsma et al. 2015 for Japanese.

Pre-stated decision rules:

- H1 is supported if, for at least two models, the descriptivist share differs by 20 points or more between two languages with non-overlapping Wilson intervals.
- H2 is supported if the between-model range at fixed language exceeds the between-language range at fixed model.
- `mentions_theory` above 30 percent in a cell flags that cell as contaminated by recall; report it separately and do not count it toward H1–H3.

### 3.5 What would falsify the deixis reading

If every model gives the causal-historical answer at 90 percent or more in every language and format, reference is anchored for these models in a way that does not depend on language, and the deixis argument must rest on the Antigone results alone. That is a legitimate outcome and should be reported as such.

## 4. Limitations known in advance

- Models may have read Kripke, Machery et al., and the replication literature. `mentions_theory` measures this, but silent recall cannot be excluded. The Jonah case and the local-name variants are less likely to be memorized than the Gödel case.
- A proportion over 10 samples at temperature 0.7 is a property of a sampling distribution, not of a population of judges. Say so in every table.
- The translations must preserve the one feature the case depends on: that the description ("the man who proved the incompleteness theorem") is the only thing the speaker knows about the name's bearer. Native review should check this specifically.
- The chart of humans versus models is a comparison of two different kinds of number; label it as illustrative.

## 5. Files

```
studies/kripke_reference/
├── README.md                     this document
├── stimuli.yaml                  36 cells × 2 option orders; en source, cs/ja draft_needs_native
├── codebook_reference.md         dependent variables, parsing rules, gates
├── run_study.py                  stateless runner (reuses the Antigone engine; enforces Gate 0)
├── analyze_study.py              parses ref_choice, tabulates by language × model × case × format
├── data/kripke_reference_codes.template.csv
├── logs/                         phase5_<run_id>/ (created on run)
└── output/                       CSV tables + charts (created on analyze)
```

## 6. Commands

```bash
# Gate 0: the runner refuses draft_needs_native cells.
# English-only smoke test (the only sanctioned use of the bypass):
python studies/kripke_reference/run_study.py --language en --replicates 2 --models openai/gpt-4o --allow-draft-translations

# Full English collection (36/3 = 12 cells × 2 orders × 6 models × 5 reps per order = 720 calls)
python studies/kripke_reference/run_study.py --language en --replicates 5

# After native sign-off, add cs and ja
python studies/kripke_reference/run_study.py --language cs ja --replicates 5

# Analyse
python studies/kripke_reference/analyze_study.py --run-dir studies/kripke_reference/logs/phase5_<run_id>
```

## 7. References

- Machery, E., Mallon, R., Nichols, S., & Stich, S. P. (2004). Semantics, cross-cultural style. *Cognition*, 92(3), B1–B12.
- Machery, E., Olivola, C. Y., & de Blanc, M. (2009). Linguistic and metalinguistic intuitions in the philosophy of language. *Analysis*, 69(4), 689–694.
- Sytsma, J., & Livengood, J. (2011). A new perspective concerning experiments on semantic intuitions. *Australasian Journal of Philosophy*, 89(2), 315–332.
- Sytsma, J., Livengood, J., Sato, R., & Oguchi, M. (2015). Reference in the land of the rising sun. *Review of Philosophy and Psychology*, 6(2), 213–230.
- Lam, B. (2010). Are Cantonese-speakers really descriptivists? *Cognition*, 115(2), 320–329.
- Kripke, S. (1980). *Naming and Necessity*. Harvard University Press.
