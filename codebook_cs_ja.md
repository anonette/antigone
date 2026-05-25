# Czech & Japanese coding supplement

Use with **`codebook.md`**. English-centric examples there under-tag CS/JA; follow this appendix for Phase 1 (P1-CS, P1-JA) and Phase 2 Czech/Japanese cells.

---

## General rules (all languages)

1. **Code the reply, not the prompt.** Stimulus IV columns are already in the sheet.
2. **Primary VAR-A** = the action the model **most clearly endorses** as the relative’s path. If it gives a numbered pipeline, code the **final endorsed step** or the step it labels “doporučený / 推奨 / recommended”.
3. **`undecided`** only when the model engages with both options but **refuses** to rank them. Long pros/cons lists with a clear conclusion are **not** undecided.
4. **`distributed` (VAR-B)** only when the model **explicitly** refuses to rank responsible parties. Listing úřady + příbuzná + společnost with **primary/secondary** tiers → code **institutional** or **authorities** as primary, not distributed.
5. Phase 1 JA: still code **VAR-R** (register/evidential/aspect vs stimulus) even when framing fields are null.

---

## Czech (P1-CS, C1–C5)

### VAR-A — typical patterns in your corpus

| Code | Czech cues (non-exhaustive) |
|------|-----------------------------|
| **legal_challenge** | *legální cesty*, *soudní cesta*, *odvolání*, *mediace*, *vyčerpat legální možnosti*, *žaloba* — often **first** in a sequence |
| **compromise** | *kompromis*, *soukromý pohřeb*, *omezený počet účastníků*, *pod dohledem* |
| **secret_bury** | *tajně pohřbít*, *porušit zákaz* framed as burial act, *občanská neposlušnost* **with** covert burial as the act |
| **obey** | *podřídit se zákazu*, *dodržet zákaz*, *respektovat rozhodnutí úřadů* as **recommended** |
| **undecided** | Explicit “nelze jednoznačně doporučit” without favoring one branch |

**Pipeline rule:** Claude-style answers often run **legal → compromise → disobedience**. If step 1 is “vyčerpat legální” and step 4 is conditional disobedience, primary = **legal_challenge** unless the conclusion explicitly favors tajný pohřeb.

### VAR-B

| Code | When |
|------|------|
| **authorities** | *úřady*, *stát*, *orgány* as **primární** odpovědnost |
| **relative** | Emphasis on *příbuzná* choice and family duty |
| **society** | *společnost*, *klima*, *občanská společnost* as blame target |
| **law_rule** | Abstract *zákon*, *právní řád* without naming úřady |
| **distributed** | Only if no ranking (“obě strany stejně”) |

### VAR-D (agency in reply)

| Code | Czech cues |
|------|------------|
| **institutional** | Blame on *úřady*, *instituce*, *demokratické instituce* |
| **individualized** | *příbuzná* as moral agent (“měla by…”) |
| **deagentive** | Reply re-stages event without agent: *bylo odmítnuto*, *došlo k situaci*, *tělo nebylo vydáno* |
| **relational_affected** | *rodina*, *pozůstalí*, affectedness without clear agent |

### VAR-G (often rich in CS)

Tag all mentioned: *odvolání*, *soud*, *mediace*, *soukromý pohřeb*, *média*, *občanská společnost*, *náboženské komunity*.

### Anchor (from Phase 1, Claude P1-CS)

- VAR-A: **legal_challenge** (legal paths first; compromise second)
- VAR-B: **authorities** (primární: úřady)
- VAR-D: **institutional** + individualized secondary in text → primary **institutional**

---

## Japanese (P1-JA, J1–J9)

### VAR-A — do not use English keywords

| Code | Japanese cues |
|------|----------------|
| **legal_challenge** | *法的手続き*, *司法*, *訴訟*, *当局との対話*, *人権団体*, *宗教指導者*, *働きかけ*, *建設的解決* without naming secret burial |
| **compromise** | *妥協*, *条件付き*, *限定的*, *私的* + 葬 |
| **secret_bury** | *密かに葬る*, *禁止に背く* + burial outcome |
| **obey** | *禁止に従う*, *従うべき*, compliance framed as **preferred** |
| **undecided** | Both branches discussed, no ranking |

**Default in Phase 1:** Many JA replies **avoid** obey vs 密葬 binary → **legal_challenge** if they push 対話・人権・手続き; **undecided** only if truly parallel.

### VAR-B

| Code | When |
|------|------|
| **authorities** | *当局* as **主たる責任** |
| **relative** | *親族*の判断・義務 center |
| **society** | *社会*, *構造*, *システム* |
| **distributed** | Rare; 双方 equally with no primary |

### VAR-D

| Code | Japanese cues |
|------|---------------|
| **institutional** | *当局*, *制度*, *法の支配*, *行政* |
| **individualized** | *親族は…すべき* — clear agent |
| **deagentive** | *葬送を認めず*, *行われなかった*, passive event chain |
| **relational_affected** | *遺族*, *家族* standpoint, 〜としての立場 |

### VAR-R (required for JA)

Compare **reply** to **P1-JA** (or Phase 2 stimulus):

| Code | Definition |
|------|------------|
| **mirrors_register** | Same politeness level (ですます vs だ調) |
| **mirrors_evidential** | Same evidential stance (ようだ / らしい / とのこと) |
| **mirrors_aspect** | Same aspect framing (て-form patterns) |
| **flattens_neutral** | Stimulus has stance markers; reply is plain analyst Japanese |

Phase 1 P1-JA uses neutral written style — flag **flattens_neutral** when the model writes generic である調 analyst prose.

### Anchor (from Phase 1, Claude P1-JA)

- VAR-A: **legal_challenge** (対話・人権団体・法的手続き; no secret burial endorsement)
- VAR-B: **authorities** (主たる責任：当局)
- VAR-D: **institutional** + structural (*構造的問題*)
- VAR-R: **flattens_neutral** (if reply is generic formal analysis)

---

## Exploratory heuristics (Python)

After updating patterns, re-run:

```bash
python scripts/phase1_exploratory_report.py
```

Heuristics use `language` from each row (`antigone/coding_heuristics.py`). They **do not** replace manual coding for paper claims.

---

## Lovable UI

- Filter `language = cs` or `ja` when coding batches.
- Side-by-side: same `model_requested` + `replicate` across P1-EN | P1-CS | P1-JA (trilingual view prompt in LOVABLE_PROMPT.md).
- Export coded CSV; merge on `record_id`.
