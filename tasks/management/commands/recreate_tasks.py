from django.core.management.base import BaseCommand
from tasks.models import Tasks
from tasks.jobs import create_task


class Command(BaseCommand):
    help = 'Recreate tasks'

    def handle(self, *args, **kwargs):
        for task in Tasks.find({}):
            task['violations'] = []
            task_id = Tasks.save(task)
            create_task(task_id)
