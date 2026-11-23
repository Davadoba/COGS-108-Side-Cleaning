# New-Cleaning / player-stats: Individual Player Stats Features

Builds the individual player-stat features from [ListOfPotentialFeatures.md](../../ListOfPotentialFeatures.md). Each source dataset has its own notebook, and `999_combining` merges them into one player-season table. That table is then left-joined onto the salary table before modeling (XGBoost).

## Notebooks (run in this order)

| Notebook | Dataset | Writes (`data-files/02-processed/`) |
|---|---|---|
| [01-llimllib-Regular-Season-Stats](01-llimllib-Regular-Season-Stats.ipynb) | [llimllib/nba_data](https://github.com/llimllib/nba_data) `player_season_stats` (regular season), `players`, `team_seasons` | `llimllib_player_regular_season_features.csv` |
| [02-llimllib-Playoff-Stats](02-llimllib-Playoff-Stats.ipynb) | llimllib `player_season_stats` (playoffs) | `llimllib_player_playoff_features.csv` |
| [03-bbref-Box-Plus-Minus](03-bbref-Box-Plus-Minus.ipynb) | [Basketball-Reference](https://www.basketball-reference.com/leagues/NBA_2026_advanced.html) advanced stats pages (regular season + playoffs) | `bbref_player_bpm_features.csv` |
| [999_combining](999_combining.ipynb) | outputs of 01 + 02 + 03 | **`player_stats_combined.csv`** |

- **01 and 03 download their raw data** into `data-files/00-raw/` the first time they run. 02 reads 01's raw files.
- **03 waits 4 seconds between pages**, to respect Basketball-Reference's limit of 20 requests per minute. Its 25 pages take under 2 minutes once and are skipped after.
- **All four notebooks import shared helpers** (paths, season range, `normalize_name`, and the new `prior_seasons_average`) from `../salary-data/nba_cleaning_utils.py`.

The two EDA notebooks (`nba_player_stats_regular_season_eda.ipynb`, `Playoffs-EDA.ipynb`) are from the earlier version of this folder. They still read the old cleaned CSVs in `data/02-processed/`, which are kept for them, and they are not part of the pipeline above.

## Final table: `player_stats_combined.csv`

One row = one player + season (5,975 rows, 2015-16 to 2025-26). That covers every player who played a regular-season or playoff game, and every row of `salary_features_combined.csv` finds its match.

| Feature | Column(s) |
|---|---|
| Regular season: PPG, RPG, APG, BPG, SPG | `rs_ppg`, `rs_rpg`, `rs_apg`, `rs_bpg`, `rs_spg` |
| Regular season: true shooting %, games played, minutes per game | `rs_ts_pct`, `rs_gp`, `rs_mpg` |
| Regular season: Box +/- | `rs_bpm` (Basketball-Reference Box Plus/Minus) |
| Playoffs: PPG, RPG, APG, BPG, SPG | `po_ppg`, `po_rpg`, `po_apg`, `po_bpg`, `po_spg` |
| Playoffs: Box +/-, true shooting %, minutes per game | `po_bpm`, `po_ts_pct`, `po_mpg` (also `po_gp`, `played_in_playoffs`) |
| Age, years in the NBA | `age`, `years_in_nba` (seasons since the player's first NBA game; a rookie is 1) |
| 3-year trend: PPG, RPG, APG, Box +/-, minutes, games played | `avg_ppg_last_3`, `avg_rpg_last_3`, `avg_apg_last_3`, `avg_bpm_last_3`, `avg_mpg_last_3`, `avg_gp_last_3`, and `seasons_played_last_3` (0-3) |
| (extra) on-court plus/minus per game | `rs_plus_minus`, `po_plus_minus` |

Key columns: `season`, `nba_player_id`, `player_name`, `name_key`, `last_team` (end-of-season team, reference only).

- **The 3-year trends are averages over the three regular seasons *before* this one** (season − 3 to season − 1), using whichever of those the player played. The current season is never included, the same rule as the team 5-year trends. `seasons_played_last_3` says how many seasons went in, and the averages are blank when it is 0 (mostly rookies). Notebooks 01 and 03 also load 2012-13 through 2014-15 for this purpose only. `avg_bpm_last_3` is weighted by minutes, because Box +/- is a rate that can be extreme for tiny samples. The others are plain averages.
- **Box +/- is real Box Plus/Minus from Basketball-Reference,** matched to NBA ids through llimllib's `bbref_salaries` table, with a unique-name fallback. Every matched row has the same games played in both sources. The database's own `plus_minus` is on-court plus/minus, a different stat that mostly reflects the team. It is kept as an extra column.
- **Every row is kept, including players with very few games.** Their per-game stats are noisy, but dropping them would also blank their age, experience, and games played in the salary join. `rs_gp` / `rs_mpg` show the sample size.
- **Traded players have one combined row per season.** In the salary table they have one row per team, and each gets the full-season stats.
- **Play-in games are in neither the regular-season nor the playoff stats.**
- **The current season's stats are fine to use,** because the project predicts only **offseason** trades.

Missing values are left as `NaN` for XGBoost:

- `po_*` for players who didn't play in the playoffs.
- `rs_*` and the trends for the 7 playoff-only players.
- the trends for players with no prior seasons.
- `*_ts_pct` for players with no shot attempts.
- `last_team` where the source has none.

## Join keys for combining with other datasets

- `season`: **end year** (2026 = 2025-26).
- `nba_player_id`: NBA.com person id, the same as `nba_player_id` in the salary tables.

Left-join from `salary_features_combined.csv` on `season` + `nba_player_id`. Don't join on `last_team`. For a name-based table, use `season` + `name_key` (built with `normalize_name()`).
