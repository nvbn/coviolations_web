from django.test import TestCase
from django.core.urlresolvers import reverse
from tools.mongo import MongoFlushMixin
from ..models import Tasks


class DetailTaskViewCase(MongoFlushMixin, TestCase):
    """Detail task view"""

    def setUp(self):
        MongoFlushMixin.setUp(self)
        task_id = Tasks.insert({})
        self.url = reverse('tasks_detail', args=(str(task_id),))

    def test_ok(self):
        """Test status=200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
