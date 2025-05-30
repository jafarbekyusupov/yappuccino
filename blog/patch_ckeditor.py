from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# TODO -- PROBLEM W IMG UPLOAD PERMISSIONS - for some reason only admin can do that
#  => DONE -- SOL - OVERRIDE ORIGINAL FUNC

def patch_ckeditor_upload():
	try:
		import django_ckeditor_5.views as ckeditor_views
		orig_upload = ckeditor_views.upload_file # might need later

		@csrf_exempt
		def new_upload_file(request):
			if request.method != 'POST' or not request.FILES.get('upload'):
				return JsonResponse({'error': 'No file provided'}, status=400)

			upldF = request.FILES['upload']
			file_extension = os.path.splitext(upldF.name)[1]

			filename = f"{uuid.uuid4()}{file_extension}"
			upload_path = os.path.join(settings.CKEDITOR_5_UPLOAD_PATH, filename)

			path = default_storage.save(upload_path, ContentFile(upldF.read()))
			file_url = default_storage.url(path)

			return JsonResponse({
				'url': file_url,
				'uploaded': '1',
				'fileName': filename
			})

		ckeditor_views.upload_file = new_upload_file
		return True

	except Exception as e:
		print(f"Error patching CKEditor: {e}")
		return False