# Cleaning & Combining

This folder replaces the single `Old-Notebook/01-DataCheckpoint.ipynb`. Each dataset now has its own notebook.
Every notebook keeps the same sections: describe the data, load it, show it is tidy (or tidy it), show its size,
check missing data, flag outliers and suspicious entries, clean it, and save it.

## Notebooks (run in this order)

| Notebook | Dataset | Reads (`data-files/00-raw/`) | Writes |
|---|---|---|---|
| [00-Download-Raw-Data](00-Download-Raw-Data.ipynb) | – | – | the Hugging Face CSVs and NBA.com JSON (skips files already present) |
| [01-BBRef-Salaries](01-BBRef-Salaries.ipynb) | #1 Basketball-Reference salaries | `bbref_team_salaries_2015_2026.csv` | `02-processed/bbref_team_salaries_clean.csv` |
| [02-Kaggle-Box-Scores](02-Kaggle-Box-Scores.ipynb) | #2 Kaggle player box scores | `PlayerStatistics.csv` | `02-processed/player_game_stats_cleaned.csv` |
| [03-Kaggle-Salaries](03-Kaggle-Salaries.ipynb) | #3 Kaggle salaries 1990-2023 | `NBA Salaries(1990-2023).csv` | `02-processed/nba_salaries_2014_2022_clean.csv` |
| [04-NBA-Stats-Player-Stats](04-NBA-Stats-Player-Stats.ipynb) | #4 NBA Stats API league leaders | `nba_league_leaders_raw.csv` (downloaded by the notebook if missing) | `02-processed/nba_player_stats_cleaned.csv` |
| [05-HF-Salary-Cap-Contracts](05-HF-Salary-Cap-Contracts.ipynb) | #5 Mr-Bridge salary cap & contracts | `hf_*.csv` | `01-interim/hf_salary_contract_rows.csv`, `02-processed/player_season_salaries.csv`, `02-processed/team_season_payrolls.csv` |
| [06-NBA-Transactions](06-NBA-Transactions.ipynb) | #6 NBA.com player movement log | `nba_player_movement.json` | `01-interim/nba_transactions_parsed.csv`, `02-processed/nba_trades.csv`, `02-processed/offseason_traded_players.csv` |
| [07-Data-Quality-Evaluation](07-Data-Quality-Evaluation.ipynb) | all | `02-processed/*` | nothing (it only checks the data) |

Notebooks 01-06 don't depend on each other and can run in any order. 07 needs all of them to have run.
`nba_cleaning_utils.py` holds the data folder paths and `normalize_name()`, the player-name join key that
Datasets #5 and #6 must build the same way.

## The six datasets

| # | Dataset (link) | What it gives us | Seasons covered |
|---|---|---|---|
| 1 | [Basketball-Reference team salary pages](https://www.basketball-reference.com/teams/) (scraped, following robots.txt) | Each player's salary by team and season | 2014-15 to 2025-26 |
| 2 | [Kaggle: Historical NBA Data and Player Box Scores](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores) | Game-by-game player box scores for the regular season **and** playoffs | We keep 2015-16 onward |
| 3 | [Kaggle: NBA Players and Team Data](https://www.kaggle.com/datasets/loganlauton/nba-players-and-team-data) (NBA Salaries 1990-2023 file) | Player salary and inflation-adjusted salary; a cross-check on Dataset #1 | 2014-15 to 2021-22 |
| 4 | [NBA Stats API](https://www.nba.com/stats) (`leagueleaders` endpoint) | Official per-game regular-season stats for players who qualify for the leaderboard | 2014-15 to 2025-26 |
| 5 | [Hugging Face: Mr-Bridge NBA Salary Cap & Contracts](https://huggingface.co/datasets/Mr-Bridge/nba-salary-cap-contracts-2016-2026) | Player salaries, team payrolls, and the cap / tax / apron lines | 2015-16 to 2026-27 |
| 6 | [NBA.com official player movement log](https://stats.nba.com/js/data/playermovement/NBA_Player_Movement.json) | Every trade, signing, and waiver with its date (our outcome label) | July 2015 to present |

## Join keys at a glance

The datasets do **not** share one season convention, player ID, or team label. See notebook 07 for the details.

| # | Season column | Player key | Team label |
|---|---|---|---|
| 1 | `season` = **end** year (2015 = 2014-15) | Basketball-Reference ID (`curryst01`) | BBRef codes (`BRK`, `CHO`, `PHO`) |
| 2 | `season` = **end** year | NBA ID (`personId`) | nickname only (`Lakers`) |
| 3 | `seasonStartYear` = **start** year | name only | none |
| 4 | `season` = **start** year | NBA ID (`player_id`) | NBA codes (`BKN`, `CHA`, `PHX`) |
| 5 | `season_year` = **start** year | HoopsHype ID / `name_key` | full name (`Brooklyn Nets`) |
| 6 | `offseason_after_season` = **start** year | NBA ID / `name_key` | full name |

## What changed from the old notebook

- Only paths, imports, and heading levels changed. The cleaning code and the write-ups are the same, and
  notebooks 01, 03, 05 and 06 reproduce the previous processed files byte for byte.
- Paths point at `data-files/` (the old notebook used `data/`).
- Dataset #2's cells now run in order: load, tidy, size, missing data, clean, outliers, save. Outliers come
  after cleaning because that dataset's summary statistics need the did-not-play rows removed first.
- The report-only sections (research question, background, hypothesis, ethics, team expectations, timeline,
  AI help, rubric) are not here. They belong in the final report and stay in `Old-Notebook/`.
