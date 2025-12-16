# EEG lab scripts (student-friendly overview)

This repo provides a single EEG preprocessing + frontal alpha asymmetry (FAA) script and student-facing guides for copying files and running the pipeline on lab machines.

## Repo layout (student-friendly folders)
- `docs/` — guides and checklists for students
  - `README.md`: USB "shuttle" rules for moving EDF inputs and FIF/CSV outputs
  - `windows_faa_setup.md`: step-by-step PowerShell walkthrough for running the script in a venv
- `scripts/eeg/` — runnable EEG utilities
  - `edf_to_fif_and_faa.py`: processes EDFs into cleaned FIF + FAA CSV
- `examples/` — sample assets students can copy alongside their own data
  - `rename_channels.example.tsv`: two-column channel rename template
  - `est13yo.edf`: curated demo EDF (keep tracked only if size policy allows)
- `requirements.txt` — minimal dependencies (mne, numpy, pandas)
- `RESTRUCTURE_INSTRUCTIONS.md` — checklist used to organize the repo into this layout

## Quick start: run the EEG → FIF/FAA pipeline
1. Copy `edf_to_fif_and_faa.py`, your EDF file(s), and a channel-rename TSV (use `rename_channels.example.tsv` as a template) into the same working folder.
2. From that folder, run `python edf_to_fif_and_faa.py` (PowerShell users: see `docs/windows_faa_setup.md` for the full venv + command sequence).
3. Outputs are written next to each EDF:
   - `<stem>_clean.fif`
   - `<stem>_faa.csv`
   - `edf_to_fif_and_faa.log`

## USB shuttle rules (students → instructor)
Follow these steps to move data safely between student machines and the instructor without syncing the whole repo.

1. **Set up the USB once**
   - Create a top-level folder named `EEG_TRANSFER` with two subfolders: `IN/` (EDF inputs) and `OUT/` (FIF + CSV outputs).
2. **Every transfer**
   - Copy EDF files into `EEG_TRANSFER/IN/`.
   - Copy output FIF + CSV files into `EEG_TRANSFER/OUT/`.
3. **Eject safely**
   - Close Excel or any program using the files, then eject the USB (Windows: taskbar eject icon; Mac: Finder eject button) before unplugging.
4. **File naming rule**
   - Use participant IDs only (examples: `sub-012.edf`, `sub-012_clean-raw.fif`, `faa_summary_sub-012.csv`).

## Need the detailed Windows guide?
See `docs/windows_faa_setup.md` for the full PowerShell walk-through, including venv creation and the single-line run command.
