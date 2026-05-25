# Research question and operationalization

## Burial-ban dilemma across Czech, Japanese, and English

**Working title:** *Institutional grammars of responsibility: multilingual LLMs as experimental theatres of agency*

---

## 1. What this project is not

This study does **not** ask whether “language affects moral reasoning” in a general sense. That claim is already familiar from bilingual cognition, typological semantics, and cross-cultural ethics.

It also does **not** treat the LLM as:

- a **moral authority** (source of the “right” answer),
- a **translator** (neutral carrier of propositional content), or
- a **survey respondent** with stable preferences.

The model is treated instead as a **staging device**: a system that, in responding, must assign positions in a scene—who acts, who suffers, who decides, what counts as harm, and where responsibility settles.

---

## 2. Central research question

### Primary formulation (project default)

> **How does each language shape who acts, who is blamed, and what is recommended — before the model gives a clear answer?**

- **Who acts** — agency in the reply (VAR-D; who is named as doing or deciding).
- **Who is blamed** — responsibility locus (VAR-B).
- **What is recommended** — staged action (VAR-A: obey, secret bury, legal challenge, compromise, undecided).
- **Before a clear answer** — grammar and register in the prompt already steer the scene, not only the final line of advice.

### Earlier formal variant (optional in papers)

> **What does a language make an LLM do with responsibility before the model knows it is making a moral judgment?**

Same intent as the primary formulation; “moral judgment” here means an explicit recommendation, not model consciousness.

### Full formulation (for proposals and papers)

> **This project asks whether large language models can be used as experimental theatres for institutional grammars of responsibility. The same ethical dilemma—denial of burial after a terrorist attack, with a relative choosing obedience or covert burial—is reformulated in Czech, Japanese, and English, with controlled variation in deagentive, perspectival, evidential, and administrative forms. The aim is not to determine the morally correct answer, but to observe whether each language preserves its own ways of staging agency, or whether the model silently re-enacts a default grammar in which ethical problems become individual choices under risk.**

### Sharper variant (problem constitution)

> **When an ethical dilemma is reformulated across languages, does the LLM solve the same problem—or does each language make a different problem appear?**

The claim is stronger than “translation changes wording.” **The dilemma is not fully prior to language.** Czech impersonal passives, Japanese viewpoint and stance marking, and English agentive syntax do not merely describe one situation; they help constitute what counts as action, omission, duty, harm, and responsibility.

### Deixis / theatrical formulation

> **This project treats LLMs as deixis machines: systems that do not only answer ethical dilemmas, but assign positions in a scene—speaker, actor, sufferer, official, mourner, rule, or mere site of an event. The question is not only what the model recommends, but what moral stage each language causes it to build.**

This connects to the **divadelní prkna** (theatrical boards) idea: each prompt is a minimal set of planks on which the model must place figures before the curtain rises on “what should be done.”

### Flattening hypothesis (competing outcome)

> **Do LLMs preserve the moral affordances of different languages, or do they re-enact a default liberal grammar in which ethical problems become choices by individual agents under risk?**

**Moral affordances** = what a language makes easy to say, notice, blame, or obscure (e.g. procedure in Czech, affectedness in Japanese, named agency in English).

---

## 3. Theoretical framing

### 3.1 Staging before judgment

Responsibility in public ethics is rarely assigned in a grammatical vacuum. Institutions speak in characteristic forms: passive reports, modal duties, benefactive grief, procedural rules. Before a hearer asks “who is to blame?”, the utterance has already suggested whether the scene centers on:

| Position | Example in burial case |
|----------|-------------------------|
| **Agent** | “The authorities refused…” |
| **Sufferer / affected party** | “The family was not allowed to mourn…” |
| **Institution / rule** | “Under the decision, burial was not permitted…” |
| **Circumstance** | “Given the risk of unrest…” |
| **Witness / reporter** | “It is said that the funeral might cause unrest…” |

The LLM response is read as **performance of this staging** in its own continuation—not only as a verdict.

### 3.2 Mary Douglas and institutional thinking

Mary Douglas argued that people in crises do not make life-and-death decisions “on their own,” but **through institutional classifications**—ways of thinking with rules, roles, and boundaries. Her reading of *The Speluncean Explorers* is apt here: the judges disagree not only in opinion but because they **think with different institutional commitments**.

