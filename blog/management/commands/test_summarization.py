import os
from django.core.management.base import BaseCommand
from blog.models import Post
import requests
import json

class Command(BaseCommand):
    help = 'Test the summarization workflow end-to-end'
    
    def add_arguments(self, parser):
        parser.add_argument('--post-id', type=int, help='Specific post ID to test')
        parser.add_argument('--create-test-post', action='store_true', help='Create a test post')
    
    def handle(self, *args, **options):
        self.stdout.write("🤖 Testing AI Summarization Workflow")
        
        if options['create_test_post']:
            self.create_test_post()
            return
        
        # Test API endpoints
        self.test_api_endpoints()
        
        # Test Ollama connection
        self.test_ollama()
        
        # Test full workflow
        if options['post_id']:
            self.test_specific_post(options['post_id'])
        else:
            self.test_workflow()
    
    def create_test_post(self):
        """Create a test post for summarization"""
        from django.contrib.auth.models import User
        
        # Get first admin user or create one
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR("No admin user found. Create one first."))
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
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Created test post: {post.title} (ID: {post.id})")
        )
        self.stdout.write(f"📝 Post URL: http://localhost:8000/post/{post.id}/")
    
    def test_api_endpoints(self):
        """Test Django API endpoints"""
        self.stdout.write("\n📡 Testing API Endpoints...")
        
        try:
            # Test posts-to-summarize endpoint
            response = requests.get('http://localhost:8000/api/posts-to-summarize/')
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(f"✅ Posts API: {data['count']} posts need summarization")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Posts API failed: {response.status_code}"))
            
            # Test stats endpoint
            response = requests.get('http://localhost:8000/api/summary-stats/')
            if response.status_code == 200:
                data = response.json()
                stats = data['stats']
                self.stdout.write(f"✅ Stats API: {stats['completion_rate']}% completion rate")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Stats API failed: {response.status_code}"))
                
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.ERROR("❌ Cannot connect to Django server. Is it running on localhost:8000?"))
    
    def test_ollama(self):
        """Test Ollama connection"""
        self.stdout.write("\n🦙 Testing Ollama Connection...")
        
        try:
            test_prompt = "Summarize this in one sentence: Django is a Python web framework."
            
            response = requests.post('http://localhost:11434/api/generate', json={
                'model': 'llama3.2',
                'prompt': test_prompt,
                'stream': False
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                summary = data['response'].strip()
                self.stdout.write(f"✅ Ollama working! Test summary: {summary}")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Ollama API failed: {response.status_code}"))
                
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.ERROR("❌ Cannot connect to Ollama. Is it running on localhost:11434?"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ollama error: {e}"))
    
    def test_specific_post(self, post_id):
        """Test summarization for a specific post"""
        self.stdout.write(f"\n📝 Testing specific post {post_id}...")
        
        try:
            post = Post.objects.get(id=post_id)
            
            # Mark for summarization
            post.needs_summary_update = True
            post.save()
            
            self.stdout.write(f"✅ Marked post '{post.title}' for summarization")
            self.stdout.write("🔄 Run your n8n workflow to process this post")
            
        except Post.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Post with ID {post_id} not found"))
    
    def test_workflow(self):
        """Test the complete workflow"""
        self.stdout.write("\n🔄 Testing Complete Workflow...")
        
        # Find a post that needs summarization
        post = Post.objects.filter(
            needs_summary_update=True,
            is_repost=False
        ).first()
        
        if not post:
            self.stdout.write("ℹ️  No posts need summarization. Creating test post...")
            self.create_test_post()
            post = Post.objects.filter(needs_summary_update=True).first()
        
        if post:
            self.stdout.write(f"📝 Found post to test: {post.title}")
            self.stdout.write("🔄 Trigger your n8n workflow to process this post")
            self.stdout.write(f"📊 Monitor progress at: http://localhost:8000/admin/summary-dashboard/")
        else:
            self.stdout.write(self.style.WARNING("⚠️  No posts available for testing"))
