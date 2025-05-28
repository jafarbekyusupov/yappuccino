from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.settings, name='settings'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('export-data/', views.export_user_data, name='export-data'),
    path('delete-account/', views.delete_account_confirm, name='delete-account-confirm'),
]
