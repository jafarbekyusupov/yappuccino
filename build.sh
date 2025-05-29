#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
cat > fix_migrations.py << 'EOF'
import os
import glob
import re

def fmgrt():
    return sorted(glob.glob('blog/migrations/00*.py'))

def rmgrt(file_path):
    with open(file_path,'r') as f: return f.read()

def wmgrt(file_path, dt):
    with open(file_path, 'w') as f: f.write(dt)
    print(f"Updated {file_path}")

def fix_duplicate_slug_migrations():
    mp = 'blog/migrations/0007_add_tag_slug_field.py'
    if os.path.exists(mp):
        dt = rmgrt(mp)
        mdt = re.sub(r"migrations\.AddField\(\s*model_name='tag',\s*name='slug',.*?\),","", dt, flags=re.DOTALL)

        if mdt != dt: wmgrt(mp, mdt); print("Fixed duplicate slug field issue")
        else: print("No changes needed in 0007_add_tag_slug_field.py")

    else: print(f"Migration file {mp} not found")

fix_duplicate_slug_migrations()
EOF

python fix_migrations.py

echo "running init migrations..."
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate sessions
python manage.py migrate admin

echo "running blog migrations..."

python manage.py migrate blog 0001_initial

python manage.py migrate blog 0002_tag_alter_post_content_post_tags
python manage.py migrate blog 0003_post_is_repost_post_original_post_post_view_count_and_more
python manage.py migrate blog 0005_merge_20250519_0111

python manage.py migrate blog 0006_add_tag_slugs --fake
python manage.py migrate blog 0007_add_tag_slug_field --fake
python manage.py migrate blog 0008_merge_0006_add_tag_slugs_0007_add_tag_slug_field --fake

python manage.py migrate blog 0009_tagalias
python manage.py migrate blog 0010_auto_20250520_0136
python manage.py migrate blog 0011_alter_tag_slug
python manage.py migrate blog 0012_alter_comment_content_alter_post_content
python manage.py migrate blog 0013_comment_edited_at_comment_is_edited_alter_post_title_and_more

python manage.py migrate

python manage.py collectstatic --no-input