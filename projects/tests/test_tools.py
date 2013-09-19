from mock import MagicMock
from django.test import TestCase
from accounts.tests.factories import UserFactory
from ..utils import ProjectAccessMixin
from ..models import Project
from . import factories


class ProjectAccessMixinCase(TestCase):
    """Project access mixin case"""

    def setUp(self):
        self._orig_can_access = Project.can_access
        Project.can_access = MagicMock()
        self._orig_update = Project.objects.update_user_projects
        Project.objects.update_user_projects = MagicMock()
        self.mixin = ProjectAccessMixin()
        self.project = factories.ProjectFactory()
        self.user = UserFactory()

    def tearDown(self):
        Project.can_access = self._orig_can_access
        Project.objects.update_user_projects = self._orig_update

    def test_can_access(self):
        """Test can access"""
        Project.can_access.return_value = True
        self.assertTrue(self.project.can_access(self.user))

    def test_call_update_if_organization(self):
        """Test call update if organization"""
        Project.can_access.return_value = False
        self.assertFalse(self.project.can_access(self.user))
        Project.objects.update_user_projects.asset_called_once_with(
            self.user,
        )