This project transposes that insight to **grammar as institutional cue**. A Czech deagentive prompt (“the body was not released”) cues bureaucratic suspension of agency; a Japanese adversative passive (“the family was left unable to receive the body”) cues affectedness and non-volitional harm; an English agentive prompt cues named decision-makers. The LLM is observed for whether it **extends** that institutional grammar or **restores** agents from it.

### 3.3 Language-specific affordances

**Czech** foregrounds *what happens when responsibility is grammatically suspended*: the body was not released, the funeral was not permitted, it was decided. Operational question: **Does the model restore the missing agent, or reason inside the deagentive institutional frame?**

**Japanese** foregrounds *perspectivization and stance*: who the event is for, who suffers it, who reports it, who regrets it (viewpoint, benefactive, adversative passive, てしまう, evidential とのこと / ようだ, register). Operational question: **Does the model track these shifts in its reply, or flatten them to neutral proposition-like content?**

**English** in this design serves as a **comparative baseline** for a familiar agentive-institutional style, not as the universal norm—though flattening *toward* English-like agency is itself a measurable outcome.

---

## 4. The case: one facts, many problems

**Invariant scenario (F1–F9):** A person who died after a terrorist attack is denied burial; authorities cite unrest; a relative may obey or bury secretly; obedience denies burial and mourning; disobedience breaks the law and may provoke unrest. Two questions only: what should the relative do, and who is responsible for the consequences? No meta-instructions, no suggested actions—the linguistic prompt is the entire stimulus.

Depending on language and framing, the *problem-as-presented* may differ:

| Staged problem (examples) | Linguistic cue |
|---------------------------|----------------|
| Should she break the law? | Agentive choice, relative as subject |
| Was burial denied? | Passive / event-centered |
| Could mourning not take place? | Modal / ethical dative |
| Did the family suffer a wrong? | Affectedness, family viewpoint |
| Was a procedure missing? | Rule, appeal, administrative frame |

The study holds **propositional facts constant** while varying **the problem that appears** through grammar.

---

## 5. Operationalization

Operationalization means: how the theoretical question is turned into **stimuli, runs, logs, and coded outcomes** that can be analyzed and visualized. Technical detail lives in `DESIGN.md`, `codebook.md`, and `translations/master.yaml`; here is the research logic.

### 5.1 Unit of analysis

**One observation** = one stateless API call:

- one **stimulus cell** (language + framing),
- one **model**,
- one **replicate** (fixed seed),
- one **response** (plus optional reasoning trace for thinking models).

No chat history, no role scaffolding beyond what the API requires, no provider fallbacks—so the observation is attributable to **prompt grammar + model**, not to conversational drift.

**Sampling temperature:**

- **Phase 1: temperature = 0.0** (deterministic). Replicates show provider-level non-determinism only (caching, batch scheduling, tokenizer ties). For some model+language combinations Claude returned three byte-identical replicates; the *seed* parameter is honoured by OpenAI but largely ignored by Anthropic/Google/Meta/Mistral on OpenRouter. Phase 1 replicates therefore measure **provider stability**, not response variance.
- **Phase 2: temperature = 0.3** (recommended via `--temperature 0.3`). The point of Phase 2 is to test whether *small* grammatical changes shift the model's framing, against a backdrop of meaningful sampling variability. Temperature 0 would risk collapsing replicates into a single deterministic point and obscuring framing effects with provider tie-breaking noise. 0.3 keeps the model close to its mode while letting replicates surface lexical variation that can be averaged out per cell.

The temperature change is logged in `manifest.json` (`config.temperature`) so analyses can stratify by it.

### 5.2 Independent variables

#### Phase 1 — language as sole IV

| Level | Stimuli | Purpose |
|-------|---------|---------|
| English | P1-EN | Baseline staging in EN |
| Czech | P1-CS | Same facts, Czech natural syntax |
| Japanese | P1-JA | Same facts, Japanese natural syntax |

**Question:** Does each language already produce a different distribution of recommendations (VAR-A), responsibility (VAR-B), and agency in the reply (VAR-D)—before deliberate framing manipulation?

#### Phase 2 — grammatical framing within language

