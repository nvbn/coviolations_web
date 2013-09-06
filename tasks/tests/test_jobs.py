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
        self._create_task()

    def _mock_prepare_violations(self):
        """Mock prepare violations"""
        self._orig_prepare_violations = jobs.prepare_violations
        jobs.prepare_violations = MagicMock()

    def tearDown(self):
        jobs.prepare_violations = self._orig_prepare_violations

    def _create_task(self):
        """Create task"""
        ProjectFactory(name='test')
        jobs.create_task({
            'service': 'dummy',
            'project': 'test',
            'branch': 'develop',
            'commit': 'asdfg',
            'violations': [
                {'name': 'dummy', 'raw': '1'},
            ]
        })
        get_worker().work(burst=True)

    def test_create(self):
        """Test create"""
        self.assertEqual(models.Tasks.count(), 1)

    def test_propagating(self):
        """Test propagating to prepare violations"""
        task = models.Tasks.find_one()
        jobs.prepare_violations.assert_called_once_with(task['_id'])


class PrepareViolationsJobCase(MongoFlushMixin, TestCase):
    """Prepare violations job case"""
    mongo_flush = ['tasks']

    def test_prepare(self):
        """Test prepare"""
        tasks = [{
            'violations': [
                {'name': 'dummy', 'raw': 'test{}'.format(n)},
            ],
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
            ]
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
