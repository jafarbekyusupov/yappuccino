#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
cat > verify_db.py << 'EOF'
import os
import sys
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.settings')
django.setup()

def check_database():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def list_tables():
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            if tables:
                print("Tables in database:")
                for tt in tables: print(f"  - {tt[0]}")
            else: print("No tables found in database!")

    except Exception as e:
        print(f"Error listing tables: {e}")

if check_database():
    list_tables()
else:
    sys.exit(1)
EOF

echo "Verifying database connection..."
python verify_db.py

echo "Removing existing migrations..."
rm -f blog/migrations/0*.py
touch blog/migrations/__init__.py

echo "Creating consolidated migration file..."
cat > blog/migrations/0001_initial.py << 'EOF'
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import MaxLengthValidator

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, validators=[MaxLengthValidator(50)])),
                ('content', CKEditor5Field(verbose_name='Content')),
                ('date_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('is_repost', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),

        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
        ),

        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='posts', to='blog.tag'),
        ),

        migrations.AddField(
            model_name='post',
            name='original_post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reposts', to='blog.post'),
        ),

        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', CKEditor5Field(verbose_name='Content')),
                ('date_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_edited', models.BooleanField(default=False)),
                ('edited_at', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='blog.comment')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blog.post')),
            ],
            options={
                'ordering': ['-date_posted'],
            },
        ),

        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_type', models.CharField(choices=[('upvote', 'Upvote'), ('downvote', 'Downvote')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='blog.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('post', 'user')},
            },
        ),

        migrations.CreateModel(
            name='CommentVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_type', models.CharField(choices=[('up', 'Upvote'), ('down', 'Downvote')], max_length=4)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='blog.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('comment', 'user')},
            },
        ),

        migrations.CreateModel(
            name='TagAlias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.SlugField(unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='blog.tag')),
            ],
            options={
                'verbose_name_plural': 'Tag Aliases',
            },
        ),
    ]
EOF

cat > blog/migrations/0002_default_tags.py << 'EOF'
from django.db import migrations
from django.utils.text import slugify

def create_default_tags(apps, schema_editor):
    Tag = apps.get_model('blog', 'Tag')
    default_tags = [
        'Software Development',
        'AI & ML',
        'Cybersecurity',
        'Hardware',
        'Design',
        'Popsci'
    ]

    for tag_name in default_tags:
        Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': slugify(tag_name)}
        )

def remove_default_tags(apps, schema_editor):
    Tag = apps.get_model('blog', 'Tag')
    default_tags = [
        'Software Development',
        'AI & ML',
        'Cybersecurity',
        'Hardware',
        'Design',
        'Popsci'
    ]

    Tag.objects.filter(name__in=default_tags).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_tags, remove_default_tags),
    ]
EOF

python manage.py migrate --verbosity 2
echo "Verifying migrations and database tables..."
python verify_db.py

cat > verify_models.py << 'EOF'
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Post, Tag, Comment, Vote, CommentVote, TagAlias

def check_models():
    models = [
        (User, 'User'),
        (Post, 'Post'),
        (Tag, 'Tag'),
        (Comment, 'Comment'),
        (Vote, 'Vote'),
        (CommentVote, 'CommentVote'),
        (TagAlias, 'TagAlias')
    ]

    for model, name in models:
        try:
            count = model.objects.count()
            print(f"Model {name} is accessible (count: {count})")
        except Exception as e:
            print(f"Error accessing model {name}: {e}")

check_models()
EOF

python verify_models.py

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Build process completed!"