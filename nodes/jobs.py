from time import sleep
from datetime import datetime
from django.conf import settings
from django_rq import job, get_scheduler
from .models import NodeTask


@job
def run_node_task(node_task_id):
    """Run node task"""
    node_task = NodeTask.objects.get(node_task_id)
    while True:
        active = NodeTask.objects.filter(state=NodeTask.STATE_ACTIVE).count()
        if active < settings.PARALLEL_TASKS:
            break
        else:
            sleep(settings.PARALLEL_TIMEOUT)
    node_task.perform()


def kill_old_nodes():
    """Kill old nodes"""
    for node_task in NodeTask.objects.filter(
        status=NodeTask.STATE_ACTIVE,
        created__lte=datetime.now() - settings.NODE_LIFETIME,
    ):
        node_task.kill()


scheduler = get_scheduler('default')
scheduler.schedule(
    datetime.now(), kill_old_nodes,
    interval=settings.NODE_KILLER_INTERVAL,
)
