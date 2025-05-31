#!/usr/bin/env python
"""
Enhanced B2 storage test script with .env file support
Run with: python test_s3.py
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    logger.info("Loading environment variables from .env file")
    # Load from .env file in the current directory
    load_dotenv()

    # Also try to load from a possible .env file in parent directory
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parent_env = os.path.join(parent_dir, '.env')
    if os.path.exists(parent_env):
        logger.info(f"Loading environment variables from parent directory: {parent_env}")
        load_dotenv(parent_env)
except ImportError:
    logger.warning("python-dotenv not installed. Will use existing environment variables only.")
    logger.warning("To install: pip install python-dotenv")

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.production')  # Use production settings

try:
    import django

    django.setup()
    logger.info("Django successfully imported and set up")

    from django.conf import settings
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile

    logger.info(f"Settings module: {settings.SETTINGS_MODULE}")
    logger.info(f"Debug mode: {settings.DEBUG}")


    def test_b2_connection():
        """Test the B2 storage configuration and connection"""
        logger.info("=== TESTING B2 STORAGE CONNECTION ===")

        # Check environment variables
        logger.info("\n=== ENVIRONMENT VARIABLES ===")
        env_vars = ['B2_ACCESS_KEY_ID', 'B2_SECRET_ACCESS_KEY', 'B2_BUCKET_NAME', 'B2_REGION']
        for var in env_vars:
            val = os.environ.get(var)
            if val:
                disp_val = val[:8] + '...' if var in ['B2_ACCESS_KEY_ID', 'B2_SECRET_ACCESS_KEY'] else val
                logger.info(f"✓ {var}: {disp_val}")
            else:
                logger.error(f"✗ {var}: Not set")

        # Check Django settings
        logger.info("\n=== DJANGO SETTINGS ===")
        logger.info(f"DEBUG: {settings.DEBUG}")
        logger.info(f"Storage backend: {default_storage.__class__.__name__}")

        # Check storage configuration
        if hasattr(settings, 'DEFAULT_FILE_STORAGE'):
            logger.info(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")

        if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
            logger.info(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
        if hasattr(settings, 'AWS_S3_ENDPOINT_URL'):
            logger.info(f"AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
        if hasattr(settings, 'MEDIA_URL'):
            logger.info(f"MEDIA_URL: {settings.MEDIA_URL}")

        # Test attributes of storage backend
        logger.info("\n=== STORAGE BACKEND ATTRIBUTES ===")
        backend_attrs = [
            'bucket_name', 'access_key', 'custom_domain',
            'default_acl', 'querystring_auth', 'file_overwrite'
        ]
        for attr in backend_attrs:
            if hasattr(default_storage, attr):
                value = getattr(default_storage, attr)
                # Don't show full secrets
                if attr == 'access_key' and value:
                    value = value[:4] + '...'
                logger.info(f"✓ {attr}: {value}")
            else:
                logger.info(f"✗ {attr}: Missing")

        # Test file upload
        logger.info("\n=== TEST FILE UPLOAD ===")
        try:
            test_content = f"This is a test file for B2 storage - {os.urandom(4).hex()}"
            test_file = ContentFile(test_content.encode('utf-8'))
            test_filename = f"test_b2_upload_{os.urandom(4).hex()}.txt"

            # Save file
            logger.info(f"Attempting to save file: {test_filename}")
            saved_path = default_storage.save(test_filename, test_file)
            logger.info(f"✓ File saved to path: {saved_path}")

            # Get URL
            file_url = default_storage.url(saved_path)
            logger.info(f"✓ File URL: {file_url}")

            # Check if file exists
            logger.info(f"Checking if file exists at: {saved_path}")
            if default_storage.exists(saved_path):
                logger.info("✓ File exists in storage")

                # Try to read the file back
                logger.info("Attempting to read file back...")
                try:
                    file_content = default_storage.open(saved_path).read()
                    if isinstance(file_content, bytes):
                        file_content = file_content.decode('utf-8')

                    logger.info(f"Read content: {file_content[:30]}...")
                    if file_content.strip() == test_content.strip():
                        logger.info("✓ File content verified")
                    else:
                        logger.error("✗ File content mismatch")
                        logger.error(f"Expected: {test_content}")
                        logger.error(f"Got: {file_content}")
                except Exception as e:
                    logger.error(f"✗ Error reading file: {str(e)}")

                # Try to delete the file
                try:
                    logger.info(f"Deleting test file: {saved_path}")
                    default_storage.delete(saved_path)
                    logger.info("✓ Test file deleted successfully")

                    if default_storage.exists(saved_path):
                        logger.error("✗ File still exists after deletion attempt")
                    else:
                        logger.info("✓ File no longer exists - deletion confirmed")
                except Exception as e:
                    logger.error(f"✗ Error deleting file: {str(e)}")
            else:
                logger.error(f"✗ File not found in storage after saving")
                logger.error(f"Attempted path: {saved_path}")

        except Exception as e:
            logger.error(f"✗ Upload test failed: {str(e)}")
            import traceback
            traceback.print_exc()

        logger.info("\nB2 Storage test completed!")


    # Run the test
    test_b2_connection()

except ImportError as e:
    logger.error(f"Failed to import Django or other modules: {e}")
    logger.error("Make sure you're running this script from the project root directory")

except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")
    import traceback

    traceback.print_exc()