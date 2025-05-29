import os
import sys
import json
import django
from django.core.management import call_command
from io import StringIO

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogpost.settings")
django.setup()
out = StringIO()
call_command('dumpdata', exclude=['contenttypes', 'auth.permission'],stdout=out)

# w utf8 encoding
data = out.getvalue()
with open('data_dump.json', 'w', encoding='utf-8') as f: f.write(data)
print("data dump completed sucsessfully")