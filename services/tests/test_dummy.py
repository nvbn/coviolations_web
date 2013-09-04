from django.test import TestCase
from projects.tests.factories import BranchFactory
from projects.models import Commit
from tasks.models import Violation, Task
from ..dummy import dummy_service


class DummyServiceCase(TestCase):
    """Dummy service case"""

    def setUp(self):
        BranchFactory(project__name='test', name='develop')
        dummy_service({
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
        self.assertEqual(Commit.objects.get().name, 'asdfg')

    def test_create_task(self):
        """Test create task"""
        self.assertEqual(Task.objects.count(), 1)

    def test_create_violations(self):
        """Test create violations"""
        self.assertEqual(Violation.objects.count(), 2)
