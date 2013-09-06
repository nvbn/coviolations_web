from tasks.models import Tasks
from .base import library


@library.register('dummy')
def dummy_service(data):
    """Create task from data dict"""
    task_id = Tasks.save(data)
    return task_id
