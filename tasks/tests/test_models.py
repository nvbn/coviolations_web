from django.test import TestCase
from . import factories


class RelationsCase(TestCase):
    """Models relations case"""

    def test_task_violation(self):
        """Test task - violation relation"""
        task = factories.TaskFactory()
        factories.ViolationFactory.create_batch(10, task=task)
        self.assertEqual(task.violations.count(), 10)
