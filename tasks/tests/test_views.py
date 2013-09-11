from mock import MagicMock
from django.test import TestCase
from django.core.urlresolvers import reverse
from tools.mongo import MongoFlushMixin
from ..models import Tasks
from ..views import TaskViewMixin


class BaseTaskViewCase(MongoFlushMixin, TestCase):
    """Base task view case"""
    mongo_flush = ['tasks']

    def setUp(self):
        MongoFlushMixin.setUp(self)
        self._orig_get_project = TaskViewMixin.get_project
        TaskViewMixin.get_project = MagicMock()

    def tearDown(self):
        TaskViewMixin.get_project = self._orig_get_project


class DetailTaskViewCase(BaseTaskViewCase):
    """Detail task view"""

    def setUp(self):
        super(DetailTaskViewCase, self).setUp()
        task_id = Tasks.insert({})
        self.url = reverse('tasks_detail', args=(str(task_id),))

    def test_ok(self):
        """Test status=200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class RawViolationViewCase(BaseTaskViewCase):
    """Raw violation view"""

    def setUp(self):
        super(RawViolationViewCase, self).setUp()
        task_id = Tasks.insert({
            'violations': [
                {'raw': ''},
            ],
        })
        self.url = reverse('tasks_raw', args=(str(task_id), 0))

    def test_ok(self):
        """Test status=200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
