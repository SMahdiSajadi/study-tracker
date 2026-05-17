#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# دستور جادویی برای ساخت ادمین در پس‌زمینه
python manage.py createsuperuser --noinput || true