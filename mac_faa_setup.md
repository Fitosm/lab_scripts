# macOS: Run `compute_faa_from_edf.py`

## Important note about USB (read this first)
- Your **outputs** (the `.csv` and `.fif`) **must be copied onto the USB stick** so you can bring them back to the instructor.
- The **exact USB folder rules + step-by-step “USB shuttle” instructions** are in the **README in the root of this repo**. Follow that README for where to put files on the USB.
- **New script behavior:** output files are **NOT** written next to your EDF. They are written **next to the script** inside the repo.

---

## 0) Rules to start out with
1. Do everything in **Terminal**.
2. Always run commands from inside the project folder: **`lab_scripts`**.
3. Copy/paste commands exactly.
4. If a path has spaces, wrap it in quotes: `"/Users/name/Path With Spaces/file.edf"`.

---

## 1) Install tools (one time)
### 1.1 Install Homebrew
In Terminal:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Close Terminal and reopen it when done.

### 1.2 Install git + Python 3.11
```bash
brew install git python@3.11
```

Check:
```bash
git --version
python3.11 --version
```

---

## 2) Clone the repo (first time on this computer)
Go to Documents:
```bash
cd ~/Documents
```

Clone:
```bash
git clone https://github.com/Fitosm/lab_scripts.git
```

Enter folder:
```bash
cd lab_scripts
```

Confirm:
```bash
ls
```
You should see `requirements.txt` and `scripts/`.

---

## 3) Create the Python environment + install packages (first time on this computer)
```bash
python3.11 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

---

## 4) Put your EDF somewhere simple
Example:
```text
~/EEG/subject1.edf
```

---

## 5) Run the script (UPDATED command)
Make sure you’re in the repo:
```bash
cd ~/Documents/lab_scripts
```

Run (replace only the EDF path):
```bash
./.venv/bin/python scripts/eeg/compute_faa_from_edf.py "/Users/YOURNAME/EEG/subject1.edf" --reference average --l-freq 1 --h-freq 40
```

Find your username (to replace `YOURNAME`) with:
```bash
whoami
```

### What the script does (important changes)
- Channels are **fixed**: **F3 (left)** and **F4 (right)**.
- It always writes **two outputs** **next to the script**:
  - `scripts/eeg/<edf_stem>_processed_raw_eeg.fif`
  - `scripts/eeg/<edf_stem>_faa.csv`

### If you need to skip montage
Default montage is `standard_1020`. To skip:
```bash
./.venv/bin/python scripts/eeg/compute_faa_from_edf.py "/Users/YOURNAME/EEG/subject1.edf" --montage ""
```

### If you re-run the same EDF and it refuses to overwrite
```bash
./.venv/bin/python scripts/eeg/compute_faa_from_edf.py "/Users/YOURNAME/EEG/subject1.edf" --overwrite
```

---

## 6) Check the outputs (UPDATED locations)
List outputs:
```bash
ls scripts/eeg/
```

View the CSV:
```bash
cat scripts/eeg/subject1_faa.csv
```

---

## 7) Copy outputs to the USB stick (required)
1. Plug in the USB stick.
2. Copy these files from:
   ```text
   lab_scripts/scripts/eeg/
   ```
   - `<edf_stem>_faa.csv`
   - `<edf_stem>_processed_raw_eeg.fif`
3. Copy them onto the USB **according to the README in the repo root** (it explains the required USB folder structure).

---

## 8) Next time (normal workflow)
```bash
cd ~/Documents/lab_scripts
git pull
```
Then run the same command again (Step 5).
