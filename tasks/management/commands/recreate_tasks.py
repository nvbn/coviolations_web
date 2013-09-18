from django.core.management.base import BaseCommand
from tasks.models import Tasks
from tasks.jobs import create_task


class Command(BaseCommand):
    help = 'Recreate tasks'

    def handle(self, *args, **kwargs):
        for task in Tasks.find({}):
            try:
                create_task(task['_id'])
            except Exception as e:
                print e
