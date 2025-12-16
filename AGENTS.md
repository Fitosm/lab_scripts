# Guidance for Codex (and future maintainers) working on this lab repo

## A) Repository map
- `edf_to_fif_and_faa.py`: Canonical preprocessing + FAA pipeline. Run in the folder containing the EDF(s) and one channel-rename TSV; writes outputs next to inputs. Self-contained (no package layout).
- `rename_channels.example.tsv`: Example two-column mapping (original → desired channel names) expected to live beside the script/EDFs.
- `est13yo.edf`: Example EDF data file in the root (avoid modifying or relying on it for automated checks).
- `README.md`: Student-facing USB transfer rules and file naming expectations.
- `windows_faa_setup.md`: Step-by-step student instructions for running `edf_to_fif_and_faa.py` on Windows with a venv created from `requirements.txt`.
- `requirements.txt`: Minimal dependency pins (mne, numpy, pandas) for running the pipeline.
- `.gitignore`: Ignores FIF and CSV outputs; keep it aligned with generated artifacts.

## B) Data and artifact policy
- Never commit analysis outputs (FIF, FIF.gz, CSV) or large derived data. `.gitignore` already ignores these patterns; respect and extend rather than remove them.
- Raw EDF files should stay out of commits unless explicitly curated/examples; prefer referencing external locations. The tracked `est13yo.edf` is an example—avoid adding more unless necessary.
- Scripts assume inputs and outputs live alongside the script (same directory). `edf_to_fif_and_faa.py` writes `<stem>_clean.fif`, `<stem>_faa.csv`, and `edf_to_fif_and_faa.log` next to each EDF.
- Keep naming consistent with the script conventions (`<stem>_clean.fif`, `<stem>_faa.csv`) and README examples (e.g., `sub-012_clean-raw.fif`, `faa_summary_sub-012.csv`).

## C) Script design rules (adding/editing scripts)
- Prefer self-contained, runnable-from-folder scripts using `argparse`-style CLIs only when necessary; current canonical script has no CLI args and derives paths relative to its own location.
- Avoid hard-coded absolute paths. Use repo-relative paths or `Path(__file__).resolve().parent` patterns so scripts work when copied beside data.
- Log to both console and a log file in the working directory (see `configure_logging` in `edf_to_fif_and_faa.py`), and include enough context for reproducibility (file names, thresholds).
- Maintain cross-platform friendliness: avoid shell-specific features, require PowerShell-friendly quoting when documenting commands, and keep path joins portable (`pathlib`).

## D) Dependency and environment rules
- Dependencies are managed via `requirements.txt`; update it when imports change. Pin new packages minimally and prefer tightening existing ranges.
- Adding dependencies should be rare and justified by script needs. Document the reason in the commit/PR message and adjust any setup docs (e.g., `windows_faa_setup.md`) if install steps change.

## E) Change policy for Codex
- Make the minimal patch necessary; do not refactor unrelated code or reorganize files without need.
- Touch as few files as possible; preserve existing CLI contracts and behavioral expectations (e.g., outputs written alongside inputs, required TSV presence).
- If behavior changes, update relevant docs/comments in the same scope to keep student instructions accurate.

## F) Verification checklist
- Basic sanity: `python -m py_compile edf_to_fif_and_faa.py` (no data required).
- If working manually with data, run `python edf_to_fif_and_faa.py` in a folder containing at least one EDF and exactly one channel-rename TSV; confirm creation of `<stem>_clean.fif`, `<stem>_faa.csv`, and `edf_to_fif_and_faa.log` next to the inputs.
- After changes involving dependencies, confirm `pip install -r requirements.txt` succeeds in a fresh venv.
