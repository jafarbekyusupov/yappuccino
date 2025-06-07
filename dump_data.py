import os
import sys
import json
import django
from django.core.management import call_command
from io import StringIO
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogpost.settings")
django.setup()

def dump_database():
    try:
        print("=== DB DUMP STARTED ===")
        out = StringIO() #outbuff
        call_command(
            'dumpdata',
            exclude=[
                'contenttypes',
                'auth.permission',
                'sessions.session',
                # 'admin.logentry',
            ],
            stdout=out,
            indent=2
        )

        data = out.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'data_dump_{timestamp}.json'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)

        print(f"=== DB DUMP DONE ===")
        print(f"++ File saved as -- {filename}")
        print(f"!! Data size -- {len(data)} chars")
        return filename

    except Exception as e:
        print(f"x Error during dump: {e}")
        return None

if __name__ == "__main__":
    dump_database()