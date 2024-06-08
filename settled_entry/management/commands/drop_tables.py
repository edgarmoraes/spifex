from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Drop unused tables'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS realizado_monthslistsettled;")
            cursor.execute("DROP TABLE IF EXISTS realizado_settledentry;")
        self.stdout.write(self.style.SUCCESS('Successfully dropped the tables'))
