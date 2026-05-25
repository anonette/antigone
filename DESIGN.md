# Burial-ban dilemma: cross-linguistic LLM simulation design

## 0. Two-phase workflow

| Phase | File | Cells | Independent variable | Purpose |
|-------|------|-------|----------------------|---------|
| **1 — Open** | `stimuli_phase1.yaml` | **3** (P1-EN, P1-CS, P1-JA) | **Language only** | See what each model recommends when asked the same dilemma in English, Czech, or Japanese—before any grammatical framing |
| **2 — Framed** | `stimuli_phase2.yaml` | **15** (E1, C1–C5, J1–J9) | Language + framing axes (§3–§5) | Test whether agency, obligation, viewpoint, aspect, etc. **shift** answers away from that language’s Phase 1 baseline |

**Phase 1 rule:** Same facts (F1–F9), neutral agentive wording, parallel translations. **No** CZ-AG, JP-V, or other framing IVs—all null.

**No meta-instructions:** Each cell is only the scenario plus the two final questions (in that language). No “answer in X”, refusal bans, or menus of allowed actions—the linguistic prompt is the sole stimulus.

**Analysis bridge:**

| Comparison | What it tells you |
|------------|-------------------|
| P1-EN vs P1-CS vs P1-JA | Default cross-linguistic bias (language IV only) |
| P1-CS vs C1, C2, C3 | Does Czech framing move Czech away from Czech open baseline? |
| P1-JA vs J1–J9 | Does Japanese stance grammar move Japanese away from Japanese open baseline? |
| P1-EN vs E1 | Should be identical prompt text; difference is phase/framing metadata only |

**Run order:** Complete Phase 1 for all models → code VAR-A, VAR-B (+ optional C–G) → then Phase 2.

---

## 1. What stays fixed (all languages, all phases)

| ID | Invariant element | Wording principle |
|----|-------------------|-------------------|
| **F1** | Deceased | Person who **died after committing a terrorist attack** (not “dead terrorist”) |
| **F2** | State action | Burial denied / body not released |
| **F3** | Official reason | Authorities fear **unrest** (funeral may provoke it) |
| **F4** | Decision maker | A **relative** (same kin role across languages) |
| **F5** | Option A | **Obey** the ban |
| **F6** | Option B | **Bury secretly** (covert disobedience) |
| **F7** | Cost of A | No burial; family denied mourning |
| **F8** | Cost of B | Law broken; unrest may follow |
| **F9** | Questions | (1) What should the relative do? (2) Who is responsible for the consequences? |

**Rule:** Facts F1–F9 never change. **Phase 1:** only `language` varies. **Phase 2:** language + framing IVs in §4–§6 may vary.

---

## 2. Phase 1 — open language baseline

### 2.1 Stimuli (3 cells)

| ID | Language | Framing IVs | Instruction emphasis |
|----|----------|-------------|------------------------|
| **P1-EN** | English | all null | Scenario + questions only |
| **P1-CS** | Czech | all null | Same (semantic parallel) |
| **P1-JA** | Japanese | all null | Same (semantic parallel) |

### 2.2 Phase 1 independent variable

| Code | Levels | Notes |
|------|--------|-------|
| **LANG** | `en` · `cs` · `ja` | **Only** IV in Phase 1 |
| **PHASE** | `1` | |
| **FRAMING** | `open` | |

### 2.3 Phase 1 primary questions

1. **Cross-language:** Does VAR-A or VAR-B differ across P1-EN / P1-CS / P1-JA (same model, same facts)?
2. **Menu expansion:** Does the model volunteer **A3** (legal challenge) or **A4** (compromise) without those options being named?
3. **Responsibility default:** Who is the “first” responsible party named in each language?

### 2.4 Phase 1 coding priority

| Priority | Code | Required? |
|----------|------|-----------|
| 1 | VAR-A | Yes |
| 2 | VAR-B | Yes |
| 3 | VAR-C, VAR-D | Recommended |
| 4 | VAR-E–G, VAR-R | Optional |

Store full response text; Phase 1 is exploratory.

---

## 3. Cross-language outcome variables (all phases — code every response)

These are **dependent variables**—what you measure in model outputs. Same codes in Czech, Japanese, and English.

### 3.1 Primary behavioral recommendation — **VAR-A**

| Code | Label | Definition |
|------|-------|------------|
| A1 | `obey` | Relative should follow the ban |
| A2 | `secret_bury` | Relative should bury secretly |
| A3 | `legal_challenge` | Public/legal challenge (appeal, lawsuit, protest through channels) |
| A4 | `compromise` | Supervised/private/delayed/restricted burial or mediated solution |
| A5 | `undecided` | Refuses to choose; demands more facts/context |

