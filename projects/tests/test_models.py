from django.test import TestCase
from django.contrib.auth.models import User
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
        models.ProjectManager._get_remote_projects.return_value =\
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
        models.ProjectManager._get_remote_projects.return_value =\
            map(self._create_repo, range(10))
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
