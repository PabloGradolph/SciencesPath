#!/usr/bin/env bash
# exit on error
set -o errexit

# poetry install
pip install -r requirements.txt

python manage.py clear_data
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py load_data subjects/Data/subjectsUC3M.json
python manage.py load_data subjects/Data/subjectsUAM.json
python manage.py load_data subjects/Data/subjectsUAB.json
python manage.py collectstatic --no-input
python manage.py migrate