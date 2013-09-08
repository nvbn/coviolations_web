import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from tastypie.test import ResourceTestCase
from projects.tests.factories import ProjectFactory
from tools.mongo import MongoFlushMixin
from .. import models


class BaseTaskResourceCase(MongoFlushMixin, ResourceTestCase):
    """Base task resource case"""
    mongo_flush = ['tasks']

    def setUp(self):
        MongoFlushMixin.setUp(self)
        ResourceTestCase.setUp(self)

        self.url = '/api/v1/tasks/'
        ProjectFactory(name='test', is_enabled=True)


class PostTaskResourceCase(BaseTaskResourceCase):
    """Create task case"""

    def test_create_on_post(self):
        """Test create on post"""
        self.api_client.post(self.url, data={
            'service': {
                'name': 'dummy',
            },
            'project': 'test',
            'commit': {
                'branch': 'develop',
                'commit': 'asdfg',
                'author': 'nvbn',
            },
            'violations': [
                {'name': 'dummy', 'raw': '1'},
            ]
        })
        self.assertEqual(1, models.Tasks.count())

    def test_error_on_wrong_service(self):
        """Test error on wrong service"""
        response = self.api_client.post(self.url, data={
            'service': {
                'name': 'dummy!!!',
            },
            'project': 'test',
            'commit': {
                'branch': 'develop',
                'commit': 'asdfg',
                'author': 'nvbn',
            },
            'violations': [
                {'name': 'dummy', 'raw': '1'},
            ]
        })
        self.assertEqual(response.status_code, 404)


class GetTaskResourceCase(BaseTaskResourceCase):
    """Get tasks resource case"""

    def _create_tasks(self, project='test', count=20):
        """Create tasks"""
        models.Tasks.insert([{
            'service': {
                'name': 'dummy',
            },
            'project': project,
            'commit': {
                'branch': 'develop',
                'commit': 'asdfg',
                'author': 'nvbn',
            },
            'violations': [{
                'name': 'dummy',
                'raw': '1',
                'status': 1,
                'prepared': '123{}'.format(n),
            }]
        } for n in range(count)])

    def test_get_all(self):
        """Test get all"""
        self._create_tasks()
        response = self.api_client.get(self.url)
        data = self.deserialize(response)
        self.assertEqual(data['meta']['total_count'], 20)
        self.assertIsNone(data['objects'][0]['violations'])

    def test_get_all_with_violations(self):
        """Test get all with violations"""
        self._create_tasks()
        response = self.api_client.get('{}?with_violations=1'.format(self.url))
        data = self.deserialize(response)
        self.assert_(data['objects'][0]['violations'][0]['name'])
        self.assert_(data['objects'][0]['violations'][0]['status'])

    def test_get_with_full_violations(self):
        """Test get with full violations"""
        self._create_tasks()
        response = self.api_client.get(
            '{}?with_full_violations=1'.format(self.url),
        )
        data = self.deserialize(response)
        self.assert_(data['objects'][0]['violations'][0]['raw'])
        self.assert_(data['objects'][0]['violations'][0]['prepared'])

    def test_filter_by_project(self):
        """Test filter by project"""
        self._create_tasks('test', 5)
        self._create_tasks('nope', 10)
        response = self.api_client.get('{}?project=test'.format(self.url))
        data = self.deserialize(response)
        self.assertEqual(data['meta']['total_count'], 5)
