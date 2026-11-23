# New-Cleaning / salary-data: Salary & Contract Features

Each source dataset has its own notebook. `999_combining` merges them into one player-season-team table, which then gets combined with the other datasets' tables before modeling (XGBoost).

## Notebooks (run in this order)

| Notebook | Dataset | Writes (`data-files/02-processed/`) |
|---|---|---|
| [01-Cap-Tax-Apron-Thresholds](01-Cap-Tax-Apron-Thresholds.ipynb) | Mr-Bridge `cap_tax_aprons.csv` (league thresholds) | `cap_thresholds_clean.csv` |
| [02-llimllib-Salaries-Payroll](02-llimllib-Salaries-Payroll.ipynb) | [llimllib/nba_data](https://github.com/llimllib/nba_data) `bbref_salaries` | `llimllib_player_salary_features.csv`, `llimllib_team_payroll_features.csv` |
| [03-ESPN-Player-Contracts](03-ESPN-Player-Contracts.ipynb) | ESPN contracts ([hoopR `espn_nba_player_contract`](https://hoopr.sportsdataverse.org/reference/espn_nba_player_contracts.html) endpoint) | `espn_contract_features.csv` |
| [999_combining](999_combining.ipynb) | outputs of 02 + 03, filtered to players under contract for the next season | **`salary_features_combined.csv`** |

02 and 03 download their raw data into `data-files/00-raw/` the first time they run.

## Final table: `salary_features_combined.csv`

One row = one player + season + team (3,478 rows, 2015-16 to 2025-26). Every row has an NBA `nba_player_id`. Rows without one were dropped in notebook 02.

**Only players under contract for the next season** (`years_remaining >= 2`). Our research question covers only these players: a player on an expiring contract becomes a free agent and can rarely be traded in the offseason. `999_combining` section 6 drops the 1,934 expiring-contract rows and the 1,355 rows with unknown contract length out of 6,767. **Use this table as the base and left-join the other datasets onto it**, so the expiring players don't come back through the stats tables.

| Feature | Column(s) |
|---|---|
| Player salary as % of salary cap | `salary_pct_of_cap` (also `cap_salary`, `is_two_way`) |
| Years left on contract | `years_remaining` (counts the current season, so it is always 2 or more here; 2 = one season left after this one) |
| Minimum-salary contract flag | `min_salary_contract`; `min_salary_over_cap` (also requires the team to be over the cap) |
| Luxury-tax markers | `over_cap`, `over_tax`, `over_first_apron`, `over_second_apron`, `tax_tier` (0 = under cap … 4 = over 2nd apron) |
| Dollars above/below each threshold | `dollars_vs_{cap,tax,first_apron,second_apron}` and the `_pct_cap` versions |
| Team payroll | `team_payroll`, `payroll_pct_of_cap` |

Option type and trade kicker were considered and **dropped**, because ESPN reports placeholder values (0) for every contract (see notebook 03, section 4a).

The expiring-contract flag (`expiring_contract`, built in notebook 03) is used only for the filter and is not in the final table, since it would be `False` for every row.

Missing values are left as `NaN` for XGBoost. After the filter, the only ones left are the second-apron columns for seasons before 2023-24.

## Join keys for combining with other datasets

- `season`: **end year** (2026 = 2025-26).
- `nba_player_id`: NBA.com person id (preferred).
- `team`: NBA 3-letter abbreviation (`GSW`, `NYK`, `SAS`, `NOP`, `UTA`, `WAS`, ...).
- `name_key`: `normalize_name(player name)` from `nba_cleaning_utils.py`, for sources without NBA ids.

## Environment note

`pyarrow` (and occasionally some pandas DLLs) is blocked by Windows Application Control on this machine. Notebook 02 reads the remote parquet catalog with `duckdb` instead (`pip install duckdb`).
