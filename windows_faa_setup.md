**0) Rules to start out with**

Do everything in PowerShell inside the project folder.

If a path has spaces, wrap it in quotes "like this".

Copy/paste commands exactly.

**1) Install Python (one time)**

Go to:

https://www.python.org/downloads/windows/


Download Python 3.11+ (64-bit).

Run installer and check: ✅ Add python.exe to PATH

Open PowerShell and run:

```
py --version
```

If py fails, try:

```
python --version
```
**2) Clone the repo using the command line interface**

Install Git for Windows:

Search “Git for Windows” and install it (defaults are fine).

Open PowerShell.

Go to Documents:

```
cd $HOME\Documents
```

Clone the repo (you provide the URL):

```
git clone https://github.com/YOURUSER/YOURREPO.git
```

Enter the folder:

```
cd YOURREPO
```

Confirm you’re in the right place:

```
dir
```

You should see requirements.txt and scripts\.

**3) Create a virtual environment (no activation)**

Copy/paste:

```
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**4) Run the script**

Put the EDF somewhere simple like:

```
C:\EEG\subject1.edf
```

Run (you must replace the EDF path and output path):

```
.\.venv\Scripts\python.exe scripts\eeg\compute_faa_from_edf.py "C:\EEG\subject1.edf" --out "C:\EEG\faa_summary.csv" --left F3 --right F4 --montage standard_1020 --reference average --l-freq 1 --h-freq 40
```

**5) Check output**

```
Get-Content "C:\EEG\faa_summary.csv"
```

**6) What to do next time (normal workflow)**

Enter the repo:

```
cd $HOME\Documents\YOURREPO
```

Pull updates:

```
git pull
```

Run the script again (same command as above).

The two most common fixes

Python not found: restart PowerShell; if still broken, reinstall Python and ensure “Add to PATH” is checked.

EDF path wrong: use File Explorer → Shift+Right-click EDF → “Copy as path” → paste inside quotes.
