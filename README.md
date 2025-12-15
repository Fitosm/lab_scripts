# lab_scripts
scripts for processing EEG files

# Secure “USB shuttle” instructions (Windows students ↔ instructor)

## What goes on the USB (and what does *not*)
- ✅ Put on USB: the **EDF** files and the **output CSV** (e.g., `faa_summary.csv`)
- ❌ Do NOT put on USB: the whole `lab_scripts` folder, `.venv`, or anything in `C:\Users\...\AppData\...`

---

## Student instructions (Windows)

### 1) Use the “right” USB behavior
1. Plug in the USB stick.
2. If Windows asks what to do, choose **Open folder to view files**.
3. Create a folder on the USB named exactly: `EEG_TRANSFER`
4. Inside `EEG_TRANSFER`, create two folders:
   - `IN`
   - `OUT`

### 2) Copy EDFs to the USB (IN folder)
1. In File Explorer, go to where your EDF is (example: `C:\EEG\`).
2. Right-click the EDF file → **Copy**.
3. Go to the USB → `EEG_TRANSFER\IN\`
4. Right-click empty space → **Paste**.
5. Wait until copying finishes (the progress bar disappears).

### 3) Run the script using the EDF from the USB (recommended)
This avoids extra copies and makes it obvious what file was used.

In PowerShell (from inside the `lab_scripts` folder), run:

```powershell
.\.venv\Scripts\python.exe scripts\eeg\compute_faa_from_edf.py "E:\EEG_TRANSFER\IN\subject1.edf" --out "E:\EEG_TRANSFER\OUT\faa_summary_subject1.csv" --left F3 --right F4 --montage standard_1020 --reference average --l-freq 1 --h-freq 40
```

**Important:** Your USB drive letter might not be `E:`. To find it:
- File Explorer → “This PC” → look for the USB drive letter (D:, E:, F:, etc.)
- Replace `E:` in the command with your letter.

### 4) Confirm the output file exists on the USB
In PowerShell:

```powershell
dir E:\EEG_TRANSFER\OUT
```

(Replace `E:` with your USB letter.) You should see the CSV file.

### 5) Safely eject the USB (this matters)
1. Close any Excel window that opened the CSV.
2. In the taskbar, click the **USB/eject icon** (may be under the `^` arrow).
3. Click **Eject USB Drive**.
4. Wait for “Safe to remove hardware”, then unplug.

---

## Instructor instructions (Mac)

### 1) Copy from USB to your Mac
1. Insert USB.
2. Finder → open `EEG_TRANSFER/OUT/`
3. Drag the CSVs to a folder on your Mac, e.g. `~/Documents/FAA_from_students/`

### 2) Safely eject
Finder → click the **eject icon** next to the USB drive name → remove.

---

## Basic security rules (include these in the handout)
- **If files are sensitive:** require an **encrypted USB** (hardware-encrypted) or BitLocker To Go (if available).
- **Do not use random USB sticks:** use only the one provided for the course.
- **Never email EDFs** and don’t upload to personal cloud (Google Drive/OneDrive) unless explicitly instructed.
- **Use IDs, not names** in filenames (e.g., `sub-012_YO.edf`, not `JaneDoe.edf`).
- **If a USB is lost, report immediately.**

**One-sentence rule:** Only move the EDF and output CSV via the USB in `EEG_TRANSFER\IN` and `EEG_TRANSFER\OUT`, always eject safely, and never include names in filenames.

