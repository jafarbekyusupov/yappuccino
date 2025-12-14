#!/bin/bash
set -e

echo "------------ postgres -----------"
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "| OK | postgres started"

echo "------------ migrations ------------"
python manage.py migrate --noinput
echo "| OK | migrations done running ------------"

echo "------------ collecting static files ------------"
python manage.py collectstatic --noinput
echo "| OK | static files collected ------------"

echo "======= create superuser if dne | on da 1st run"
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='prodadmin').exists():
    User.objects.create_superuser('prodadmin', 'admin@admin.com', 'supausa123')
    print('superuser created')
else:
    print('superuser already exists')
EOF

echo "========= GUNICORN STARTING ========="
exec gunicorn blogpost.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
