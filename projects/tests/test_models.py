from django.test import TestCase
from django.contrib.auth.models import User
from accounts.tests.factories import UserFactory
from tools.mongo import MongoFlushMixin
from tasks.models import Tasks
from .. import models
from . import factories
from .base import MockGithubMixin


class ProjectManagerCase(MockGithubMixin, TestCase):
    """Project manager case"""

    def setUp(self):
        super(ProjectManagerCase, self).setUp()
        self.user = User.objects.create_user('user')

    def test_create(self):
        """Test create"""
        User.github.get_user.return_value.get_repos.return_value =\
            map(self._create_repo, range(10))
        projects = models.Project.objects.get_or_create_for_user(self.user)
        self.assertEqual(projects.count(), 10)

    def test_get(self):
        """Test get without creating new"""
        for n in range(10):
            factories.ProjectFactory(
                owner=self.user, url='http://test{}.com'.format(n),
                name='project {}'.format(n)
            )
        User.github.get_user.return_value.get_repos.return_value =\
            map(self._create_repo, range(10))
        User.github.get_user.return_value.get_repos.get_orgs = []
        projects = models.Project.objects.get_or_create_for_user(self.user)
        self.assertEqual(projects.count(), 10)

    def test_get_enabled_for_user(self):
        """"Test get enabled for user"""
        enabled = factories.ProjectFactory.create_batch(
            10, owner=self.user, is_enabled=True,
        )
        factories.ProjectFactory.create_batch(
            30, owner=self.user, is_enabled=False,
        )
        self.assertItemsEqual(
            enabled, models.Project.objects.get_enabled_for_user(self.user),
        )

    def test_get_for_user_in_organization(self):
        """Test get for user in organization"""
        organization = factories.OrganizationFactory(users=[self.user])
        factories.ProjectFactory.create_batch(10)
        projects = factories.ProjectFactory.create_batch(
            10, organization=organization,
        )
        self.assertItemsEqual(
            projects, models.Project.objects.get_for_user(self.user),
        )


class ProjectModelCase(MongoFlushMixin, TestCase):
    """Project model case"""
    mongo_flush = ['tasks']

    def test_project_branches(self):
        """Test getting project branches"""
        project = factories.ProjectFactory()
        Tasks.insert([{'project': project.name, 'commit': {
            'branch': 'master',
        }}, {'project': project.name, 'commit': {
            'branch': 'develop',
        }}, {'project': project.name, 'commit': {
            'branch': 'master',
        }}, {'project': project.name, 'commit': {
            'branch': 'develop',
        }}])
        self.assertItemsEqual(project.branches, ['master', 'develop'])

    def test_owner_can_access(self):
        """Test owner can access project"""
        project = factories.ProjectFactory()
        self.assertTrue(project.can_access(project.owner))

    def test_organization_member_can_access(self):
        """Test organization member can access project"""
        project = factories.ProjectFactory()
        self.assertTrue(project.can_access(
            project.organization.users.all()[0],
        ))

    def test_other_user_cant_access(self):
        """Test other user can't access"""
        project = factories.ProjectFactory(is_private=True)
        user = UserFactory()
        self.assertFalse(project.can_access(user))

    def test_get_allowed_users_only_owner(self):
        """Test get allowed users only owner"""
        project = factories.ProjectFactory(
            organization=None, is_private=True,
        )
        self.assertItemsEqual(
            project.get_allowed_users(), [project.owner],
        )

    def test_get_allowed_users_with_organization(self):
        """Test get allowed users with organization"""
        project = factories.ProjectFactory(is_private=True)
        self.assertItemsEqual(
            project.get_allowed_users(),
            [project.owner] + list(project.organization.users.all()),
        )


class OrganizationManagerCase(TestCase):
    """Organization manager case"""

    def setUp(self):
        self.user = User.objects.create_user('user')

    def test_create_and_add_user(self):
        """Test create and add user"""
        organization =\
            models.Organization.objects.get_with_user('test', self.user)
        self.assertEqual(organization.users.count(), 1)
        self.assertEqual(models.Organization.objects.count(), 1)

    def test_create_with_exists_user(self):
        """Test create with exists user"""
        factories.OrganizationFactory(
            name='test', users=[self.user],
        )
        organization =\
            models.Organization.objects.get_with_user('test', self.user)
        self.assertItemsEqual(organization.users.all(), [self.user])
        self.assertEqual(models.Organization.objects.count(), 1)

    def test_add_user_to_exists(self):
        """Test add user to exists"""
        factories.OrganizationFactory(
            name='test', users=[self.user],
        )
        user = UserFactory()
        organization =\
            models.Organization.objects.get_with_user('test', user)
        self.assertItemsEqual(organization.users.all(), [self.user, user])
