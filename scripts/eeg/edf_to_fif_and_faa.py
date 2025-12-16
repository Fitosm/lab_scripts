#!/usr/bin/env python3
"""Clean EDF files sitting alongside this script, then compute log10 FAA (F4 - F3).

This self-contained helper follows the PREP-style preprocessing pipeline that
previously yielded the most usable data in this repository. Settings are fully
listed here so students know exactly what happens to the data:

- Mandatory channel renaming via the only ``*.tsv`` in the same folder.
- Standard 10-20 montage assignment with ``on_missing='warn'``.
- EEG average reference (``kind='average'``).
- FIR bandpass filter on EEG: 1–40 Hz (``firwin`` design).
- Notch filter on EEG: 50 and 100 Hz.
- Re-type channels lacking finite positions or overlapping positions to
  ``misc`` before interpolation.
- PREP-inspired bad-channel detection using robust z-scores:
  - Amplitude z-threshold: 5.0 (log10 peak-to-peak after downsampling).
  - Correlation z-threshold: 5.0 (1 - |r| against channel median).
  - High-frequency ratio z-threshold: 5.0 (50–125 Hz vs 1–40 Hz power).
  - RANSAC-style predictability z-threshold: 5.0.
- Bad-channel interpolation with ``reset_bads=False``.
- Frontal alpha asymmetry (FAA) as ``log10(power_F4) - log10(power_F3)`` in the
  8–13 Hz band, saved to CSV.

Usage
-----
1. Place this script, at least one ``.edf`` file, and a two-column channel
   rename TSV (original name, desired name) in the **same folder**.
2. Run ``python edf_to_fif_and_faa.py`` from that folder.

Inputs (same folder as the script)
----------------------------------
- One or more EDF+ files.
- A mandatory two-column TSV mapping original channel names to desired ones.

Outputs (same folder as the script)
-----------------------------------
- One cleaned FIF per EDF (``<stem>_clean_eeg.fif``).
- One FAA CSV per EDF with participant, condition, ``log10_F3``, ``log10_F4``,
  and ``faa_log10`` (F4 - F3).
"""
from __future__ import annotations

import csv
import logging
import re
from pathlib import Path
from typing import Iterable, Tuple

import mne
import numpy as np
from mne.time_frequency import psd_array_welch

ALPHA_BAND: Tuple[float, float] = (8.0, 13.0)
TRAINING_CHANNELS = ["[T1] EEG Trainin", "[T2] EEG Trainin"]
L_FREQ = 1.0
H_FREQ = 40.0
NOTCH_FREQS = [50.0, 100.0]
REF_KIND = "average"
BAD_Z_THRESH_AMP = 5.0
BAD_Z_THRESH_CORR = 5.0
BAD_Z_THRESH_HF = 5.0
BAD_Z_THRESH_RANSAC = 5.0
BAD_LF_BAND: Tuple[float, float] = (1.0, 40.0)
BAD_HF_BAND: Tuple[float, float] = (50.0, 125.0)
SCRIPT_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_filename(filename: str) -> Tuple[str | None, str]:
    """Extract participant ID and condition from an EDF stem.

    Filenames like ``est001yo.edf`` map to participant ``001`` with condition
    ``eyes-open``. ``est001yc.edf`` maps to ``eyes-closed``. Anything else is
    labeled ``unknown``.
    """

    stem = Path(filename).stem
    match = re.search(r"est(?P<id>\d+)(?P<cond>yo|yc)?$", stem, flags=re.IGNORECASE)
    participant_id = match.group("id") if match else None
    cond_suffix = match.group("cond").lower() if match and match.group("cond") else ""
    if cond_suffix == "yo":
        condition = "eyes-open"
    elif cond_suffix == "yc":
        condition = "eyes-closed"
    else:
        condition = "unknown"
    return participant_id, condition


def _robust_zscore(values: np.ndarray) -> np.ndarray:
    """Compute robust z-scores using median and MAD with epsilon fallback."""

    med = np.median(values)
    mad = np.median(np.abs(values - med))
    if mad == 0:
        mad = 1e-12
    return (values - med) / (1.4826 * mad)


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


