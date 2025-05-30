from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.module_loading import import_string
import os
import io
import logging

logger = logging.getLogger(__name__)

# to pass the instance of storage explciitly
try:
    if hasattr(settings, 'DEFAULT_FILE_STORAGE'):
        S3Storage = import_string(settings.DEFAULT_FILE_STORAGE)
        strg_inst = S3Storage()
        logger.info(f"uS3Sing {S3Storage.__name__} for Profile images")
    else:
        strg_inst = default_storage
        logger.info(f"Using default_storage for Profile images")
except ImportError:
    logger.warning(f"Could not import storage class, using default_storage")
    strg_inst = default_storage

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        default='default.jpg',
        upload_to='profile_pics',
        storage=strg_inst # YAY
    )

    show_email = models.BooleanField(default=False)
    show_activity = models.BooleanField(default=True)

    email_comments = models.BooleanField(default=True)
    email_replies = models.BooleanField(default=True)
    email_reposts = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)

    theme = models.CharField(max_length=20, default='light')
    posts_per_page = models.IntegerField(default=5)

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def image_url(self):
        try:
            if self.image and hasattr(self.image, 'url'): return self.image.url
        except (ValueError, OSError) as e:
            logger.warning(f"Error getting image URL for user {self.user.username}: {e}")
        return '/static/images/default-profile.png'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image and self.image.name != 'default.jpg':
            try:
                logger.info(f"Processing image upload for user: {self.user.username}")
                logger.info(f"Storage backend: {self.image.storage.__class__.__name__}")
                logger.info(f"Current image path: {self.image.name}")

                img = Image.open(self.image.open())
                logger.info("Opened image for processing")

                if img.height>300 or img.width>300:
                    output_size = (300,300)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    logger.info(f"Resized image to: {img.size}")

                img_io = io.BytesIO()
                img_format = img.format if img.format else 'JPEG'

                if img_format == 'JPEG':
                    if img.mode in ('RGBA', 'LA', 'P'):
                        bg = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P': img = img.convert('RGBA')
                        bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = bg

                # BUFFER SAVE
                img.save(img_io, format=img_format, quality=85, optimize=True)
                img_io.seek(0)

                # UPD -- solving path dup bug
                filename = os.path.basename(self.image.name)
                if 'profile_pics/profile_pics/' in self.image.name: # UPD -- brute solving path dup bug
                    parts = self.image.name.split('profile_pics/')
                    filename = parts[-1]
                    logger.info(f"Fixed duplicated path, new filename: {filename}")

                # cement ittttttttttttttttttttttttttt
                proper_path = f'profile_pics/{filename}'
                logger.info(f"Will save image to: {proper_path}")

                self.image.save( proper_path,ContentFile(img_io.getvalue()),save=False)

                super().save(update_fields=['image'])
                logger.info(f"Image saved successfully at: {self.image.name}")
                logger.info(f"Image URL: {self.image.url}")

            except Exception as e: logger.error(f"Error processing image for user {self.user.username}: {e}", exc_info=True)