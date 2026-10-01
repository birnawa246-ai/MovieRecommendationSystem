#!/bin/bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/import_credits.py
python seed_admin.py
python app.py
