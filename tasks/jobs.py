from datetime import datetime
from django_rq import job
from violations.exceptions import ViolationDoesNotExists
import services.base
import violations.base
from .models import Tasks
from . import const


@job
def create_task(task_id):
    """Create task job"""
    data = Tasks.find_one(task_id)
    data['created'] = datetime.now()
    task = services.base.library.get(data['service']['name'])(data)
    prepare_violations(task)


def _prepare_violation(violation):
    """Prepare single violation"""
    try:
        violation_creator = violations.base.library.get(violation['name'])
        return violation_creator(violation)
    except ViolationDoesNotExists:
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
