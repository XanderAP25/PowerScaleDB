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

## Architecture

PowerScaleDB is built as a lightweight Flask application using SQLAlchemy for ORM modeling and Jinja2 for templating.

The core components include:

- models.py: SQLAlchemy models for Verse, Character, Key, and Hax, including the many-to-many relationship.
- routes.py: Centralized view logic for all CRUD operations.
- powerstats.py: Encapsulated tier-calculation logic derived from Attack Potency values.
- templates/: Jinja2 templates for list views, detail pages, and dynamic forms.
- static/: Custom CSS styling and Select2 integration for multi-hax selection.

The app uses SQLite for persistence and automatically initializes its schema on first run.

## Interface Preview

### Character List
<img width="2048" height="311" alt="image" src="https://github.com/user-attachments/assets/b7dfb15b-b2d2-4cb8-aff2-4bd80b6404dd" />

### Keys List
<img width="1653" height="790" alt="image" src="https://github.com/user-attachments/assets/45f1b965-0da9-40d2-bf2b-913fd8feb8f0" />

### Verses List
<img width="1662" height="628" alt="image" src="https://github.com/user-attachments/assets/21da65d6-9350-4bc6-8dbf-e40eb0345c0a" />

### Hax List
<img width="1658" height="1347" alt="image" src="https://github.com/user-attachments/assets/f08dc5aa-357b-403d-bc5e-948cb95a2a31" />

### Key Addition Page
<img width="1655" height="1139" alt="image" src="https://github.com/user-attachments/assets/0ed97c0a-753e-46c3-9866-c1b383f95774" />

### Character Table With Keys
<img width="1672" height="890" alt="image" src="https://github.com/user-attachments/assets/081d716c-c90d-4778-a491-42c0e654503f" />

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
