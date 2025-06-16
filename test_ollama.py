# test_ollama.py - Complete Ollama test for your blog project
import requests
import json
import time

def test_ollama_connection():
    """Test Ollama API connection and model availability"""
    print("🦙 Testing Ollama Connection...")
    print("=" * 50)
    
    # Test 1: Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            print("✅ Ollama is running on localhost:11434")
            
            models = response.json().get('models', [])
            print(f"📦 Available models: {len(models)}")
            
            # List all models
            for model in models:
                print(f"   - {model.get('name', 'Unknown')}")
            
            # Check if llama3.2 is available
            llama_models = [m for m in models if 'llama3.2' in m.get('name', '')]
            if llama_models:
                print("✅ llama3.2 model is available")
                model_name = llama_models[0]['name']
                print(f"   Using model: {model_name}")
                return model_name
            else:
                print("❌ llama3.2 model not found")
                print("   Run: ollama pull llama3.2")
                return None
                
        else:
            print(f"❌ Ollama not responding (status: {response.status_code})")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running?")
        print("   Try: ollama serve (if not running)")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_summarization(model_name):
    """Test text summarization with real blog content"""
    print("\n🧠 Testing text summarization...")
    print("=" * 50)
    
    # Test with Russian game dev article (like your blog content)
    test_text = """
    Ребята, привет! Если заглянуть на сайты или каналы по поиску работы в геймдеве, 
    то как минимум в половине вакансий на позицию гейм-дизайнера требования включают 
    в себя знания и умения проанализировать игровые показатели, строить и проверять 
    гипотезы на основе этих данных. Что может быть полезнее для гейм-дизайнера XXI века, 
    чем основные аналитические метрики? 
    
    Существует три группы метрик: метрики привлечения, метрики активности и метрики выручки.
    
    CPI (стоимость привлечения клиента) - это затраты на рекламу, делённые на число новых 
    пользователей. Conversion Rate измеряет долю пользователей, совершивших целевое действие. 
    Retention показывает процент пользователей, которые возвращаются к игре через определённые 
    промежутки времени.
    """
    
    prompt = f"Summarize this Russian text about game development metrics in 2-3 sentences in English: {test_text.strip()}"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "max_tokens": 150
        }
    }
    
    try:
        print("⏳ Generating summary (this may take 10-30 seconds)...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json=payload,
            timeout=60
        )
        
        end_time = time.time()
        processing_time = round((end_time - start_time) * 1000)  # Convert to milliseconds
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get('response', '').strip()
            
            print("✅ Summary generated successfully!")
            print(f"⏱️  Processing time: {processing_time}ms")
            print(f"📝 Summary: {summary}")
            
            # Test quality
            if len(summary) > 20:
                print("✅ Summary quality: Good")
                return True
            else:
                print("⚠️  Summary seems short")
                return True
                
        else:
            print(f"❌ API call failed (status: {response.status_code})")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Ollama might be slow or overloaded.")
        return False
    except Exception as e:
        print(f"❌ Error during summarization: {e}")
        return False

def test_django_blog_content():
    """Test with typical Django blog content"""
    print("\n📝 Testing with Django blog content...")
    print("=" * 50)
    
    blog_content = """
    <h2>Understanding Django Models and Database Integration</h2>
    <p>Django's Object-Relational Mapping (ORM) is one of its most powerful features, 
    allowing developers to interact with databases using Python code instead of raw SQL queries. 
    The Django ORM provides a high-level abstraction layer that makes database operations 
    intuitive and secure.</p>
    
    <p>Models in Django are Python classes that represent database tables. Each model class 
    corresponds to a single database table, and each attribute of the model represents a 
    database field. Django automatically generates SQL to create the database schema based 
    on your model definitions.</p>
    
    <p>Key benefits include automatic SQL generation, database-agnostic code, built-in 
    validation, and powerful query capabilities. Django supports multiple database backends 
    including PostgreSQL, MySQL, SQLite, and Oracle.</p>
    """
    
    # Clean HTML tags for summarization
    import re
    clean_content = re.sub(r'<[^>]+>', '', blog_content)
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
    
    prompt = f"Summarize this Django tutorial in exactly 2 sentences: {clean_content}"
    
    payload = {
        "model": "llama3.2",  # Direct model name
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "max_tokens": 100
        }
    }
    
    try:
        print("⏳ Processing Django content...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json=payload,
            timeout=60
        )
        
        processing_time = round((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get('response', '').strip()
            
            print("✅ Django content summary generated!")
            print(f"⏱️  Processing time: {processing_time}ms")
            print(f"📝 Summary: {summary}")
            print(f"📊 Original length: {len(clean_content)} chars")
            print(f"📊 Summary length: {len(summary)} chars")
            print(f"📊 Compression ratio: {round(len(summary)/len(clean_content)*100, 1)}%")
            
            return True
        else:
            print(f"❌ Failed to process Django content")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Ollama Tests for Yappuccino Blog")
    print("=" * 60)
    
    # Test 1: Connection and model availability
    model_name = test_ollama_connection()
    if not model_name:
        print("\n❌ Cannot proceed without working Ollama setup")
        return
    
    # Test 2: Summarization with multilingual content
    success1 = test_summarization(model_name)
    
    # Test 3: Django blog content processing
    success2 = test_django_blog_content()
    
    # Results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    if success1 and success2:
        print("✅ All tests passed! Ollama is ready for your blog project.")
        print("🔄 Next step: Set up n8n workflow")
        print("📊 Expected performance:")
        print("   - Processing time: 5-30 seconds per article")
        print("   - Model: llama3.2 (good for summarization)")
        print("   - Multilingual support: ✅")
    else:
        print("⚠️  Some tests failed. Check Ollama setup.")
        print("💡 Try: ollama pull llama3.2")

if __name__ == "__main__":
    main()