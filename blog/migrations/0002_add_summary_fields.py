# Generated by Django 5.2.1 on 2025-06-11 19:55

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
