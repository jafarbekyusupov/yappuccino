from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.settings, name='settings'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('export-data/', views.export_user_data, name='export-data'),
    path('delete-account/', views.delete_account_confirm, name='delete-account-confirm'),
    path('test-storage/', views.test_storage, name='test-storage'),
    path('debug-storage/', views.debug_storage, name='debug-storage'),
    path('simple-settings/', views.simple_settings_check, name='simple-settings'),
    path('test-storage-reload/', views.test_storage_reload, name='test-storage-reload'),
]
