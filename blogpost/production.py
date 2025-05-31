import os
import dj_database_url
from pathlib import Path
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

# S3 settings
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

print(f"=== S3 Configuration Check ===")
print(f"AWS_ACCESS_KEY_ID: {'- OK - Set' if AWS_ACCESS_KEY_ID else 'x Missing'}")
print(f"AWS_SECRET_ACCESS_KEY: {'- OK - Set' if AWS_SECRET_ACCESS_KEY else 'x Missing'}")
print(
    f"AWS_STORAGE_BUCKET_NAME: {'- OK - ' + str(AWS_STORAGE_BUCKET_NAME) if AWS_STORAGE_BUCKET_NAME else 'x Missing'}")
print(f"AWS_S3_REGION_NAME: {'- OK - ' + str(AWS_S3_REGION_NAME) if AWS_S3_REGION_NAME else 'x Missing'}")

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    print("===================================== AWS S3 CONFIG =====================================")
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = True

    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

    CKEDITOR_5_FILE_STORAGE = DEFAULT_FILE_STORAGE
    CKEDITOR_5_UPLOAD_PATH = "uploads/"

    print(f"- OK - DEFAULT_FILE_STORAGE = {DEFAULT_FILE_STORAGE}")
    print(f"- OK - Media URL = {MEDIA_URL}")
    print(f"- OK - S3 Bucket = {AWS_STORAGE_BUCKET_NAME}")

    try:
        import django.core.files.storage
        from storages.backends.s3boto3 import S3Boto3Storage

        s3_storage = S3Boto3Storage()
        django.core.files.storage.default_storage = s3_storage

        print(f"OK FORCED DEFAULT_STORAGE: {django.core.files.storage.default_storage.__class__.__name__}")

    except Exception as e:
        print(f"X STORAGE RELOAD FAILED: {e}")

else:
    print("x S3 credentials incomplete - Using local storage")
    missing = []
    if not AWS_ACCESS_KEY_ID: missing.append('AWS_ACCESS_KEY_ID')
    if not AWS_SECRET_ACCESS_KEY: missing.append('AWS_SECRET_ACCESS_KEY')
    if not AWS_STORAGE_BUCKET_NAME: missing.append('AWS_STORAGE_BUCKET_NAME')
    print(f"x Missing: {missing}")

    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    print(f"x Fallback: DEFAULT_FILE_STORAGE = {DEFAULT_FILE_STORAGE}")

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

# # lets see wth is going on
# print(f"=== SETTINGS CHECK ===")
# print(f"MODULE DEFAULT_FILE_STORAGE = {locals().get('DEFAULT_FILE_STORAGE', 'NOT SET')}")
# print(f"MEDIA_URL = {locals().get('MEDIA_URL', 'NOT SET')}")
#
# # FORCE THIS STUPD ... TO REINIT STRG
# print("==== FORCING DJANGO to REINIT STORAGE ====")
# try:
#     from django.core.files.storage import default_storage
#     from django.utils.module_loading import import_string
#
#     scp = locals().get('DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')
#     StorageClass = import_string(scp)
#
#     import django.core.files.storage
#     django.core.files.storage.default_storage = StorageClass()
#
#     print(f"- OK - Forced storage to: {django.core.files.storage.default_storage.__class__.__name__}")
#
# except Exception as e:
#     print(f"x Failed to force storage reinit: {e}")