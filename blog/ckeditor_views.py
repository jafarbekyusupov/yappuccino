from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
import uuid
from .ckeditor_upload_permissions import user_has_upload_permission


@csrf_exempt
@login_required
@user_has_upload_permission  # decorator to enforce permissions
def ckeditor_upload(request):
	if request.method != 'POST' or 'upload' not in request.FILES:
		return JsonResponse({'error': 'No image found in request'}, status=400)

	upldd_file = request.FILES['upload']
	file_extension = os.path.splitext(upldd_file.name)[1]
	filename = f"{uuid.uuid4()}{file_extension}"
	upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

	os.makedirs(os.path.dirname(upload_path), exist_ok=True)

	with open(upload_path, 'wb+') as destination:
		for chunk in upldd_file.chunks():
			destination.write(chunk)

	file_url = f"{settings.MEDIA_URL}uploads/{filename}"
	return JsonResponse({
		'url': file_url,
		'uploaded': '1',
		'fileName': filename
	})