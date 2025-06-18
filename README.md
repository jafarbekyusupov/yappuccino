# [Yappuccino 🗣️☕ + 🤖 AI Post Summarizer Agent](https://yappuccino.onrender.com/)
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

## 🔥 [Live Demo](https://yappuccino.onrender.com/)
[![Try It Now](https://img.shields.io/badge/TRY_IT_HERE-FF6B6B?style=for-the-badge&logo=firefox&logoColor=white)](https://yappuccino.onrender.com/)
> [!IMPORTANT]  
> 🔸 **Cold Start Delay**: This demo runs on a free-tier cloud service. If the link hasn't been clicked recently, the server may enter *sleep mode*.  
> 🔸 **First load** could take from **10-50 seconds**. After first load, following ones will be fast

## 🌟 Overview

Yappuccino is a social blogging platform where you can share posts, comment, vote, and repost. **Plus, it uses n8n AI agent to automatically summarize everything, so you get the gist instantly.**


## 🚀 Key Features

### 🤖 **AI Integration & Automation**
- **Built AI workflow** using n8n for automated summaries
- **Integrated multiple AI providers** - Groq & DeepSeek (also on local version, used Ollama models)
- **Real-time webhooks trigger** instant processing
- **Added Admin Panel - AI Summary Dashboard -** for viewing and monitoring processes with live stats provided

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

### Rich Text & Media
- **Editor**: CKEditor 5 with custom upload handling
- **Content Sanitization**: Bleach for XSS protection
- **Image Processing**: Pillow for profile picture optimization

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- Virtual environment (recommended)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/jafarbekyusupov/yappuccino.git
   cd yappuccino
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

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


## 💡 Usage Examples

### Creating a Post
1. Register/Login to your account
2. Click "New Post" in the navigation
3. Add title, content (with rich text formatting), and tags
4. Publish or save as draft

### Engaging with Content
- **Vote**: Click upvote/downvote buttons on posts
- **Comment**: Add comments with nested replies
- **Repost**: Share interesting content with your followers
- **Tag Navigation**: Click tags to view related content

### User Management
- **Profile**: Customize your profile picture and information
- **Settings**: Manage privacy, notifications, and appearance
- **Activity**: View your posts, comments, and voting history

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

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

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
- [ ] Configure email backend
- [ ] Set environment variables for secrets

## 📁 Project Structure

```
yappuccino/
├── blog/                              # MAIN blog application
│   ├── admin.py                       # admin panel config
│   ├── api_views.py                   # api endpoints for n8n ai agent integration
│   ├── apps.py                        # app config
│   ├── ckeditor_views.py              # CKEditor implementation to override conflicting views
│   ├── ckeditor_upload_permissions.py # upload permissions
│   ├── context_processors.py          # custom context processors
│   ├── forms.py                       # form definitions
│   ├── management/                    # custom management commands
│   │   └── commands/
│   │       ├── create_superuser.py   # SUPERUSER creation
│   │       ├── test_s3.py            # s3 storage testing
│   │       └── test_summarization.py # ai summarization testing
│   │
│   ├── migrations/                # database migrations -- mostly generate by django
│   ├── models.py                  # database models
│   ├── patch_ckeditor.py          # CKEditor customization
│   ├── static/blog/               # static files
│   │   ├── components.css         # component styles
│   │   ├── main.css               # main stylesheet
│   │   ├── navbar_styles.css      # navigation bar styling
│   │   └── js/                    # javascript dir
│   │       ├── comment_voting.js  # comment voting functionality
│   │       ├── main.js            # core JS
│   │       ├── social_features.js # social interaction features
│   │       └── tag_widget.js      # tag selection widget
│   │
│   ├── templates/blog/            # HTML templates
│   │   ├── includes/              # reusable components
│   │   │   ├── comment_section.html
│   │   │   ├── filter_ctrls.html     # post filtering
│   │   │   ├── footer.html          
│   │   │   ├── pagination.html
│   │   │   ├── sidebar.html   
│   │   │   └── ult_post_card.html    # post display component
│   │   ├── about.html             # about page
│   │   ├── base.html              # base template -- which other pages extend from
│   │   ├── home.html              # homepage
│   │   ├── post_detail.html       # post view
│   │   ├── post_form.html         # post creation/editing
│   │   ├── summary_dashboard.html # ADMIN PANEL -- ai summary dashboard
│   │   ├── tag_list.html          # tag management
│   │   └── user_activity.html     # user activity view
│   ├── templatetags/              # custom template tags
│   │   └── blog_extras.py         # template helpers
│   ├── urls.py                    # URL routing
│   ├── views.py                   # view logic
│   └── widgets.py                 # custom form widgets
│
├── users/                         # USER MANAGEMENT APP
│   ├── admin.py                   # user admin config
│   ├── apps.py                    # app config
│   ├── forms.py                   # user-related forms
│   ├── migrations/                # user model migrations
│   ├── models.py                  # user profile models
│   ├── signals.py                 # user signal handlers
│   ├── templates/users/           # user-related templates
│   │   ├── login.html             # login page
│   │   ├── logout.html            # logout page
│   │   ├── profile.html           # user profile
│   │   ├── register.html          # registration page
│   │   └── settings.html          # user settings
│   ├── urls.py                    # user URL patterns
│   └── views.py                   # user view logic
│
├── blogpost/                      # PROJECT CONFIG DIRECTORY
│   ├── __init__.py                # package init
│   ├── asgi.py                    # ASGI configuration
│   ├── production.py              # production settings
│   ├── settings.py                # development settings
│   ├── urls.py                    # main URL routing
│   └── wsgi.py                    # WSGI configuration
│
├── media/                         # user-uploaded files (only for dev|local)
│
├── .gitignore                     
├── build.sh                       # deployment build script
├── dump_data.py                   # database backup utils
├── manage.py                      # django management script
├── Procfile                       # Heroku/Render deployment
├── README.md                      # TIHS FILE -- project documentation
├── render.yaml                    # render.com config
├── requirements.txt               # python dependencies
└── runtime.txt                    # python runtime speciifcation
```