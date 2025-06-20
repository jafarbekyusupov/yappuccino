set -o errexit

export DJANGO_SETTINGS_MODULE=blogpost.production

pip install -r requirements.txt
cat > verify_settings.py << 'EOF'
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.production')
django.setup()

print("=== settings verif ===")
print(f"Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"DEBUG: {settings.DEBUG}")
print(f"Storage backend: {settings.DEFAULT_FILE_STORAGE if hasattr(settings, 'DEFAULT_FILE_STORAGE') else 'Not set'}")

b2v = ['B2_ACCESS_KEY_ID', 'B2_SECRET_ACCESS_KEY', 'B2_BUCKET_NAME', 'B2_REGION']
print("\n=== b2 env vars ===")
for ii in b2v:
    vv = os.environ.get(ii)
    if vv:
        dspv = vv[:8] + '...' if 'KEY' in ii else vv
        print(f"OK {ii}: {dspv}")
    else: print(f"x {ii}: Not set")

if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
    print(f"\n OK AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
if hasattr(settings, 'AWS_S3_ENDPOINT_URL'):
    print(f"OK AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
if hasattr(settings, 'MEDIA_URL'):
    print(f"MEDIA_URL: {settings.MEDIA_URL}")

# check ai api keys
ai_keys = ['DEEPSEEK_API_KEY', 'GROQ_API_KEY', 'OPENAI_API_KEY']
print("\n=== ai api keys ===")
for key in ai_keys:
    value = os.environ.get(key)
    if value:
        print(f"OK {key}: {value[:8]}...")
    else:
        print(f"x {key}: Not set")
EOF

echo "verif settings n env"
python verify_settings.py

cat > verify_db.py << 'EOF'
import os
import sys
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.production')
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

if check_database(): list_tables()
else: sys.exit(1)
EOF

echo "Verifying database connection..."
python verify_db.py

# check if we need to reset migrations or if we can work with existing database
cat > check_migration_state.py << 'EOF'
import os
import django
from django.db import connection
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.production')
django.setup()

def check_migration_state():
    with connection.cursor() as cursor:
        try:
            # check if django_migrations table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'django_migrations'
                );
            """)
            migrations_table_exists = cursor.fetchone()[0]
            
            if not migrations_table_exists:
                print("fresh database - no migrations table found")
                return "fresh"
            
            # check if blog_post table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'blog_post'
                );
            """)
            post_table_exists = cursor.fetchone()[0]
            
            if not post_table_exists:
                print("blog app not migrated yet")
                return "fresh"
                
            # check if summary columns exist
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'blog_post'
                AND column_name IN ('summary', 'summary_generated_at', 'needs_summary_update', 'summary_model_version');
            """)
            summary_columns = [row[0] for row in cursor.fetchall()]
            
            if len(summary_columns) == 4:
                print("database has all summary columns - up to date")
                return "complete"
            elif len(summary_columns) == 0:
                print("database missing all summary columns - needs migration")
                return "needs_summary_migration"
            else:
                print(f"database has partial summary columns: {summary_columns}")
                return "partial"
                
        except Exception as e:
            print(f"error checking migration state: {e}")
            return "error"

migration_state = check_migration_state()
print(f"migration_state={migration_state}")

# write state to file for build script
with open('migration_state.txt', 'w') as f:
    f.write(migration_state)
EOF

echo "checking migration state..."
python check_migration_state.py
MIGRATION_STATE=$(cat migration_state.txt)
echo "migration state: $MIGRATION_STATE"

if [ "$MIGRATION_STATE" = "fresh" ]; then
    echo "fresh database detected - creating consolidated migrations..."
    
    # remove existing migrations
    rm -f blog/migrations/0*.py
    rm -f users/migrations/0*.py
    touch blog/migrations/__init__.py
    touch users/migrations/__init__.py

    # create consolidated migration for blog
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
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True, max_length=50)),
            ],
        ),

        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, validators=[MaxLengthValidator(50)])),
                ('content', CKEditor5Field(verbose_name='Content')),
                ('date_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('is_repost', models.BooleanField(default=False)),
                # ------------------------------ SMRY FIELDS ------------------------------ #
                ('summary', models.TextField(blank=True, null=True, help_text="AI-generated summary")),
                ('summary_generated_at', models.DateTimeField(blank=True, null=True)),
                ('needs_summary_update', models.BooleanField(default=True)),
                ('summary_model_version', models.CharField(max_length=50, blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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

    cat > users/migrations/0001_initial.py << 'EOF'
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='default.jpg', upload_to='profile_pics')),
                ('show_email', models.BooleanField(default=False)),
                ('show_activity', models.BooleanField(default=True)),
                ('email_comments', models.BooleanField(default=True)),
                ('email_replies', models.BooleanField(default=True)),
                ('email_reposts', models.BooleanField(default=True)),
                ('email_newsletter', models.BooleanField(default=False)),
                ('theme', models.CharField(default='light', max_length=20)),
                ('posts_per_page', models.IntegerField(default=5)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
EOF

elif [ "$MIGRATION_STATE" = "needs_summary_migration" ]; then
    echo "existing database without summary fields - keeping existing migrations and adding summary migration..."
    
    if [ ! -f "blog/migrations/0002_add_summary_fields.py" ]; then
        echo "creating summary fields migration..."
        cat > blog/migrations/0002_add_summary_fields.py << 'EOF'
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='needs_summary_update',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='post',
            name='summary',
            field=models.TextField(blank=True, help_text='AI-generated summary', null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='summary_generated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='summary_model_version',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
EOF
    fi

elif [ "$MIGRATION_STATE" = "complete" ]; then
    echo "database alr has all required fields - no migration changes needed"

else
    echo "unexpected migration state: $MIGRATION_STATE - proceeding with caution..."
fi

echo "running migrations..."
python manage.py migrate --noinput --verbosity 2

cat > lverif.py << 'EOF'
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpost.production')
django.setup()

def verify_tables():
    with connection.cursor() as cursor:
        reqTbs = ['blog_post', 'blog_tag', 'blog_comment', 'blog_vote', 'users_profile']
        
        for tt in reqTbs:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, [tt])
            
            exists = cursor.fetchone()[0]
            if exists:
                print(f"-- OK -- {tt}: exists")
            else:
                print(f"-- X -- {tt}: missing")
                return False
        
        # check if post table has basic required columns
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'blog_post'
            AND column_name IN ('id', 'title', 'content', 'author_id');
        """)
        bscCls = [row[0] for row in cursor.fetchall()]
        
        if len(bscCls) >= 4:
            print("-- OK -- blog_post table has required columns")
            return True
        else:
            print(f"-- X -- blog_post missing basic columns: {bscCls}")
            return False

if verify_tables():
    print("database verification passed")
else:
    print("database verification failed")
    exit(1)
EOF

echo "verifying database structure..."
python lverif.py

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Testing storage configuration..."
if [ -f "blog/management/commands/test_s3.py" ]; then
    python manage.py test_s3 || echo "S3 test failed - check env vars"
fi

echo "CREATING SUPERUSER..."
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py create_superuser || echo "superuser creation failed - prob alr exists"
else
    echo "no DJANGO_SUPERUSER_PASSWORD set - skipping superuser creation"
fi

echo "=== testing ai api connectivity ==="
# test if any ai api keys are available
if [ -n "$DEEPSEEK_API_KEY" ]; then
    echo "-- OK -- deepseek api key detected"
elif [ -n "$GROQ_API_KEY" ]; then
    echo "-- OK -- groq api key detected"
else
    echo "-- FAIL -- no ai api keys detected → summaries wont work"
fi

# cleanup tmp files
rm -f migration_state.txt verify_settings.py verify_db.py check_migration_state.py lverif.py
echo "Build process completed with AI API integration!"