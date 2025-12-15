#!/usr/bin/env python3
"""Clean a single EDF file, save a FIF, and compute log10 FAA (F4 - F3).

This student-friendly wrapper reuses the resting-state preprocessing steps
from ``preprocess_rest_eeg.py`` (montage assignment, filtering, notch, bad
channel detection, and interpolation). After cleaning, it computes frontal
alpha asymmetry (FAA) as ``log10(power_F4) - log10(power_F3)`` using Welch PSD
in the 8–13 Hz band.

Usage
-----
python scripts/eeg/edf_to_fif_and_faa.py \\
  --edf data_raw/resting_state/est001yo.edf \\
  --out-dir data_derived/eeg/student_clean

Inputs
------
- ``--edf``: Path to an EDF+ file with EEG channels.
- ``--rename-tsv`` (optional): Two-column TSV mapping original channel names to
  desired ones. Defaults to the repo template.

Outputs
-------
- Cleaned FIF file in ``<out-dir>`` with the suffix ``_clean.fif``.
- FAA CSV in ``<out-dir>`` with columns for participant ID, condition,
  ``log10_F3``, ``log10_F4``, and ``faa_log10`` (F4 - F3).
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Tuple

import mne
import numpy as np

from scripts.eeg.preprocess_rest_eeg import (
    TRAINING_CHANNELS,
    apply_channel_renames,
    detect_bad_channels_prep,
    detect_bad_channels_ptp,
    ensure_valid_eeg_positions,
    load_rename_map,
    parse_filename,
    set_channel_types_ignore_missing,
)

ALPHA_BAND: Tuple[float, float] = (8.0, 13.0)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Clean an EDF file with the standard pipeline and compute frontal "
            "alpha asymmetry (log10 F4 - log10 F3)."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--edf", required=True, type=Path, help="Path to EDF+ file")
    parser.add_argument(
        "--out-dir",
        required=True,
        type=Path,
        help="Directory for the cleaned FIF and FAA CSV outputs",
    )
    parser.add_argument("--l-freq", type=float, default=1.0, help="High-pass cutoff (Hz)")
    parser.add_argument("--h-freq", type=float, default=40.0, help="Low-pass cutoff (Hz)")
    parser.add_argument(
        "--notch-freqs",
        nargs="+",
        type=float,
        default=[50.0, 100.0],
        help="Notch filter frequencies (Hz)",
    )
    parser.add_argument("--ref", default="average", help="EEG reference type")
    parser.add_argument(
        "--rename-tsv",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "configs"
        / "rename_channels.example.tsv",
        help="TSV with original and desired channel names (two columns)",
    )
    parser.add_argument(
        "--bad-method",
        choices=["ptp", "prep"],
        default="prep",
        help="Bad channel detection: peak-to-peak (ptp) or PREP-inspired (prep)",
    )
    parser.add_argument("--bad-z-thresh-amp", type=float, default=5.0)
    parser.add_argument("--bad-z-thresh-corr", type=float, default=5.0)
    parser.add_argument("--bad-z-thresh-hf", type=float, default=5.0)
    parser.add_argument("--bad-z-thresh-ransac", type=float, default=5.0)
    parser.add_argument("--bad-lf-band", type=float, nargs=2, default=(1.0, 40.0))
    parser.add_argument("--bad-hf-band", type=float, nargs=2, default=(50.0, 125.0))
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def configure_logging(out_dir: Path) -> logging.Logger:
    out_dir.mkdir(parents=True, exist_ok=True)
    log_file = out_dir / "edf_to_fif_and_faa.log"
    logger = logging.getLogger("edf_to_fif_and_faa")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(fmt)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def compute_faa_log10(raw: mne.io.BaseRaw) -> dict[str, float]:
    """Return log10 PSD for F3/F4 (alpha band) and FAA as F4 - F3."""

    picks = {ch: idx for idx, ch in enumerate(raw.ch_names)}
    missing = [ch for ch in ("F3", "F4") if ch not in picks]
    if missing:
        raise RuntimeError(f"Missing required frontal channels: {', '.join(missing)}")

    psd = raw.compute_psd(
        method="welch",
        fmin=ALPHA_BAND[0],
        fmax=ALPHA_BAND[1],
        picks=["F3", "F4"],
    )
    power = psd.get_data()
    mean_power = power.mean(axis=1)
    log10_power = np.log10(mean_power)

    log10_f3 = float(log10_power[0])
    log10_f4 = float(log10_power[1])
    faa = log10_f4 - log10_f3
    return {
        "log10_F3": log10_f3,
        "log10_F4": log10_f4,
        "faa_log10": faa,
    }


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    logger = configure_logging(args.out_dir)

    try:
        rename_map = load_rename_map(args.rename_tsv)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return

    participant_id, condition = parse_filename(args.edf.stem)
    subject_label = participant_id or "unknown"
    logger.info("Processing %s (participant=%s, condition=%s)", args.edf.name, subject_label, condition)

    raw = mne.io.read_raw_edf(args.edf, preload=True, verbose="ERROR")

    apply_channel_renames(raw, rename_map, args.rename_tsv.name, logger)
    status_mapping = {"Status": "stim"}
    set_channel_types_ignore_missing(raw, status_mapping, logger, "Status stim channel")

    training_misc = {ch: "misc" for ch in TRAINING_CHANNELS if ch in raw.ch_names}
    if training_misc:
        set_channel_types_ignore_missing(raw, training_misc, logger, "training electrodes")

    montage = mne.channels.make_standard_montage("standard_1020")
    raw.set_montage(montage, on_missing="warn")
    raw.set_eeg_reference(args.ref)

    ensure_valid_eeg_positions(raw, logger)

    raw.filter(args.l_freq, args.h_freq, picks="eeg", method="fir", fir_design="firwin")
    raw.notch_filter(args.notch_freqs, picks="eeg")

    if args.bad_method == "ptp":
        bads = detect_bad_channels_ptp(raw)
    else:
        bads = detect_bad_channels_prep(
            raw,
            z_thresh_amp=args.bad_z_thresh_amp,
            z_thresh_corr=args.bad_z_thresh_corr,
            z_thresh_hf=args.bad_z_thresh_hf,
            z_thresh_ransac=args.bad_z_thresh_ransac,
            lf_band=tuple(args.bad_lf_band),
            hf_band=tuple(args.bad_hf_band),
            logger=logger,
        )
    raw.info["bads"] = bads
    logger.info("Marked %d bad channels: %s", len(bads), ", ".join(bads) if bads else "none")

    try:
        raw.interpolate_bads(reset_bads=False)
    except ValueError as exc:  # noqa: BLE001
        logger.warning("Skipping bad-channel interpolation: %s", exc)

    clean_fname = args.out_dir / f"{args.edf.stem}_clean.fif"
    raw.save(clean_fname, overwrite=True)
    logger.info("Saved cleaned FIF: %s", clean_fname)

    try:
        faa_metrics = compute_faa_log10(raw)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to compute FAA: %s", exc)
        return

    faa_csv = args.out_dir / f"{args.edf.stem}_faa.csv"
    faa_rows = {
        "participant_id": subject_label,
        "condition": condition,
        "alpha_band_hz": f"{ALPHA_BAND[0]}-{ALPHA_BAND[1]}",
        **faa_metrics,
    }
    import pandas as pd

    pd.DataFrame([faa_rows]).to_csv(faa_csv, index=False)
    logger.info("Saved FAA CSV: %s", faa_csv)


if __name__ == "__main__":
    main()
