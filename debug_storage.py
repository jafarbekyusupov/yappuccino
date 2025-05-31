"""
Save as debug_storage.py in your project root
Run with: python debug_storage.py
"""
import os
import django
from django.conf import settings

# Load .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.production')
django.setup()

# Import after Django setup
from django.core.files.storage import default_storage, get_storage_class
from storages.backends.s3boto3 import S3Boto3Storage
import inspect

print("==== STORAGE CONFIGURATION DEBUG ====")

# Check actual default storage class vs configured class
print(f"DEFAULT_FILE_STORAGE setting: {settings.DEFAULT_FILE_STORAGE}")
print(f"default_storage class: {default_storage.__class__.__name__}")
print(f"default_storage module: {default_storage.__class__.__module__}")

# Check if FileSystemStorage is being used instead of S3Boto3Storage
if hasattr(settings, 'DEFAULT_FILE_STORAGE'):
    configured_storage_class = get_storage_class(settings.DEFAULT_FILE_STORAGE)
    print(f"Configured storage class: {configured_storage_class.__name__}")

    if not isinstance(default_storage, configured_storage_class):
        print(f"WARNING: default_storage is not an instance of the configured storage class!")
        print(f"This suggests Django is not properly initializing your storage backend.")

# Check S3/B2 specific settings
s3_settings = {
    'AWS_ACCESS_KEY_ID': getattr(settings, 'AWS_ACCESS_KEY_ID', None),
    'AWS_SECRET_ACCESS_KEY': 'Set' if getattr(settings, 'AWS_SECRET_ACCESS_KEY', None) else 'Not set',
    'AWS_STORAGE_BUCKET_NAME': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None),
    'AWS_S3_ENDPOINT_URL': getattr(settings, 'AWS_S3_ENDPOINT_URL', None),
    'AWS_S3_CUSTOM_DOMAIN': getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None),
    'AWS_S3_ADDRESSING_STYLE': getattr(settings, 'AWS_S3_ADDRESSING_STYLE', None),
    'AWS_DEFAULT_ACL': getattr(settings, 'AWS_DEFAULT_ACL', None),
    'AWS_QUERYSTRING_AUTH': getattr(settings, 'AWS_QUERYSTRING_AUTH', None),
    'MEDIA_URL': getattr(settings, 'MEDIA_URL', None),
}

print("\n==== S3/B2 SETTINGS ====")
for key, value in s3_settings.items():
    print(f"{key}: {value}")

# Test direct S3Boto3Storage initialization
print("\n==== DIRECT S3BOTO3STORAGE TEST ====")
try:
    # Create a direct instance of S3Boto3Storage
    direct_storage = S3Boto3Storage()
    print(f"S3Boto3Storage direct instance class: {direct_storage.__class__.__name__}")

    # Test a file upload URL with direct storage
    test_file_path = "test_debug_direct.txt"
    file_url = direct_storage.url(test_file_path)
    print(f"Direct storage URL format: {file_url}")

    # Check if the URL matches the expected format with AWS_S3_CUSTOM_DOMAIN
    expected_domain = s3_settings['AWS_S3_CUSTOM_DOMAIN']
    if expected_domain and expected_domain not in file_url:
        print(f"WARNING: URL doesn't contain expected domain {expected_domain}")

except Exception as e:
    print(f"Error testing direct S3Boto3Storage: {e}")

# Check profile model storage
print("\n==== PROFILE MODEL STORAGE ====")
try:
    from users.models import Profile

    profile_model = Profile

    # Check if the model's image field has a custom storage
    image_field = profile_model._meta.get_field('image')
    custom_storage = getattr(image_field, 'storage', None)

    print(f"Profile image field storage: {custom_storage.__class__.__name__ if custom_storage else 'Uses default'}")

    # Get a sample profile and check its image URL
    try:
        sample_profile = Profile.objects.first()
        if sample_profile:
            print(f"Sample profile image name: {sample_profile.image.name if sample_profile.image else 'No image'}")
            print(f"Sample profile image URL: {sample_profile.image.url if sample_profile.image else 'No image'}")
    except Exception as e:
        print(f"Error accessing profile data: {e}")

except ImportError:
    print("Could not import Profile model")
except Exception as e:
    print(f"Error checking profile model: {e}")

print("\n==== DEBUG COMPLETE ====")