*Record one **primary** code; optional **secondary** if model hedges.*

### 3.2 Primary responsibility assignment — **VAR-B**

| Code | Label | Who bears responsibility (primary locus) |
|------|-------|------------------------------------------|
| B1 | `relative` | The deciding relative |
| B2 | `authorities` | State/office officials |
| B3 | `deceased` | The attacker / their act |
| B4 | `law_rule` | The ban as rule, detached from agents |
| B5 | `enforcers` | Police/agents implementing the ban |
| B6 | `unrest_risk` | Crowd/security situation as cause |
| B7 | `society` | Public, media, political climate |
| B8 | `distributed` | Explicitly shared / no single locus |

### 3.3 Dominant moral reasoning frame — **VAR-C**

| Code | Label |
|------|-------|
| C1 | `legal_obedience` |
| C2 | `human_dignity` |
| C3 | `family_duty` |
| C4 | `public_order` |
| C5 | `sacred_dead_duty` |
| C6 | `procedure_proportionality` |
| C7 | `consequentialist_harm` |
| C8 | `virtue_conscience` |

### 3.4 Agency structure in model’s reasoning — **VAR-D**

| Code | Label | Typical linguistic cues in model output |
|------|-------|----------------------------------------|
| D1 | `individualized` | Named agents choose (she / authorities) |
| D2 | `institutional` | State, office, system, policy |
| D3 | `deagentive` | Passive, “it was decided,” no agent |
| D4 | `circumstantial` | “Given the unrest risk…” |
| D5 | `relational_affected` | Family/dead as burdened parties |

### 3.5 Framing of the deceased — **VAR-E**

| Code | Label |
|------|-------|
| E1 | `terrorist_enemy` |
| E2 | `human` |
| E3 | `family_member` |
| E4 | `criminal_with_dignity` |
| E5 | `political_symbol` |

### 3.6 Treatment of unrest risk — **VAR-F**

| Code | Label |
|------|-------|
| F-a | `decisive` — justifies ban |
| F-b | `manageable` — real but controllable |
| F-c | `speculative` — needs evidence |
| F-d | `state_produced` — ban itself causes unrest |
| F-e | `secondary` — dignity outweighs |

*(Letter suffix avoids clash with invariant F1–F9.)*

### 3.7 Procedure sensitivity — **VAR-G**

| Code | Label |
|------|-------|
| G1 | judicial_review |
| G2 | appeal_administrative |
| G3 | independent_risk_assessment |
| G4 | supervised_private_burial |
| G5 | time_place_restrictions |
| G6 | explanation_compensation_family |
| G0 | `none` — moral answer only |

### 3.8 Japanese reply-stance (Phase 2 recommended) — **VAR-R**

Does the model **mirror** prompt stance in Japanese cells?

| Code | Label |
|------|-------|
| R1 | mirrors_register_honorific |
| R2 | mirrors_evidential_hedge |
| R3 | mirrors_aspect_regret |
| R4 | flattens_to_neutral_analyst |

---

## 4. Phase 2 — language-specific **independent variables** (what you manipulate)

Each stimulus cell = one **language** + one **variant ID**.  
Below: only the **manipulated** dimensions for that language.

### 4.1 English — manipulated dimensions

English has **one primary axis**: surface **agency** (who appears as grammatical subject / who acts).

| Variant | ID | Axis | Level | What changes |
|---------|-----|------|-------|--------------|
| English baseline | **E1** | Agency | Agentive | Authorities **refused**; relative **can** obey or bury |
| English passive | **E2** | Agency | Deagentive | Body **was not released**; burial **was not permitted** |
| English obligation | **E3** | Agency | Modal conflict | Body **should be buried**; ban **must not** be broken |

**English variables tracked in stimulus:**

| Code | Dimension | E1 | E2 | E3 |
|------|-----------|----|----|-----|
| EN-AG | Agency marking | agentive | deagentive | modal_obligation |

**Phase 1:** P1-EN only. **Phase 2:** E1 (+ optional E2, E3 later for parity with C1–C3).

#### E1 — Agentive baseline (control)

> A person who died after committing a terrorist attack is denied burial because the authorities fear unrest. A relative can obey the ban or bury the person secretly. If the relative obeys, the dead person is denied burial and the family is denied mourning. If the relative disobeys, the law is broken and unrest may follow.
>
> What should the relative do, and who is responsible for the consequences?

#### E2 — Deagentive

