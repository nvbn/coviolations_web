from testfixtures import LogCapture
from django.test import TestCase
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
