from time import sleep
from django.conf import settings
from django_rq import job
from .models import NodeTask


@job
def run_node_task(node_task):
    """Run node task"""
    while True:
        active = NodeTask.objects.filter(state=NodeTask.STATE_ACTIVE).count()
        if active < settings.PARALLEL_TASKS:
            break
        else:
            sleep(settings.PARALLEL_TIMEOUT)
    node_task.perform()