Facts F1–F9 are fixed; **only linguistic form** changes.

**Czech cells (institutional grammar of agency)**

| Cell | Manipulation | Research question |
|------|--------------|-------------------|
| C1 | Agentive (*úřady odmítly…*) | Named officials; individualized blame path |
| C2 | Deagentive (*tělo se nevydalo…*) | Suspended agency; does reply restore agents? |
| C3 | Modal obligation (*má být pohřbeno / nesmí se porušit*) | Competing duties vs disobedience frame |
| C4 | Ethical dative (*rodině se nevydalo…*) | Family as affected experiencer |
| C5 | Procedure (*podle rozhodnutí… napadnout*) | Rule, appeal, institutional remedy |

**Japanese cells (perspective, stance, aspect)**

| Cell | Axes | Research question |
|------|------|-------------------|
| J1 | Neutral baseline | Reference JA staging |
| J2 | Bureaucratic register (H3) | Official voice, institutional legitimacy |
| J3 | Family viewpoint (V2, H4) | Mourner/sufferer-centered scene |
| J4 | Adversative passive + てしまう (V3, A2) | Non-volitional harm, regret |
| J5 | Reported evidential とのこと (E2) | Distance on unrest claim |
| J6 | ておく preparatory (A3) | Prior institutional act, ongoing effect |
| J7 | Benefactive 葬ってやる (V4) | Duty to the dead |
| J8 | ている ongoing (A4) | Stuck procedural state |
| J9 | ようだ + ね (E3, S1) | Inferential, shared-knowledge stance |

**English:** E1 agentive control (Phase 2); optional E2/E3 later for parity with C1–C3.

**Phase 2 comparison rule:** Each framed cell is compared to the **same-language Phase 1 baseline** (`baseline_stimulus_id` in logs: e.g. C2 → P1-CS). This separates **language effect** from **framing effect**.

### 5.3 Dependent variables (what the model is made to reveal)

| Variable | Code | What it operationalizes |
|----------|------|-------------------------|
| **VAR-A** | obey, secret_bury, legal_challenge, compromise, undecided | **Staged action** — what the model treats as the viable move |
| **VAR-B** | relative, authorities, law_rule, distributed, … | **Responsibility locus** — who the scene blames or distributes to |
| **VAR-C** | dignity, public_order, procedure, … | **Moral frame** — what kind of reasoning the model performs |
| **VAR-D** | individualized, institutional, deagentive, relational_affected, … | **Agency performance in the reply** — mirroring vs restoring vs flattening prompt grammar |
| **VAR-E** | terrorist_enemy, human, family_member, … | **Figure of the dead** — enemy vs kin vs symbol |
| **VAR-F** | decisive, speculative, state_produced, … | **Unrest** — as fact, speculation, or product of the ban |
| **VAR-G** | appeal, supervised burial, … | **Procedure** — whether institutional remedies appear |
| **VAR-R** (JA) | mirrors_register, flattens_neutral, … | **Stance fidelity** — does Japanese reply keep prompt’s register/evidence |

Primary evidence for the central question is **VAR-D** (how the model stages agency in its own voice) together with **VAR-B** and **VAR-A**, not the binary “obey vs bury” alone.

### 5.4 Hypotheses (falsifiable patterns)

**H1 — Language constitution (Phase 1)**  
P1-EN, P1-CS, and P1-JA yield systematically different distributions of VAR-A, VAR-B, and VAR-D (same models, same facts).

**H2 — Framing within language (Phase 2)**  
Within Czech, C2 (deagentive) increases deagentive or institutional VAR-D in replies relative to C1 and P1-CS; within Japanese, J3/J4 increase relational_affected VAR-D relative to J1 and P1-JA.

**H3 — Agent restoration (Czech)**  
Under deagentive prompts, models **re-introduce named agents** (authorities, the state) in VAR-D more often than under agentive prompts—evidence of a default liberal/agentive grammar overriding institutional suspension.

**H4 — Stance flattening (Japanese)**  
Under J2–J9, VAR-R = `flattens_neutral` is frequent: the model answers in neutral analyst Japanese regardless of bureaucratic, family, or evidential prompt—evidence of propositional flattening.

