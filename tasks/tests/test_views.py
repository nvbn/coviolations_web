import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from projects.tests.factories import BranchFactory
from .. import models


class CreateTaskViewCase(TestCase):
    """Create task view case"""

    def setUp(self):
        self.url = reverse('tasks_create')
        BranchFactory(project__name='test', name='develop')

    def test_create_on_post(self):
        """Test create on post"""
        response = self.client.post(self.url, data=json.dumps({
            'service': 'dummy',
            'project': 'test',
            'branch': 'develop',
            'commit': 'asdfg',
            'violations': [
                {'name': 'dummy', 'data': '1'},
            ]
        }), content_type='application/json')
        data = json.loads(response.content)
        self.assertTrue(data['ok'])
        self.assertEqual(1, models.Task.objects.count())

    def test_error_on_wrong_service(self):
        """Test error on wrong service"""
        response = self.client.post(self.url, data=json.dumps({
            'service': 'dummy!!!',
            'project': 'test',
            'branch': 'develop',
            'commit': 'asdfg',
            'violations': [
                {'name': 'dummy', 'data': '1'},
            ]
        }), content_type='application/json')
        data = json.loads(response.content)
        self.assertFalse(data['ok'])
