from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from .. import models
from .base import MockGithubMixin
from . import factories


class ProjectsResourceCase(MockGithubMixin, ResourceTestCase):
    """User projects resources case"""

    def setUp(self):
        MockGithubMixin.setUp(self)
        ResourceTestCase.setUp(self)
        self.user = User.objects.create_user(
            'test', 'test@test.test', 'test',
        )
        self.api_client.client.login(
            username='test',
            password='test',
        )
        self.url = '/api/v1/projects/project/'

    def test_read_list(self):
        """Test read list"""
        User.github.get_user.return_value.get_repos.return_value =\
            map(self._create_repo, range(10))
        response = self.api_client.get('{}?fetch=true'.format(self.url))
        self.assertHttpOK(response)
        self.assertEqual(self.deserialize(response)['meta']['total_count'], 10)

    def test_read_self(self):
        """Test read self"""
        project = factories.ProjectFactory.create(owner=self.user)
        response = self.api_client.get('{}{}/'.format(self.url, project.id))
        self.assertHttpOK(response)

    def test_read_other(self):
        """Test read self"""
        project = factories.ProjectFactory.create()
        response = self.api_client.get('{}{}/'.format(self.url, project.id))
        self.assertHttpUnauthorized(response)

    def test_update_is_enabled(self):
        """Test update is_enabled"""
        project = factories.ProjectFactory.create(owner=self.user)
        response = self.api_client.put(
            '{}{}/'.format(self.url, project.id), data={
                'is_enabled': True,
            },
        )
        self.assertHttpAccepted(response)
        self.assertTrue(models.Project.objects.get().is_enabled)

    def test_not_update_name(self):
        """Test not update name"""
        project = factories.ProjectFactory.create(
            owner=self.user, name='test',
        )
        response = self.api_client.put(
            '{}{}/'.format(self.url, project.id), data={
                'name': 'nope',
            },
        )
        self.assertHttpAccepted(response)
        self.assertEqual(
            models.Project.objects.get().name, 'test',
        )

    def test_not_update_url(self):
        """Test not update url"""
        project = factories.ProjectFactory.create(
            owner=self.user, url='http://test.test',
        )
        response = self.api_client.put(
            '{}{}/'.format(self.url, project.id), data={
                'url': 'http://nope.nope/',
            },
        )
        self.assertHttpAccepted(response)
        self.assertEqual(
            models.Project.objects.get().url, 'http://test.test',
        )

    def test_get_enabled(self):
        """Test get enabled"""
        factories.ProjectFactory.create_batch(
            10, owner=self.user, is_enabled=True,
        )
        factories.ProjectFactory.create_batch(
            30, owner=self.user, is_enabled=False,
        )
        response = self.api_client.get('{}'.format(self.url))
        self.assertHttpOK(response)
        self.assertEqual(self.deserialize(response)['meta']['total_count'], 10)
