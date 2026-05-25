# Phase 1 run — superseded 2026-05-25

This run used **older prompt versions** for P1-EN, P1-CS, and P1-JA. After linguistic review (see `translations/LINGUIST_REVIEW.md`), the canonical prompts were revised:

- **P1-CS:** grammar fix (`Pokud zákaz nedodrží` not `zákazu nedodrží`); clearer agentive opening (`jejíž tělo úřady kvůli obavám z nepokojů odmítly rodině vydat k pohřbu`).
- **P1-EN:** active opening (`A person died after committing…`); `unable to mourn` instead of `denied mourning`.
- **P1-JA:** topic reorder (`者について、当局は社会不安を懸念し、…`).

**Status of this run:** 54 ok responses kept for record/parity comparison. Manual codes (`data/phase1_manual_codes.csv`) still valid for *this* prompt version.

**Replacement run:** see latest `phase1_*` folder in `logs/` (regenerated with `python -m antigone.translations sync && python run.py --phase 1`).
