import os
from django.core.management.base import BaseCommand
from blog.models import Post
import requests
import json

class Command(BaseCommand):
    help = 'test smry workflow end2end'
    def add_arguments(self, parser):
        parser.add_argument('--post-id', type=int, help='Specific post ID to test')
        parser.add_argument('--create-test-post', action='store_true', help='Create a test post')
    
    def handle(self, *args, **options):
        self.stdout.write(" === testing ai summarization workflow === ")
        
        if options['create_test_post']:
            self.create_test_post()
            return
        
        self.test_api_endpoints()
        self.test_ollama() # test lama connection
        if options['post_id']: self.test_specific_post(options['post_id'])
        else: self.test_workflow()
    
    def create_test_post(self):
        from django.contrib.auth.models import User
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR("no admin user found → gonna create one"))
            return
        
        test_content = """
        <h2>Understanding Artificial Intelligence in Modern Web Development</h2>
        <p>Artificial Intelligence has revolutionized the way we approach web development, bringing unprecedented capabilities to automate tasks, enhance user experiences, and process data intelligently.</p>
        <p>In this comprehensive guide, we explore how AI can be integrated into Django applications using tools like n8n for workflow automation and Ollama for local language model processing. The combination of these technologies allows developers to create sophisticated AI-powered features without relying on expensive cloud services.</p>
        <p>Key benefits include:</p>
        <ul>
            <li>Cost-effective local processing</li>
            <li>Privacy-preserving data handling</li>
            <li>Customizable AI workflows</li>
            <li>Seamless integration with existing systems</li>
        </ul>
        
        <p>By implementing these technologies, developers can create intelligent content summarization, automated tagging, sentiment analysis, and much more. The future of web development is increasingly AI-driven, and these tools make that future accessible to developers of all skill levels.</p>
        """
        
        post = Post.objects.create(
            title="AI in Web Development: A Complete Guide",
            content=test_content,
            author=admin_user,
            needs_summary_update=True
        )
        
        self.stdout.write(self.style.SUCCESS(f"-- OK -- Created test post: {post.title} (ID: {post.id})"))
        self.stdout.write(f"-- URL -- Post URL: http://localhost:8000/post/{post.id}/")
    
    def test_api_endpoints(self): # dj endpts
        self.stdout.write("\n=== TESTING === testing api endpoints...")
        
        try:
            postsToSmryz = requests.get('http://localhost:8000/api/posts-to-summarize/')
            if postsToSmryz.status_code == 200:
                data = postsToSmryz.json()
                self.stdout.write(f"-- OK -- posts API: {data['count']} posts need summarization")
            else: self.stdout.write(self.style.ERROR(f"-- FAIL -- posts api failed: {postsToSmryz.status_code}"))
            
            smryStats = requests.get('http://localhost:8000/api/summary-stats/')
            if smryStats.status_code == 200:
                data = smryStats.json()
                stats = data['stats']
                self.stdout.write(f"-- OK -- stats api: {stats['completion_rate']}% completion rate")
            else:
                self.stdout.write(self.style.ERROR(f"-- FAIL -- Stats API failed: {smryStats.status_code}"))
                
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.ERROR("-- ERRCONNECT -- Cannot connect to Django server"))
    
    def test_ollama(self):
        self.stdout.write("\n-- 🦙 -- testing ollama conection...")
        try:
            tprompt = "Summarize this in one sentence: Django is a Python web framework."
            resp = requests.post('http://localhost:11434/api/generate', json={'model': 'llama3.2','prompt': tprompt,'stream': False},timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                summary = data['response'].strip()
                self.stdout.write(f"-- OK -- YAY LAMA is WOKRINGG | test summary: {summary}")
            else: self.stdout.write(self.style.ERROR(f"-- FAIL -- ollama api failed: {resp.status_code}"))
                
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.ERROR("-- ERRCONNECT -- cant connect to lama | 11434?"))
        except Exception as e: 
            self.stdout.write(self.style.ERROR(f"-- LAMAERR -- ollama error: {e}"))
    
    def test_specific_post(self, post_id):
        self.stdout.write(f"\n===TESTING specific post {post_id}...")
        try:
            post = Post.objects.get(id=post_id)
            post.needs_summary_update = True
            post.save()
            self.stdout.write(f"-- OK -- marked post '{post.title}' for summarization")
            self.stdout.write("-- RUN -- run n8n workflow to process this post")
            
        except Post.DoesNotExist: self.stdout.write(self.style.ERROR(f"-- 404 -- post with id {post_id} not found"))
    
    def test_workflow(self):
        self.stdout.write("\n===TESTING complete workflow...")
        post = Post.objects.filter(needs_summary_update=True,is_repost=False).first() #filer out posts that got smry
        if not post:
            self.stdout.write("-- WELL --  no posts need summarization → creating test post...")
            self.create_test_post()
            post = Post.objects.filter(needs_summary_update=True).first()
        
        if post:
            self.stdout.write(f"-- FOUND -- found post to test: {post.title}")
            self.stdout.write("-- RUN -- trigger n8n workflow to process tha post")
            self.stdout.write(f"-- VIEW -- Monitor progress at: http://localhost:8000/admin/summary-dashboard/")
        else: self.stdout.write(self.style.WARNING("-- WARNING -- no posts available for testing"))
