from mock import MagicMock
from django.test import TestCase
from django_rq import get_worker
from projects.tests.factories import BranchFactory
from .. import jobs, models, const
from . import factories


class CreateTaskJobCase(TestCase):
    """Create task job case"""

    def setUp(self):
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
        BranchFactory(project__name='test', name='develop')
        jobs.create_task('dummy', {
            'project': 'test',
            'branch': 'develop',
            'commit': 'asdfg',
            'violations': [
                {'name': 'dummy', 'data': '1'},
            ]
        })
        get_worker().work(burst=True)

    def test_create(self):
        """Test create"""
        self.assertEqual(models.Task.objects.count(), 1)

    def test_propagating(self):
        """Test propagating to prepare violations"""
        task = models.Task.objects.get()
        jobs.prepare_violations.assert_called_once_with(task)


class PrepareViolationsJobCase(TestCase):
    """Prepare violations job case"""

    def test_prepare(self):
        """Test prepare"""
        task = factories.TaskFactory.create()
        factories.ViolationFactory.create_batch(
            10, task=task, violation='dummy',
        )
        jobs.prepare_violations(task)
        get_worker().work(burst=True)
        self.assertEqual(models.Violation.objects.filter(
            status=const.STATUS_SUCCESS,
        ).count(), 10)

    def test_not_fail_all(self):
        """Not fail all if fail one"""
        task = factories.TaskFactory.create()
        factories.ViolationFactory.create_batch(
            7, task=task, violation='dummy',
        )
        factories.ViolationFactory.create_batch(
            3, task=task, violation='dummy!!!',
        )
        jobs.prepare_violations(task)
        get_worker().work(burst=True)
        self.assertEqual(models.Violation.objects.filter(
            status=const.STATUS_SUCCESS,
        ).count(), 7)
        self.assertEqual(models.Violation.objects.filter(
            status=const.STATUS_FAILED,
        ).count(), 3)
