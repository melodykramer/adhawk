from django.core.management.base import BaseCommand
from django.db import transaction

from db_script.import_reporting_youtube import ReportingYouTubeImporter

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):

        i = ReportingYouTubeImporter()
        i.make_sql_table()
        i.upload()
