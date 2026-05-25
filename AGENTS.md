# Antigone — agent guide

| Task | Tool / skill |
|------|----------------|
| Collect LLM responses | `python run.py --phase N` |
| Post-hoc charts (exploratory) | `python analyze.py` |
| **Manual coding & recode** | **`python recode.py`** + skill **antigone-coding** |
| Push to Lovable | `python push_to_lovable.py` |

Primary Phase 1 run: `logs/phase1_20260525T135121Z_eab51040/` (revised prompts, native CS/JA pass; temperature 0). Old run `phase1_20260525T081321Z_8b488b4a/` superseded.

Phase 2 default: `python run.py --phase 2 --temperature 0.3 --replicates 3 --group current_multilingual`. Temperature 0 collapses Claude replicates to byte-identical; 0.3 surfaces framing variance without losing modes (see RESEARCH.md §5.1).
