from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Post
import json
import logging
from django.utils.html import strip_tags
import re

logger = logging.getLogger(__name__)

class SummaryAPIView(View):
    """API endpoints for n8n summarization workflow"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

@method_decorator(csrf_exempt, name='dispatch')
class PostsToSummarizeView(SummaryAPIView):
    """Get posts that need summarization"""
    
    def get(self, request):
        try:
            # Get posts that need summarization
            posts = Post.objects.filter(
                needs_summary_update=True,
                is_repost=False  # Don't summarize reposts
            ).order_by('-date_posted')
            
            # Pagination
            limit = int(request.GET.get('limit', 5))
            posts = posts[:limit]
            
            posts_data = []
            for post in posts:
                # Clean content for summarization
                clean_content = strip_tags(post.content)
                clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                
                posts_data.append({
                    'id': post.id,
                    'title': post.title,
                    'content': clean_content,
                    'word_count': post.word_count,
                    'author': post.author.username,
                    'date_posted': post.date_posted.isoformat(),
                    'url': f'/post/{post.id}/',
                    'needs_summary': post.needs_summary_update,
                    'current_summary': post.summary or ''
                })
            
            return JsonResponse({
                'success': True,
                'count': len(posts_data),
                'posts': posts_data
            })
            
        except Exception as e:
            logger.error(f"Error fetching posts to summarize: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class SaveSummaryView(SummaryAPIView):
    """Save AI-generated summary"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            post_id = data.get('post_id')
            summary = data.get('summary', '').strip()
            model_version = data.get('model_version', 'llama3.2')
            
            if not post_id or not summary:
                return JsonResponse({
                    'success': False,
                    'error': 'post_id and summary are required'
                }, status=400)
            
            # Get and update post
            post = Post.objects.get(id=post_id)
            post.summary = summary
            post.summary_generated_at = timezone.now()
            post.needs_summary_update = False
            post.summary_model_version = model_version
            post.save()
            
            logger.info(f"Summary saved for post {post_id}: {summary[:100]}...")
            
            return JsonResponse({
                'success': True,
                'message': f'Summary saved for post "{post.title}"',
                'post_id': post_id,
                'summary_length': len(summary)
            })
            
        except Post.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Post not found'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class SummaryStatsView(SummaryAPIView):
    """Get summarization statistics"""
    
    def get(self, request):
        try:
            total_posts = Post.objects.filter(is_repost=False).count()
            summarized_posts = Post.objects.filter(
                is_repost=False,
                summary__isnull=False
            ).exclude(summary='').count()
            pending_posts = Post.objects.filter(
                needs_summary_update=True,
                is_repost=False
            ).count()
            
            return JsonResponse({
                'success': True,
                'stats': {
                    'total_posts': total_posts,
                    'summarized_posts': summarized_posts,
                    'pending_summary': pending_posts,
                    'completion_rate': round((summarized_posts / total_posts * 100), 2) if total_posts > 0 else 0
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting summary stats: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

