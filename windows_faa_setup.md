# Windows: Run `compute_faa_from_edf.py` (painstakingly detailed, first-time CLI users)

## Important note about USB (read this first)
- Your **outputs** (the `.csv` and any `.fif` files the pipeline produces) **must be copied onto the USB stick** so you can bring them back to the instructor.
- The **step-by-step USB “shuttle” instructions** are in the **README in the root of this repo**. Read and follow those for how to move files safely.

---

## What you are doing (in one sentence)
You will (1) install Python, (2) download our lab code using **git**, (3) install the needed Python packages into a local folder, and (4) run one command that reads an EDF and writes a CSV.

---

## 0) Rules to start out with (read this first)
1. **Only type commands in PowerShell** (the blue/black terminal window).
2. **Always run commands from inside the project folder** (`lab_scripts`).
3. **Copy/paste commands exactly** (don’t retype unless you must).
4. If a path has spaces, wrap it in quotes:
   - ✅ `"C:\Users\Jane Doe\Documents\file.edf"`
   - ❌ `C:\Users\Jane Doe\Documents\file.edf`
5. If you get stuck, **do not keep trying random commands**—re-read the step you’re on and check the “Common problems” section.

---

## 1) Install Python 3.11+ (one time)

### 1.1 Download Python
1. Open your web browser (Chrome/Edge).
2. Go to:
   ```text
   https://www.python.org/downloads/windows/
   ```
3. Download Python 3.11+ (64-bit).

### 1.2 Install Python (this checkbox matters)
1. Run the installer.
2. On the first screen, **CHECK**:
   - ✅ **Add python.exe to PATH**
3. Finish the install.

### 1.3 Verify Python installed correctly
1. Open **PowerShell** (Start menu → type `PowerShell`).
2. Run:
   ```powershell
   py --version
   ```
3. You should see something like:
   ```text
   Python 3.11.x
   ```
4. If `py` does not work, try:
   ```powershell
   python --version
   ```

If both fail: close PowerShell, reopen it, and try again. If it still fails, reinstall Python and make sure “Add to PATH” is checked.

---

## 2) Install Git + download the lab repo (first time)

### 2.1 Install Git for Windows
1. Search: **Git for Windows**
2. Install it (defaults are fine).

### 2.2 Open PowerShell
Start menu → PowerShell.

### 2.3 Go to Documents
Copy/paste:
```powershell
cd $HOME\Documents
```

To confirm where you are:
```powershell
pwd
```
You should see a path ending in `\Documents`.

### 2.4 Clone the repo
Copy/paste:
```powershell
git clone https://github.com/Fitosm/lab_scripts.git
```

This creates a folder named `lab_scripts` inside Documents.

### 2.5 Enter the project folder (this is where you must stay)
Copy/paste:
```powershell
cd lab_scripts
```

### 2.6 Confirm you’re in the right place
Run:
```powershell
dir
```

You should see:
- `requirements.txt`
- a `scripts` folder

If you do **not** see those, run:
```powershell
cd $HOME\Documents\lab_scripts
dir
```

---

## 3) Create the Python environment + install packages (first time per computer)

This creates a folder named `.venv` inside `lab_scripts` and installs packages there.
**We are not “activating” anything**—this avoids Windows execution-policy problems.

### 3.1 Make sure you are still in `lab_scripts`
Run:
```powershell
pwd
```
You should see a path ending in `\Documents\lab_scripts`.

### 3.2 Create the environment + install requirements
Copy/paste these three commands **one at a time**:

```powershell
py -m venv .venv
```

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This can take a few minutes the first time.

---

## 4) Put your EDF somewhere simple (do this before running)

### 4.1 Make a simple folder for EDF files
1. Open File Explorer.
2. Click **This PC → Local Disk (C:)**
3. Create a new folder named:
   ```text
   EEG
   ```
So you now have:
```text
C:\EEG
```

### 4.2 Put your EDF file in there
Move/copy your EDF into:
```text
C:\EEG\subject1.edf
```

If your file has a different name, that’s fine—you will use its real name in the command.

### 4.3 (Best way) Copy the exact EDF path
1. In File Explorer, click your EDF file.
2. Hold **Shift** and right-click the file.
3. Click **Copy as path**
4. Paste it into Notepad so you can see it. It will look like:
```text
"C:\EEG\your_real_file_name.edf"
```
If it already includes quotes, keep them.

---

## 5) Run the FAA script (the actual computation)

### 5.1 Make sure PowerShell is in the repo folder
In PowerShell:
```powershell
cd $HOME\Documents\lab_scripts
```

### 5.2 Run the command (copy/paste, then edit only the EDF name if needed)
If your EDF really is `C:\EEG\subject1.edf`, copy/paste this:

```powershell
.\.venv\Scripts\python.exe scripts\eeg\compute_faa_from_edf.py "C:\EEG\subject1.edf" --out "C:\EEG\faa_summary.csv" --left F3 --right F4 --montage standard_1020 --reference average --l-freq 1 --h-freq 40
```

If your EDF has a different name, replace only this part:
- replace `"C:\EEG\subject1.edf"` with your real EDF path (preferably pasted via “Copy as path”).

### 5.3 What “success” looks like
- It prints progress/log messages.
- It finishes without a red error message.
- It creates:
```text
C:\EEG\faa_summary.csv
```

---

## 6) Check the output CSV
Copy/paste:
```powershell
Get-Content "C:\EEG\faa_summary.csv"
```

Or open `C:\EEG\faa_summary.csv` in Excel.

---

## 7) Copy outputs to the USB stick (required)
1. Plug in the USB stick.
2. Open File Explorer → click the USB drive (it will have a name like `USB (E:)`).
3. Copy the **output files** onto the USB stick:
   - the `.csv` output (e.g., `faa_summary.csv`)
   - any `.fif` output files produced by the pipeline
4. For the exact USB folder structure and “what goes where,” follow the **USB instructions in the README in the repo root**.

---

## 8) What to do next time (normal workflow)

### 8.1 Open PowerShell
Start menu → PowerShell.

### 8.2 Go into the repo folder
```powershell
cd $HOME\Documents\lab_scripts
```

### 8.3 Pull updates (only if we changed the code)
```powershell
git pull
```

### 8.4 Run the script again (same command as above)
```powershell
.\.venv\Scripts\python.exe scripts\eeg\compute_faa_from_edf.py "C:\EEG\subject1.edf" --out "C:\EEG\faa_summary.csv" --left F3 --right F4 --montage standard_1020 --reference average --l-freq 1 --h-freq 40
```

### 8.5 Copy outputs to the USB again
Copy the new `.csv` and any `.fif` outputs to the USB, following the repo-root README USB instructions.

---

## The two most common fixes

### Fix 1: “python/py not found”
1. Close PowerShell completely.
2. Open PowerShell again.
3. Try:
   ```powershell
   py --version
   ```
4. If still broken: reinstall Python and make sure ✅ **Add python.exe to PATH** is checked.

### Fix 2: EDF path wrong
- Use File Explorer → Shift + right-click EDF → **Copy as path**
- Paste into the command **inside quotes**.
- Example:
```powershell
.\.venv\Scripts\python.exe scripts\eeg\compute_faa_from_edf.py "C:\Users\Name\Downloads\My EDF File.edf" --out "C:\EEG\faa_summary.csv" ...
```
