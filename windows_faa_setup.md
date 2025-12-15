# Windows: Clean an EDF → save `_clean.fif` + compute FAA (`edf_to_fif_and_faa.py`)

## USB requirement (read this first)
Copy your outputs back onto the USB stick. The exact USB folder rules and step-by-step “USB shuttle” instructions are in the README in the repo root.

Outputs you must copy to USB:
- `*_clean.fif`
- `*_faa.csv`
- `edf_to_fif_and_faa.log`

---

## What this script does
It cleans one EDF (montage, filtering, notch, bad-channel detection + interpolation), saves a cleaned FIF, then computes FAA as:

`faa_log10 = log10(power_F4) - log10(power_F3)` using alpha 8–13 Hz.

---

## 0) Rules
1. Use PowerShell only.
2. Run commands inside the repo folder: `lab_scripts`.
3. Copy/paste commands exactly.
4. Put quotes around any path with spaces.

---

## 1) One-time installs

### Install Python 3.11+
1. Go to:
   ```text
   https://www.python.org/downloads/windows/
   ```
2. Download Python 3.11+ (64-bit).
3. Run the installer and check: “Add python.exe to PATH”.
4. Open PowerShell and run:
   ```powershell
   py --version
   ```
   If that fails:
   ```powershell
   python --version
   ```

### Install Git for Windows
Search “Git for Windows” and install it (defaults are fine).

---

## 2) One-time: download the repo (clone)

Open PowerShell.

Go to Documents:
```powershell
cd $HOME\Documents
```

Clone:
```powershell
git clone https://github.com/Fitosm/lab_scripts.git
```

Enter the folder:
```powershell
cd lab_scripts
```

Check you see the right files:
```powershell
dir
```
You should see `requirements.txt`, `scripts`, and `configs`.

---

## 3) One-time: create the environment + install packages (no activation)

From inside `lab_scripts`, run these one at a time:
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 4) Confirm the channel rename TSV exists (required)
This script expects channel names to be standardized (so it can find `F3` and `F4`). We do that using a TSV mapping file.

From inside `lab_scripts`, run:
```powershell
dir configs\rename_channels.example.tsv
```

If PowerShell says it cannot find that file, stop and tell the instructor.

---

## 5) Plug in the USB and locate your input/output folders
1. Plug in the USB stick.
2. Open File Explorer and click the USB drive (it will look like `USB (E:)` or similar).
3. Follow the repo-root README to find the USB `in` and `out` folders.

Example paths (yours will differ):
```text
Input EDF:  E:\lab_usb\in\est001yo.edf
Output dir: E:\lab_usb\out
```

Tip (best way to get the EDF path):
- Shift + right-click the EDF → “Copy as path”

---

## 6) Run the script (this is the command)

Go to the repo root (do this every time):
```powershell
cd $HOME\Documents\lab_scripts
```

Run (replace only the EDF path and output folder):
```powershell
.\.venv\Scripts\python.exe scripts\eeg\edf_to_fif_and_faa.py --edf "E:\lab_usb\in\est001yo.edf" --out-dir "E:\lab_usb\out" --rename-tsv "configs\rename_channels.example.tsv"
```

---

## 7) Check that the files were created

List what’s in the output folder:
```powershell
dir "E:\lab_usb\out"
```

You should see:
- `est001yo_clean.fif`
- `est001yo_faa.csv`
- `edf_to_fif_and_faa.log`

View the CSV:
```powershell
Get-Content "E:\lab_usb\out\est001yo_faa.csv"
```

If something failed, view the log:
```powershell
Get-Content "E:\lab_usb\out\edf_to_fif_and_faa.log"
```

---

## 8) Copy outputs to USB (required)
Copy these from the output folder to the USB, following the README’s folder rules:
- `*_clean.fif`
- `*_faa.csv`
- `edf_to_fif_and_faa.log`

---

## 9) Next time (normal workflow)
Go to the repo:
```powershell
cd $HOME\Documents\lab_scripts
```

Pull updates only if the instructor tells you to:
```powershell
git pull
```

Run the same command again (Section 6).

---

## Common problems

### “File not found” for the EDF
Your EDF path is wrong. Use “Copy as path” in File Explorer and paste it inside quotes.

### “Missing required frontal channels: F3, F4”
Renaming did not produce `F3` and `F4`.
Do not guess. Stop and tell the instructor.
