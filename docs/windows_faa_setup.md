# Windows: Run `edf_to_fif_and_faa.py` (students new to PowerShell)

## What you will do
You will:
1) install Python once,  
2) download the lab repo once,  
3) set up the Python environment once,  
4) copy the EDF + TSV + script into ONE local folder on your computer,  
5) run ONE command that processes all EDFs in that folder,  
6) copy the output files back onto the USB stick.

---

## USB rule
The USB stick is for moving files. Do not run the script on the USB (it is too slow).

- Copy **inputs** (EDF + TSV) from the USB to your computer.
- Run the script on your computer.
- Copy **outputs** back to the USB:
  - `*_clean.fif`
  - `*_faa.csv`
  - `edf_to_fif_and_faa.log`

The exact USB folder structure is in the README at the root of the repo.

---

## 0) Rules
1. Use PowerShell only.
2. Copy/paste commands exactly.
3. If a path has spaces, wrap it in quotes.

---

## 1) One-time: Install Python 3.11+
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

---

## 2) One-time: Install Git + download the lab repo
1. Install “Git for Windows” (defaults are fine).
2. Open PowerShell.
3. Go to Documents:
   ```powershell
   cd $HOME\Documents
   ```
4. Download the repo:
   ```powershell
   git clone https://github.com/Fitosm/lab_scripts.git
   ```
5. Enter the folder:
   ```powershell
   cd lab_scripts
   ```
6. Check you see the right files:
   ```powershell
   dir
   ```
   You should see `requirements.txt` and the folders `docs`, `scripts`, and `examples`.

---

## 3) One-time: Create the environment + install packages (no activation)
Still inside `lab_scripts`, run these one at a time:
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

## 4) Make one local working folder (on your hard drive)
You will run everything from a local folder like:
```text
C:\EEG\work\
```

### 4.1 Create the folder
1. Open File Explorer.
2. Go to `C:\`
3. Create a folder named `EEG`
4. Inside `C:\EEG`, create a folder named `work`

So you have:
```text
C:\EEG\work\
```

---

## 5) Copy files from the USB into your local working folder
Plug in the USB stick. Follow the repo README to find where your USB `in` folder is.

Copy these into:
```text
C:\EEG\work\
```

### 5.1 Copy your EDF file(s)
Example:
```text
C:\EEG\work\est001yo.edf
C:\EEG\work\est001yc.edf
```

### 5.2 Copy exactly one channel rename TSV
Example:
```text
C:\EEG\work\rename_channels.tsv
```

There must be exactly one `.tsv` in `C:\EEG\work\`.

Need a template? Copy this file from the repo and rename it to `rename_channels.tsv` once it is in your working folder:
```text
C:\Users\<YOU>\Documents\lab_scripts\examples\rename_channels.example.tsv
```

### 5.3 Copy the script
Copy this file from the repo:
```text
C:\Users\<YOU>\Documents\lab_scripts\scripts\eeg\edf_to_fif_and_faa.py
```

Into your working folder:
```text
C:\EEG\work\edf_to_fif_and_faa.py
```

---

## 6) Open PowerShell in the working folder
1. Open File Explorer and go to:
   ```text
   C:\EEG\work\
   ```
2. Click the address bar.
3. Type:
   ```text
   powershell
   ```
4. Press Enter.

---

## 7) Confirm the folder contains what it needs
In PowerShell, run:
```powershell
dir
```

You must see:
- `edf_to_fif_and_faa.py`
- at least one `.edf`
- exactly one `.tsv`

---

## 8) Run the script (one command)
This uses the Python environment you installed in the repo, but runs the script from your local working folder.

Copy/paste:
```powershell
& "$HOME\Documents\lab_scripts\.venv\Scripts\python.exe" .\edf_to_fif_and_faa.py
```

What it does:
- Processes every `.edf` file in `C:\EEG\work\`
- Creates, for each EDF:
  - `<stem>_clean.fif`
  - `<stem>_faa.csv`
- Also creates:
  - `edf_to_fif_and_faa.log`

---

## 9) Check outputs (local folder)
Run:
```powershell
dir
```

You should now see:
- `*_clean.fif`
- `*_faa.csv`
- `edf_to_fif_and_faa.log`

To view one CSV:
```powershell
Get-Content .\est001yo_faa.csv
```

If something failed, open the log:
```powershell
Get-Content .\edf_to_fif_and_faa.log
```

---

## 10) Copy outputs back onto the USB stick (required)
Copy these files from:
```text
C:\EEG\work\
```
to the USB output folder (as defined in the repo README):
- `*_clean.fif`
- `*_faa.csv`
- `edf_to_fif_and_faa.log`

---

## Common problems

### “No EDF files found next to this script”
Your `.edf` files are not in `C:\EEG\work\`. Run `dir` and confirm you can see them.

### “No TSV found” or “Multiple TSV files found”
There must be exactly one `.tsv` in `C:\EEG\work\`. Remove extra TSVs.

### “Missing required frontal channels: F3, F4”
The TSV did not rename the channels into `F3` and `F4`. Stop and tell the instructor.
