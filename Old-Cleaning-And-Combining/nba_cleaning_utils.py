"""Shared helpers for the dataset-cleaning notebooks in this folder.

Every notebook imports its data paths from here, so the folder layout is defined in one place:

    <project root>/
        data-files/00-raw/        raw downloads (never edited)
        data-files/01-interim/    intermediate outputs
        data-files/02-processed/  final cleaned tables
        Cleaning-And-Combining/   these notebooks + this module
"""
import os
import re
import unicodedata
from pathlib import Path

import numpy as np

_DATA_DIR = Path(__file__).resolve().parent.parent / 'data-files'


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


def normalize_name(name):
    """Name key used to match players across sources: no accents/punctuation/suffixes, lower case.

    Used by Dataset #5 (salary cap) and Dataset #6 (transactions) so both build the *same* join key.
    """
    if not isinstance(name, str):
        return np.nan
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    name = re.sub(r"[.'`’]", '', name.lower())   # "P.J." -> "pj", "De'Aaron" -> "deaaron"
    name = re.sub(r'[-,]', ' ', name)
    name = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', ' ', name)
    return ' '.join(name.split())
