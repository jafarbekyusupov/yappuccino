from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import io
import logging

logger = logging.getLogger(__name__)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    # privacy settings
    show_email = models.BooleanField(default=False)
    show_activity = models.BooleanField(default=True)

    # email notif settings
    email_comments = models.BooleanField(default=True)
    email_replies = models.BooleanField(default=True)
    email_reposts = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)

    # appearance settings
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
        if self.image and self.image.name != 'default.jpg':
            try:
                logger.info(f"Processing image upload for user: {self.user.username}")
                logger.info(f"Storage backend: {default_storage.__class__.__name__}")

                image_file = self.image.open()
                img = Image.open(image_file)

                logger.info(f"Original image size: {img.size}")

                if img.height>300 or img.width>300:
                    output_size = (300, 300)
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

                img.save(img_io, format=img_format, quality=85, optimize=True)
                img_io.seek(0)

                new_image = ContentFile(img_io.getvalue())

                orig_img = self.image.name

                if hasattr(default_storage, 'bucket_name'): # b2/s3
                    if default_storage.exists(orig_img):
                        logger.info(f"Deleting old file: {orig_img}")
                        default_storage.delete(orig_img)

                self.image.save(orig_img, new_image, save=False)

                image_file.close()
                img_io.close()

                logger.info(f"Image processed and saved successfully for user: {self.user.username}")

            except Exception as e:
                logger.error(f"Error processing image for user {self.user.username}: {e}")

        super().save(*args, **kwargs)