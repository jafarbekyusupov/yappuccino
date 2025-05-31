"""
Save as fix_profile_images.py in your project root
Run with: python fix_profile_images.py
"""
import os
import django
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except ImportError:
    logger.warning("python-dotenv not installed, using environment variables as is")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.production')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from users.models import Profile


def fix_profile_images():
    """Fix profile images with duplicated paths and storage issues"""
    logger.info("Starting profile image path fix")

    # Check current storage
    logger.info(f"Default storage: {default_storage.__class__.__name__}")

    # Get all profiles
    profiles = Profile.objects.all()
    logger.info(f"Found {profiles.count()} profiles")

    fixed_count = 0
    error_count = 0

    for profile in profiles:
        if not profile.image or profile.image.name == 'default.jpg':
            logger.info(f"Skipping profile {profile.id} - using default image")
            continue

        try:
            original_path = profile.image.name
            logger.info(f"Processing profile {profile.id}, image: {original_path}")

            # Check for path duplication
            if 'profile_pics/profile_pics/' in original_path:
                logger.info(f"Found duplicated path: {original_path}")

                # Extract the actual filename
                parts = original_path.split('profile_pics/')
                filename = parts[-1]

                # Create correct path
                new_path = f'profile_pics/{filename}'
                logger.info(f"New path will be: {new_path}")

                try:
                    # If we can access the current image
                    image_content = None
                    try:
                        # Try to read the current image
                        image_content = profile.image.read()
                        logger.info(f"Successfully read image content: {len(image_content)} bytes")
                    except Exception as read_error:
                        logger.warning(f"Could not read image {original_path}: {read_error}")

                    if image_content:
                        # Save to the new path
                        profile.image.save(new_path, ContentFile(image_content), save=True)
                        logger.info(f"Image saved to new path: {profile.image.name}")

                        # Try to delete the old file if it's different
                        if original_path != profile.image.name:
                            try:
                                if hasattr(default_storage, 'delete'):
                                    default_storage.delete(original_path)
                                    logger.info(f"Deleted old file: {original_path}")
                            except Exception as del_error:
                                logger.warning(f"Could not delete old file {original_path}: {del_error}")

                        fixed_count += 1
                    else:
                        logger.warning(f"No image content to save for {original_path}")
                        error_count += 1

                except Exception as save_error:
                    logger.error(f"Error saving image: {save_error}")
                    error_count += 1
            else:
                logger.info(f"No path duplication detected for {original_path}")

        except Exception as e:
            logger.error(f"Error processing profile {profile.id}: {e}")
            error_count += 1

    logger.info(f"Profile image fix complete: {fixed_count} fixed, {error_count} errors")


if __name__ == "__main__":
    fix_profile_images()