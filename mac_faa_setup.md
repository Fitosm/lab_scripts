# macOS: Run `compute_faa_from_edf.py`

## Important note about USB (read this first)
- Your **outputs** (the `.csv` and any `.fif` files the pipeline produces) **must be copied onto the USB stick** so you can bring them back to the instructor.
- The **step-by-step USB “shuttle” instructions** are in the **README in the root of this repo**. Read and follow those for how to move files safely.

---

## What you are doing (in one sentence)
You will (1) install Python, (2) download our lab code using **git**, (3) install the needed Python packages into a local folder, and (4) run one command that reads an EDF and writes a CSV.

---

## 0) Rules to start out with (read this first)
1. **Only type commands in Terminal** (the app named “Terminal”).
2. **Always run commands from inside the project folder** (`lab_scripts`).
3. **Copy/paste commands exactly** (don’t retype unless you must).
4. If a path has spaces, wrap it in quotes:
   - ✅ `"/Users/Jane Doe/Documents/file.edf"`
   - ❌ `/Users/Jane Doe/Documents/file.edf`
5. When you paste into Terminal, it’s OK if it looks long—just press **Return** to run it.

---

## 1) Open Terminal (macOS built-in)
1. Press **Command (⌘) + Space** to open Spotlight Search.
2. Type: `Terminal`
3. Press **Return** to open it.

You will see a window with a prompt that ends in `$` (or `%`). That is normal.

---

## 2) Install the tools (one time)

### 2.1 Install Homebrew (package manager)
Homebrew is the simplest way to install git and a fresh Python on macOS.

1. In Terminal, copy/paste this (all one line), then press Return:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. If it asks for your password, type your Mac login password and press Return.
   (You will not see the characters while typing. That is normal.)

3. When it finishes, close Terminal and open it again.

### 2.2 Install git + Python using Homebrew
In Terminal, copy/paste:

```bash
brew install git python@3.11
```

### 2.3 Verify they installed
Copy/paste each line:

```bash
git --version
```

```bash
python3.11 --version
```

You should see versions printed (that means it worked).

---

## 3) Download the lab repo (clone)

### 3.1 Go to your Documents folder
Copy/paste:

```bash
cd ~/Documents
```

### 3.2 Clone the repo
Copy/paste:

```bash
git clone https://github.com/Fitosm/lab_scripts.git
```

This creates a folder named `lab_scripts` inside your Documents folder.

### 3.3 Enter the project folder (this is where you must stay)
Copy/paste:

```bash
cd lab_scripts
```

### 3.4 Confirm you’re in the right place
Copy/paste:

```bash
ls
```

You should see:
- `requirements.txt`
- a folder named `scripts`

If you do not, run:
```bash
cd ~/Documents/lab_scripts
ls
```

---

## 4) Create the Python environment + install packages (first time per computer)

This creates a folder named `.venv` inside `lab_scripts` and installs packages there.

### 4.1 Make sure you are still in `lab_scripts`
Copy/paste:

```bash
pwd
```

You should see something ending in:
`/Documents/lab_scripts`

### 4.2 Create the environment
Copy/paste:

```bash
python3.11 -m venv .venv
```

### 4.3 Install requirements (no activation)
Copy/paste these two commands:

```bash
./.venv/bin/python -m pip install --upgrade pip
```

```bash
./.venv/bin/python -m pip install -r requirements.txt
```

This can take a few minutes the first time.

---

## 5) Put your EDF somewhere simple (do this before running)

### 5.1 Make a simple folder for EDF files
1. Open Finder.
2. Go to your home folder.
3. Create a folder named:
   `EEG`

So you have a folder at:
`~/EEG`

### 5.2 Put your EDF file in there
Move/copy your EDF into:
`~/EEG/subject1.edf`

If your file has a different name, that’s fine—you will use its real name in the command.

### 5.3 Find your Mac username (needed for the command)
In Terminal, run:
```bash
whoami
```
Remember what it prints (that is `YOURNAME` in paths like `/Users/YOURNAME/...`).

---

## 6) Run the FAA script (the actual computation)

### 6.1 Make sure Terminal is in the repo folder
Copy/paste:

```bash
cd ~/Documents/lab_scripts
```

### 6.2 Run the command (copy/paste, then edit only the EDF name if needed)
Replace `YOURNAME` with the result of `whoami`.

```bash
./.venv/bin/python scripts/eeg/compute_faa_from_edf.py "/Users/YOURNAME/EEG/subject1.edf" --out "/Users/YOURNAME/EEG/faa_summary.csv" --left F3 --right F4 --montage standard_1020 --reference average --l-freq 1 --h-freq 40
```

---

## 7) Check the output CSV
Replace `YOURNAME` with your username:

```bash
cat "/Users/YOURNAME/EEG/faa_summary.csv"
```

---

## 8) Copy outputs to the USB stick (required)
1. Plug in the USB stick.
2. Open Finder → look for the USB under **Locations**.
3. Copy the **output files** onto the USB stick:
   - the `.csv` output (e.g., `faa_summary.csv`)
   - any `.fif` output files produced by the pipeline
4. For the exact USB folder structure and “what goes where,” follow the **USB instructions in the README in the repo root**.

---

## 9) What to do next time (normal workflow)

### 9.1 Open Terminal
Spotlight → Terminal.

### 9.2 Go into the repo folder
```bash
cd ~/Documents/lab_scripts
```

### 9.3 Pull updates (only if we changed the code)
```bash
git pull
```

### 9.4 Run the script again (same command as above)
```bash
./.venv/bin/python scripts/eeg/compute_faa_from_edf.py "/Users/YOURNAME/EEG/subject1.edf" --out "/Users/YOURNAME/EEG/faa_summary.csv" --left F3 --right F4 --montage standard_1020 --reference average --l-freq 1 --h-freq 40
```

### 9.5 Copy outputs to the USB again
Copy the new `.csv` and any `.fif` outputs to the USB, following the repo-root README USB instructions.

---

## The two most common fixes

### Fix 1: `git: command not found` or `brew: command not found`
- Homebrew did not install fully, or Terminal was not restarted.
- Close Terminal completely and reopen it, then try:
```bash
brew --version
```

### Fix 2: EDF path wrong
- Make sure the EDF is really inside `~/EEG`.
- If there are spaces in the filename, keep the quotes.
- You can also rename the EDF to something simple like `subject1.edf`.
