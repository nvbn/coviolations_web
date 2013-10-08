import sure
from mock import MagicMock
from django.core.exceptions import PermissionDenied
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
        self.mixin.get_project = MagicMock(return_value=self.project)
        self.user = UserFactory()

    def tearDown(self):
        Project.can_access = self._orig_can_access
        Project.objects.update_user_projects = self._orig_update

    def test_can_access(self):
        """Test can access"""
        Project.can_access.return_value = True
        self.mixin.check_can_access(
            MagicMock(user=self.user),
        ).should.be.none

    def test_call_update_if_organization(self):
        """Test call update if organization"""
        Project.can_access.return_value = False
        self.mixin.check_can_access.when\
            .called_with(MagicMock(user=self.user))\
            .should.throw(PermissionDenied)
        Project.objects.update_user_projects.asset_called_once_with(
            self.user,
        )
