import os
import dj_database_url
from pathlib import Path
from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']
if os.environ.get('ALLOWED_HOSTS'):
    ALLOWED_HOSTS += os.environ.get('ALLOWED_HOSTS').split(',')

# DATABASES = {
#     'default': dj_database_url.config(
#         conn_max_age=0,
#         ssl_require=True,
#     )
# }

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}

DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
#
# if 'DATABASE_URL' in os.environ and 'pgbouncer=true' in os.environ.get('DATABASE_URL'):
#     DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
#     DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
#     DATABASES['default']['CONN_MAX_AGE'] = 0

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

if 'B2_ACCESS_KEY_ID' in os.environ:
    B2_ACCESS_KEY_ID = os.environ.get('B2_ACCESS_KEY_ID')
    B2_SECRET_ACCESS_KEY = os.environ.get('B2_SECRET_ACCESS_KEY')
    B2_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME')
    B2_REGION = os.environ.get('B2_REGION', 'eu-central-003')

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_ACCESS_KEY_ID = B2_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = B2_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME = B2_BUCKET_NAME
    AWS_S3_ENDPOINT_URL = f'https://s3.{B2_REGION}.backblazeb2.com'
    AWS_S3_REGION_NAME = B2_REGION
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_VERIFY = True

    CKEDITOR_5_FILE_STORAGE = DEFAULT_FILE_STORAGE
    CKEDITOR_5_UPLOAD_PATH = "uploads/"

    MEDIA_URL = f'https://f003.backblazeb2.com/file/{B2_BUCKET_NAME}/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'