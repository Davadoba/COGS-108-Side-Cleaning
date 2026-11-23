# New-Cleaning / team-performance: Team Standings & Playoff Features

Builds the **Team Stats** features from [ListOfPotentialFeatures.md](../../ListOfPotentialFeatures.md). Each source dataset has its own notebook, and `999_combining` merges them into one team-season table. That table is then joined onto the player tables before modeling (XGBoost).

## Notebooks (run in this order)

| Notebook | Dataset | Writes (`data-files/02-processed/`) |
|---|---|---|
| [01-llimllib-Team-Records-Playoffs](01-llimllib-Team-Records-Playoffs.ipynb) | [llimllib/nba_data](https://github.com/llimllib/nba_data) `team_seasons`, `bbref_team_stats`, `games`, `team_game_logs` | `llimllib_team_playoff_features.csv` |
| [02-ESPN-Conference-Standings](02-ESPN-Conference-Standings.ipynb) | ESPN standings API (`site.api.espn.com/apis/v2/sports/basketball/nba/standings`) | `espn_standings_features.csv` |
| [999_combining](999_combining.ipynb) | outputs of 01 + 02 | **`team_performance_combined.csv`** |

01 and 02 download their raw data into `data-files/00-raw/` the first time they run. 02 also reads two of 01's raw files (team ids and play-in games), so run 01 first. All three import paths and the season range from `../salary-data/nba_cleaning_utils.py`.

The standings come from ESPN because NBA.com's `leaguestandingsv3` endpoint (stats.nba.com) doesn't respond to scripted requests from our network (see notebook 02).

## Final table: `team_performance_combined.csv`

One row = one team + season (330 rows = 30 teams × 11 seasons, 2015-16 to 2025-26). No missing values.

| Feature | Column(s) |
|---|---|
| Regular-season final standing (seed) | `regular_season_standing`: the official order (with tiebreakers) at the end of the regular season, 1-15 within the conference. `conference_seed`: the seed after the play-in, 1-15. The two differ only for some play-in teams (7-10) from 2020-21 on. |
| Games won | `wins` (also `win_pct`, since 2019-20 and 2020-21 were shortened) |
| Made the playoffs | `made_playoffs` (play-in losers count as `False`; equals `conference_seed <= 8`) |
| Furthest playoff round | `furthest_playoff_round`: 0 = missed, 1-3 = lost in that round, 4 = lost in the Finals, 5 = champion |
| 5-year trend: playoff appearances | `playoff_appearances_last_5` (0-5) |
| 5-year trend: playoff round | `avg_playoff_round_last_5` (0-5, missed seasons count as 0) |

Identifier columns: `season`, `team`, `team_id`, `full_name`, `conference`.

- **The 5-year trends use the five seasons *before* each row,** not the current one. Notebook 01 loads 2010-11 through 2014-15 for this purpose only, so every row has a full five-season history.
- **The current season's standings and playoff results are fine to use,** because the project predicts only **offseason** trades, and those results are final by then.
- **Cross-checks in 999:** ESPN and Basketball-Reference agree on every team's record and conference. Ranking by win % alone would have mis-ranked 51 team-seasons with tied records; the official standings fix all of them.

## Join keys for combining with other datasets

- `season`: **end year** (2026 = 2025-26).
- `team`: NBA 3-letter abbreviation (`GSW`, `NYK`, `SAS`, `NOP`, `UTA`, `WAS`, ...), matching the salary tables.

Left-join from the player table (e.g. `salary_features_combined.csv`) on `season` + `team`. Each player row gets their team's values for that season.
