#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

python manage.py collectstatic --no-input
echo "Build process completed successfully!"