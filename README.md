# Crypto Dashboard

A Python desktop dashboard for Bybit spot-market prices and account data. The UI is built with Tkinter, and market history and account snapshots are stored in a local SQLite database.

## Features

- Browse Bybit spot prices and sort them by symbol or capture time.
- Register an account and view its spot trades and latest balances.
- View a pie chart of the saved balance allocation.
- Refresh public prices, account trades, and balances every 60 seconds while the app is open.

## Requirements

- Python 3 with Tkinter available.
- Python packages: `requests`, `numpy`, `schedule`, `Pillow`, and `matplotlib`.

Install the Python packages:

```sh
python -m pip install requests numpy schedule Pillow matplotlib
```

On Windows, install Python from python.org and enable Tcl/Tk support in the installer. On Linux, install your distribution's Tkinter package (often named `python3-tk`) as well.

## Run

From the repository directory:

```sh
python main.py
```

Choose **View market data** to see prices. Choose **View account data** to register a Bybit account, select it, and view its trades or balance.

The app connects to the **Bybit testnet** (`api-testnet.bybit.com`). Use a dedicated testnet account and API keys only. Public market prices do not require keys.

## Important security notes

- This app stores account API keys and secret keys in the local `crypto.db` SQLite database as plain text. Do not use real exchange credentials or store this database in a shared or public location.
- A `crypto.db` file is present in this repository. If it contains your credentials, treat them as exposed: revoke and replace those keys in Bybit, and remove the database from the repository and its Git history.
- The code has not been security-audited. Use only with disposable testnet credentials.

## Current setup note

The main window currently tries to load `awthemes/awdark.tcl`, while the repository includes `awdark.tcl` at its root. The dark theme also depends on the Tcl `awthemes` package, which is not included in this repository. If startup reports a missing theme or Tcl package, the theme dependency/path needs to be installed or corrected before launch.

## Data files

The app creates or uses `crypto.db` in its working directory for prices, account records, trades, and balances. Keep a backup if you need the saved history. Do not commit a database containing credentials.
