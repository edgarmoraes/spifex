import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spifex.settings")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    tables_to_delete = [table for table in tables if 'settled_entry' in table]
    for table in tables_to_delete:
        print(f"Deletando tabela {table}...")
        cursor.execute(f"DROP TABLE {table};")