"""
Token based service
"""
from tasks.models import Tasks
from projects.models import Project
from .base import library
from .utils import logger


@library.register('token')
def token_service(data):
    """Find project by token and create task

    :param data: Data received from service
    :type data: dict
    :returns: bson.ObjectId or None -- pk of created task
    """
    try:
        project = Project.objects.get(token=data['service']['token'])

        assert data['project'] == project.name

        return Tasks.save(data)
    except Exception as e:
        # remove task on error
        Tasks.remove(data['_id'])
        logger.exception('Token service fail: {}'.format(e))
