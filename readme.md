# PowerScaleDB

A Flask web application used to store, organize, and analyze fictional character power-scaling data across verses.

## Features
- Add verses, characters, and keys
- Multi-hax tagging with Select2
- Automatic tier calculation from Attack Potency
- Per-verse and global key listings with hax aggregation
- Manual hax creation and autocomplete
- SQLite-backed persistent database

## Setup
python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

flask run
