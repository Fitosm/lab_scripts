#!/usr/bin/env python3
"""Compute frontal alpha asymmetry (FAA) directly from an EDF file.

Usage
-----
python compute_faa_from_edf.py path/to/recording.edf [options]

Inputs
------
- EDF file containing EEG with at least F3 and F4 channels.
- Optional CLI parameters for montage, reference, filter bounds, alpha band, and
  PSD segment length.

Outputs (always next to this script)
------------------------------------
1) <edf_stem>_processed_raw_eeg.fif – filtered, re-referenced MNE Raw object.
2) <edf_stem>_faa.csv – single-row FAA summary for channels F3 (left) and
   F4 (right).

Processing steps
----------------
1) Load EDF and optionally apply a montage.
2) Apply re-reference and bandpass filtering.
3) Save the processed FIF (mandatory output).
4) Compute Welch PSD, average power in the 8–13 Hz alpha band for F3/F4, and
   take log10 of each.
5) Compute FAA as log10(F4) - log10(F3) and write the CSV summary.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable, Tuple

import mne
import numpy as np
import pandas as pd

ALPHA_BAND: Tuple[float, float] = (8.0, 13.0)
DEFAULT_FILTER: Tuple[float | None, float | None] = (1.0, 40.0)
DEFAULT_MONTAGE = "standard_1020"

# Fixed channels for this project
LEFT_CH = "F3"
RIGHT_CH = "F4"


def configure_logging(verbose: bool) -> None:
    """Set up basic console logging."""

    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")


def read_edf(path: Path, montage: str | None) -> mne.io.BaseRaw:
    """Load the EDF file and apply an optional montage."""

    logging.info("Loading EDF: %s", path)
    raw = mne.io.read_raw_edf(path, preload=True, verbose=False)
    if montage:
        try:
            raw.set_montage(montage, match_case=False, on_missing="ignore")
            logging.info("Applied montage: %s", montage)
        except Exception as exc:  # noqa: BLE001
            logging.warning("Could not set montage %s: %s", montage, exc)
    return raw


def apply_reference_and_filter(
    raw: mne.io.BaseRaw,
    reference: str | None,
    l_freq: float | None,
    h_freq: float | None,
) -> mne.io.BaseRaw:
    """Apply re-referencing and bandpass filtering."""

    if reference:
        logging.info("Re-referencing to %s", reference)
        raw.set_eeg_reference(reference)
    if l_freq is not None or h_freq is not None:
        logging.info("Bandpass filtering: l_freq=%s, h_freq=%s", l_freq, h_freq)
        raw.filter(l_freq=l_freq, h_freq=h_freq)
    return raw


def compute_alpha_power(
    raw: mne.io.BaseRaw,
    *,
    alpha_band: Tuple[float, float],
    segment_s: float | None,
) -> tuple[float, float]:
    """Return alpha-band power for fixed channels F3 (left) and F4 (right)."""

    if segment_s is not None and segment_s <= 0:
        raise ValueError("Segment length must be positive when provided")

    if LEFT_CH not in raw.ch_names or RIGHT_CH not in raw.ch_names:
        missing = [ch for ch in (LEFT_CH, RIGHT_CH) if ch not in raw.ch_names]
        raise ValueError(
            "Missing required channel(s) in EDF (must include F3 and F4): "
            + ", ".join(missing)
        )

    picks = mne.pick_channels(raw.ch_names, include=[LEFT_CH, RIGHT_CH])
    psd, freqs = mne.time_frequency.psd_welch(
        raw,
        fmin=alpha_band[0] - 2.0,
        fmax=alpha_band[1] + 2.0,
        picks=picks,
        n_per_seg=int(segment_s * raw.info["sfreq"]) if segment_s else None,
        average="mean",
        verbose=False,
    )

    alpha_mask = (freqs >= alpha_band[0]) & (freqs <= alpha_band[1])
    if not np.any(alpha_mask):
        raise RuntimeError("Alpha mask is empty; check alpha band or PSD range")

    alpha_power = psd[:, alpha_mask].mean(axis=1)

    # picks order is [F3, F4]
    left_power = float(alpha_power[0])
    right_power = float(alpha_power[1])
    return left_power, right_power


def to_output_frame(subject_id: str, left_power: float, right_power: float) -> pd.DataFrame:
    """Create a single-row DataFrame summarizing FAA for the fixed channels."""

    left_log = np.log10(left_power)
    right_log = np.log10(right_power)
    faa_log = right_log - left_log  # F4 - F3

    return pd.DataFrame(
        [
            {
                "subject_id": subject_id,
                "left_channel": LEFT_CH,
                "right_channel": RIGHT_CH,
                "alpha_power_left": left_power,
                "alpha_power_right": right_power,
                "alpha_power_left_log10": left_log,
                "alpha_power_right_log10": right_log,
                "faa_log10": faa_log,
            }
        ]
    )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("edf", type=Path, help="Path to the EDF recording")
    parser.add_argument(
        "--subject-id",
        type=str,
        default=None,
        help="Optional subject identifier (defaults to EDF stem)",
    )
    parser.add_argument(
        "--montage",
        type=str,
        default=DEFAULT_MONTAGE,
        help="Name of MNE montage to apply (set blank to skip)",
    )
    parser.add_argument(
        "--reference",
        type=str,
        default="average",
        help="EEG reference (e.g., 'average' or a channel name)",
    )
    parser.add_argument(
        "--l-freq",
        type=float,
        default=DEFAULT_FILTER[0],
        help="High-pass cutoff for bandpass filter (Hz)",
    )
    parser.add_argument(
        "--h-freq",
        type=float,
        default=DEFAULT_FILTER[1],
        help="Low-pass cutoff for bandpass filter (Hz)",
    )
    parser.add_argument(
        "--alpha-low",
        type=float,
        default=ALPHA_BAND[0],
        help="Lower bound of alpha band (Hz)",
    )
    parser.add_argument(
        "--alpha-high",
        type=float,
        default=ALPHA_BAND[1],
        help="Upper bound of alpha band (Hz)",
    )
    parser.add_argument(
        "--segment",
        type=float,
        default=None,
        help="Optional segment length in seconds for Welch PSD windows",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing output files",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.edf.exists():
        raise SystemExit(f"EDF file not found: {args.edf}")
    configure_logging(args.verbose)

    script_dir = Path(__file__).resolve().parent
    subject_id = args.subject_id or args.edf.stem

    # Outputs always next to this script
    out_fif = script_dir / f"{args.edf.stem}_processed_raw_eeg.fif"
    out_csv = script_dir / f"{args.edf.stem}_faa.csv"

    if out_fif.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite existing file: {out_fif}")
    if out_csv.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite existing file: {out_csv}")

    logging.info("Subject ID: %s", subject_id)
    logging.info("FAA channels fixed: right=%s, left=%s", RIGHT_CH, LEFT_CH)
    logging.info("Will write FIF: %s", out_fif)
    logging.info("Will write CSV: %s", out_csv)

    raw = read_edf(args.edf, args.montage or None)
    raw = apply_reference_and_filter(raw, args.reference or None, args.l_freq, args.h_freq)

    # Mandatory FIF output
    raw.save(out_fif, overwrite=args.overwrite)

    left_power, right_power = compute_alpha_power(
        raw,
        alpha_band=(args.alpha_low, args.alpha_high),
        segment_s=args.segment,
    )

    df = to_output_frame(subject_id, left_power, right_power)
    df.to_csv(out_csv, index=False)
    logging.info("Saved outputs: %s and %s", out_fif, out_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