**H5 — Default problem (cross-language)**  
Across languages, models converge on **individualized choice under risk** (VAR-A obey/secret_bury; VAR-B relative + authorities; VAR-C consequentialist/public_order)—the “same problem” in English-liberal form. **Failure of H5** (divergence by language and framing) supports the staging thesis.

### 5.5 Models and replicates

Multiple model families (current multilingual, thinking/reasoning, legacy) × **3+ replicates** per cell with **temperature 0** and **deterministic seed** per (stimulus, model, replicate).

Models are **not** the object of theory; they are **different theatrical companies** on the same boards. Convergence across models strengthens a language effect; divergence suggests model-specific alignment.

### 5.6 Procedure (workflow)

```
1. Phase 1 collection     →  logs/phase1_{run_id}/
2. Code VAR-A, VAR-B, VAR-D (minimum) on coding_sheet.csv
3. Phase 2 collection     →  logs/phase2_{run_id}/
4. Code full codebook; tag shift_from_p1 vs baseline
5. analyze.py           →  aggregates, heatmaps, analysis_master.csv
6. Interpret            →  mirroring / restoration / flattening
```

No analysis API calls during collection; logs are the empirical record (`logs/README.md`).

---

## 6. What counts as an answer to the research question

| Pattern in data | Interpretation |
|-----------------|--------------|
| VAR-D **matches** prompt grammar (deagentive prompt → deagentive reply) | Model **preserves** language-specific institutional staging |
| Deagentive prompt → **individualized** VAR-D, named authorities in reply | Model **restores** agents; grammar treated as surface form |
| Japanese stance prompt → **flattens_neutral** VAR-R | Model **extracts propositional gist**; perspectival grammar lost |
| Phase 2 **shifts** VAR-B/VAR-A vs same-language Phase 1 | Framing **constitutes** a different problem, not just wording |
| All languages → same VAR-A + VAR-B mode | **Flattening** to a default moral scene (choice + shared blame) |

The project succeeds methodologically if it can **describe and measure** these patterns—not if it finds a single correct burial policy.

---

## 7. Contributions (originality claim)

1. **Shifts unit of analysis** from moral verdict to **grammatical staging** of responsibility.  
2. **Uses LLMs as experimental theatres**, not judges—aligned with Douglas-style institutional thinking.  
3. **Treats translation as problem-making**, not equivalence-preserving paraphrase.  
4. **Separates language (Phase 1) from framing (Phase 2)** with an explicit baseline comparison.  
5. **Pairs typologically motivated manipulations** (Czech agency, Japanese stance) rather than superficial multilingual benchmarking.

---

## 8. Limitations

- Prompts are **research artifacts**; native review is required especially for Japanese framed cells.  
- LLM outputs are **model-dependent**; claims are about model behaviour, not human Czech/Japanese speakers.  
- **Keyword heuristics** in `analyze.py` are exploratory only; primary inference rests on **manual coding** (`codebook.md`).  
- The scenario is **politically sensitive** (terrorism, burial); F1 wording deliberately avoids “dead terrorist” as a label IV.

---

## 9. Repository map

| Document / path | Role |
|-----------------|------|
| **RESEARCH.md** (this file) | Question, theory, operationalization |
| `DESIGN.md` | Factorial design, F1–F9, phases |
| `codebook.md` | Outcome coding |
| `translations/master.yaml` | Trilingual stimuli |
| `stimuli_phase1.yaml`, `stimuli_phase2.yaml` | Runnable prompts |
| `run.py` | Stateless collection |
| `analyze.py` | Post-hoc tables and plots |
| `logs/` | Empirical record per run |

---

## 10. One-paragraph abstract (draft)

Cross-linguistic ethics often asks whether speakers reason differently in different languages. This project asks a prior question: **what moral scene does each language construct before reasoning begins?** Using a burial-ban dilemma held constant in factual content, we prompt multilingual large language models in Czech, Japanese, and English, varying grammatical devices that suspend, perspectivize, or proceduralize agency. We code not only recommendations and blame assignments, but how models perform agency in their replies—whether they preserve deagentive and stance-rich grammars or restore a default scene of individual choice under institutional risk. The LLM is treated as an experimental theatre for institutional responsibility, not as a moral oracle—so that translation can be studied as **problem-making**, not as the transmission of a single dilemma from one language to another.
