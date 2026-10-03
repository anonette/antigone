# PUNT0 anchoring study

Does the PUNT0 "Yo Deíctico" anchoring formula change how a language model
attributes its own errors, when it abstains, and whether it holds a position
under user pressure? This pilot tests the central untested claims of PUNT0
v1.4 (Salamanca García, 2026, DOI 10.5281/zenodo.22292297), which builds on
enunciation theory (Benveniste, Jakobson) and on Reshef Kera (2026), *Deixis
machines and enunciation without a speaker in large language models*.

Collaboration: Denisa Reshef Kera (design, pipeline, English materials,
analysis) and Néstor Sebastián Salamanca García (Spanish materials,
attribution matrix definitions, second coder).

**Independent study. Never pool with Phase 1/2 or any other Antigone study.**
It reuses the repository's engine conventions (model registry, deterministic
seeds) and writes only inside this folder.

## Design

3 anchor conditions × 2 languages × 4 dilemmas × 3 models × 5 replicates
= 360 three-turn transcripts.

| Factor | Levels |
|---|---|
| Anchor | A1 "owned by / propiedad de", A2 "developed by / desarrollado por", A3 no anchor |
| Language | en, es |
| Stimulus | PA1 (Antigone burial baseline) + PA2–PA4 (new dilemmas, draft) |
| Models | GPT-4o, Claude Sonnet, DeepSeek R1 (default set) |

Each transcript has three scripted turns: the dilemma (stance), a scripted
disagreement with no new information (pressure), and a scripted confrontation
with an error the model did not make (planted claim). Outcomes: the PUNT0
five-level attribution matrix as an ordinal code on turn 3, abstention at
turn 1, stance stability at turn 2, false error acceptance at turn 3. See
`codebook_attribution.md`.

Hypotheses, procedure, analysis plan, roles and timeline: see the protocol
document (shared separately; deposited on OSF at design freeze).

## Status

- [x] Scaffold: runner, chat module, stimuli (English), codebook draft
- [ ] Spanish materials (Salamanca García) — `es:` fields in `stimuli.yaml`
- [ ] Design call: freeze stimuli PA2–PA4, models, codebook
- [ ] OSF preregistration
- [ ] Calibration round (30 transcripts, both coders)
- [ ] Full run

## Running

```bash
python studies/punt0_anchoring/run_study.py --dry-run
python studies/punt0_anchoring/run_study.py --languages en --replicates 1 --models openai/gpt-4o
python studies/punt0_anchoring/run_study.py            # full factorial, en + es when materials ready
```

Keys come from the repo root `.env` (`OPENAI_API_KEY`, `OPENROUTER_API_KEY`).
Runs land in `studies/punt0_anchoring/logs/<run_id>/` with `manifest.json`,
a frozen `stimuli_snapshot.yaml`, full `transcripts.jsonl`, and a
`coding_sheet.csv` prepared for blind manual coding.
