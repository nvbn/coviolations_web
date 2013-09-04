from mock import MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from .. import models
from . import factories
from .base import MockGithubMixin


class RelationsCase(TestCase):
    """Relations case"""

    def test_project_branch_relations(self):
        """Test project - branch relations"""
        project = factories.ProjectFactory()
        factories.BranchFactory.create_batch(10, project=project)
        self.assertEqual(project.branches.count(), 10)

    def test_branch_commit_relations(self):
        """Test branch - commit relations"""
        branch = factories.BranchFactory()
        factories.CommitFactory.create_batch(10, branch=branch)
        self.assertEqual(branch.commits.count(), 10)


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
        factories.ProjectFactory.create_batch(10, owner=self.user)
        models.ProjectManager._get_remote_projects.return_value =\
            map(self._create_repo, range(1, 11))
        projects = models.Project.objects.get_or_create_for_user(self.user)
        self.assertEqual(projects.count(), 10)
