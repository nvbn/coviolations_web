from mock import MagicMock
from django.test import TestCase
from django_rq import get_worker
from projects.tests.factories import BranchFactory
from .. import jobs, models


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
