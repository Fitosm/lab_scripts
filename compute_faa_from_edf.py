#!/usr/bin/env python3
"""Compute frontal alpha asymmetry (FAA) directly from an EDF file.

Behavior (for this project)
---------------------------
- Channels are fixed: Left = F3, Right = F4.
- Outputs are always saved into the SAME folder as this script:
    1) <edf_stem>_processed_raw_eeg.fif
    2) <edf_stem>_faa.csv

Minimal example
---------------
python scripts/eeg/compute_faa_from_edf.py inputs/edf/example.edf
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
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")


def read_edf(path: Path, montage: str | None) -> mne.io.BaseRaw:
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
#!/usr/bin/env python3
"""Compute frontal alpha asymmetry (FAA) directly from an EDF file.

This script is designed for students who want a transparent, end-to-end FAA
calculation without relying on intermediate FIF files. It performs the
following steps:

1. Load an EDF recording with MNE-Python.
2. Apply an optional montage (10-20 by default) and average reference.
3. Bandpass filter the data (default 1–40 Hz) to focus on physiologic EEG.
4. Estimate channel-wise power spectral density (PSD) with Welch's method.
5. Summarize alpha (8–13 Hz) band power for left/right frontal channels.
6. Compute FAA as ``log10(alpha_right) - log10(alpha_left)``.
7. Save a tidy CSV that is easy to import into statistics notebooks.

Outputs
-------
- CSV with one row containing ``subject_id``, ``left_channel``,
  ``right_channel``, ``alpha_power_left``, ``alpha_power_right``,
  ``alpha_power_left_log10``, ``alpha_power_right_log10``, and ``faa_log10``.

Minimal example (Windows-friendly)
----------------------------------
```
python scripts/eeg/compute_faa_from_edf.py ^
  inputs/edf/example.edf ^
  --out derived/eeg/faa/example_faa.csv
```
The caret (``^``) is the Windows line continuation symbol; replace it with a
backslash (``\``) on macOS/Linux.

Notes
-----
- By default, the script expects standard 10-20 channel names and uses F3 (left)
  and F4 (right). Override them with ``--left``/``--right`` if your montage uses
  different labels (e.g., ``F7``/``F8``).
- The PSD calculation uses epochs as long as the recording; adjust ``--segment``
  if shorter windows are desired.
- FAA is computed on log10 power to reduce skew; this matches common approaches
  in the literature.
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


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def configure_logging(verbose: bool) -> None:
    """Configure console logging."""

    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")


def read_edf(path: Path, montage: str | None) -> mne.io.BaseRaw:
    """Load EDF data with an optional montage."""

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
    left: str,
    right: str,
    *,
    alpha_band: Tuple[float, float] = ALPHA_BAND,
    segment_s: float | None = None,
) -> tuple[float, float]:
    """Return alpha-band power for left and right channels."""

    if left not in raw.ch_names or right not in raw.ch_names:
        missing = [ch for ch in (left, right) if ch not in raw.ch_names]
        raise ValueError(f"Missing channel(s) in EDF: {', '.join(missing)}")

    picks = mne.pick_channels(raw.ch_names, include=[left, right])
    logging.debug("Using channel picks: %s", picks)

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
    left_power, right_power = float(alpha_power[0]), float(alpha_power[1])
    logging.debug("Alpha power left=%s, right=%s", left_power, right_power)
    return left_power, right_power


def to_output_frame(
    subject_id: str,
    left: str,
    right: str,
    left_power: float,
    right_power: float,
) -> pd.DataFrame:
    """Create a single-row DataFrame summarizing FAA."""

    left_log = np.log10(left_power)
    right_log = np.log10(right_power)
    faa_log = right_log - left_log

    return pd.DataFrame(
        [
            {
                "subject_id": subject_id,
                "left_channel": left,
                "right_channel": right,
                "alpha_power_left": left_power,
                "alpha_power_right": right_power,
                "alpha_power_left_log10": left_log,
                "alpha_power_right_log10": right_log,
                "faa_log10": faa_log,
            }
        ]
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("edf", type=Path, help="Path to the EDF recording")
    parser.add_argument("--out", type=Path, required=True, help="Output CSV path")
    parser.add_argument(
        "--subject-id",
        type=str,
        default=None,
        help="Optional subject identifier (defaults to EDF stem)",
    )
    parser.add_argument("--left", type=str, default="F3", help="Left frontal channel")
    parser.add_argument("--right", type=str, default="F4", help="Right frontal channel")
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
        help="Allow overwriting an existing output CSV",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging for step-by-step visibility",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose)

    if args.out.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite existing file: {args.out}")

    subject_id = args.subject_id or args.edf.stem
    logging.info("Subject ID: %s", subject_id)

    raw = read_edf(args.edf, args.montage or None)
    raw = apply_reference_and_filter(raw, args.reference or None, args.l_freq, args.h_freq)

    left_power, right_power = compute_alpha_power(
        raw,
        args.left,
        args.right,
        alpha_band=(args.alpha_low, args.alpha_high),
        segment_s=args.segment,
    )

    df = to_output_frame(subject_id, args.left, args.right, left_power, right_power)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    logging.info("Saved FAA summary to %s", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
