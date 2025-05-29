#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate sessions
python manage.py migrate admin

python manage.py migrate blog 0003_post_is_repost_post_original_post_post_view_count_and_more
python manage.py migrate

python manage.py collectstatic --no-input