# blog/migrations/XXXX_add_tag_slug_field.py

from django.db import migrations, models
from django.utils.text import slugify


def generate_unique_slugs(apps, schema_editor):
	"""Generate unique slugs for existing tags"""
	Tag = apps.get_model('blog', 'Tag')

	for tag in Tag.objects.all():
		base_slug = slugify(tag.name)
		slug = base_slug
		counter = 1

		# Check for existing slugs
		while Tag.objects.filter(slug=slug).exclude(id=tag.id).exists():
			slug = f"{base_slug}-{counter}"
			counter += 1

		tag.slug = slug
		tag.save()


class Migration(migrations.Migration):
	dependencies = [
		('blog', '0005_merge_20250519_0111'),  # Make sure this matches your actual previous migration
	]

	operations = [
		# First add the field allowing null
		migrations.AddField(
			model_name='tag',
			name='slug',
			field=models.SlugField(null=True, blank=True, max_length=50),
		),

		# Run the data migration
		migrations.RunPython(generate_unique_slugs),

		# Make the field required and unique
		migrations.AlterField(
			model_name='tag',
			name='slug',
			field=models.SlugField(unique=True, max_length=50),
		),
	]