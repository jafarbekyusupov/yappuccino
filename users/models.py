from django.db import models
from django.contrib.auth.models import User
from PIL import Image

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
        """ return image url ( default, if image doesnt exist)"""
        try:
            if self.image and hasattr(self.image, 'url'):
                return self.image.url
        except (ValueError, OSError):
            pass
        return '/static/images/default-profile.png'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # process image ONLY IF it exists
        if self.image and hasattr(self.image, 'path'):
            try:
                img = Image.open(self.image.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
            except Exception as e:
                print(f"Error processing image: {e}")