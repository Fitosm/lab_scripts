# Secure “USB shuttle” instructions (students → instructor)

## What goes on the USB (and what does *not*)
- ✅ Put on USB:
  - **EDF files** (inputs)
  - **CSV outputs** (results)
  - **FIF outputs** (processed EEG files)
- ❌ Do NOT put on USB: project folders (`lab_scripts`, `hundoc`), `.venv`, screenshots, notes, or anything from `Downloads` you don’t mean to share

---

## One-time setup on the USB
1. Plug in the USB stick.
2. Open it (File Explorer on Windows / Finder on Mac).
3. Create a folder named exactly: `EEG_TRANSFER`
4. Inside `EEG_TRANSFER`, create two folders:
   - `IN` (inputs: EDF)
   - `OUT` (outputs: CSV + FIF)

Your USB should look like:

```text
EEG_TRANSFER/
  IN/
  OUT/
```

---

## Every time you transfer files

### A) Put EDF files onto the USB (IN folder)
1. Find your EDF file on your computer.
2. Copy it into `EEG_TRANSFER/IN/`.
3. Wait until copying finishes (progress bar/spinner disappears).

### B) Put output files onto the USB (OUT folder)
1. Find your output file(s) on your computer:
   - CSV (example: `faa_summary_sub-012.csv`)
   - FIF (example: `sub-012_clean-raw.fif`)
2. Copy them into `EEG_TRANSFER/OUT/`.
3. Wait until copying finishes.

---

## Safety steps (don’t skip)
1. Close Excel (or anything that opened the CSV) and any program that might be using the FIF.
2. **Eject** the USB:
   - **Windows:** click the USB/eject icon in the taskbar → Eject
   - **Mac:** in Finder, click the eject symbol next to the drive
3. Unplug only after it says it’s safe / the drive disappears.

---

## File naming rule
- Use **IDs only** (no names).
  - Examples: `sub-012.edf`, `faa_summary_sub-012.csv`, `sub-012_clean-raw.fif`
