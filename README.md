# [☕ Yappuccino ](https://yappuccino.jafarbekyusupov.com/)
*A platform for Certified Yappers*

<div>  
   <img src="https://img.shields.io/badge/Django-5.2.1-white?logo=django&logoColor=white&labelColor=092E20&style=for-the-badge" alt="Django">  
  <img src="https://img.shields.io/badge/Python-3.8+-white?logo=python&logoColor=white&labelColor=3776AB&style=for-the-badge" alt="Python">  
  <img src="https://img.shields.io/badge/Bootstrap-5-white?logo=bootstrap&logoColor=white&labelColor=7952B3&style=for-the-badge" alt="Bootstrap">  
  <img src="https://img.shields.io/badge/PostgreSQL-white?logo=postgresql&logoColor=white&labelColor=4169E1&style=for-the-badge" alt="PostgreSQL">  
  <img src="https://img.shields.io/badge/AWS_S3-white?logo=amazons3&logoColor=white&labelColor=FF9900&style=for-the-badge" alt="AWS S3">
  <img src="https://img.shields.io/badge/n8n-white?logo=n8n&logoColor=white&labelColor=EA4B71&style=for-the-badge" alt="n8n">
  <img src="https://img.shields.io/badge/DeepSeek-white?logo=lightning&logoColor=white&labelColor=1E40AF&style=for-the-badge" alt="DeepSeek">
  <img src="https://img.shields.io/badge/Groq-white?logo=lightning&logoColor=white&labelColor=F55036&style=for-the-badge" alt="Groq">
</div>

## 🔥 [Live Demo](https://yappuccino.jafarbekyusupov.com/)
<a href="https://www.digitalocean.com/?refcode=b75e7d1f645d&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge"><img src="https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg" alt="DigitalOcean Referral Badge" /></a>

## 🌟 Overview

Yappuccino is a social blogging platform where you can share posts, comment, vote, and repost. **Platform integrates n8n AI agent to automatically summarize posts.**

> [!NOTE]
> #### [Detailed Project Overview & Analysis](https://deepwiki.com/jafarbekyusupov/yappuccino)
> Explore the complete project overview, including UML Diagrams and in-depth explanations, provided by **Cognition** [here.](https://deepwiki.com/jafarbekyusupov/yappuccino)

## 🚀 Key Features

### 🤖 **AI Integration & Automation**
- **[n8n AI workflow](https://github.com/jafarbekyusupov/yappuccino/blob/master/media/README-MEDIA/n8n-summarizer-workflow.png)** - for automated summaries
- **Multiple LLM API Providers** - Groq & DeepSeek
- **Real-time webhooks trigger** instant processing
- **Added Admin Panel - [AI Summary Dashboard](https://github.com/jafarbekyusupov/yappuccino/blob/master/media/README-MEDIA/ai-summary-dashboard.png) -** for viewing and monitoring processes with live stats provided

### 📝 Content Management
- **Rich Text Editor**: CKEditor 5 integration with image upload
- **Tag System**: Create and manage tags with auto-slugs and aliases
- **Post Management**: Full CRUD operations with draft support
- **Content Filtering**: Advanced filtering and sorting options

### 👥 Social Features
- **Voting System**: Upvote/downvote posts and comments
- **Comment System**: Nested comments with threading
- **Repost Functionality**: Share content with attribution
- **User Profiles**: Customizable profiles with activity tracking

### 🎨 User Experience
- **Responsive Design**: Mobile-first approach with touch-friendly interface
- **Real-time Interactions**: AJAX-powered voting and commenting
- **Search Functionality**: Full-text search across posts and content
- **Tag-based Navigation**: Browse content by categories

### 🔐 User Management
- **Authentication System**: Registration, login, password reset
- **Profile Management**: Image uploads, privacy settings
- **Activity Tracking**: View user's posts, comments, and interactions
- **Settings Panel**: Comprehensive user preferences

## 🛠️ Technical Stack

### Backend
- **Framework**: Django 5.2.1
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Django's built-in auth system
- **File Storage**: Django's file handling with Pillow for images

### Frontend
- **CSS Framework**: Bootstrap 4.0
- **JavaScript**: jQuery with custom AJAX implementations
- **Icons**: Bootstrap Icons
- **Fonts**: Google Fonts (Roboto Condensed, Underdog)

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- Virtual environment **(recommended)**

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/jafarbekyusupov/yappuccino.git
cd yappuccino
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate
```
> [!NOTE]
> **On Windows:**
> ```
> python -m venv venv
> venv\Scripts\activate
> ```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up the database**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser**
```bash
python manage.py createsuperuser
```

6. **Run the development server**
```bash
python manage.py runserver
```

7. **Access the application**
 - Main site: http://127.0.0.1:8000/
 - Admin panel: http://127.0.0.1:8000/admin/

## 🔧 Troubleshooting

### HTTPS Error on Development Server 
<!-- TODO -- create sep file for err fixes -->

**Problem**: Getting SSL/HTTPS errors when running `python manage.py runserver`

**Symptoms**:
```
code 400, message Bad request syntax ('\x16\x03\x01\x06À\x01\x00\x06¼\x03\x03%')
You're accessing the development server over HTTPS, but it only supports HTTP.
```

**Solutions**:
1. **Switch to HTTP** manually:
```
http://127.0.0.1:8000  ✅
https://127.0.0.1:8000 ❌
```

2. **Clear browser cache/HSTS for localhost:**
- Chrome: Go to **chrome://net-internals/#hsts** → **Delete localhost**
- Or use incognito/private mode

3. **HTTPS in development:**
- Packages already included in requirements.txt, install if you didnt
```bash
pip install -r requirements.txt
```
- If you DID install requirement.txt, then just run the following command:
```bash
python manage.py runserver_plus --cert-file cert.pem
```

## 🎨 Customization

### Styling
- Main styles in `blog/static/blog/main.css`
- Component styles in `blog/static/blog/components.css`
- Color scheme defined in CSS variables

### Configuration
- Django settings in `blogpost/settings.py`
- CKEditor configuration for rich text editing
- Bleach settings for content sanitization

## 🔧 API Endpoints

### AJAX Endpoints
- `POST /post/<id>/vote/<type>/` - Vote on posts
- `POST /post/<id>/comment/` - Add comments
- `POST /comment/<id>/vote/` - Vote on comments
- `GET /tag-suggestions/` - Tag autocomplete

<!-- ## 🧪 Testing
Run the test suite:
```bash
python manage.py test
``` -->
<!-- TODO -- add unit e2e tests -->

## 📱 Mobile Support

The application includes comprehensive mobile support:
- Responsive design for all screen sizes
- Touch-friendly interface elements
- Mobile-optimized navigation
- Swipe gestures for interactions

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure allowed hosts
- [ ] Set up production database (PostgreSQL recommended)
- [ ] Configure static file serving
- [ ] Set up media file handling
- [ ] Set environment variables

---

<div align="center">

#### [Yappuccino](https://github.com/jafarbekyusupov/yappuccino) @ [`jafarbekyusupov`](https://github.com/jafarbekyusupov)

[⭐ Star this **Repo**](https://github.com/jafarbekyusupov/yappuccino) • [🐛 Report **Bug**](https://github.com/jafarbekyusupov/yappuccino/issues) • [💡 Request | Suggest **Feature**](https://github.com/jafarbekyusupov/yappuccino/issues)

</div>
