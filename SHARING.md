# Sharing logs and visualizations

Two places hold data: **your machine (Python)** and **Antigone Lab (Lovable web app)**. They are not connected automatically. You generate locally first; the app **displays and shares** what you upload.

---

## Where files are saved (on your PC)

After `python run.py`:

```
c:\dev\antigone\logs\phase1_20250525T120000Z_a1b2c3d4\
  manifest.json
  responses.jsonl          ← canonical data
  responses_flat.csv
  coding_sheet.csv         ← fill codes here OR in Lovable
  prompts_audit.csv
  stimuli_snapshot.yaml
```

After `python analyze.py`:

```
c:\dev\antigone\output\
  analysis_master.csv
  aggregate_by_cell.csv
  runs_index.csv
  heatmap_p1_response_chars.png
  heatmap_p2_response_chars.png
  phase1_by_language.png
  phase1_heuristic_stacked.png
  mean_chars_by_model_group.png
  errors.csv                 (if any)
```

Both `logs/` and `output/` are gitignored by default (not pushed to GitHub unless you choose).

---

## Recommended workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. LOCAL: Collect                                         │
│    python run.py --phase 1                                  │
│    → logs/phase1_{run_id}/                                  │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. LOCAL: Exploratory charts (optional)                     │
│    python analyze.py --phase 1                              │
│    → output/*.png + *.csv                                   │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. PACKAGE for sharing                                      │
│    Zip one run folder + output PNGs (see below)             │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. LOVABLE: Import                                          │
│    Upload zip → browse, code, compare, export               │
│    Charts: built-in from data OR static PNGs you uploaded   │
└─────────────────────────────────────────────────────────────┘
```

**Yes — generate here first.** Lovable does not call OpenRouter or run `run.py`. It only reads files you give it.

---

## What to give collaborators

### Minimum (interpretation + coding in app)

Zip the **run folder**:

```
phase1_20250525T120000Z_abc12345.zip
  manifest.json
  responses.jsonl
  coding_sheet.csv
  prompts_audit.csv
```

They import in Antigone Lab → Browse / Code / Detail.

### Full (interpretation + your Python charts)

```
antigone_share_phase1_abc12345.zip
  run/
    manifest.json
    responses.jsonl
    coding_sheet.csv
    prompts_audit.csv
    responses_flat.csv
  charts/
    heatmap_p1_response_chars.png
    phase1_by_language.png
    aggregate_by_cell.csv
  README.txt                 ← one-line: what run this is
```

In Lovable, add an optional **Charts** page that displays images from `charts/` if present (ask Lovable in a follow-up prompt).

### After coding in Lovable

Use **Export coded CSV** in the app → that becomes the master for R / paper. You can also copy back to `coding_sheet.csv` locally.

---

## How to create a share zip (PowerShell)

```powershell
cd c:\dev\antigone

# After run.py — note your run_id from terminal output
$runId = "20250525T120000Z_abc12345"   # replace
$runDir = "logs\phase1_$runId"

# Optional: regenerate charts
.venv\Scripts\python analyze.py --phase 1 --run-id $runId

# Package
$out = "share\phase1_$runId"
New-Item -ItemType Directory -Force -Path "$out\run", "$out\charts" | Out-Null
Copy-Item "$runDir\*" "$out\run\"
Copy-Item "output\*.png" "$out\charts\" -ErrorAction SilentlyContinue
Copy-Item "output\aggregate_by_cell.csv" "$out\charts\"
Compress-Archive -Path $out -DestinationPath "share\phase1_$runId.zip" -Force
```

Send `share\phase1_$runId.zip` by email, Drive, or OneDrive.

---

## How collaborators get access

| Method | Who | What they see |
|--------|-----|----------------|
| **Zip + import** | Anyone with the file | Full app after upload; data stays in their browser / your Supabase if you configured it |
| **Supabase + Lovable URL** | Team with link | Persistent DB; read-only share link (build in Lovable phase 2) |
| **GitHub release** | Public / lab | Attach zip per run; no live app |
| **Screenshots / PNG only** | Supervisors quick look | `output/*.png` only — no interactive browse |
| **CSV in Excel** | Non-technical | `coding_sheet.csv` — no Lovable |

There is **no automatic sync** from `c:\dev\antigone\logs` to the cloud until you upload or connect Supabase storage yourself.

---

## Visualizations: two sources

| Source | When | Pros |
|--------|------|------|
| **`python analyze.py`** | After logs exist; before or after coding | Fast, fixed PNGs; good for slides |
| **Lovable Compare page** | After import | Interactive filters; uses coded VAR-A/B/D when filled |
| **Both** | Recommended | PNG for papers; app for exploration |

Heuristic charts from `analyze.py` are **exploratory** (keyword matching). Research charts should use **manual codes** from `coding_sheet.csv` / Lovable — either re-run analysis on coded CSV later or rely on Lovable charts.

---

## If you use Supabase (Lovable)

Typical setup:

1. You import run once → data in Supabase.
2. Collaborators open the **published Lovable URL**.
3. Role **editor**: can code. Role **viewer** (read-only link): browse + charts, no edit.

You still **run `run.py` locally**; then **Import** new runs when a collection wave finishes. New run = new import (or new `run_id` partition in DB).

---

## Checklist before sharing

- [ ] `run.py` finished; `manifest.json` shows expected `completed_ok` count
- [ ] `python analyze.py` run if you want PNGs in the zip
- [ ] Remove or redact anything sensitive from prompts/responses (if needed)
- [ ] Zip includes `prompts_audit.csv` so readers see full prompts
- [ ] Tell recipients which **phase** (1 or 2) and **run_id** the package is

---

## Quick answers

**Do I generate here first?**  
Yes. `run.py` → `logs/`. `analyze.py` → `output/`. Then upload to Lovable.

**Where do they save?**  
`c:\dev\antigone\logs\phase{N}_{run_id}\` and `c:\dev\antigone\output\`.

**Does Lovable watch that folder?**  
No. You import manually (or build a future sync script).

**How do they get access?**  
Share the zip or a Lovable app URL with Supabase backend.
