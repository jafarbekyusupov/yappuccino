from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
import uuid

# TODO -- PROBLEM W IMG UPLOAD PERMISSIONS - for some reason only admin can do that
#  => DONE -- SOL - OVERRIDE ORIGINAL FUNC

def patch_ckeditor_upload():
	try:
		import django_ckeditor_5.views as ckeditor_views

		orig_upload = ckeditor_views.upload_file # might need later

		@csrf_exempt
		def new_upload_file(request): # upload func with no permission checks
			if request.method != 'POST' or not request.FILES.get('upload'):
				return JsonResponse({'error': 'No file provided'}, status=400)

			upldd_file = request.FILES['upload']
			file_extension = os.path.splitext(upldd_file.name)[1]

			filename = f"{uuid.uuid4()}{file_extension}"
			upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

			os.makedirs(os.path.dirname(upload_path), exist_ok=True) # checking that dir is there

			with open(upload_path, 'wb+') as destination:
				for chunk in upldd_file.chunks():
					destination.write(chunk)

			# url to ckeditor
			file_url = f"{settings.MEDIA_URL}uploads/{filename}"
			return JsonResponse({
				'url': file_url,
				'uploaded': '1',
				'fileName': filename
			})

		ckeditor_views.upload_file = new_upload_file
		return True

	except:
		return False