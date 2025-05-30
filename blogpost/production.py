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

ENABLE_DEBUG_LOGGING = os.environ.get('ENABLE_DEBUG_LOGGING', 'False') == 'True'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers':{
        'console':{
            'level': 'DEBUG',  # tmp -- INFO → DEBUG
            'class': 'logging.StreamHandler',
        },
    },
    'loggers':{
        'users.models':{
            'handlers': ['console'],
            'level': 'DEBUG' if ENABLE_DEBUG_LOGGING else 'INFO',  # tmp -- INFO → DEBUG
            'propagate': False,
        },
        'blog.patch_ckeditor':{
            'handlers': ['console'],
            'level': 'DEBUG',  # tmp -- INFO → DEBUG
            'propagate': True,
        },
        'storages':{
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers':{
#         'console':{
#             'level': 'INFO',
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers':{
#         'users.models':{
#             'handlers': ['console'],
#             'level': 'INFO',
#         },
#         'blog.patch_ckeditor':{
#             'handlers': ['console'],
#             'level': 'INFO',
#         },
#     },
# }

if 'postgresql' in DATABASES['default']['ENGINE']: #ssl config for postg
    DATABASES['default']['OPTIONS'] = { 'sslmode': 'require',}
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True

#security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# b2
B2_ACCESS_KEY_ID = os.environ.get('B2_ACCESS_KEY_ID')
B2_SECRET_ACCESS_KEY = os.environ.get('B2_SECRET_ACCESS_KEY')
B2_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME')
B2_REGION = os.environ.get('B2_REGION', 'eu-central-003')

print(f"B2 Configuration Debug:")
print(f"B2_ACCESS_KEY_ID: {'Set' if B2_ACCESS_KEY_ID else 'Not Set'}")
print(f"B2_SECRET_ACCESS_KEY: {'Set' if B2_SECRET_ACCESS_KEY else 'Not Set'}")
print(f"B2_BUCKET_NAME: {B2_BUCKET_NAME}")
print(f"B2_REGION: {B2_REGION}")

if B2_ACCESS_KEY_ID and B2_SECRET_ACCESS_KEY and B2_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_ACCESS_KEY_ID = B2_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = B2_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME = B2_BUCKET_NAME
    AWS_S3_ENDPOINT_URL = f'https://s3.{B2_REGION}.backblazeb2.com'
    AWS_S3_REGION_NAME = B2_REGION

    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_VERIFY = True
    AWS_S3_FILE_OVERWRITE = False # True

    AWS_S3_CUSTOM_DOMAIN = f'{B2_BUCKET_NAME}.s3.{B2_REGION}.backblazeb2.com'

    CKEDITOR_5_FILE_STORAGE = DEFAULT_FILE_STORAGE
    CKEDITOR_5_UPLOAD_PATH = "uploads/"

    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

    print(f"B2 Storage configured successfully!")
    print(f"Endpoint: {AWS_S3_ENDPOINT_URL}")
    print(f"Media URL: {MEDIA_URL}")
else:
    print("B2 credentials not found, using local storage")
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'