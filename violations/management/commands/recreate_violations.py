from pymongo import ASCENDING
from django.core.management.base import BaseCommand
from tasks.models import Tasks
from tasks.jobs import prepare_violations


class Command(BaseCommand):
    help = 'Recreate violations'

    def handle(self, *args, **kwargs):
        for task in Tasks.find({}, sort=[('created', ASCENDING)]):
            try:
                prepare_violations(task['_id'])
            except Exception as e:
                print e
