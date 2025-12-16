# Windows: Run `edf_to_fif_and_faa.py`

## What you will do
You will:
1) install Python once,  
2) open PowerShell,  
3) run a few copy/paste commands to set up the tool,  
4) place three kinds of files in ONE folder, and  
5) run one command: `python edf_to_fif_and_faa.py`

---

## USB rule (read this first)
Your outputs must end up on the USB stick:
- `*_clean.fif`
- `*_faa.csv`
- `edf_to_fif_and_faa.log`

The exact USB folder structure and “where to put things” is in the README at the root of the repo.

---

## 0) Vocabulary (so the instructions make sense)
- “PowerShell” = the Windows command line app.
- “Command” = one line you paste into PowerShell and press Enter.
- “Folder” = a normal Windows File Explorer folder.

---

## 1) One-time: Install Python 3.11+
1. In a browser, go to:
   ```text
   https://www.python.org/downloads/windows/
   ```
2. Download Python 3.11+ (64-bit).
3. Run the installer.
4. On the first screen, check: “Add python.exe to PATH”.
5. Finish installation.

Open PowerShell (Start Menu → type `PowerShell` → open it) and test:
```powershell
py --version
```
If that fails, try:
```powershell
python --version
```

---

## 2) One-time: Download the lab repo (the code)
1. Install Git for Windows (search “Git for Windows”, defaults are fine).
2. Open PowerShell.
3. Go to Documents:
   ```powershell
   cd $HOME\Documents
   ```
4. Download the repo:
   ```powershell
   git clone https://github.com/Fitosm/lab_scripts.git
   ```
5. Enter the repo folder:
   ```powershell
   cd lab_scripts
   ```
6. Quick check:
   ```powershell
   dir
   ```
   You should see `scripts` and `requirements.txt`.

---

## 3) One-time: Set up the Python environment (no activation)
Still inside `lab_scripts`, copy/paste these (one at a time):
```powershell
py -m venv .venv
```
```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 4) The “one folder” rule for this script (most important part)
This script ONLY works if these are all in the SAME folder:
- `edf_to_fif_and_faa.py`
- your `.edf` file(s)
- exactly ONE `*.tsv` channel rename file (two columns: original name, desired name)

On Windows, the easiest place to do this is:
```text
USB_STICK:\out\
```
(Your repo README explains the correct USB folders; follow it.)

### 4.1 Put the script in the output folder
From your repo, the script is located at:
```text
lab_scripts\scripts\eeg\edf_to_fif_and_faa.py
```

Copy that file into your USB output folder (example):
```text
E:\lab_usb\out\
```

### 4.2 Put the channel rename TSV in the same output folder
Copy the rename TSV into the SAME folder as the script (example):
```text
E:\lab_usb\out\rename_channels.tsv
```

Important: there must be exactly ONE `.tsv` in that folder.  
If there are two or more `.tsv` files, the script will stop.

### 4.3 Put your EDF file(s) in the same output folder
Copy your EDF(s) into the SAME folder (example):
```text
E:\lab_usb\out\est001yo.edf
E:\lab_usb\out\est001yc.edf
```

---

## 5) Run the script (this is the command)
### 5.1 Open PowerShell in the folder that contains the files
1. Open File Explorer and go to the folder with the script + EDF + TSV (example: `E:\lab_usb\out`).
2. Click the address bar at the top (where it shows the path), type:
   ```text
   powershell
   ```
   and press Enter.

### 5.2 Confirm the folder contains the right files
Run:
```powershell
dir
```
You must see:
- `edf_to_fif_and_faa.py`
- one or more `.edf`
- exactly one `.tsv`

### 5.3 Run (copy/paste)
This uses the environment you installed in the repo, but runs the script in your current folder.

Copy/paste:
```powershell
python "$HOME\Documents\lab_scripts\.venv\Scripts\python.exe" 2>$null
```

Do NOT use that. Use the correct command below (copy/paste exactly):

```powershell
$py="$HOME\Documents\lab_scripts\.venv\Scripts\python.exe"
& $py .\edf_to_fif_and_faa.py
```

What it will do:
- It processes every `.edf` file in this folder.
- For each EDF, it writes:
  - `<stem>_clean.fif`
  - `<stem>_faa.csv`
- It also writes:
  - `edf_to_fif_and_faa.log`

---

## 6) Check outputs
Run:
```powershell
dir
```

You should now see files like:
- `est001yo_clean.fif`
- `est001yo_faa.csv`
- `edf_to_fif_and_faa.log`

To view the CSV:
```powershell
Get-Content .\est001yo_faa.csv
```

If something failed, open the log:
```powershell
Get-Content .\edf_to_fif_and_faa.log
```

---

## 7) Copy outputs to USB (required)
If you ran the script on the USB already, the outputs are already on it.
If you ran it somewhere else, copy these to the USB output folder (per README):
- `*_clean.fif`
- `*_faa.csv`
- `edf_to_fif_and_faa.log`

---

## Common mistakes (and what to do)

### “No EDF files found next to this script”
You are not in the folder that contains the EDF(s). Use `dir` and check you see the `.edf` files.

### “No TSV found” or “Multiple TSV files found”
Your folder must contain exactly one `.tsv` (the channel rename file). Remove extra TSVs.

### “Missing required frontal channels: F3, F4”
The TSV did not rename the channels into `F3` and `F4`. Stop and tell the instructor.
