import os
import time
import random
import requests
import threading
from datetime import datetime
from django.conf import settings

class DjangoKeepAlive:
    def __init__(self):
        self.app_url = getattr(settings, 'DJANGO_BASE_URL', 'https://yappuccino.onrender.com')
        self.endpoint = '/health/'
        self.enabled = self._should_beOn()
        self.running = False
        self.thread = None
        
    def _should_beOn(self): return(not settings.DEBUG and ('onrender.com' in self.app_url or os.environ.get('RENDER'))) # prod mode onyl
    
    def start(self):
        if not self.enabled:
            print("kepe alive disabled | not in prod mode")
            return
            
        if self.running:
            print("| OK | keep alive alr RUNNING")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
        self.thread.start()
        print(f"django blog keep-alive started for {self.app_url}")
    
    def stop(self):
        self.running = False
        if self.thread:
            print("django keep-alive service stopped")
        
    def _keep_alive_loop(self):
        """main keep-alive loop"""
        while self.running:
            try:
                response = requests.get(
                    f"{self.app_url}{self.endpoint}",
                    timeout=10,
                    headers={
                        'User-Agent': 'django-blog-keepalive/1.0',
                        'X-Keep-Alive': 'true'
                    }
                )
                
                if response.status_code == 200:
                    print("✅ django blog self ping successful")
                else:
                    print(f"⚠️ django ping returned {response.status_code}")
                    
            except Exception as e:
                print(f"❌ django blog self ping failed: {e}")
            
            # wait random time (1-9 minutes)
            if self.running:
                wait_time = random.randint(60, 540)
                mins, secs = divmod(wait_time, 60)
                print(f"django waiting {mins} mins {secs} secs til next ping")
                
                # sleep in chunks for graceful shutdown
                for _ in range(wait_time):
                    if not self.running:
                        break
                    time.sleep(1)

# global keepalive instance
django_keepalive = DjangoKeepAlive()


# =====================================
# update blog/apps.py:
# =====================================

"""
replace or update your blog/apps.py with this:

from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    
    def ready(self):
        # import here to avoid circular imports
        from .keepalive import django_keepalive
        
        # start keep-alive when django is ready
        if django_keepalive.enabled:
            def delayed_start():
                import time
                time.sleep(30)  # wait for server to be fully ready
                django_keepalive.start()
            
            import threading
            thread = threading.Thread(target=delayed_start, daemon=True)
            thread.start()
"""


# =====================================
# add health endpoint - blog/views.py:
# =====================================

"""
add this view to your blog/views.py:

from django.http import JsonResponse
from django.contrib.auth.models import User
from datetime import datetime

def health_check(request):
    '''lightweight health check endpoint for keep-alive'''
    try:
        # simple database check
        user_count = User.objects.count()
        
        # you could also check blog-specific models
        from .models import Post
        post_count = Post.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'service': 'django-blog',
            'database': 'connected',
            'users': user_count,
            'posts': post_count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'service': 'django-blog', 
            'error': str(e)
        }, status=500)
"""


# =====================================
# update blogpost/urls.py:
# =====================================

"""
add this to your urlpatterns in blogpost/urls.py:

from blog import views as blog_views

urlpatterns = [
    # ... your existing urls ...
    
    # add health endpoint for keep-alive
    path('health/', blog_views.health_check, name='health'),
    
    # ... rest of your urls ...
]
"""


# =====================================
# alternative: management command
# =====================================

"""
if you prefer a management command approach, create:
blog/management/commands/keepalive.py

from django.core.management.base import BaseCommand
from blog.keepalive import django_keepalive

class Command(BaseCommand):
    help = 'run keep-alive service for render deployment'
    
    def handle(self, *args, **options):
        if not django_keepalive.enabled:
            self.stdout.write("keep-alive disabled (not in production)")
            return
            
        try:
            self.stdout.write("starting django keep-alive service...")
            django_keepalive.start()
            
            # keep the command running
            import time
            while True:
                time.sleep(60)
                
        except KeyboardInterrupt:
            self.stdout.write("stopping keep-alive service...")
            django_keepalive.stop()

then you can run: python manage.py keepalive
but the apps.py method is better for automatic startup.
"""