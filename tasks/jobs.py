from datetime import datetime
from django_rq import job
from violations.exceptions import ViolationDoesNotExists
import services.base
import violations.base
from push.base import sender
from .models import Tasks
from .utils import logger
from . import const


@job
def create_task(task_id):
    """Create task job"""
    logger.info('Task received: {}'.format(task_id))
    data = Tasks.find_one(task_id)
    data['created'] = datetime.now()
    task = services.base.library.get(data['service']['name'])(data)

    if task:
        prepare_violations.delay(task)
    else:
        logger.warning('Task failed: {}'.format(task_id))


def _prepare_violation(violation):
    """Prepare single violation"""
    try:
        violation_creator = violations.base.library.get(violation['name'])
        return violation_creator(violation)
    except ViolationDoesNotExists as e:
        logger.warning("Violation doesn't exists: {}".format(e))

        violation['status'] = const.STATUS_FAILED
        return violation


@job
def prepare_violations(task_id):
    """Prepare violations"""
    task = Tasks.find_one(task_id)
    task['violations'] = map(_prepare_violation, task['violations'])
    task['status'] = const.STATUS_SUCCESS if all([
        violation.get('status') != const.STATUS_FAILED
        for violation in task['violations']
    ]) else const.STATUS_FAILED
    Tasks.save(task)

    sender.send(
        type='task', owner=task['owner_id'],
        task=str(task_id), project=task['project'],
    )
