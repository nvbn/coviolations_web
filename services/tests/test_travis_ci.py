import sure
from mock import MagicMock
from testfixtures import LogCapture
from django.test import TestCase
from tools.mongo import MongoFlushMixin
from tasks.models import Tasks
from .. import travis_ci


class TravisCiServiceCase(MongoFlushMixin, TestCase):
    """Travis ci service case"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(TravisCiServiceCase, self).setUp()
        self._orig_requests = travis_ci.requests
        travis_ci.requests = MagicMock()

    def tearDown(self):
        travis_ci.requests = self._orig_requests

    def _create_task(self):
        """Create task"""
        task_id = Tasks.save({
            'project': 'test',
            'service': {
                'name': 'travis_ci',
                'job_id': 15,
            }
        })
        return Tasks.find_one(task_id)

    def test_fail_if_already_exists(self):
        """Test fail if job already exists"""
        self._create_task()
        data = self._create_task()
        with LogCapture() as log_capture:
            travis_ci.travis_ci_service(data).should.be.none
            list(log_capture.actual())[0].should.contain('ERROR')
        Tasks.find({}).count().should.be.equal(1)

    def test_fail_on_travis_api_error(self):
        """Test fail on travis api error"""
        travis_ci.requests.get.side_effect = Exception
        data = self._create_task()
        with LogCapture() as log_capture:
            travis_ci.travis_ci_service(data).should.be.none
            list(log_capture.actual())[0].should.contain('ERROR')
        Tasks.find({}).count().should.be.equal(0)

    def test_fail_on_wrong_project(self):
        """Test fail on wrong project"""
        travis_ci.requests.get.return_value = MagicMock(
            json=MagicMock(return_value={
                'repository_id': 2,
                'slug': 'wrong',
            })
        )
        data = self._create_task()
        with LogCapture() as log_capture:
            travis_ci.travis_ci_service(data).should.be.none
            list(log_capture.actual())[0].should.contain('ERROR')
        Tasks.find({}).count().should.be.equal(0)

    def test_success(self):
        """Test success create task"""
        travis_ci.requests.get.return_value = MagicMock(
            json=MagicMock(return_value={
                'repository_id': 2,
                'slug': 'test',
            })
        )
        data = self._create_task()
        travis_ci.travis_ci_service(data).should.be.equal(data['_id'])
