# FlatShare Splitter

A small desktop app for splitting shared expenses between flatmates. Add people, log who paid for what, and the app works out the minimum number of payments needed to settle up.

Built with Python, Tkinter ([ttkbootstrap](https://ttkbootstrap.readthedocs.io/)) and SQLite. The interface is in Czech and amounts are shown in CZK (Kč).

## Features

- Add roommates and record payments (payer, amount, description, who it was for)
- Each payment is split equally between the selected people
- Payment history table, sortable by clicking any column header
- Filter history by date range (`Od` / `Do`)
- **Settlement calculator**: shows who should send money to whom, using a greedy algorithm that keeps the number of transfers low. It respects the active date filter.
- Data is stored locally in a SQLite database, so it persists between runs

## Project structure

```
FlatShare-Splitter/
├── main.py          # Entry point: creates the DB, window and app
├── gui.py           # ttkbootstrap UI (main window, dialogs, toasts)
├── models.py        # Roommate, Transaction, Household (balance & settlement logic)
├── storage.py       # SQLite persistence (DatabaseManager)
├── test_data.db     # SQLite database (created automatically if missing)
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.8 or newer
- Tkinter (bundled with the official Python installers on Windows and macOS; on Linux it may need a separate package, see below)
- The packages in `requirements.txt` (just `ttkbootstrap`)

## Quick start: running it on another computer

### 1. Get the project

Copy the project folder to the new computer (or clone/unzip it), then open a terminal **inside that folder**:

```bash
cd FlatShare-Splitter
```

### 2. Check Python

```bash
python --version      # Windows
python3 --version     # macOS / Linux
```

You need 3.8+. If it's missing, install it from [python.org](https://www.python.org/downloads/). On Windows, tick **"Add Python to PATH"** in the installer.

**Linux only:** install Tkinter and venv support if they're missing:

```bash
# Debian / Ubuntu
sudo apt install python3-tk python3-venv

# Fedora
sudo dnf install python3-tkinter
```

### 3. Create a virtual environment

**Windows (PowerShell or CMD)**
```powershell
python -m venv venv
```

**macOS / Linux**
```bash
python3 -m venv venv
```

### 4. Activate it

**Windows PowerShell**
```powershell
venv\Scripts\Activate.ps1
```
> If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` first, or use CMD instead.

**Windows CMD**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux**
```bash
source venv/bin/activate
```

Your prompt should now start with `(venv)`.

### 5. Install the requirements

```bash
pip install -r requirements.txt
```

### 6. Run the app

```bash
python main.py
```

(Use `python3 main.py` if `python` isn't available on macOS/Linux. Inside an activated venv, `python` normally works.)

A dark-themed window opens. The database file is created automatically on first run if it doesn't exist.

### 7. When you're done

```bash
deactivate
```

Next time, just activate the venv again (step 4) and run `python main.py`. There's no need to reinstall anything.

## How to use

1. Click **+ Přidat osobu** and add each flatmate.
2. Click **+ Přidat platbu**, choose who paid, enter the amount and a description, and tick everyone the expense applies to (include the payer if they also share in it).
3. Browse the history on the left. Click a column header to sort, or pick a date range and press **Filtrovat**.
4. Click **✨ Vypočítat vyrovnání** to see who owes whom. If a date filter is active, only the filtered payments are counted.

## Data and backups

All data lives in `test_data.db` in the project folder (the path is set in `storage.py`, `DatabaseManager(db_path=...)`).

- To **move your data** to another computer, copy `test_data.db` along with the code.
- To **start fresh**, close the app and delete `test_data.db`. A new empty one is created on next launch.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'ttkbootstrap'` | The venv isn't activated, or step 5 was skipped. Activate it and run `pip install -r requirements.txt`. |
| `ModuleNotFoundError: No module named 'tkinter'` | Install Tkinter (see step 2, Linux section). On macOS with Homebrew Python: `brew install python-tk`. |
| `python` not found | Try `python3` (macOS/Linux) or `py` (Windows). |
| PowerShell refuses to run `Activate.ps1` | See the note in step 4. |
| `pip` is outdated warning | Optional: `python -m pip install --upgrade pip`. |

## How the settlement works

For every payment, the payer is credited the full amount and each participant is debited an equal share. This produces a balance per person (positive = is owed money, negative = owes money). Debtors and creditors are then sorted by size and matched greedily, largest with largest, until everyone is at zero. This gives a small number of transfers, though not always the theoretical minimum.
