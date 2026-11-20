# NBA Trade Probability: Data Cleaning & Feature Engineering

Notebooks that download, clean, and combine NBA datasets into player-season-team features for an XGBoost model that predicts whether a player gets traded. See [ListOfPotentialFeatures.md](ListOfPotentialFeatures.md) for the feature list.

## Setup (once)

Requires Python 3.14 (tested with 3.14.7).

```bash
python -m venv venv

# activate it
venv\Scripts\activate          # Windows (PowerShell / cmd)
source venv/Scripts/activate   # Windows (Git Bash)
source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
```

In VS Code, open a notebook, click **Select Kernel**, and choose the `venv` interpreter.

## Run the notebooks

`data-files/` is not in git. **The notebooks download their own raw data** into `data-files/00-raw/` on the first run (internet required, about 1-2 minutes total) and skip the download after that.

### Salary features: `New-Cleaning/salary-data/`

Run in this order. Each notebook reads the previous one's output.

| # | Notebook | What it does |
|---|---|---|
| 1 | `01-Cap-Tax-Apron-Thresholds.ipynb` | League salary cap, luxury-tax line, and aprons for each season |
| 2 | `02-llimllib-Salaries-Payroll.ipynb` | Player salaries → % of cap, team payroll, luxury-tax markers, dollars above/below each line |
| 3 | `03-ESPN-Player-Contracts.ipynb` | Years left on contract, expiring-contract flag, minimum-salary flag |
| 4 | `999_combining.ipynb` | Merges 2 + 3 → **`data-files/02-processed/salary_features_combined.csv`** |

Either open each notebook and choose **Run All**, or run them all from the terminal (with the venv activated):

```bash
cd New-Cleaning/salary-data
jupyter nbconvert --to notebook --execute --inplace 01-Cap-Tax-Apron-Thresholds.ipynb
jupyter nbconvert --to notebook --execute --inplace 02-llimllib-Salaries-Payroll.ipynb
jupyter nbconvert --to notebook --execute --inplace 03-ESPN-Player-Contracts.ipynb
jupyter nbconvert --to notebook --execute --inplace 999_combining.ipynb
```

Details on each dataset, the output columns, and the join keys are in [New-Cleaning/salary-data/README.md](New-Cleaning/salary-data/README.md).

## Folder layout

```
data-files/
  00-raw/          raw downloads (never edited by hand)
  01-interim/      intermediate outputs
  02-processed/    cleaned tables (what modeling reads)
New-Cleaning/      current cleaning notebooks, one subfolder per feature group
  salary-data/
Old-Cleaning-And-Combining/, Old-Notebook/   earlier versions, kept for reference
```

## Conventions

- **One row = one player + season + team.**
- `season` is the **end year** of the season (2026 = 2025-26). The project covers 2015-16 to 2025-26 (2016-2026).
- `team` is the NBA 3-letter abbreviation (`GSW`, `NYK`, ...).
- Join tables on `season` + `nba_player_id` when possible. Otherwise use `season` + `team` + `name_key`, building `name_key` with `normalize_name()` in `nba_cleaning_utils.py`.

## Refreshing the data

To re-download a source, delete its file in `data-files/00-raw/` and re-run that notebook. llimllib's and ESPN's data are updated continuously, so counts can shift slightly between downloads.

## Troubleshooting

- **`DLL load failed ... Application Control policy has blocked this file`** (Windows): your machine's security policy blocked a compiled library. `pyarrow` is blocked on some machines, which is why it isn't a requirement (DuckDB reads the parquet files instead). If it happens inside pandas, restart the kernel. If it keeps happening, the pandas function that triggers it needs a workaround (notebook 01 avoids `pct_change()` for this reason).
- **`ModuleNotFoundError`**: the notebook isn't using the `venv` kernel. Select it in VS Code, or activate the venv before running `jupyter`.
