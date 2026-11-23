"""Shared helpers for the notebooks in New-Cleaning/.

Folder layout (paths are defined once, here):

    <project root>/
        data-files/00-raw/        raw downloads (never edited)
        data-files/01-interim/    intermediate outputs
        data-files/02-processed/  final cleaned tables
        New-Cleaning/salary-data/ these notebooks + this module

Join keys shared by every output table, so the final merge before XGBoost is simple:
    season     -> END year of the season (2026 = 2025-26)
    team       -> standard NBA 3-letter abbreviation (GSW, NYK, SAS, NOP, UTA, WAS, PHX, BKN, CHA, ...)
    name_key   -> normalize_name(player name)
"""
import json
import os
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

_DATA_DIR = Path(__file__).resolve().parents[2] / 'data-files'


def _relative(path):
    """Show paths relative to the notebook's folder when possible (shorter, machine-independent output)."""
    try:
        return Path(os.path.relpath(path))
    except ValueError:          # e.g. a different drive on Windows
        return path


DATA_DIR = _relative(_DATA_DIR)
RAW = DATA_DIR / '00-raw'
INTERIM = DATA_DIR / '01-interim'
PROCESSED = DATA_DIR / '02-processed'

for _d in (RAW, INTERIM, PROCESSED):
    _d.mkdir(parents=True, exist_ok=True)

# Project scope: 2015-16 through 2025-26, written as season END years.
FIRST_SEASON, LAST_SEASON = 2016, 2026


def normalize_name(name):
    """Name key used to match players across sources: no accents/punctuation/suffixes, lower case."""
    if not isinstance(name, str):
        return np.nan
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    name = re.sub(r"[.'`’]", '', name.lower())   # "P.J." -> "pj", "De'Aaron" -> "deaaron"
    name = re.sub(r'[-,]', ' ', name)
    name = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', ' ', name)
    return ' '.join(name.split())


def prior_seasons_average(df, id_col, value_cols, n=3):
    """Average of each value column over the player's rows in the n seasons BEFORE each row (season-n .. season-1).

    The current season is never included. Seasons the player has no row for are skipped, so the average uses
    whichever of the n seasons he played. Returns one row per (id_col, season) of `df`, with
    avg_<col>_last_<n> columns and seasons_played_last_<n> (0-n). The averages are NaN when that count is 0.
    """
    base = df[[id_col, 'season'] + value_cols]
    # Relabel each row as season+1, season+2, ..., season+n, so each row lands on the n seasons that follow it.
    shifted = pd.concat([base.assign(season=base['season'] + k) for k in range(1, n + 1)], ignore_index=True)
    agg = shifted.groupby([id_col, 'season']).agg(
        **{f'avg_{c}_last_{n}': (c, 'mean') for c in value_cols},
        **{f'seasons_played_last_{n}': ('season', 'size')},
    ).reset_index()
    out = df[[id_col, 'season']].merge(agg, on=[id_col, 'season'], how='left', validate='one_to_one')
    out[f'seasons_played_last_{n}'] = out[f'seasons_played_last_{n}'].fillna(0).astype(int)
    return out


# ESPN uses a few non-standard abbreviations; map them to the NBA's own.
ESPN_TO_NBA_ABBREV = {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP', 'UTAH': 'UTA', 'WSH': 'WAS'}

# ------------------------------------------------------------------------------------------------
# ESPN download (used by 03-ESPN-Player-Contracts.ipynb)
# ------------------------------------------------------------------------------------------------
ESPN_CORE = 'https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba'
ESPN_SITE = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba'
ESPN_STATS = 'https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/statistics/byathlete'


def _get_json(session, url, params=None, tries=4):
    """GET a URL and return its JSON; returns {'_status': code} for a 404 and retries other failures."""
    for attempt in range(tries):
        try:
            r = session.get(url, params=params, timeout=30)
            if r.status_code == 404:
                return {'_status': 404}
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError):
            if attempt == tries - 1:
                return {'_status': 'error'}
            time.sleep(2 ** attempt)


def download_espn_contracts(athletes_path, contracts_path, teams_path,
                            seasons=range(FIRST_SEASON, LAST_SEASON + 1), workers=8):
    """Download the raw ESPN data that hoopR's espn_nba_player_contract() wraps.

    1. For each season, list every athlete who played (ESPN's by-athlete stats leaderboard).
    2. For each (athlete, season), fetch /athletes/{id}/contracts/{season} -- the same endpoint as hoopR.
    3. Fetch ESPN's team list (team id -> abbreviation).
    Files that already exist are skipped, so re-running the notebook does not re-download.
    """
    session = requests.Session()
    session.headers['User-Agent'] = 'cogs108-student-project'

    if not Path(athletes_path).exists():
        rows = []
        for season in seasons:
            data = _get_json(session, ESPN_STATS, {'season': season, 'seasontype': 2, 'limit': 1000})
            for a in data.get('athletes', []):
                ath = a['athlete']
                rows.append({'season': season, 'athlete_id': ath['id'],
                             'name': ath.get('displayName'), 'team_abbrev_stats': ath.get('teamShortName')})
        with open(athletes_path, 'w', encoding='utf-8') as f:
            json.dump(rows, f)
        print(f'saved {len(rows):,} athlete-season rows to {athletes_path}')

    if not Path(teams_path).exists():
        data = _get_json(session, f'{ESPN_SITE}/teams')
        teams = [{'espn_team_id': t['team']['id'], 'espn_abbrev': t['team']['abbreviation'],
                  'team_name': t['team']['displayName']}
                 for t in data['sports'][0]['leagues'][0]['teams']]
        with open(teams_path, 'w', encoding='utf-8') as f:
            json.dump(teams, f)
        print(f'saved {len(teams)} teams to {teams_path}')

    if not Path(contracts_path).exists():
        with open(athletes_path, encoding='utf-8') as f:
            pairs = sorted({(r['athlete_id'], r['season']) for r in json.load(f)})

        def fetch(pair):
            athlete_id, season = pair
            rec = _get_json(session, f'{ESPN_CORE}/athletes/{athlete_id}/contracts/{season}')
            rec['athlete_id'], rec['season_requested'] = athlete_id, season
            return rec

        with ThreadPoolExecutor(max_workers=workers) as pool:
            records = list(pool.map(fetch, pairs))
        with open(contracts_path, 'w', encoding='utf-8') as f:
            json.dump(records, f)
        print(f'saved {len(records):,} contract records to {contracts_path}')
