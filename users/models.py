from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import io


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
            if self.image and hasattr(self.image, 'url'):
                return self.image.url
        except (ValueError, OSError):
            pass
        return '/static/images/default-profile.png'

    def save(self, *args, **kwargs):
        if self.image and self.image.name != 'default.jpg':
            try:
                image_file = self.image.open()
                img = Image.open(image_file)

                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
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

                    if default_storage.exists(orig_img):    default_storage.delete(orig_img)

                    self.image.save(orig_img, new_image, save=False)

                image_file.close()

            except Exception as e:
                print(f"Error processing image: {e}")

        super().save(*args, **kwargs)