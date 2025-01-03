#!/bin/sh

python manage.py wait_for_db
python manage.py migrate --noinput
python manage.py loaddata theatre_api_db_data.json
python manage.py createsuperuser --noinput || true
python manage.py runserver 0.0.0.0:8000
