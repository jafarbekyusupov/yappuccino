"""
Save as simple_debug.py in your project root
Run with: python simple_debug.py
"""
import os
import django
from django.conf import settings

# Load .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("Environment variables loaded from .env file")
except ImportError:
    print("Warning: python-dotenv not installed")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.production')
django.setup()

# Import after Django setup
from django.core.files.storage import default_storage
from django.utils.module_loading import import_string

print("\n==== STORAGE CONFIGURATION DEBUG ====")

# Check actual default storage class vs configured class
print(f"DEFAULT_FILE_STORAGE setting: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
print(f"default_storage class: {default_storage.__class__.__name__}")
print(f"default_storage module: {default_storage.__class__.__module__}")

# Try to get the configured storage class
if hasattr(settings, 'DEFAULT_FILE_STORAGE'):
    try:
        # Use import_string instead of get_storage_class
        configured_storage_class = import_string(settings.DEFAULT_FILE_STORAGE)
        print(f"Configured storage class: {configured_storage_class.__name__}")

        if not isinstance(default_storage, configured_storage_class):
            print(f"WARNING: default_storage is not an instance of the configured storage class!")
    except ImportError as e:
        print(f"Error importing storage class: {e}")

# Check S3/B2 specific settings
s3_settings = {
    'AWS_ACCESS_KEY_ID': getattr(settings, 'AWS_ACCESS_KEY_ID', 'Not set'),
    'AWS_SECRET_ACCESS_KEY': 'Set' if getattr(settings, 'AWS_SECRET_ACCESS_KEY', None) else 'Not set',
    'AWS_STORAGE_BUCKET_NAME': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set'),
    'AWS_S3_ENDPOINT_URL': getattr(settings, 'AWS_S3_ENDPOINT_URL', 'Not set'),
    'AWS_S3_CUSTOM_DOMAIN': getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'Not set'),
    'AWS_DEFAULT_ACL': getattr(settings, 'AWS_DEFAULT_ACL', 'Not set'),
    'MEDIA_URL': getattr(settings, 'MEDIA_URL', 'Not set'),
}

print("\n==== S3/B2 SETTINGS ====")
for key, value in s3_settings.items():
    print(f"{key}: {value}")

# Test a sample URL generation
print("\n==== URL GENERATION TEST ====")
test_path = "test_file.txt"
try:
    url = default_storage.url(test_path)
    print(f"URL for '{test_path}': {url}")

    # Check if the URL has the expected format
    expected_domain = s3_settings['AWS_S3_CUSTOM_DOMAIN']
    if expected_domain != 'Not set' and expected_domain not in url:
        print(f"WARNING: URL doesn't contain expected domain '{expected_domain}'")

except Exception as e:
    print(f"Error generating URL: {e}")

# Check profile model storage
print("\n==== PROFILE MODEL STORAGE ====")
try:
    from users.models import Profile

    # Check if the model's image field has a custom storage
    image_field = Profile._meta.get_field('image')
    field_storage = getattr(image_field, 'storage', None)
    print(f"Profile image field upload_to: {getattr(image_field, 'upload_to', 'Not found')}")

    if field_storage:
        print(f"Profile image field has custom storage: {field_storage.__class__.__name__}")
    else:
        print("Profile image field uses default storage")

    # Get a sample profile and check its image URL
    try:
        sample_profile = Profile.objects.first()
        if sample_profile:
            print(f"Sample profile found: {sample_profile}")
            if sample_profile.image:
                print(f"Image name: {sample_profile.image.name}")
                print(f"Image URL: {sample_profile.image.url}")

                # Check for path duplication
                if 'profile_pics/profile_pics' in sample_profile.image.name:
                    print("ISSUE DETECTED: Path duplication in image name!")
            else:
                print("Profile has no image")
        else:
            print("No profiles found in the database")
    except Exception as e:
        print(f"Error accessing profile data: {e}")

except ImportError:
    print("Could not import Profile model")
except Exception as e:
    print(f"Error checking profile model: {e}")

# Test file upload
print("\n==== TEST FILE UPLOAD ====")
try:
    from django.core.files.base import ContentFile

    test_content = b"Test file content"
    test_filename = f"debug_test_file.txt"

    print(f"Uploading test file: {test_filename}")
    path = default_storage.save(test_filename, ContentFile(test_content))
    print(f"Saved to: {path}")

    url = default_storage.url(path)
    print(f"URL: {url}")

    # Clean up
    default_storage.delete(path)
    print(f"Test file deleted")

except Exception as e:
    print(f"Error testing file upload: {e}")

print("\n==== DEBUG COMPLETE ====")