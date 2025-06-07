import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

class Command(BaseCommand):
    help = 'create superuser from env vars during prod state | CUZ SHELL IN RENDER IS NOT FREEEEEEEE'
    def add_arguments(self, parser):
        # override args opt
        parser.add_argument('--username',type=str,help='username for SUPAUSA',)
        parser.add_argument('--email',type=str,help='email for SUPAUSA',)
        parser.add_argument('--password',type=str,help='password for SUPAUSA',)

    def handle(self, *args, **options):
        # get from args or env vars
        username = options['username'] or os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = options['email'] or os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@admin.com')
        pwd = options['password'] or os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not pwd:
            self.stdout.write(self.style.ERROR('no password provided → go set DJANGO_SUPERUSER_PASSWORD env var OR use --password'))
            return

        try:
            with transaction.atomic():
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.WARNING(f'superuser "{username}" already exists'))
                    return

                # ====== CREATING SUPAUSA
                supausa = User.objects.create_superuser(username=username,email=email,password=pwd)
                self.stdout.write(self.style.SUCCESS(f'superuser "{username}" created sucessfulyl'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'error creating superuser: {str(e)}'))
            raise