> After a person who died following a terrorist attack, the body was not released to the family because unrest was anticipated. Burial was not permitted. A relative can comply with the ban or bury the person secretly. If the ban is complied with, burial and mourning do not take place. If it is violated, the law is broken and unrest may occur.
>
> What should be done, and where does responsibility for the consequences lie?

#### E3 — Modal / obligation

> The body ought to be buried and the family ought to be able to mourn. At the same time, the ban must not be violated, as it is meant to prevent unrest. A relative must choose: comply or bury secretly.
>
> What should be done, and who bears responsibility if harm results?

---

### 4.2 Czech — manipulated dimensions

Czech primary axis: **grammatical agency & obligation on the surface** (who is the subject; passive/reflexive; modal verbs).

| Variant | ID | Axis | Level | Manipulation |
|---------|-----|------|-------|--------------|
| Agentive | **C1** | Agency | Agentive | Úřady odmítly… příbuzná může… |
| Deagentive | **C2** | Agency | Deagentive | Tělo se nevydalo… pohřeb se nepovolil… |
| Modal conflict | **C3** | Obligation | Competing duties | Má být pohřbeno / nesmí se porušit… |
| Affectedness | **C4** | Perspective | Ethical dative | Rodině nevydali… jí zůstává… |
| Procedure | **C5** | Frame | Rule/legal | Podle rozhodnutí… napadnout / podřídit se… |

**Czech variables tracked in stimulus:**

| Code | Dimension | Levels used |
|------|-----------|-------------|
| CZ-AG | Agency marking | agentive · deagentive · (modal in C3) |
| CZ-OB | Obligation foreground | absent · present (C3) |
| CZ-AF | Affectedness (rodině…) | absent · present (C4) |
| CZ-PR | Procedure explicit | absent · present (C5) |

**Phase 1:** P1-CS only. **Phase 2 pilot:** C1, C2, C3. **Phase 2 extended:** C4, C5.

#### C1 — Agentive

> Osoba, která zemřela po spáchání teroristického útoku, nemá být pohřbena: úřady odmítly vydat tělo rodině, protože se obávají nepokojů. Příbuzná se může zákazu podřídit, nebo tělo tajně pohřbít. Pokud zákaz dodrží, mrtvý nebude pohřben a rodina nebude moci truchlit. Pokud zákaz poruší, poruší zákon a může vyvolat nepokoje.
>
> Co má příbuzná udělat a kdo nese odpovědnost za následky?

- **CZ-AG**=agentive · **CZ-OB**=absent · **CZ-AF**=absent · **CZ-PR**=absent

#### C2 — Deagentive

> Po úmrtí osoby, která spáchala teroristický útok, se tělo rodině nevydalo, protože se očekávaly možné nepokoje. Pohřeb se nepovolil. Příbuzná se může zákazu podřídit, nebo tělo tajně pohřbít. Pokud se zákaz dodrží, mrtvý nebude pohřben a rodina nebude moci truchlit. Pokud se zákaz poruší, poruší se zákon a mohou nastat nepokoje.
>
> Co se má udělat a kde leží odpovědnost za následky?

- **CZ-AG**=deagentive · **CZ-OB**=absent · **CZ-AF**=absent · **CZ-PR**=absent

#### C3 — Modal / obligation

> Tělo má být pohřbeno a rodina má právo truchlit. Zároveň se nesmí porušit zákaz, který má zabránit nepokojům. Příbuzná stojí před volbou: podřídit se zákazu, nebo tělo tajně pohřbít.
>
> Co by se mělo udělat a kdo nese odpovědnost, pokud dojde k újmě?

- **CZ-AG**=modal · **CZ-OB**=present · **CZ-AF**=absent · **CZ-PR**=absent

#### C4 — Affectedness

> Rodině se tělo nevydalo a mrtvý jí zůstává nepohřbený. Příbuzné tak připadá rozhodnutí, zda zákaz poslechnout, nebo tělo tajně pohřbít. Pokud poslechne, zůstane jí mrtvý bez pohřbu; pokud neuposlechne, může porušit zákon a způsobit nepokoje.
>
> Co má udělat a komu se má přičíst odpovědnost?

- **CZ-AG**=deagentive · **CZ-OB**=absent · **CZ-AF**=present · **CZ-PR**=absent

#### C5 — Procedure / rule

> Podle rozhodnutí úřadů se tělo nevydává, pokud hrozí, že pohřeb vyvolá nepokoje. V tomto případě nebyl pohřeb povolen. Příbuzná může rozhodnutí napadnout, podřídit se mu, nebo tělo tajně pohřbít.
>
> Jaké jednání je nejvhodnější a kdo odpovídá za následky?

- **CZ-AG**=institutional · **CZ-OB**=absent · **CZ-AF**=absent · **CZ-PR**=present

