# PowerScaleDB

A Flask web application for storing, organizing, and analyzing fictional character power-scaling data across verses.  
Designed to serve as a personalized, fast, and structured database for Attack Potency, durability, tiers, speed, and complex hax interactions.

The goal is to make power-scaling workflows intuitive, editable, and expandable without relying on poorly structured wikis.

---

## Features

- Add **verses**, **characters**, and **keys**
- Multi-hax tagging with **Select2** including:
  - Autocomplete
  - Multi-select
  - Manual creation of new hax from the form
- Automatic **Tier assignment from Attack Potency**
- Per-verse + global key listings with **aggregated hax**
- SQLite-backed persistent local database
- Clean, extendable model design
- Web UI for all core actions (no manual DB editing required)

---

## Setup

### Create virtual environment

python -m venv .venv

### Activate environment

**Windows:**
.venv\Scripts\activate

**Mac/Linux:**
source .venv/bin/activate

### Install dependencies
pip install -r requirements.txt

### Run the Application

flask run

The server will start at: http://127.0.0.1:5000/

## Database

The database is automatically created in: instance/powerscale.db

This folder is part of Flask’s application structure and is intentionally ignored by Git to avoid committing personal character data.

On first run, the database and tables will be created automatically.

---

## Data Model Overview

Verse (1)
|
|--- (many) Character
|
|--- (many) Key
|
|--- (many-to-many) Hax


### Tables

- **Verse**
  - id, name

- **Character**
  - id, name, verse_id

- **Key**
  - id, character_id, key_name  
  - ap, tier, durability, speed  
  - notes  
  - many-to-many → Hax  

- **Hax**
  - id, name


## TODO

### Core Enhancements
- Add filtering/sorting by speed, tier, AP range, and hax groups  

### Export / Analysis Features
- Export keys as JSON, CSV, and Markdown  
- Add cross-verse comparison tools  
- Add AP/tier visualization charts  

### UI / UX Improvements
- Add navigation breadcrumbs  
- Add table search functionality  

### Optional Long-Term Goals
- Hax categorization into functional groups  

---

## License

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Contributing

This is a personal project, but contributions, suggestions, and feature ideas are welcome.  
Open an issue or submit a pull request if you want to collaborate.
