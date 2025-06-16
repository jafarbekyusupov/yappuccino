from django.contrib import admin
from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    UserActivityView,
    TagListView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView,
    TagDetailView,
    vote_post,
    add_comment,
    edit_comment,
    delete_comment,
    vote_comment,
    repost
)
from . import views
from .ckeditor_views import ckeditor_upload
from users.views import CustomPasswordChangeView
from .api_views import PostsToSummarizeView, SaveSummaryView, SummaryStatsView
urlpatterns = [
    # --- CORE --- #
    path('', PostListView.as_view(), name='blog-home'),
    path('about/', views.about, name='blog-about'),
    path('settings/', views.settings, name='settings'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),

    # --- POST MANAGEMENT --- #
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),

    # --- USER SPECIFIC POST PATHS --- #
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('user/<str:username>/activity/', UserActivityView.as_view(), name='user-activity'),

    # --- POST INTERACTIONS --- #
    path('post/<int:pk>/vote/<str:vote_type>/', vote_post, name='vote-post'),
    path('post/<int:pk>/comment/', add_comment, name='add-comment'),
    path('post/<int:pk>/repost/', repost, name='repost'),

    # --- COMMENT MANAGEMENT --- #
    path('comment/<int:pk>/edit/', edit_comment, name='edit-comment'),
    path('comment/<int:pk>/delete/', delete_comment, name='delete-comment'),
    path('comment/<int:pk>/vote/', vote_comment, name='vote-comment'),

    # --- TAG MANAGEMENT --- #
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/new/', TagCreateView.as_view(), name='tag-create'),
    path('tags/<int:pk>/update/', TagUpdateView.as_view(), name='tag-update'),
    path('tags/<int:pk>/delete/', TagDeleteView.as_view(), name='tag-delete'),
    path('tag/<slug:slug>/', TagDetailView.as_view(), name='tag-detail'),
    path('tag-suggestions/', views.tag_suggestions, name='tag-suggestions'),

    # --- POST/COMMENT EDITOR --- #
    path('ckeditor5/custom-upload/', ckeditor_upload, name='ckeditor_custom_upload'),
    
    # --- AI AGENT SUMMARY ENDPOINTS --- #
    path('api/posts-to-summarize/', PostsToSummarizeView.as_view(), name='api-posts-to-summarize'),
    path('api/save-summary/', SaveSummaryView.as_view(), name='api-save-summary'),
    path('api/summary-stats/', SummaryStatsView.as_view(), name='api-summary-stats'),
    path('admin/summary-dashboard/', views.summary_dashboard, name='summary-dashboard'),
]