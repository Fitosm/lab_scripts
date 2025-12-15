# Windows: Run `compute_faa_from_edf.py` (painstakingly detailed, first-time CLI users)

## What you are doing (in one sentence)
You will (1) install Python, (2) download our lab code using **git**, (3) install the needed Python packages into a local folder, and (4) run one command that reads an EDF and writes a CSV.

---

## 0) Rules to start out with (read this first)
1. **Only type commands in PowerShell** (the blue/black terminal window).
2. **Always run commands from inside the project folder** (`lab_scripts`).
3. **Copy/paste commands exactly** (don’t retype unless you must).
4. If a file path has spaces, wrap it in quotes:
   - ✅ `"C:\Users\Jane Doe\Documents\file.edf"`
   - ❌ `C:\Users\Jane Doe\Documents\file.edf`
5. If you get stuck, **do not keep trying random commands**—re-read the step you’re on and check the “Common problems” section.

---

## 1) Install Python (one time)

### 1.1 Download Python
1. Open your web browser (Chrome/Edge).
2. Go to:
   ```text
   https://www.python.org/downloads/windows/
   ```
3. Click the big download button for the newest Python 3.11+.

### 1.2 Install Python (this checkbox matters)
1. Run the downloaded installer.
2. On the very first installer screen, **CHECK THIS BOX**:
   - ✅ **Add python.exe to PATH**
3. Click **Install Now** (or continue with defaults).

### 1.3 Verify Python installed correctly
1. Click Start menu, type **PowerShell**, open **Windows PowerShell**.
2. In PowerShell, run:
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

If both fail: restart PowerShell once and try again. If it still fails, Python was not added to PATH—re-run the installer and make sure the checkbox is checked.

---

## 2) Install Git + download the lab repo (first time)

### 2.1 Install Git for Windows
1. In your browser, search: **Git for Windows**
2. Download it from the official site and install it.
3. Accept defaults (keep clicking **Next** until **Install**).

### 2.2 Open PowerShell
1. Start menu → type **PowerShell** → open it.

### 2.3 Go to your Documents folder
Copy/paste:
```powershell
cd $HOME\Documents
```

To confirm where you are, run:
```powershell
pwd
```
You should see a path ending in `\Documents`.

### 2.4 Download (“clone”) the lab repo
Copy/paste:
```powershell
git clone https://github.com/Fitosm/lab_scripts.git
```

What you should see:
- It prints lines about “Cloning into 'lab_scripts' …”
- It creates a new folder named **lab_scripts** inside your Documents.

### 2.5 Enter the project folder (this is where you must stay)
Copy/paste:
```powershell
cd lab_scripts
```

**Important:** A common typo is `cd cd lab_scripts`. The correct command is just:
```powershell
cd lab_scripts
```

### 2.6 Confirm you’re in the right place
Run:
```powershell
dir
```

You should see items including:
- `requirements.txt`
- a `scripts` folder (it might show as `scripts` or `scripts\`)

If you do **not** see those, you are not in the right folder. Do:
```powershell
cd $HOME\Documents\lab_scripts
dir
```

---

## 3) Create the Python environment + install packages (first time per computer)

You will create a folder named `.venv` inside `lab_scripts`. This keeps Python packages contained so nothing breaks your system Python.

### 3.1 Make sure you are still in `lab_scripts`
Run:
```powershell
pwd
```
You should see a path ending in `\Documents\lab_scripts`.

### 3.2 Create the environment and install requirements
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
2. Go to **This PC → Local Disk (C:)**
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

If your file is not named `subject1.edf`, that’s fine—you will use its real name in the command.

### 4.3 (Best way) Copy the exact EDF path
1. In File Explorer, click your EDF file.
2. Hold **Shift** and right-click the file.
3. Click **Copy as path**
4. Paste it into Notepad for a second so you can see it. It will look like:
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
In PowerShell, copy/paste:
```powershell
Get-Content "C:\EEG\faa_summary.csv"
```

Or open `C:\EEG\faa_summary.csv` in Excel.

---

## 7) What to do next time (normal workflow)

### 7.1 Open PowerShell
Start menu → PowerShell.

### 7.2 Go into the repo folder
```powershell
cd $HOME\Documents\lab_scripts
```

### 7.3 Pull updates (only if we changed the code)
```powershell
git pull
```

### 7.4 Run the script again (same command as Step 5)
```powershell
.\.venv\Scripts\python.exe scripts\eeg\compute_faa_from_edf.py "C:\EEG\subject1.edf" --out "C:\EEG\faa_summary.csv" --left F3 --right F4 --montage standard_1020 --reference average --l-freq 1 --h-freq 40
```

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

### Fix 2: “File not found” / EDF path wrong
- Use File Explorer → Shift + right-click EDF → **Copy as path**
- Paste into the command **inside quotes**.
- Example:
   ```powershell
   .\.venv\Scripts\python.exe scripts\eeg\compute_faa_from_edf.py "C:\Users\Name\Downloads\My EDF File.edf" --out "C:\EEG\faa_summary.csv" ...
   ```
