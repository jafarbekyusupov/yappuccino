from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import os
import io
import logging

logger = logging.getLogger(__name__)

# try:
#     from storages.backends.s3boto3 import S3Boto3Storage
#     s3stg = S3Boto3Storage()
#     logger.info("Using s3boto3storage for profile imgs")
# except ImportError:
#     s3stg = default_storage
#     logger.info("Using default_storage for profile imgs")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    # image = models.ImageField(
    #     default='default.jpg',
    #     upload_to='profile_pics',
    #     storage=s3stg
    # )

    show_email = models.BooleanField(default=False)
    show_activity = models.BooleanField(default=True)
    email_comments = models.BooleanField(default=True)
    email_replies = models.BooleanField(default=True)
    email_reposts = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)
    theme = models.CharField(max_length=20, default='light')
    posts_per_page = models.IntegerField(default=5)

    def __str__(self): return f'{self.user.username} Profile'

    @property
    def image_url(self):
        try:
            if self.image and hasattr(self.image, 'url'): return self.image.url
        except (ValueError, OSError) as e:
            logger.warning(f"Error getting image URL for user {self.user.username}: {e}")
        return '/static/images/default-profile.png'

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'name'):
            if 'profile_pics/profile_pics/' in self.image.name:
                parts = self.image.name.split('profile_pics/')
                filename = parts[-1]
                self.image.name = f'profile_pics/{filename}'

        super().save(*args, **kwargs)

        try:
            if not hasattr(settings, 'DEFAULT_FILE_STORAGE') or 'S3Boto3Storage' not in settings.DEFAULT_FILE_STORAGE:
                # local - safe to resize
                if self.image and hasattr(self.image, 'path') and self.image.name != 'default.jpg':
                    img = Image.open(self.image.path)
                    if img.height>300 or img.width>300:
                        output_size = (300,300)
                        img.thumbnail(output_size)
                        img.save(self.image.path)
                        logger.info(f"Resized image for user {self.user.username}")
        except Exception as e:
            logger.warning(f"Could not resize image for user {self.user.username}: {e}")
            pass

    # def save(self, *args, **kwargs):
    #     is_new_image = not self.pk or not Profile.objects.filter(pk=self.pk).exists()
    #
    #     super().save(*args, **kwargs)
    #
    #     if self.image and self.image.name != 'default.jpg':
    #         try:
    #             logger.info(f"Processing image for user {self.user.username}: {self.image.name}")
    #             try:
    #                 img = Image.open(self.image.open())
    #             except Exception as e:
    #                 logger.error(f"Error opening image: {e}")
    #                 return
    #
    #             if img.height>300 or img.width>300:
    #                 output_size = (300, 300)
    #                 img.thumbnail(output_size, Image.Resampling.LANCZOS)
    #                 logger.info(f"Resized image to {img.size}")
    #
    #             img_io = io.BytesIO()
    #             img_format = img.format if img.format else 'JPEG'
    #
    #             if img_format == 'JPEG':
    #                 if img.mode in ('RGBA', 'LA', 'P'):
    #                     bg = Image.new('RGB', img.size, (255, 255, 255))
    #                     if img.mode == 'P': img = img.convert('RGBA')
    #                     bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
    #                     img = bg
    #
    #             img.save(img_io, format=img_format, quality=85, optimize=True)
    #             img_io.seek(0)
    #
    #             filename = os.path.basename(self.image.name)
    #             ppath = 'profile_pics/'+filename
    #
    #             if 'profile_pics/profile_pics/' in self.image.name:
    #                 logger.info(f"Fixing duplicated path: {self.image.name}")
    #                 parts = self.image.name.split('profile_pics/')
    #                 filename = parts[-1]  # Get the last part
    #                 ppath = 'profile_pics/' + filename
    #
    #             logger.info(f"Saving image to {ppath}")
    #             self.image.save(ppath, ContentFile(img_io.getvalue()), save=False)
    #
    #             super().save(update_fields=['image'])
    #             logger.info(f"Saved image successfully: {self.image.url}")
    #
    #         except Exception as e:
    #             logger.error(f"Error processing image: {e}", exc_info=True)