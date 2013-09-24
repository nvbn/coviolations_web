from mock import MagicMock
from django.test import TestCase
from django_rq import get_worker
from tools.mongo import MongoFlushMixin
from projects.tests.factories import ProjectFactory
from .. import jobs, models, const


class CreateTaskJobCase(MongoFlushMixin, TestCase):
    """Create task job case"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(CreateTaskJobCase, self).setUp()
        self._mock_prepare_violations()
        self._mock_fill_task()
        self._create_task()

    def _mock_prepare_violations(self):
        """Mock prepare violations"""
        self._orig_prepare_violations = jobs.prepare_violations
        jobs.prepare_violations = MagicMock()

    def _mock_fill_task(self):
        """Mock fill task from github"""
        self._orig_fill_task = jobs._fill_task_from_github
        jobs._fill_task_from_github = MagicMock()

    def tearDown(self):
        jobs.prepare_violations = self._orig_prepare_violations
        jobs._fill_task_from_github = self._orig_fill_task

    def _create_task(self):
        """Create task"""
        ProjectFactory(name='test')
        data = {
            'service': {
                'name': 'dummy',
            },
            'project': 'test',
            'branch': 'develop',
            'commit': 'asdfg',
            'violations': [
                {'name': 'dummy', 'raw': '1'},
            ]
        }
        jobs.create_task(models.Tasks.save(data))
        get_worker().work(burst=True)

    def test_create(self):
        """Test create"""
        self.assertEqual(models.Tasks.count(), 1)

    def test_propagating(self):
        """Test propagating to prepare violations"""
        task = models.Tasks.find_one()
        jobs.prepare_violations.delay.assert_called_once_with(task['_id'])


class PrepareViolationsJobCase(MongoFlushMixin, TestCase):
    """Prepare violations job case"""
    mongo_flush = ['tasks']

    def test_prepare(self):
        """Test prepare"""
        tasks = [{
            'violations': [
                {
                    'name': 'dummy',
                    'raw': 'test{}'.format(n),
                },
            ],
            'owner_id': 1,
            'project': 'test',
        } for n in range(10)]

        for task in tasks:
            task_id = models.Tasks.save(task)
            jobs.prepare_violations(task_id)
        get_worker().work(burst=True)
        self.assertEqual(10, sum(
            [len(task['violations']) for task in models.Tasks.find()]
        ))

    def test_not_fail_all(self):
        """Not fail all if fail one"""
        task = {
            'violations': [
                {'name': 'dummy', 'raw': 'rew'},
                {'name': 'dummy!!!', 'raw': 'rwww'},
                {'name': 'dummy', 'raw': 'row'},
            ],
            'owner_id': 1,
            'project': 'test',
        }
        task_id = models.Tasks.insert(task)
        jobs.prepare_violations(task_id)
        get_worker().work(burst=True)

        task = models.Tasks.find_one(task_id)
        self.assertEqual(len([
            violation for violation in task['violations']
            if violation['status'] is const.STATUS_SUCCESS
        ]), 2)
        self.assertEqual(len([
            violation for violation in task['violations']
            if violation['status'] is const.STATUS_FAILED
        ]), 1)

    def test_nofail_argument(self):
        """Test nofail argument"""
        task = {
            'violations': [
                {'name': 'dummy!!!', 'raw': 'rwww', 'nofail': True},
            ],
            'owner_id': 1,
            'project': 'test',
        }
        task_id = models.Tasks.insert(task)
        jobs.prepare_violations(task_id)
        get_worker().work(burst=True)

        task = models.Tasks.find_one(task_id)
        self.assertEqual(
            task['violations'][0]['status'], const.STATUS_SUCCESS,
        )


class CommentPullRequestJob(MongoFlushMixin, TestCase):
    """Comment pull request job case"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(CommentPullRequestJob, self).setUp()
        self._orig_github = jobs.Github
        jobs.Github = MagicMock()

    def tearDown(self):
        jobs.Github = self._orig_github

    def test_comment(self):
        """Test comment"""
        ProjectFactory(name='test')
        task = {
            'project': 'test',
            'pull_request_id': 2,
            'violations': [
                {'name': 'dummy', 'preview': 'rew'},
                {'name': 'dummy!!!', 'raw': 'rwww'},
                {'name': 'dummy', 'raw': 'row'},
            ],
            'commit': {'hash': 'test'},
        }
        jobs.comment_pull_request(models.Tasks.save(task))
        self.assert_(True)
