import os
import uuid
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def ckeditor_upload(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    if 'upload' not in request.FILES:
        return JsonResponse({'error': 'No image found in request'}, status=400)

    try:
        upldd_file = request.FILES['upload']

        if upldd_file.size > 5*1024*1024:
            return JsonResponse({'error': 'File too large. Maximum size is 5MB.'}, status=400)

        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if upldd_file.content_type not in allowed_types:
            return JsonResponse({'error': 'Invalid file type. Only JPEG, PNG and GIF files are allowed.'}, status=400)

        file_extension = os.path.splitext(upldd_file.name)[1].lower()
        if not file_extension: file_extension = '.jpg' # default

        filename = f"{uuid.uuid4()}{file_extension}"

        upload_path = os.path.join(getattr(settings, 'CKEDITOR_5_UPLOAD_PATH', 'uploads/'), filename)

        logger.info(f"User {request.user.username} uploading file: {filename}")
        logger.info(f"Upload path: {upload_path}")
        logger.info(f"Storage backend: {default_storage.__class__.__name__}")

        file_content = upldd_file.read()
        path = default_storage.save(upload_path, ContentFile(file_content))

        file_url = default_storage.url(path)

        logger.info(f"File uploaded successfully: {file_url}")

        return JsonResponse({
            'url': file_url,
            'uploaded': '1',
            'fileName': filename
        })

    except Exception as e:
        logger.error(f"Error uploading file for user {request.user.username}: {str(e)}")
        return JsonResponse({ 'error': f'Upload failed: {str(e)}'}, status=500)