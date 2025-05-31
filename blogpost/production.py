import os
import dj_database_url
from pathlib import Path
from botocore.config import Config
from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']
if os.environ.get('ALLOWED_HOSTS'):
    ALLOWED_HOSTS += os.environ.get('ALLOWED_HOSTS').split(',')

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

if 'postgresql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

B2_ACCESS_KEY_ID = os.environ.get('B2_ACCESS_KEY_ID')
B2_SECRET_ACCESS_KEY = os.environ.get('B2_SECRET_ACCESS_KEY')
B2_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME')
B2_REGION = os.environ.get('B2_REGION', 'eu-central-003')

print(f"=== B2 Configuration Check ===")
print(f"B2_ACCESS_KEY_ID: {'- OK - Set' if B2_ACCESS_KEY_ID else 'x Missing'}")
print(f"B2_SECRET_ACCESS_KEY: {'- OK - Set' if B2_SECRET_ACCESS_KEY else 'x Missing'}")
print(f"B2_BUCKET_NAME: {'- OK - ' + str(B2_BUCKET_NAME) if B2_BUCKET_NAME else 'x Missing'}")
print(f"B2_REGION: {'- OK - ' + str(B2_REGION) if B2_REGION else 'x Missing'}")

if B2_ACCESS_KEY_ID and B2_SECRET_ACCESS_KEY and B2_BUCKET_NAME:
    print("===================================== B2 STG CONFIG =====================================")
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    boto3_config = Config(
        request_checksum_calculation='when_required',
        response_checksum_validation='when_required'
    )

    AWS_ACCESS_KEY_ID = B2_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = B2_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME = B2_BUCKET_NAME
    AWS_S3_ENDPOINT_URL = f'https://s3.{B2_REGION}.backblazeb2.com'
    AWS_S3_REGION_NAME = B2_REGION

    AWS_S3_ADDRESSING_STYLE = 'path'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_VERIFY = True
    AWS_S3_FILE_OVERWRITE = True

    AWS_S3_BOTO3_CONFIG = boto3_config

    AWS_S3_USE_SSL = True
    AWS_S3_SIGNATURE_NAME = 's3v4'
    AWS_S3_REGION_NAME = B2_REGION

    AWS_IS_GZIPPED = False
    AWS_S3_GZIP = False

    # env vars to fix boto3 checksum errs
    import os

    os.environ['AWS_S3_ADDRESSING_STYLE'] = 'path'
    os.environ['AWS_S3_SIGNATURE_VERSION'] = 's3v4'

    AWS_S3_CUSTOM_DOMAIN = f'{B2_BUCKET_NAME}.s3.{B2_REGION}.backblazeb2.com'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

    CKEDITOR_5_FILE_STORAGE = DEFAULT_FILE_STORAGE
    CKEDITOR_5_UPLOAD_PATH = "uploads/"

    print(f"- OK - DEFAULT_FILE_STORAGE = {DEFAULT_FILE_STORAGE}")
    print(f"- OK - Media URL = {MEDIA_URL}")
    print(f"- OK - S3 Endpoint = {AWS_S3_ENDPOINT_URL}")

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'users.models': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'blog.patch_ckeditor': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'storages': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# lets see wth is going on
print(f"=== SETTINGS CHECK ===")
print(f"MODULE DEFAULT_FILE_STORAGE = {locals().get('DEFAULT_FILE_STORAGE', 'NOT SET')}")
print(f"MEDIA_URL = {locals().get('MEDIA_URL', 'NOT SET')}")

# FORCE THIS STUPD ... TO REINIT STRG
print("==== FORCING DJANGO to REINIT STORAGE ====")
try:
    from django.core.files.storage import default_storage
    from django.utils.module_loading import import_string

    scp = locals().get('DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')
    StorageClass = import_string(scp)

    import django.core.files.storage
    django.core.files.storage.default_storage = StorageClass()

    print(f"- OK - Forced storage to: {django.core.files.storage.default_storage.__class__.__name__}")

except Exception as e:
    print(f"x Failed to force storage reinit: {e}")