from django.test import TestCase
from projects.tests.factories import ProjectFactory
from tasks.models import Tasks
from tools.mongo import MongoFlushMixin
from ..dummy import dummy_service


class DummyServiceCase(MongoFlushMixin, TestCase):
    """Dummy service case"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(DummyServiceCase, self).setUp()
        ProjectFactory(name='test')
        dummy_service({
            'project': 'test',
            'branch': 'develop',
            'commit': 'asdfg',
            'violations': [
                {'name': 'dummy', 'data': '1'},
                {'name': 'dummy', 'data': '2'},
            ]
        })

    def test_create_task(self):
        """Test create task"""
        self.assertEqual(Tasks.count(), 1)