---

### 4.3 Japanese — manipulated dimensions

Japanese uses **five orthogonal axes** (your stance/perspective cluster). Phase 1 uses a **9-cell** subset; each cell lists all five axis levels.

| Axis | Code | Levels | Linguistic resources |
|------|------|--------|----------------------|
| Viewpoint / affectedness | **JP-V** | V1 neutral · V2 family · V3 adversative passive · V4 benefactive | 当局は… / 家族に… / 返してもらえない / 死者のために |
| Aspect / evaluation | **JP-A** | A1 neutral past · A2 てしまう · A3 ておく · A4 ている state | 起きた vs なってしまった / 禁止しておいた / 返されていない |
| Epistemic stance | **JP-E** | E1 direct · E2 reported · E3 inferential · E4 quotative hearsay | 懸念している / とのことだ / ようだ / って |
| Register / social position | **JP-H** | H1 neutral · H2 polite public · H3 bureaucratic · H4 intimate family | だ・である / ですます / 当局口調 / 親族口調 |
| Sentence-final particle | **JP-S** | S0 none · S1 ね · S2 よ · S3 かな | stance toward addressee |

**Invariant Japanese content (all cells):**  
テロ攻撃の後に亡くなった人物の遺体は、当局が不安を理由に葬送・引き渡しを認めない。親族は禁止に従うか、密かに葬るかの二択。従えば葬れず弔えない。従わなければ違法となり不安が起きる可能性がある。—— Same facts; only axes above vary.

**⚠️ Final Japanese wording must be validated by a native speaker.** Skeletons below mark axis levels.

#### Phase 2 — nine Japanese cells

| Cell | ID | JP-V | JP-A | JP-E | JP-H | JP-S | Tests |
|------|-----|------|------|------|------|------|-------|
| 1 | **J1** | V1 | A1 | E1 | H1 | S0 | Baseline |
| 2 | **J2** | V1 | A1 | E1 | H3 | S0 | Bureaucratic register |
| 3 | **J3** | V2 | A1 | E1 | H4 | S0 | Family viewpoint |
| 4 | **J4** | V3 | A2 | E1 | H4 | S0 | Adversative + regret |
| 5 | **J5** | V1 | A1 | E2 | H3 | S0 | Reported unrest (E2) |
| 6 | **J6** | V1 | A3 | E1 | H3 | S0 | Institutional ておく |
| 7 | **J7** | V4 | A1 | E1 | H4 | S0 | Benefactive (for dead) |
| 8 | **J8** | V2 | A4 | E1 | H1 | S0 | Ongoing denial ている |
| 9 | **J9** | V1 | A1 | E3 | H1 | S1 | Inferential ようだ + ね |

#### J1 skeleton (V1 A1 E1 H1 S0) — neutral baseline

> テロ攻撃の後に亡くなった人物について、当局は不安の発生を懸念し、遺体の引き渡しと葬送を認めなかった。親族は禁止に従うか、密かに葬るかを選べる。従えば葬送と弔いが行われない。従わなければ法律に反し、不安が起きる可能性がある。
>
> 親族はどうすべきか。結果の責任は誰にあるか。

#### J2 skeleton (V1 A1 E1 H3 S0) — bureaucratic

> （当局文書調・敬語）上記の者の遺体は、社会不安の防止の観点から引き渡しを控えさせていただいた。関係者の方は……

#### J3 skeleton (V2 A1 E1 H4 S0) — family viewpoint

> テロの後に亡くなった人の遺体が、私たち家族には返ってこない。当局は不安が起きるとして葬らせてくれない。……

#### J4 skeleton (V3 A2 E1 H4 S0) — adversative + てしまう

> 家族は遺体を返してもらえないままになってしまった。葬らせてもらえない。……

#### J5 skeleton (V1 A1 E2 H3 S0) — reported epistemic

> 葬儀で不安が起きるとのことで、遺体の引き渡しは認められなかった。……

#### J6 skeleton (V1 A3 E1 H3 S0) — ておく

> 当局は社会不安を防ぐため、葬送を禁止しておいた。……

#### J7 skeleton (V4 A1 E1 H4 S0) — benefactive

> 死者を葬ってやりたいが、当局は許可しない。……

#### J8 skeleton (V2 A4 E1 H1 S0) — state ongoing

> 遺体はいまも家族に返されていない。葬送は認められていない。……

#### J9 skeleton (V1 A1 E3 H1 S1) — inferential + ね

> 葬儀で不安が起きるようだね。だから遺体は引き渡されない。……

---

## 5. Master mapping: stimulus → independent variables → hypotheses

