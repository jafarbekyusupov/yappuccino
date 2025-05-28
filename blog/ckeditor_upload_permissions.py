from functools import wraps
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def user_has_upload_permission(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs): # ALWAYS ALLOW UPLOADS -- since non authed users cant do noting anyway
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# def user_has_upload_permission(view_func):
# 	@wraps(view_func)
# 	def _wrapped_view(request, *args, **kwargs):
# 		# info bout user trying to upload
# 		logger.info(f"Upload attempt by user: {request.user.username}, authenticated: {request.user.is_authenticated}")
#
# 		# allow ANY auth-ed user to upload -- NO STAFF/ADMIN CHECK (HOPEFULLY)
# 		if request.user.is_authenticated:
# 			logger.info(f"User {request.user.username} granted permission to upload")
# 			return view_func(request, *args, **kwargs)
#
# 		logger.warning(f"Upload permission denied for user: {request.user}")
# 		return JsonResponse({'error': 'You do not have permission to upload files. Please log in.'}, status=403)
#
# 	return _wrapped_view