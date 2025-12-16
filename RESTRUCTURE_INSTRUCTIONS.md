# Manual repo reorganization plan (student-friendly folders)

This checklist describes where to place current files and which docs to edit when converting the repo to a student-friendly layout. Follow it step by step when the GitHub connector is available.

## Target folder layout (top level)
- `docs/`
  - `README.md` (USB transfer instructions)
  - `windows_faa_setup.md` (PowerShell walkthrough)
  - Add a short `README.md` inside `docs/` explaining what student guides live here.
- `scripts/`
  - `eeg/` (subfolder for EEG processing utilities)
    - `edf_to_fif_and_faa.py`
    - Add a short `README.md` inside `scripts/` or `scripts/eeg/` explaining how to run the scripts and expected inputs/outputs.
- `examples/`
  - `rename_channels.example.tsv`
  - `est13yo.edf` (or any curated demo EDF kept in git)
  - Add a short `README.md` inside `examples/` summarizing what the sample assets are for and any usage caveats.
- `requirements.txt`
- `.gitignore`

## File moves
- Move `README.md` → `docs/README.md`.
- Move `windows_faa_setup.md` → `docs/windows_faa_setup.md`.
- Move `edf_to_fif_and_faa.py` → `scripts/eeg/edf_to_fif_and_faa.py`.
- Move `rename_channels.example.tsv` → `examples/rename_channels.example.tsv`.
- Move `est13yo.edf` → `examples/est13yo.edf` (keep tracked only if size policy allows; otherwise note external location in the folder README).

## Document updates needed after moving files
- **`docs/windows_faa_setup.md`**: adjust all path references that currently point to the repo root. Specifically:
  - Section “2) One-time: Install Git + download the lab repo”: update the expectation after `dir` to mention `scripts/`, `docs/`, and `examples/` instead of flat files.【F:windows_faa_setup.md†L27-L58】
  - Section “5) Copy files from the USB…” and “5.3 Copy the script”: change the source path for the script from `lab_scripts\scripts\eeg\edf_to_fif_and_faa.py` (once moved) and update any mention of `rename_channels.tsv` location to `examples/` if students copy it from the repo.【F:windows_faa_setup.md†L75-L132】
  - Section “8) Run the script (one command)”: ensure the venv Python path still points to the repo root, but the script path in the example command should reference the new `scripts/eeg/` location if the command runs from within the repo rather than a working folder.【F:windows_faa_setup.md†L133-L164】
- **`docs/README.md`**: if it references example filenames or locations, confirm they still match the `examples/` folder (no path changes currently mentioned, but verify after move).【F:README.md†L1-L47】
- **New folder READMEs**: add brief context in `docs/`, `scripts/`/`scripts/eeg/`, and `examples/` so students know what lives there and how to use or copy the files.
- **Any future references**: search the repo for `edf_to_fif_and_faa.py` or `rename_channels` once moved to update relative paths in other materials (none beyond the two docs above today).

## Notes for the manual move
- Keep `.gitignore` rules for FIF/CSV outputs; update patterns if the new folder names change where outputs are produced.
- Preserve the rule that students run scripts from a working folder with EDF + TSV + script together; the docs should clarify where to copy the script from in the new layout.
- Avoid adding more sample EDFs unless they are small and intentionally tracked.
