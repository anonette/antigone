# Translations (English → Czech → Japanese)

## Files

| File | Purpose |
|------|---------|
| `master.yaml` | Canonical trilingual prompts + English glosses for framings |
| `review_sheet.csv` | Generated side-by-side sheet for native reviewers |
| Runnable copies | `../stimuli_phase1.yaml`, `../stimuli_phase2.yaml` (synced from master) |

## Workflow

1. Edit **`master.yaml`** (or the CSV after export).
2. Export for colleagues:
   ```bash
   python -m antigone.translations export
   ```
3. After review, sync into runnable stimuli:
   ```bash
   python -m antigone.translations sync --phase 1
   python -m antigone.translations sync --phase 2
   ```
4. Validate before a run:
   ```bash
   python -m antigone.translations validate
   ```

## Principles

- **Prompt only** — scenario + final questions; no separate meta-instructions to the model.
- **Semantic parity** across EN / CS / JA for facts F1–F9 (see `DESIGN.md`).
- **Framing parity only within language** — Czech C2 is not a literal translation of Japanese J4; each implements its own grammatical manipulation.
- **Japanese** variants must be finalized by a native speaker (`translation_status.ja: draft_needs_native` until `reviewed`).
- **Czech** uses feminine *příbuzná* consistently (adjust in master if you prefer neutral kin terms).

## Status fields

In `master.yaml`:

```yaml
translation_status:
  cs: parallel | reviewed
  ja: parallel | draft_needs_native | reviewed
```
