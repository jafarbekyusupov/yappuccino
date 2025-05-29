#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

# skip bs
python manage.py migrate blog 0003_post_is_repost_post_original_post_post_view_count_and_more --fake
python manage.py migrate blog 0005_merge_20250519_0111 --fake
python manage.py migrate blog 0006_add_tag_slugs --fake
python manage.py migrate blog 0007_add_tag_slug_field --fake
python manage.py migrate blog 0008_merge_0006_add_tag_slugs_0007_add_tag_slug_field --fake
python manage.py migrate blog 0009_tagalias --fake
python manage.py migrate blog 0010_auto_20250520_0136 --fake
python manage.py migrate blog 0011_alter_tag_slug --fake
python manage.py migrate blog 0012_alter_comment_content_alter_post_content --fake
python manage.py migrate blog 0013_comment_edited_at_comment_is_edited_alter_post_title_and_more --fake

python manage.py migrate

python manage.py collectstatic --no-input