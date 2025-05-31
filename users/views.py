import logging
import traceback

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt

from .forms import (
    UserRegisterForm,
    UserUpdateForm,
    ProfileUpdateForm,
    PrivacySettingsForm,
    NotificationSettingsForm,
    AppearanceSettingsForm,
    AccountDeletionForm
)

# messages.debug
# messages.info
# messages.success
# messages.warning
# messages.error

def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f"Your account has been created! You can now log in.")
			return redirect('login')
	else:
		form = UserRegisterForm()

	return render(request, 'users/register.html', {'form': form})


logger = logging.getLogger(__name__)


@login_required
def profile(request):
	if request.method == 'POST':
		try:
			logger.info(f"Profile update started for user: {request.user.username}")
			logger.info(f"POST data keys: {list(request.POST.keys())}")
			logger.info(f"FILES data keys: {list(request.FILES.keys())}")

			u_form = UserUpdateForm(request.POST, instance=request.user)
			p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

			logger.info(f"Forms created successfully")

			u_form_valid = u_form.is_valid()
			p_form_valid = p_form.is_valid()

			logger.info(f"User form valid: {u_form_valid}")
			logger.info(f"Profile form valid: {p_form_valid}")

			if not u_form_valid:
				logger.error(f"User form errors: {u_form.errors}")
			if not p_form_valid:
				logger.error(f"Profile form errors: {p_form.errors}")

			if u_form_valid and p_form_valid:
				logger.info("Both forms valid, attempting to save...")

				try:
					u_form.save()
					logger.info("User form saved successfully")
				except Exception as e:
					logger.error(f"Error saving user form: {e}")
					logger.error(f"User form save traceback: {traceback.format_exc()}")
					raise

				try:
					if 'image' in request.FILES:
						uploaded_file = request.FILES['image']
						logger.info(f"Processing uploaded image: {uploaded_file.name}")
						logger.info(f"Image size: {uploaded_file.size} bytes")
						logger.info(f"Image content type: {uploaded_file.content_type}")

					p_form.save()
					logger.info("Profile form saved successfully")

				except Exception as e:
					logger.error(f"Error saving profile form: {e}")
					logger.error(f"Profile form save traceback: {traceback.format_exc()}")

					if 'image' in request.FILES:
						logger.error("This error occurred during image upload")

					messages.error(request, f'Error uploading profile picture: {str(e)}')
					return redirect('profile')

				messages.success(request, "Your account has been updated!")
				return redirect('profile')
			else:
				error_msg = "Please correct the errors below:"
				if u_form.errors:
					error_msg += f" User: {u_form.errors}"
				if p_form.errors:
					error_msg += f" Profile: {p_form.errors}"
				messages.error(request, error_msg)

		except Exception as e:
			logger.error(f"Unexpected error in profile view: {e}")
			logger.error(f"Full traceback: {traceback.format_exc()}")

			# if its stg related err
			if 'B2' in str(e) or 'S3' in str(e) or 'storage' in str(e).lower():
				messages.error(request, 'File storage error. Please check your B2 configuration.')
			elif 'PIL' in str(e) or 'Image' in str(e):
				messages.error(request, 'Image processing error. Please try a different image format.')
			else:
				messages.error(request, f'An error occurred: {str(e)}')

			return redirect('profile')

	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)

	context = { 'u_form': u_form, 'p_form': p_form,}
	return render(request, 'users/profile.html', context)


