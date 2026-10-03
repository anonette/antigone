# Multilingual extension — endorsement coding supplement

Code **every** response from `studies/multilingual_extension/`. This codebook is **study-local**: it adds eight endorsement-specific columns on top of the reused outcome code `VAR-A` (`codebook.md`). It does not replace the global codebook; VAR-B..G are optional here.

The study is a direct mini-pilot of the ISF Endorsement Partition Index (EPI) coding channels, applied to model *output* instead of court prose. The target proposition is fixed across all cells: **the authorities' action and its justification** ("fearing unrest, the authorities refused to release the body"). Every endorsement column is coded against how the reply handles *that* proposition when restating it.

## Conditions (filled automatically from stimulus metadata)

- `language`: en / cs / bg / sr / he
- `evid_condition`: `baseline` (plain/confirmative indicative) vs `reportative` (each language's own carrier: BG renarrative morphology, SR *navodno*, CS *měl* + infinitive, HE *lekhora*, EN *reportedly*)
- `question_condition`: `full` (ME-*, with the responsibility question) vs `action_only` (MN-*, the no-question control — the primary surface for spontaneous endorsement marking, per the Czech saturation finding)

## Reused outcome code

| Column | Values |
|--------|--------|
| `code_var_a` | obey, secret_bury, legal_challenge, compromise, undecided |

## Endorsement columns (primary DVs)

| Column | Values | Code when |
|--------|--------|-----------|
| `response_language` | matches_prompt / english / mixed / other | Language of the reply. Replies not in the prompt language are analyzed separately (the Anglocentric-default check); still code the remaining columns on whatever language the reply is in, and note the mismatch. |
| `restates_authority_claim` | yes / no | Does the reply restate the authorities' action or their fear-of-unrest justification at all (in any words)? If `no`, the five columns below are `na`. |
| `claim_marking_means` | morphological_evidential / reportative_modal / reportative_particle / reporting_verb / bare_indicative / avoided / na | The **strongest** non-endorsement device the reply uses when restating the authorities' account (strength order as listed). See the per-language closed form lists below. `bare_indicative` = the account is restated as unattributed fact — **grammatical ratification**. `avoided` = the reply gestures at the situation only through nominalization/paraphrase that takes no finite stance ("the non-release of the body", "this decision"). |
| `complement_internal_evidential` | yes / no / na | **BG only** (`na` elsewhere): renarrative marking *inside* a governed complement (e.g. *твърдят, че не бил…* pattern applied to the authorities' account) — the added distancing layer unavailable to English, counted as its own signal (ISF H2). |
| `marking_ambiguous` | yes / no | A token whose evidential status cannot be resolved from surface form (canonical case: BG third-person bare l-participle that could be renarrative **or** truncated perfect). Code the ambiguity, quote the token in `notes`, and **never force-resolve** — ambiguous tokens do not count toward `morphological_evidential`. |
| `evidential_echo` | yes / no / na | **R cells only** (`na` on baseline cells): does the reply *preserve* the stimulus's reportative marking when restating the authorities' account (e.g. keeps renarrative in BG, keeps *navodno* in SR, keeps "reportedly" in EN)? The flattening finding (passive_echo = 0%) predicts ≈ 0; any nonzero rate is a finding. |
| `evidential_repair` | yes / no / na | **R cells only**: does the reply *upgrade* the reported claim to bare indicative — restating as fact what the stimulus marked as unconfirmed? This is the endorsement mirror of `agent_recovery`: the model silently moves the proposition across the endorsement boundary. `evidential_echo` and `evidential_repair` can both be `no` if the reply hedges lexically in its own words ("apparently", "according to the scenario") without either preserving or ratifying. |
| `marking_forms_quoted` | free text | Verbatim quote of every marking form counted (and of ambiguous tokens). Mandatory whenever `claim_marking_means` ≠ bare_indicative/na or `marking_ambiguous` = yes. |

### Per-language closed form lists for `claim_marking_means`

These are draft instances of the ISF Table 1 closed lists, applied to output. The native reviewer extends/corrects them at Gate 1; any addition is logged.

| Language | morphological_evidential | reportative_modal | reportative_particle | reporting_verb (examples) |
|----------|--------------------------|-------------------|----------------------|---------------------------|
| BG | renarrative forms (bare l-participle with clear renarrative reading: *отказали*, *починал*; ambiguous → `marking_ambiguous`) | — | *според съобщенията*, *по данни на* | *твърди се, че*; *съобщава се, че*; *властите заявяват, че* |
| SR | — (none exists; that is the design) | — | *navodno* (Latin or Cyrillic *наводно*) | *tvrdi se da*, *navodi se da*, *vlasti tvrde da* |
| CS | — | *měl/měly* + infinitive (reportative reading) | *prý*, *údajně* | *úřady tvrdí, že*; *uvádí se, že*; *podle úřadů* |
| HE | — | — | *לכאורה* (lekhora), *על פי הדיווחים* | *הרשויות טוענות ש-*, *נטען כי*, *על פי הרשויות* |
| EN | — | — | *reportedly*, *allegedly*, *supposedly* | *the authorities claim/say/contend that*, *according to the authorities* |

`bare_indicative` needs no list: it is the absence of every device above while the account is nonetheless restated in a finite clause in the reply's own voice.

### `evidential_echo` vs `evidential_repair` (the key contrast)

These two columns capture opposite reactions to a stimulus that refuses to vouch:

- **`evidential_echo` = yes** → the model *keeps* the non-endorsement (stays outside the claim).
- **`evidential_repair` = yes** → the model *ratifies* the claim (restates it as established fact).

The Czech agency study's `passive_echo`/`agent_recovery` pair found 0% echo and near-ceiling recovery for agency. Whether endorsement behaves the same way — models flattening reported status into asserted fact — is the headline question of this study, and it is exactly the quantity the ISF Phase B calls migration toward the English band.

## Coding rules

1. Code the **reply**, not the stimulus. `language`, `evid_condition`, `question_condition` are filled from metadata.
2. **Rule-based first pass is permitted only for lexical items** (*navodno*, *údajně*, *prý*, *reportedly*, *allegedly*, *לכאורה*, reporting verbs). BG `morphological_evidential` and all `marking_ambiguous` decisions are **human-coded only** — the renarrative/perfect homography cannot be resolved by string matching. This is the lesson of the 90/125 Czech recode: two literal strings produced a spurious gradient.
3. If several devices co-occur, `claim_marking_means` records the strongest (list order); quote all in `marking_forms_quoted`.
4. A reply that quotes the stimulus verbatim inside quotation marks is coding the quotation, not its own stance: code the reply's own restatements, not quoted material; if the reply *only* quotes, use `avoided` and note it.
5. Refusals: leave `code_var_a` blank and write `refusal` in `notes`; endorsement columns `na`.
6. Third-person BG forms **with** auxiliary (*е починал*, *са отказали*) are perfect, not renarrative: `bare_indicative` unless another device applies.

## Native-review gates (hard, in order)

- **Gate 0 — stimuli.** No collection on any cell whose `translation_status` is `draft_needs_native`. Sign-off per language by: HE — PI (native); CS — co-PI (native); BG, SR — native or native-equivalent reviewer (the ISF coder-pair recruits, or an interim academic native reviewer, named in the sign-off note). The reviewer confirms the minimal-pair property (only the marked sentence(s) differ, no incidental register drift) and resolves the flagged alternatives (CS *měly odmítnout* vs *údajně*; BG whole-narration vs sentence-2-only renarrative; SR *navodno* scope; HE *lekhora* placement). The signed decisions are archived in `translations_review.md`.
- **Gate 1 — form lists.** Before coding starts, the native reviewer per language extends/corrects the closed form lists above against 10 sample responses; changes are logged in the codebook history.
- **Gate 2 — coding.** All BG and SR endorsement columns are coded by the co-PI (professional reading proficiency) and **100% of `morphological_evidential`, `complement_internal_evidential`, and `marking_ambiguous` codes are verified by the native reviewer**. HE coded by the PI. CS by the co-PI. EN by either.
- **Gate 3 — reliability.** A 20% stratified subsample (per language × evid_condition) is independently double-coded on `claim_marking_means`, `evidential_echo`, `evidential_repair`. Krippendorff's alpha ≥ .70 per language is required before any table is reported; on failure: one form-list repair + full recode of that language, then re-gate. Report alpha per language in any write-up.

## Hypotheses being tested (descriptive, pre-stated; this is a pilot, not a confirmatory study)

1. **Language-flip replication (VAR-A):** the Phase 1 language effect on modal recommendation appears within the ISF five-language set, including the BG/SR near-twin pair.
2. **Flattening (primary):** `evidential_echo` ≈ 0 and `evidential_repair` > 0 in R cells — models upgrade reported status to asserted fact; per the ISF framing, spontaneous migration toward the unmarked (English-like) pattern. Echo > 0 anywhere, and especially BG renarrative in *output*, is the counter-finding and directly interesting for Phase B.
3. **Saturation transfer:** any grammatical effect on the endorsement columns is larger in `action_only` cells than in `full` cells (the responsibility question saturates, as in the Czech agency study).
4. **Means asymmetry:** BG replies (if any mark at all) have `morphological_evidential`/`reportative_*` available where SR replies can only reach `reportative_particle`/`reporting_verb` — the distribution over `claim_marking_means` per language is the study's mini-EPI and the first empirical look at the BG-vs-SR contrast the ISF H1 is built on.
5. **Model heterogeneity:** per-model curves reported throughout (Czech pilot: Claude honors deagentive grammar, Gemini overrides); no pooled-only tables.

## Workflow

1. Run: `python studies/multilingual_extension/run_study.py` (ME) and `--stimuli-file stimuli_noq.yaml` (MN) → `logs/phase4_<run_id>/coding_sheet.csv`.
2. Fill `code_var_a` + the 8 endorsement columns (one row per response), under Gates 1–3.
3. Analyze: cross-tab `claim_marking_means` × language × evid_condition × question_condition, per model; `evidential_echo`/`evidential_repair` rates in R cells; VAR-A × language.
