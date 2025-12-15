# Windows: Run `compute_faa_from_edf.py`

## Important note about USB (read this first)
- Your **outputs** (the `.csv` and `.fif`) **must be copied onto the USB stick** so you can bring them back to the instructor.
- The **exact USB folder rules + step-by-step “USB shuttle” instructions** are in the **README in the root of this repo**. Follow that README for where to put files on the USB.
- **New script behavior:** output files are **NOT** written next to your EDF. They are written **next to the script** inside the repo.

---

## What you are doing (in one sentence)
You will (1) install Python, (2) download our lab code using **git**, (3) install Python packages into a local folder, and (4) run one command that reads an EDF and writes a **CSV + FIF**.

---

## 0) Rules to start out with
1. Do everything in **PowerShell**.
2. Always run commands from inside the project folder: **`lab_scripts`**.
3. Copy/paste commands exactly.
4. If a path has spaces, wrap it in quotes: `"C:\Path With Spaces\file.edf"`.

---

## 1) Install Python 3.11+ (one time)
1. Go to:
   ```text
   https://www.python.org/downloads/windows/
   ```
2. Download Python 3.11+ (64-bit).
3. Run installer and **CHECK**: ✅ **Add python.exe to PATH**
4. Open PowerShell and run:
   ```powershell
   py --version
   ```
   If `py` fails:
   ```powershell
   python --version
   ```

---

## 2) Clone the repo (first time on this computer)

### 2.1 Install Git for Windows
Search “Git for Windows” and install it (defaults are fine).

### 2.2 Open PowerShell, go to Documents
```powershell
cd $HOME\Documents
```

### 2.3 Clone
```powershell
git clone https://github.com/Fitosm/lab_scripts.git
```

### 2.4 Enter the folder
```powershell
cd lab_scripts
```

### 2.5 Confirm you’re in the right place
```powershell
dir
```
You should see `requirements.txt` and a `scripts` folder.

---

## 3) Create the Python environment + install packages (first time on this computer)
**No activation** (this avoids Windows execution-policy problems).

Run these one at a time:
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 4) Put your EDF somewhere simple
Put your EDF file somewhere easy, for example:
```text
C:\EEG\subject1.edf
```

Tip: In File Explorer, **Shift + right-click** the EDF → **Copy as path**.

---

## 5) Run the script (UPDATED command)
### 5.1 Make sure you are in the repo folder
```powershell
cd $HOME\Documents\lab_scripts
```

### 5.2 Run (replace only the EDF path)
```powershell
.\.venv\Scripts\python.exe scripts\eeg\compute_faa_from_edf.py "C:\EEG\subject1.edf" --reference average --l-freq 1 --h-freq 40
```

### What the script does (important changes)
- Channels are **fixed**: **F3 (left)** and **F4 (right)**. 
- It always writes **two outputs** **next to the script** (inside the repo):
  - `scripts\eeg\<edf_stem>_processed_raw_eeg.fif`
  - `scripts\eeg\<edf_stem>_faa.csv`

Example: if your EDF is `subject1.edf`, outputs will be:
- `scripts\eeg\subject1_processed_raw_eeg.fif`
- `scripts\eeg\subject1_faa.csv`

### If you need to skip montage
The script tries `standard_1020` by default. To skip montage:
```powershell
.\.venv\Scripts\python.exe scripts\eeg\compute_faa_from_edf.py "C:\EEG\subject1.edf" --montage ""
```

### If you re-run the same EDF and it refuses to overwrite
By default it will stop if the output files already exist. To overwrite:
```powershell
.\.venv\Scripts\python.exe scripts\eeg\compute_faa_from_edf.py "C:\EEG\subject1.edf" --overwrite
```

---

## 6) Check the outputs (UPDATED locations)
List what got created:
```powershell
dir .\scripts\eeg\
```

View the CSV:
```powershell
Get-Content .\scripts\eeg\subject1_faa.csv
```

---

## 7) Copy outputs to the USB stick (required)
1. Plug in the USB stick.
2. Find the outputs in:
   ```text
   lab_scripts\scripts\eeg\
   ```
   Specifically:
   - `<edf_stem>_faa.csv`
   - `<edf_stem>_processed_raw_eeg.fif`
3. Copy those onto the USB stick **according to the README in the repo root** (it explains the required USB folder structure).

---

## 8) Next time (normal workflow)
Go into the repo:
```powershell
cd $HOME\Documents\lab_scripts
```

Pull updates:
```powershell
git pull
```

Run the same command again (Step 5).

---

## Two most common fixes
- **Python not found**: close PowerShell, reopen, try `py --version`. If still broken, reinstall Python and check “Add to PATH”.
- **Missing F3/F4**: the script requires both channels. If your EDF labels are different, the script will stop with an error.
