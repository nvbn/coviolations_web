import sure
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from tools.tests import MockGithubMixin
from .. import models
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
        response.status_code.should.be.equal(200)
        self.deserialize(response)['meta']['total_count'].should.be.equal(10)

    def test_read_self(self):
        """Test read self"""
        project = factories.ProjectFactory.create(owner=self.user)
        response = self.api_client.get('{}{}/'.format(self.url, project.name))
        response.status_code.should.be.equal(200)

    def test_read_other(self):
        """Test read other"""
        project = factories.ProjectFactory.create()
        response = self.api_client.get('{}{}/'.format(self.url, project.name))
        response.status_code.should.be.equal(200)

    def test_read_other_private(self):
        """Test read other private project"""
        project = factories.ProjectFactory.create(is_private=True)
        response = self.api_client.get('{}{}/'.format(self.url, project.name))
        response.status_code.should.be.equal(401)

    def test_update_is_enabled(self):
        """Test update is_enabled"""
        project = factories.ProjectFactory.create(owner=self.user)
        response = self.api_client.put(
            '{}{}/'.format(self.url, project.name), data={
                'is_enabled': True,
            },
        )
        response.status_code.should.be.within([202, 204])
        models.Project.objects.get().is_enabled.should.be.true

    def test_not_update_name(self):
        """Test not update name"""
        project = factories.ProjectFactory.create(
            owner=self.user, name='test',
        )
        response = self.api_client.put(
            '{}{}/'.format(self.url, project.name), data={
                'name': 'nope',
            },
        )
        response.status_code.should.be.within([202, 204])
        models.Project.objects.get().name.should.be.equal('test')

    def test_not_update_url(self):
        """Test not update url"""
        project = factories.ProjectFactory.create(
            owner=self.user, url='http://test.test',
        )
        response = self.api_client.put(
            '{}{}/'.format(self.url, project.name), data={
                'url': 'http://nope.nope/',
            },
        )
        response.status_code.should.be.within([202, 204])
        models.Project.objects.get().url.should.be.equal('http://test.test')

    def test_get_enabled(self):
        """Test get enabled"""
        factories.ProjectFactory.create_batch(
            10, owner=self.user, is_enabled=True,
        )
        factories.ProjectFactory.create_batch(
            30, owner=self.user, is_enabled=False,
        )
        response = self.api_client.get('{}'.format(self.url))
        response.status_code.should.be.equal(200)
        self.deserialize(response)['meta']['total_count'].should.be.equal(10)

    def test_has_token_if_owner(self):
        """Test has token if owner"""
        project = factories.ProjectFactory(owner=self.user)
        response = self.api_client.get('{}{}/'.format(
            self.url,
            project.name,
        ))
        response.status_code.should.be.equal(200)
        self.deserialize(response)['token'].should.be.equal(project.token)

    def test_blank_token_if_not_owner(self):
        """Test has blank token if owner"""
        project = factories.ProjectFactory()
        response = self.api_client.get('{}{}/'.format(
            self.url,
            project.name,
        ))
        response.status_code.should.be.equal(200)
        self.deserialize(response)['token'].should.be.equal('')

    def test_regenerate_token(self):
        """Test regenerate token"""
        project = factories.ProjectFactory(owner=self.user)
        self.api_client.put('{}{}/'.format(
            self.url,
            project.name,
        ), data={'token': None})
        updated = models.Project.objects.get(id=project.id)
        updated.token.should_not.be.equal(project.token)

    def test_attach_success_percent(self):
        """Test attach success percent"""
        project = factories.ProjectFactory(owner=self.user)
        response = self.api_client.get(
            '{}{}/?with_success_percent=true'.format(self.url, project.name),
        )
        self.deserialize(response)['success_percents'].should.be.equal([])
