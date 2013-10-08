from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from projects.tests.factories import ProjectFactory
from tools.mongo import MongoFlushMixin
from .. import models
from ..const import STATUS_SUCCESS


class BaseTaskResourceCase(MongoFlushMixin, ResourceTestCase):
    """Base task resource case"""
    mongo_flush = ['tasks']

    def setUp(self):
        MongoFlushMixin.setUp(self)
        ResourceTestCase.setUp(self)

        ProjectFactory(name='test', is_enabled=True)


class RawTaskResourceCase(BaseTaskResourceCase):
    """Create task case"""

    def setUp(self):
        super(RawTaskResourceCase, self).setUp()
        self.url = '/api/v1/tasks/raw/'

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

    def test_error_on_wrong_project(self):
        """Test error on wrong project"""
        response = self.api_client.post(self.url, data={
            'service': {
                'name': 'dummy',
            },
            'project': 'test!!',
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


class TaskResourceCase(BaseTaskResourceCase):
    """Get tasks resource case"""

    def setUp(self):
        super(TaskResourceCase, self).setUp()
        self.url = '/api/v1/tasks/task/'

    def _create_tasks(self, project='test', count=20, **kwargs):
        """Create tasks"""
        models.Tasks.insert([dict(
            service={
                'name': 'dummy',
            },
            project=project,
            status=STATUS_SUCCESS,
            commit={
                'branch': 'develop',
                'commit': 'asdfg',
                'author': 'nvbn',
            },
            violations=[{
                'name': 'dummy',
                'raw': '1',
                'status': 1,
                'prepared': '123{}'.format(n),
            }],
            **kwargs
        ) for n in range(count)])

    def _create_user(self):
        """Create user"""
        user = User.objects.create_user('test', 'test@test.test', 'test')
        self.api_client.client.login(
            username='test',
            password='test',
        )
        return user

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

    def test_owner_access_private(self):
        """Test owner access private"""
        user = self._create_user()
        ProjectFactory(owner=user, is_private=True, name='test')
        self._create_tasks(is_private=True, allowed_users=[user.id])
        response = self.api_client.get(self.url)
        data = self.deserialize(response)
        self.assertEqual(data['meta']['total_count'], 20)

    def test_organization_member_access_private(self):
        """Test organization member access private"""
        user = self._create_user()
        project = ProjectFactory(
            owner=user, is_private=True,
            name='test', organization__users=[user],
        )
        self._create_tasks(
            is_private=True, organization=project.organization.id,
        )
        response = self.api_client.get(self.url)
        data = self.deserialize(response)
        self.assertEqual(data['meta']['total_count'], 20)

    def test_other_user_cant_access_private(self):
        """Test other user cant access private"""
        user = self._create_user()
        ProjectFactory(
            owner=user, is_private=True, name='test',
        )
        self._create_tasks(is_private=True)
        response = self.api_client.get(self.url)
        data = self.deserialize(response)
        self.assertEqual(data['meta']['total_count'], 0)
