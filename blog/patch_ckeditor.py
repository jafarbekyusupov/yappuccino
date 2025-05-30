from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging

# TODO -- PROBLEM W IMG UPLOAD PERMISSIONS - for some reason only admin can do that
#  => DONE -- SOL - OVERRIDE ORIGINAL FUNC

logger = logging.getLogger(__name__)


def patch_ckeditor_upload():
	try:
		import django_ckeditor_5.views as ckeditor_views
		orig_upload = ckeditor_views.upload_file # might need later

		@csrf_exempt
		@login_required
		def new_upload_file(request):
			if request.method != 'POST':
				return JsonResponse({'error': 'Only POST method allowed'}, status=405)

			if not request.FILES.get('upload'):
				return JsonResponse({'error': 'No file provided'}, status=400)

			try:
				upldF = request.FILES['upload']

				if upldF.size > 5*1024*1024:
					return JsonResponse({'error': 'File too large. Maximum size is 5MB.'}, status=400)

				allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
				if upldF.content_type not in allowed_types:
					return JsonResponse({'error': 'Invalid file type. Only JPEG, PNG and GIF files are allowed.'}, status=400)

				file_extension = os.path.splitext(upldF.name)[1].lower()
				filename = f"{uuid.uuid4()}{file_extension}"

				upload_path = os.path.join(getattr(settings, 'CKEDITOR_5_UPLOAD_PATH', 'uploads/'), filename)

				logger.info(f"Attempting to upload file: {filename} to path: {upload_path}")
				logger.info(f"Using storage backend: {default_storage.__class__.__name__}")

				file_content = upldF.read()
				path = default_storage.save(upload_path, ContentFile(file_content))

				file_url = default_storage.url(path)

				logger.info(f"File uploaded successfully: {file_url}")

				return JsonResponse({
					'url': file_url,
					'uploaded': '1',
					'fileName': filename
				})

			except Exception as e:
				logger.error(f"Error uploading file: {str(e)}")
				return JsonResponse({ 'error': f'Upload failed: {str(e)}'}, status=500)

		ckeditor_views.upload_file = new_upload_file
		logger.info("cke upl func patch done")
		return True

	except Exception as e:
		logger.error(f"Error patching CKEditor: {e}")
		return False