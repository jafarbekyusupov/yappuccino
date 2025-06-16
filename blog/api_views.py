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
    """ -- API ENDPOINTS for N8N SUMMRY GENERATION -- """
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

@method_decorator(csrf_exempt, name='dispatch')
class PostsToSummarizeView(SummaryAPIView): # get posts that need summry
    def get(self, request):
        try:
            psts = Post.objects.filter(needs_summary_update=True, is_repost=False).order_by('-date_posted') # no summry for reposts
            
            # pagination
            lim = int(request.GET.get('limit', 5))
            psts = psts[:lim]            
            psData = []
            for pp in psts:
                clnCont = strip_tags(pp.content)
                clnCont = re.sub(r'\s+', ' ', clnCont).strip()
                psData.append({
                    'id': pp.id,
                    'title': pp.title,
                    'content': clnCont,
                    'word_count': pp.word_count,
                    'author': pp.author.username,
                    'date_posted': pp.date_posted.isoformat(),
                    'url': f'/post/{pp.id}/',
                    'needs_summary': pp.needs_summary_update,
                    'current_summary': pp.summary or ''
                })
            
            return JsonResponse({'success': True,'count': len(psData),'posts': psData})
            
        except Exception as e:
            logger.error(f"err fetching posts to summariez: {e}")
            return JsonResponse({'success': False,'error': str(e)},status=500)

@method_decorator(csrf_exempt, name='dispatch')
class SaveSummaryView(SummaryAPIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            pid = data.get('post_id')
            smry = data.get('summary', '').strip()
            mdlv = data.get('model_version', 'llama3.2')
            if not pid or not smry: return JsonResponse({'success': False,'error': 'post_id and summary are required'},status=400)
            
            # upd post
            post = Post.objects.get(id=pid)
            post.summary = smry
            post.summary_generated_at = timezone.now()
            post.needs_summary_update = False
            post.summary_model_version = mdlv
            post.save()
            
            logger.info(f"Summary saved for post {pid}: {smry[:100]}...")
            return JsonResponse({'success': True,'message': f'summary saved for post "{post.title}"','post_id': pid,'summary_length': len(smry)})
            
        except Post.DoesNotExist:
            return JsonResponse({'success': False,'error': 'post not found'},status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False,'error': 'Invalid JSON data'},status=400)
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
            return JsonResponse({'success': False,'error': str(e)},status=500)

@method_decorator(csrf_exempt, name='dispatch')
class SummaryStatsView(SummaryAPIView):
    def get(self, request):
        try:
            total_posts = Post.objects.filter(is_repost=False).count()
            summarized_posts = Post.objects.filter(is_repost=False,summary__isnull=False).exclude(summary='').count()
            pending_posts = Post.objects.filter(needs_summary_update=True,is_repost=False).count()
            return JsonResponse({
                'success': True,
                'stats': {
                    'total_posts': total_posts,
                    'summarized_posts': summarized_posts,
                    'pending_summary': pending_posts,
                    'completion_rate': round((summarized_posts / total_posts*100), 2) if total_posts>0 else 0
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting summary stats: {e}")
            return JsonResponse({'success': False,'error': str(e)},status=500)