def load_rename_map(tsv_path: Path, logger: logging.Logger) -> dict[str, str]:
    """Load mandatory channel rename mapping from a two-column TSV."""

    if not tsv_path.exists():
        raise FileNotFoundError(f"Rename TSV not found: {tsv_path}")

    rename_map: dict[str, str] = {}
    with tsv_path.open("r", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            if len(row) < 2:
                continue
            original, new = (cell.strip() for cell in row[:2])
            if not original or not new:
                continue

            candidates = {original}
            if "+" in original:
                candidates.add(original.replace("+", "~"))
            if "~" in original:
                candidates.add(original.replace("~", "+"))

            for key in candidates:
                rename_map.setdefault(key, new)
    if not rename_map:
        raise ValueError(f"Rename TSV is empty: {tsv_path}")

    return rename_map


def find_single_tsv(directory: Path, logger: logging.Logger) -> Path:
    """Find exactly one TSV in ``directory`` for channel renaming."""

    tsvs = sorted(directory.glob("*.tsv"))
    if not tsvs:
        raise FileNotFoundError(
            f"No TSV found in {directory}; add a two-column channel rename TSV."
        )
    if len(tsvs) > 1:
        raise RuntimeError(
            "Multiple TSV files found; keep only the channel rename TSV: "
            + ", ".join(t.name for t in tsvs)
        )

    chosen = tsvs[0]
    logger.info("Using channel rename TSV: %s", chosen.name)
    return chosen


def find_edf_files(directory: Path) -> Iterable[Path]:
    """Yield EDF files in ``directory`` sorted by name."""

    return sorted(directory.glob("*.edf"))


def set_channel_types_ignore_missing(
    raw: mne.io.BaseRaw, mapping: dict[str, str], logger: logging.Logger, context: str
) -> None:
    """Set channel types while tolerating missing channels on older MNE versions."""

    if not mapping:
        return

    try:
        raw.set_channel_types(mapping, on_missing="ignore")
    except TypeError as exc:
        logger.debug(
            "set_channel_types missing on_missing support while handling %s; retrying without ignore (%s)",
            context,
            exc,
        )
        present = {ch: kind for ch, kind in mapping.items() if ch in raw.ch_names}
        missing = sorted(set(mapping) - set(present))
        if missing:
            logger.info(
                "Channels missing when setting types for %s: %s", context, ", ".join(missing)
            )
        if present:
            raw.set_channel_types(present)


def apply_channel_renames(
    raw: mne.io.BaseRaw, rename_map: dict[str, str], rename_label: str, logger: logging.Logger
) -> None:
    """Rename channels using the provided mapping and set EEG types."""

    if not rename_map:
        logger.info("No rename map provided; keeping channel names as-is")
        return

    present_map = {orig: new for orig, new in rename_map.items() if orig in raw.ch_names}
    if present_map:
        raw.rename_channels(present_map)
        present_eeg = {new: "eeg" for new in present_map.values()}
        set_channel_types_ignore_missing(
            raw,
            present_eeg,
            logger,
            f"channel renaming via {rename_label}",
        )
        logger.info("Renamed %d channels using %s", len(present_map), rename_label)

    missing_keys = set(rename_map) - set(present_map)
    for orig in present_map:
        if "+" in orig:
            missing_keys.discard(orig.replace("+", "~"))
        if "~" in orig:
            missing_keys.discard(orig.replace("~", "+"))

    missing = sorted(missing_keys)
    if missing:
        logger.info("Channels from rename template not found: %s", ", ".join(missing))


def _retype_eeg_without_positions(raw: mne.io.BaseRaw, logger: logging.Logger) -> None:
    eeg_picks = mne.pick_types(raw.info, eeg=True, meg=False)
    if len(eeg_picks) == 0:
        return

    to_misc: dict[str, str] = {}
    for idx in eeg_picks:
        ch = raw.info["chs"][idx]
        loc = np.asarray(ch["loc"][:3], float)
        if loc.shape[0] != 3 or not np.all(np.isfinite(loc)):
            ch_name = raw.ch_names[idx]
            logger.warning(
                "Channel %s lacks a finite position; retyping as 'misc' to avoid interpolation failures",
                ch_name,
            )
            to_misc[ch_name] = "misc"

    if to_misc:
        set_channel_types_ignore_missing(
            raw,
            to_misc,
            logger,
            "EEG channels without finite positions",
        )


def _deduplicate_overlapping_eeg_positions(
    raw: mne.io.BaseRaw, logger: logging.Logger, decimal: int = 6
) -> None:
    eeg_picks = mne.pick_types(raw.info, eeg=True, meg=False)
    if len(eeg_picks) == 0:
        return

    pos_seen: dict[tuple[float, float, float], str] = {}
    to_misc: dict[str, str] = {}

    for idx in eeg_picks:
        ch = raw.info["chs"][idx]
        loc = np.asarray(ch["loc"][:3], float)
        if loc.shape[0] != 3:
            continue
        key = tuple(np.round(loc, decimal))
        if key in pos_seen:
            ch_name = raw.ch_names[idx]
            first_name = pos_seen[key]
            logger.warning(
                "Channel %s shares position with %s; retyping %s as 'misc' to avoid overlapping topomap issues",
                ch_name,
                first_name,
                ch_name,
            )
            to_misc[ch_name] = "misc"
        else:
            pos_seen[key] = raw.ch_names[idx]

    if to_misc:
        set_channel_types_ignore_missing(
            raw,
            to_misc,
            logger,
            "deduplicate overlapping EEG positions",
        )


def ensure_valid_eeg_positions(raw: mne.io.BaseRaw, logger: logging.Logger) -> None:
    """Retype channels without usable positions and drop overlapping EEG sites."""

    _retype_eeg_without_positions(raw, logger)
    _deduplicate_overlapping_eeg_positions(raw, logger)


def detect_bad_channels_prep(
    raw: mne.io.BaseRaw,
    z_thresh_amp: float = 5.0,
    z_thresh_corr: float = 5.0,
    z_thresh_hf: float = 5.0,
    z_thresh_ransac: float = 5.0,
    lf_band: Tuple[float, float] = (1.0, 40.0),
    hf_band: Tuple[float, float] = (50.0, 125.0),
    logger: logging.Logger | None = None,
) -> list[str]:
    """PREP-inspired bad channel detection using robust z-score criteria."""

    eeg_picks = mne.pick_types(raw.info, eeg=True, meg=False)
    if len(eeg_picks) == 0:
        return []

    data = raw.get_data(picks=eeg_picks)
    sfreq = raw.info["sfreq"]
    n_chans, n_times = data.shape

    ds = max(1, int(n_times // 20000))
    data_ds = data[:, ::ds]

    amp = np.ptp(data_ds, axis=1)
    z_amp = _robust_zscore(np.log10(amp + np.finfo(float).eps))
    bad_amp = set(np.where(np.abs(z_amp) > z_thresh_amp)[0])

    bad_corr: set[int] = set()
    uncorr_vals = []
    for idx in range(n_chans):
        others = np.delete(data_ds, idx, axis=0)
        if others.size == 0:
            uncorr_vals.append(0.0)
            continue
        y = np.median(others, axis=0)
        r = np.corrcoef(data_ds[idx], y)[0, 1]
        uncorr_vals.append(1.0 if np.isnan(r) else 1.0 - np.abs(r))
    z_corr = _robust_zscore(np.asarray(uncorr_vals))
    bad_corr.update(np.where(z_corr > z_thresh_corr)[0])

    psd, freqs = psd_array_welch(data, sfreq=sfreq, average="mean")
    lf_mask = (freqs >= lf_band[0]) & (freqs <= lf_band[1])
    hf_mask = (freqs >= hf_band[0]) & (freqs <= hf_band[1])
    lf_power = np.trapz(psd[:, lf_mask], freqs[lf_mask], axis=1)
    hf_power = np.trapz(psd[:, hf_mask], freqs[hf_mask], axis=1)
    hf_ratio = np.log10((hf_power + np.finfo(float).eps) / (lf_power + np.finfo(float).eps))
    z_hf = _robust_zscore(hf_ratio)
    bad_hf = set(np.where(z_hf > z_thresh_hf)[0])

    bad_ransac: set[int] = set()
    pred_errors = []
    for idx in range(n_chans):
        others = np.delete(data_ds, idx, axis=0)
        if others.size == 0:
            pred_errors.append(0.0)
            continue
        X = others.T
        y = data_ds[idx]
        try:
            coefs, *_ = np.linalg.lstsq(X, y, rcond=None)
            y_hat = X @ coefs
            r_pred = np.corrcoef(y, y_hat)[0, 1]
            pred_error = 1.0 if np.isnan(r_pred) else 1.0 - np.abs(r_pred)
        except np.linalg.LinAlgError:
            pred_error = 1.0
        pred_errors.append(pred_error)
    z_ransac = _robust_zscore(np.asarray(pred_errors))
    bad_ransac.update(np.where(z_ransac > z_thresh_ransac)[0])

    bad_indices = bad_amp | bad_corr | bad_hf | bad_ransac
    bads = sorted([raw.ch_names[eeg_picks[i]] for i in bad_indices])

    if logger:
        logger.info(
            "PREP-like bad channels: %d (amp=%d, corr=%d, hf=%d, ransac=%d)",
            len(bads),
            len(bad_amp),
            len(bad_corr),
            len(bad_hf),
            len(bad_ransac),
        )
    return bads


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

def process_edf(
    edf_path: Path,
    rename_map: dict[str, str],
    rename_label: str,
    logger: logging.Logger,
) -> None:
    """Run the PREP-style pipeline on a single EDF and compute FAA."""

    participant_id, condition = parse_filename(edf_path.stem)
    subject_label = participant_id or "unknown"
    logger.info(
        "Processing %s (participant=%s, condition=%s)", edf_path.name, subject_label, condition
    )

    raw = mne.io.read_raw_edf(edf_path, preload=True, verbose="ERROR")

    apply_channel_renames(raw, rename_map, rename_label, logger)
    status_mapping = {"Status": "stim"}
    set_channel_types_ignore_missing(raw, status_mapping, logger, "Status stim channel")

    training_misc = {ch: "misc" for ch in TRAINING_CHANNELS if ch in raw.ch_names}
    if training_misc:
        set_channel_types_ignore_missing(raw, training_misc, logger, "training electrodes")

    montage = mne.channels.make_standard_montage("standard_1020")
    raw.set_montage(montage, on_missing="warn")
    raw.set_eeg_reference(REF_KIND)

    ensure_valid_eeg_positions(raw, logger)

    raw.filter(L_FREQ, H_FREQ, picks="eeg", method="fir", fir_design="firwin")
    raw.notch_filter(NOTCH_FREQS, picks="eeg")

    bads = detect_bad_channels_prep(
        raw,
        z_thresh_amp=BAD_Z_THRESH_AMP,
        z_thresh_corr=BAD_Z_THRESH_CORR,
        z_thresh_hf=BAD_Z_THRESH_HF,
        z_thresh_ransac=BAD_Z_THRESH_RANSAC,
        lf_band=BAD_LF_BAND,
        hf_band=BAD_HF_BAND,
        logger=logger,
    )
    raw.info["bads"] = bads
    logger.info("Marked %d bad channels: %s", len(bads), ", ".join(bads) if bads else "none")

    try:
        raw.interpolate_bads(reset_bads=False)
    except ValueError as exc:  # noqa: BLE001
        logger.warning("Skipping bad-channel interpolation: %s", exc)

    clean_fname = edf_path.with_name(f"{edf_path.stem}_clean_eeg.fif")
    raw.save(clean_fname, overwrite=True)
    logger.info("Saved cleaned FIF: %s", clean_fname)

    faa_csv = edf_path.with_name(f"{edf_path.stem}_faa.csv")
    try:
        faa_metrics = compute_faa_log10(raw)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to compute FAA for %s: %s", edf_path.name, exc)
        return

    faa_rows = {
        "participant_id": subject_label,
        "condition": condition,
        "alpha_band_hz": f"{ALPHA_BAND[0]}-{ALPHA_BAND[1]}",
        **faa_metrics,
    }
    with faa_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(faa_rows))
        writer.writeheader()
        writer.writerow(faa_rows)
    logger.info("Saved FAA CSV: %s", faa_csv)


def main() -> None:
    logger = configure_logging(SCRIPT_DIR)

    try:
        rename_tsv = find_single_tsv(SCRIPT_DIR, logger)
        rename_map = load_rename_map(rename_tsv, logger)
    except Exception as exc:  # noqa: BLE001
        logger.error("Rename TSV required but unavailable: %s", exc)
        return

    edf_files = list(find_edf_files(SCRIPT_DIR))
    if not edf_files:
        logger.error("No EDF files found next to this script in %s", SCRIPT_DIR)
        return

    for edf_path in edf_files:
        try:
            process_edf(edf_path, rename_map, rename_tsv.name, logger)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to process %s: %s", edf_path.name, exc)


if __name__ == "__main__":
    main()
