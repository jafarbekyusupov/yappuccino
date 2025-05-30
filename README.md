# Yappuccino 🗣️☕
*A platform for Certified Yappers*

<div>  
   <img src="https://img.shields.io/badge/Django-5.2.1-white?logo=django&logoColor=white&labelColor=092E20&style=for-the-badge" alt="Django">  
  <img src="https://img.shields.io/badge/Python-3.8+-white?logo=python&logoColor=white&labelColor=3776AB&style=for-the-badge" alt="Python">  
  <img src="https://img.shields.io/badge/Bootstrap-4-white?logo=bootstrap&logoColor=white&labelColor=7952B3&style=for-the-badge" alt="Bootstrap">  
  <img src="https://img.shields.io/badge/CKEditor-5-white?logo=ckeditor&logoColor=white&labelColor=0287D0&style=for-the-badge" alt="CKEditor">  
  <img src="https://img.shields.io/badge/PostgreSQL-white?logo=postgresql&logoColor=white&labelColor=4169E1&style=for-the-badge" alt="PostgreSQL">  
  <img src="https://img.shields.io/badge/Backblaze_B2-white?logo=backblaze&logoColor=white&labelColor=003B88&style=for-the-badge" alt="Backblaze B2">  
</div>

## 🔥 [Live Demo](https://yappuccino.onrender.com/)
[![Try It Now](https://img.shields.io/badge/TRY_IT_HERE-FF6B6B?style=for-the-badge&logo=firefox&logoColor=white)](https://yappuccino.onrender.com/)
> [!IMPORTANT]  
> 🔸 **Cold Start Delay**: This demo runs on a free-tier cloud service. If the link hasn't been clicked recently, the server may enter *sleep mode*.  
> 🔸 **First load** could upto **50 seconds**

## 🌟 Overview

Yappuccino is a feature-rich social blogging platform that combines traditional blogging with modern social media features. Users can create posts, engage through comments, vote on content, and share posts through a repost system.


## 🚀 Key Features

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

## 📁 Project Structure

```
yappuccino/
├── blog/                          # Main blog application
│   ├── migrations/                # Database migrations
│   ├── static/blog/               # Static files (CSS, JS, images)
│   │   ├── css/                   # Stylesheets
│   │   └── js/                    # JavaScript files
│   ├── templates/blog/            # HTML templates
│   │   └── includes/              # Reusable template components
│   ├── templatetags/              # Custom template tags
│   ├── models.py                  # Database models
│   ├── views.py                   # View logic
│   ├── forms.py                   # Form definitions
│   └── urls.py                    # URL routing
├── users/                         # User management application
│   ├── templates/users/           # User-related templates
│   ├── models.py                  # User profile models
│   ├── views.py                   # User views
│   └── forms.py                   # User forms
├── media/                         # User-uploaded files
└── requirements.txt               # Python dependencies
```

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