import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from tastypie.test import ResourceTestCase
from projects.tests.factories import ProjectFactory
from tools.mongo import MongoFlushMixin
from .. import models


class CreateTaskViewCase(MongoFlushMixin, ResourceTestCase):
    """Create task view case"""
    mongo_flush = ['tasks']

    def setUp(self):
        MongoFlushMixin.setUp(self)
        ResourceTestCase.setUp(self)

        self.url = '/api/v1/tasks/'
        ProjectFactory(name='test')

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
            'branch': 'develop',
            'commit': 'asdfg',
            'violations': [
                {'name': 'dummy', 'raw': '1'},
            ]
        })
        self.assertEqual(response.status_code, 404)
