"""
WSGI config for blogpost project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

if 'RENDER' in os.environ or os.environ.get('DJANGO_SETTINGS_MODULE') == 'blogpost.production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.production')
    print("--- production settings ---")
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.settings')
    print("dev settings")

application = get_wsgi_application()