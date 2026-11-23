# EDA: Exploratory Data Analysis

These notebooks explore the cleaned feature tables. They're separate from the cleaning pipeline in `New-Cleaning/`.

- They **only read** from `data-files/02-processed/` and **write no data**, so run the matching cleaning notebooks first.
- They get the path to `data-files/` from `New-Cleaning/salary-data/nba_cleaning_utils.py`, like the cleaning notebooks do.

| Notebook | What it explores | Reads (`data-files/02-processed/`) | Run first |
|---|---|---|---|
| [llimllib-salary/llimllib_salary_eda.ipynb](llimllib-salary/llimllib_salary_eda.ipynb) | Player salaries and team payroll vs. being traded in the next offseason | `llimllib_player_salary_features.csv`, `llimllib_team_payroll_features.csv`, `offseason_traded_players.csv` | `New-Cleaning/salary-data/01`, `02`; `Old-Cleaning-And-Combining/06` (for the trades file) |
| [player-stats/01-Regular-Season-EDA.ipynb](player-stats/01-Regular-Season-EDA.ipynb) | Regular-season stats: distributions, age and experience, minutes, correlations (including Box +/-), league trends, the 3-year averages | `player_stats_combined.csv` | `New-Cleaning/player-stats/01` → `999` |
| [player-stats/02-Playoffs-EDA.ipynb](player-stats/02-Playoffs-EDA.ipynb) | The same for the playoffs, compared with the regular season, and why there is no playoff 3-year trend | `player_stats_combined.csv` | `New-Cleaning/player-stats/01` → `999` |

**What the player-stats EDA looks at.** The features table keeps every player-season, but the EDA describes typical stats, so it uses only:

- regular-season rows with **10+ games**;
- playoff rows with **4+ games**.

It also recomputes two flags for its own use (`ppg_outlier`, by the IQR rule within each season, and `suspicious_entry`). Neither is a feature in the pipeline.

```bash
cd EDA/player-stats
jupyter nbconvert --to notebook --execute --inplace 01-Regular-Season-EDA.ipynb
jupyter nbconvert --to notebook --execute --inplace 02-Playoffs-EDA.ipynb
```
