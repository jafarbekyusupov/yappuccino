"""
WSGI config for blogpost project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

if 'RENDER' in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.settings')

application = get_wsgi_application()