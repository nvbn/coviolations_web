"""
Dummy service
"""
from tasks.models import Tasks
from .base import library


@library.register('dummy')
def dummy_service(data):
    """Create task from data dict

    :param data: Data received from service
    :type data: dict
    :returns: bson.ObjectId -- pk of created task
    """
    task_id = Tasks.save(data)
    return task_id
