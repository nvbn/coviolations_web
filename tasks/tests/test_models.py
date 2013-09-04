from testfixtures import LogCapture
from django.test import TestCase
from projects.models import Commit
from projects.tests.factories import BranchFactory
from tasks.models import Violation, Task
from .. import const
from . import factories


class RelationsCase(TestCase):
    """Models relations case"""

    def test_task_violation(self):
        """Test task - violation relation"""
        task = factories.TaskFactory()
        factories.ViolationFactory.create_batch(10, task=task)
        self.assertEqual(task.violations.count(), 10)


class ViolationModelCase(TestCase):
    """Violation model case"""

    def test_prepare(self):
        """Test prepare"""
        violation = factories.ViolationFactory(
            violation='dummy',
            raw_data='test',
        )
        violation.prepare()
        self.assertEqual(violation.raw_data, violation.prepared_data)
        self.assertEqual(violation.status, const.STATUS_SUCCESS)

    def test_fail_on_prepare(self):
        """Test fail on prepare"""
        violation = factories.ViolationFactory(
            violation='dummy!!!',
            raw_data='test',
        )
        with LogCapture(const.LOGGER) as log_capture:
            violation.prepare()
            log_capture.check((
                const.LOGGER, 'WARNING', 'Prepare violation failed',
            ))
        self.assertEqual(violation.status, const.STATUS_FAILED)


class TaskManagerCase(TestCase):
    """Task manager  case"""

    def _create_task(self):
        BranchFactory(project__name='test', name='develop')
        Task.objects.create_task({
            'project': 'test',
            'branch': 'develop',
            'commit': 'asdfg',
            'violations': [
                {'name': 'dummy', 'data': '1'},
                {'name': 'dummy', 'data': '2'},
            ]
        })

    def test_create_commit(self):
        """Test create commit"""
        self._create_task()
        self.assertEqual(Commit.objects.get().name, 'asdfg')

    def test_create_task(self):
        """Test create task"""
        self._create_task()
        self.assertEqual(Task.objects.count(), 1)

    def test_create_violations(self):
        """Test create violations"""
        self._create_task()
        self.assertEqual(Violation.objects.count(), 2)