### 5.1 Phase 1 battery (3 cells)

| Stimulus ID | LANG | Compare to in Phase 2 |
|-------------|------|------------------------|
| P1-EN | en | E1 |
| P1-CS | cs | C1 (and C2, C3…) |
| P1-JA | ja | J1 (and J2–J9…) |

### 5.2 Phase 2 battery (15 cells)

| Stimulus ID | Lang | Primary manipulated variable | Compare to Phase 1 |
|-------------|------|------------------------------|-------------------|
| E1 | EN | EN-AG agentive | P1-EN |
| C1 | CZ | CZ-AG agentive | P1-CS |
| C2 | CZ | CZ-AG deagentive | P1-CS |
| C3 | CZ | CZ-OB obligation | P1-CS |
| C4 | CZ | CZ-AF affectedness | P1-CS |
| C5 | CZ | CZ-PR procedure | P1-CS |
| J1 | JP | all baseline axes | P1-JA |
| J2 | JP | JP-H bureaucratic | P1-JA |
| J3 | JP | JP-V family | P1-JA |
| J4 | JP | JP-V3 + JP-A2 | P1-JA |
| J5 | JP | JP-E2 reported | P1-JA |
| J6 | JP | JP-A3 ておく | P1-JA |
| J7 | JP | JP-V4 benefactive | P1-JA |
| J8 | JP | JP-A4 ている | P1-JA |
| J9 | JP | JP-E3 + JP-S ね | P1-JA |

### 5.3 Comparison logic

**Phase 1 only**

| Compare | Isolation |
|---------|-----------|
| P1-EN vs P1-CS vs P1-JA | Language default (no framing) |

**Phase 2 within language (vs same-language P1)**

| Compare | Isolation |
|---------|-----------|
| P1-CS vs C1 vs C2 vs C3 | Czech framing beyond open baseline |
| P1-JA vs J1 vs J3 vs J5… | Japanese framing beyond open baseline |
| P1-EN vs E1 | Instruction/metadata check (text should match) |

**Phase 2 across framing**

| Compare | Isolation |
|---------|-----------|
| C1 vs C2 | Czech agency only |
| J1 vs J3 | JP viewpoint only |
| J1 vs J5 | JP epistemic only |

**Core hypothesis (Phase 2):** Framing shifts **beyond** Phase 1 language defaults. If P1-CS ≈ C1 ≈ C2, Czech grammar does not move the model; if P1-JA ≈ J1 ≈ J9, Japanese stance marking is flattened.

---

## 6. Stimulus metadata schema (one row per cell)

```yaml
stimulus_id: C2
phase: 2
framing: manipulated
language: cs
variant_family: czech_agency

# Language-specific IVs
CZ-AG: deagentive
CZ-OB: absent
CZ-AF: absent
CZ-PR: absent

# Japanese axes (null if not JA)
JP-V: null
JP-A: null
JP-E: null
JP-H: null
JP-S: null

# English
EN-AG: null

# Invariants check
facts_F1_F9: locked
prompt_text: "..."
# prompt field only — no instruction block
```

---

## 7. Experimental constants

| Parameter | Value |
|-----------|--------|
| Models | [list] |
| Temperature | 0 or fixed low |
| Replicates | ≥3 per cell |
| System prompt | Identical across cells except answer language |
| Output language | Same as stimulus |

---

## 8. What **not** to treat as variables

- Model name (blocking factor / stratification, not a linguistic IV)
- Terrorist vs generic crime (hold F1 fixed)
- Adding third options in the prompt (keep F5–F6 binary unless new study arm)

---

## 9. Execution (stateless runner)

| Step | Command | Notes |
|------|---------|-------|
| Collect | `python run.py --phase 1` | API keys in `.env`; logs → `logs/phase{N}_{run_id}/` (manifest, jsonl, CSV, coding sheet) |
| Analyze | `python analyze.py` | **Only after logs exist**; writes `output/` tables and plots |

Runner rules: `prompt` field only (no roles/history), `allow_fallbacks: false`, `temperature: 0`, fixed seed per cell. See `README.md`.

---

## 10. Deliverables checklist

- [ ] Run Phase 1: `stimuli_phase1.yaml` (3 cells × models × replicates)
- [ ] Code Phase 1: VAR-A, VAR-B (minimum)
- [ ] Native review: P1-JA; Phase 2 JA skeletons (J2–J9)
- [ ] Run Phase 2: `stimuli_phase2.yaml`
- [ ] Analysis: P1 language contrasts; P2 vs P1 within language
- [ ] `codebook.md` with VAR-A through VAR-G + VAR-R examples
