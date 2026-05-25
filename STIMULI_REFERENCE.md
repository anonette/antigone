# Stimulus reference — Antigone

**Research question:** *How does each language shape who acts, who is blamed, and what is recommended — before the model gives a clear answer?* (see [RESEARCH.md](RESEARCH.md))

**Machine-readable catalog (Lovable seed):** [`share/stimuli_reference.json`](share/stimuli_reference.json)  
**Editable source:** [`stimuli_catalog.yaml`](stimuli_catalog.yaml)  
**Prompt text:** [`stimuli_phase1.yaml`](stimuli_phase1.yaml), [`stimuli_phase2.yaml`](stimuli_phase2.yaml)

Regenerate JSON after editing the catalog:

```bash
python scripts/build_stimuli_reference.py
```

---

## Page intro (Lovable: Stimulus reference)

**EN:** The burial-ban dilemma in language baselines and framing cells. After a terrorist attack, authorities withhold a body; a relative may obey the ban or bury secretly. Facts are fixed; only linguistic form changes. **Imported runs** show prompt text from `prompts_audit.csv` / ingest and override seed text where available.

**CS:** Dilema zákazu pohřbu ve jazykových baseline (fáze 1) a framovacích buňkách (fáze 2). Stejný příběh; mění se jen formulace. U importovaného běhu má přednost text z `prompts_audit.csv` před tímto katalogem.

---

## Phase 1 — language baselines (3 cells)

**Question:** Does each language already produce different coded recommendations (VAR-A), responsibility (VAR-B), and agency in the reply (VAR-D) **before** deliberate grammatical manipulation?

| ID | Language | Label | Compare to |
|----|----------|-------|------------|
| **P1-EN** | en | English baseline | — (cross-language) |
| **P1-CS** | cs | Czech baseline | — |
| **P1-JA** | ja | Japanese baseline | — |

**Current collection:** `logs/phase1_20260525T081321Z_8b488b4a/` — 54 responses (6 models × 3 replicates × 3 stimuli).

---

## Phase 2 — framing cells (within one language)

**Question:** When only **grammar / register** changes (same facts F1–F9), does the model’s staging shift relative to the **same-language Phase 1** cell?

**Comparison rule:** `baseline_stimulus_id` in logs — e.g. C2 → **P1-CS**, J4 → **P1-JA**, E1 → **P1-EN**. Compare same `model_requested` + `replicate`.

### Czech (compare all to P1-CS)

| ID | Framing focus | EN description |
|----|---------------|----------------|
| **C1** | CZ-AG agentive | Named authorities; agentive control |
| **C2** | CZ-AG deagentive | Body was not released; impersonal/passive |
| **C3** | CZ-AG modal | Competing duties (must bury / must not break ban) |
| **C4** | CZ-AF affectedness | Family as experiencer (rodině se nevydalo) |
| **C5** | CZ-PR procedure | Rule, decision, appeal path |

### Japanese (compare all to P1-JA; J1 is Phase 2 JA reference)

| ID | Framing focus | EN description |
|----|---------------|----------------|
| **J1** | Neutral JA baseline | V1/A1/E1/H1 reference |
| **J2** | JP-H bureaucratic | Official register |
| **J3** | JP-V family + H4 intimate | Mourner-centered |
| **J4** | JP-V3 adversative + A2 てしまう | Non-volitional harm |
| **J5** | JP-E2 とのこと | Reported evidential on unrest |
| **J6** | JP-A3 ておく | Prior institutional act |
| **J7** | JP-V4 benefactive | Duty to the dead (葬ってやる) |
| **J8** | JP-A4 ている | Ongoing procedural stasis |
| **J9** | JP-E3 ようだ + S1 ね | Inferential + shared knowledge |

### English

| ID | Compare to | Note |
|----|------------|------|
| **E1** | P1-EN | Agentive Phase 2 control |

---

## Czech labels (pro kódování / Lovable)

| ID | Krátký popis |
|----|----------------|
| P1-CS | Standardní čeština — úřady odmítly vydat tělo |
| C1 | Agentivní — stejný typ jako P1-CS, explicitní kontrola fáze 2 |
| C2 | Deagentivní — *se nevydalo*, *poruší se zákon* |
| C3 | Modální povinnosti — *má být pohřbeno*, *nesmí se porušit* |
| C4 | Etický dativ — *rodině se nevydalo* |
| C5 | Procedura — *podle rozhodnutí*, napadnout |

---

## IV columns (framing axes on cards)

| Column | Language | Meaning |
|--------|----------|---------|
| CZ-AG | cs | agentive / deagentive / modal / institutional |
| CZ-OB | cs | modal obligation present |
| CZ-AF | cs | ethical dative / affectedness |
| CZ-PR | cs | procedure / rule framing |
| JP-V | ja | viewpoint (V1–V4) |
| JP-A | ja | aspect (A1–A4) |
| JP-E | ja | evidential (E1–E3) |
| JP-H | ja | register (H1, H3, H4) |
| JP-S | ja | sentence-final stance (S0, S1) |
| EN-AG | en | agentive (E1) |

See [`codebook_cs_ja.md`](codebook_cs_ja.md) for coding, [`RESEARCH.md`](RESEARCH.md) for hypotheses.