@login_required
def settings(request):
	profile = request.user.profile

	if request.method == 'POST':
		# privacy settings
		if 'privacy_submit' in request.POST:
			privacy_form = PrivacySettingsForm(request.POST, instance=profile)
			if privacy_form.is_valid():
				privacy_form.save()
				messages.success(request, 'Privacy settings updated successfully!')
				return redirect('settings')

		# notif settings
		elif 'notification_submit' in request.POST:
			notification_form = NotificationSettingsForm(request.POST, instance=profile)
			if notification_form.is_valid():
				notification_form.save()
				messages.success(request, 'Notification settings updated successfully!')
				return redirect('settings')

		# TODO -- appearance settings
		elif 'appearance_submit' in request.POST:
			appearance_form = AppearanceSettingsForm(request.POST, instance=profile)
			if appearance_form.is_valid():
				appearance_form.save()
				messages.success(request, 'Appearance settings updated successfully!')
				return redirect('settings')

		# acc deletion
		elif 'delete_account' in request.POST:
			deletion_form = AccountDeletionForm(request.user, request.POST)
			if deletion_form.is_valid():
				user = request.user
				logout(request)  # logout first
				user.delete()
				messages.success(request, 'Your account has been permanently deleted.')
				return redirect('blog-home')
			else:
				messages.error(request, 'Username confirmation failed. Please try again.')

	# init forms with cur values
	privacy_form = PrivacySettingsForm(instance=profile)
	notification_form = NotificationSettingsForm(instance=profile)
	appearance_form = AppearanceSettingsForm(instance=profile)
	deletion_form = AccountDeletionForm(request.user)

	context = {
		'privacy_form': privacy_form,
		'notification_form': notification_form,
		'appearance_form': appearance_form,
		'deletion_form': deletion_form,
	}

	return render(request, 'users/settings.html', context)


class CustomPasswordChangeView(PasswordChangeView):
	template_name = 'users/password_change.html'
	success_url = reverse_lazy('settings')

	def form_valid(self, form):
		messages.success(self.request, 'Your password has been changed successfully!')
		return super().form_valid(form)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title'] = 'Change Password'
		return context


@login_required
def delete_account_confirm(request):
	if request.method == 'POST':
		form = AccountDeletionForm(request.user, request.POST)
		if form.is_valid():
			user = request.user
			logout(request)
			user.delete()
			messages.success(request, 'Your account has been permanently deleted.')
			return redirect('blog-home')
	else:
		form = AccountDeletionForm(request.user)

	return render(request, 'users/delete_account_confirm.html', {
		'form': form,
		'username': request.user.username
	})


@login_required
def export_user_data(request):
	# TODO -- data export here
	#  → json or csv with users posts, comments, etc

	messages.info(request, 'Data export feature is coming soon!')
	return redirect('settings')


def profile_completion_check(user):
	""" check if user has completed their profile -- for FUTURE mechanics"""
	profile = user.profile

	completion = {
		'has_profile_image': profile.image and profile.image.name != 'default.jpg',
		'has_email': bool(user.email),
		'total_posts': user.post_set.count(),
		'total_comments': user.comment_set.count(),
	}

	# score for completion %
	completed_items = sum([
		completion['has_profile_image'],
		completion['has_email'],
		completion['total_posts'] > 0,
		completion['total_comments'] > 0,
	])

	completion['percentage'] = (completed_items / 4) * 100

	return completion


@csrf_exempt
def test_storage(request):
	try:
		test_content = "test file content"
		test_file = ContentFile(test_content.encode('utf-8'))

		file_path = default_storage.save('test_uploads/test.txt', test_file)
		logger.info(f"Test file saved to: {file_path}")

		file_url = default_storage.url(file_path)
		logger.info(f"Test file URL: {file_url}")

		if default_storage.exists(file_path):
			with default_storage.open(file_path, 'r') as f:
				content = f.read()
				logger.info(f"Test file content: {content}")

		default_storage.delete(file_path)

		return JsonResponse({
			'success': True,
			'message': 'Storage test passed',
			'file_path': file_path,
			'file_url': file_url,
			'storage_class': default_storage.__class__.__name__
		})

	except Exception as e:
		logger.error(f"Storage test failed: {e}")
		return JsonResponse({
			'success': False,
			'error': str(e),
			'storage_class': default_storage.__class__.__name__
		})