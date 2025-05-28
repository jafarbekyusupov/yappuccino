# In the new migration file
from django.db import migrations


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
		Tag.objects.get_or_create(name=tag_name)


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
		('blog', '0001_initial'),  # Update this to the latest migration
	]

	operations = [
		migrations.RunPython(create_default_tags, remove_default_tags),
	]