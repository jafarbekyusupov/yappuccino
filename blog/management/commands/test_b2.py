import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

class Command(BaseCommand):
    help = 'testing B2 storage connect n config'
    def handle(self, *args, **options):
        self.stdout.write("testingggg STORAGE...")

        self.stdout.write("\n=== ENV VARIABLES ===")
        envv = ['B2_ACCESS_KEY_ID', 'B2_SECRET_ACCESS_KEY', 'B2_BUCKET_NAME', 'B2_REGION']
        for var in envv:
            val = os.environ.get(var)
            if val:
                dspv = val[:8] + '...' if var in ['B2_ACCESS_KEY_ID', 'B2_SECRET_ACCESS_KEY'] else val
                self.stdout.write(f"OK {var}: {dspv}")
            else: self.stdout.write(self.style.ERROR(f"x {var}: Not set"))

        self.stdout.write("\n=== DJ STGS ===")
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"Storage backend: {default_storage.__class__.__name__}")

        if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
            self.stdout.write(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
        if hasattr(settings, 'AWS_S3_ENDPOINT_URL'):
            self.stdout.write(f"AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
        if hasattr(settings, 'MEDIA_URL'):
            self.stdout.write(f"MEDIA_URL: {settings.MEDIA_URL}")

        # FILE UPL TEST
        self.stdout.write("\n=== TEST FILE UPLOAD ===")
        try:
            test_content = "test file for B2 storage"
            test_file = ContentFile(test_content.encode('utf-8'))
            test_filename = "test_upload.txt"

            # SAVE FILE
            saved_path = default_storage.save(test_filename, test_file)
            self.stdout.write(f"OK File saved to: {saved_path}")

            # GET URL
            file_url = default_storage.url(saved_path)
            self.stdout.write(f"OK File URL: {file_url}")

            if default_storage.exists(saved_path):
                self.stdout.write("OK File exists in storage")

                # READING IT BACKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK
                with default_storage.open(saved_path, 'r') as f:
                    cntt = f.read()
                    if cntt.strip() == test_content:
                        self.stdout.write("OK File content verified")
                    else:
                        self.stdout.write(self.style.ERROR("x File content mismatch"))

                # CLEAN PU
                default_storage.delete(saved_path)
                self.stdout.write("OK Test file cleaned up")

            else: self.stdout.write(self.style.ERROR("x File not found in storage"))

        except Exception as e: self.stdout.write(self.style.ERROR(f"x Upload test failed: {str(e)}"))

        self.stdout.write("\nB2 Storage test completed!")