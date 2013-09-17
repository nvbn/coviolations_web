import requests
from tasks.models import Tasks
from .base import library
from .utils import logger


@library.register('travis_ci')
def travis_ci_service(data):
    """Create tasks from data received from travis-c

    :param data: Data received from service
    :type data: dict
    :returns: bson.ObjectId or None -- pk of created task
    """
    try:
        assert Tasks.find({
            'service.name': 'travis_ci',
            'service.job_id': data['service']['job_id'],
        }).count() <= 1

        job = requests.get(
            'https://api.travis-ci.org/jobs/{}'.format(
                data['service']['job_id'],
            ),
        ).json()

        repo = requests.get(
            'https://api.travis-ci.org/repos/{}'.format(
                job['repository_id'],
            ),
        ).json()

        # TODO: add pull request support
        assert data['project'] == repo['slug']

        if data['service'].get('pull_request_id'):
            pull_request = data['service']['pull_request_id']
            if pull_request != 'false':
                data['pull_request_id'] = int(
                    data['service']['pull_request_id'],
                )

        return Tasks.save(data)
    except Exception as e:
        # remove task on error
        Tasks.remove(data['_id'])
        logger.exception('Travis-ci service fail: {}'.format(e))
