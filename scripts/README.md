# EEG scripts

This folder holds runnable utilities for EEG preprocessing and analysis.

## `eeg/edf_to_fif_and_faa.py`
- Copy this script into the same working folder as your EDF file(s) and one channel-rename TSV (use `examples/rename_channels.example.tsv` as a template).
- Run it from that working folder with Python (see `docs/windows_faa_setup.md` for PowerShell commands).
- Outputs per EDF: `<stem>_clean.fif`, `<stem>_faa.csv`, and a shared `edf_to_fif_and_faa.log`.
