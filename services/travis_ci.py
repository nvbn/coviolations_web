import requests
from tasks.models import Tasks
from .base import library
from .utils import logger


@library.register('travis_ci')
def travis_ci_service(data):
    """Create task from data dict"""
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

        assert data['project'] == repo['slug']

        data['service'].update(job)

        return Tasks.save(data)
    except Exception as e:
        # remove task on error
        Tasks.remove(data['_id'])
        logger.exception('Travis-ci service fail: {}'.format(e), task=data)
