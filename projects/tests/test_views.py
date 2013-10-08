import sure
from datetime import datetime
from testfixtures import LogCapture
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from tools.mongo import MongoFlushMixin
from tools.tests import MockGithubMixin
from tasks.models import Tasks
from tasks import const
from ..models import Project
from . import factories


class ManageProjectViewCase(TestCase):
    """Manage project view case"""

    def setUp(self):
        self.url = reverse('projects_manage')

    def test_authorised_ok(self):
        """Test status=200"""
        User.objects.create_user('test', 'test@test.test', 'test')
        self.client.login(
            username='test',
            password='test',
        )
        response = self.client.get(self.url)
        response.status_code.should.be.equal(200)


class ProjectViewCase(MockGithubMixin, TestCase):
    """Project view case"""

    def setUp(self):
        project = factories.ProjectFactory.create()
        self.url = reverse('projects_project', args=(project.name,))
        self.user = User.objects.create_user('test', 'test@test.test', 'test')
        super(ProjectViewCase, self).setUp()

    def test_ok(self):
        """Test status=200"""
        response = self.client.get(self.url)
        response.status_code.should.be.equal(200)

    def test_404_for_private_and_not_authenticated(self):
        """Test 404 for private and not authenticated"""
        project = factories.ProjectFactory(is_private=True)
        response = self.client.get(
            reverse('projects_project', args=(project.name,)),
        )
        response.status_code.should.be.equal(302)

    def test_404_for_private_and_not_owner(self):
        """Test 404 for private and not owner"""
        self.client.login(
            username='test',
            password='test',
        )
        project = factories.ProjectFactory(is_private=True)
        response = self.client.get(
            reverse('projects_project', args=(project.name,)),
        )
        response.status_code.should.be.equal(403)

    def test_ok_for_private_and_owner(self):
        """Test 200 for private and owner"""
        self.client.login(
            username='test',
            password='test',
        )
        project = factories.ProjectFactory(
            is_private=True,
            owner=self.user,
        )
        response = self.client.get(
            reverse('projects_project', args=(project.name,)),
        )
        response.status_code.should.be.equal(200)


class ProjectBadgeViewCase(MongoFlushMixin, TestCase):
    """Project badge view case"""
    mongo_flush = ['tasks']

    def _get_and_assert(self, slug, badge, query=''):
        """Preform get and assert"""
        response = self.client.get(
            reverse('projects_badge', args=(slug,)) + query,
        )
        response.status_code.should.be.equal(302)
        badge.should.be.within(response['Location'])

    def test_unknown_because_project_not_exists(self):
        """Test redirect to unknown badge if project not exists"""
        self._get_and_assert('test111', 'unknown')

    def test_unknown_because_no_tasks_preformed(self):
        """Test unknown because not tasks performed"""
        project = factories.ProjectFactory.create()
        self._get_and_assert(project.name, 'unknown')

    def test_unknown_because_last_task_not_finished(self):
        """Test unknown because not tasks performed"""
        project = factories.ProjectFactory.create()
        Tasks.insert([{
            'created': datetime(2010, 10, 10),
            'status': const.STATUS_SUCCESS,
            'project': project.name,
        }, {
            'created': datetime(2011, 11, 11),
            'status': const.STATUS_NEW,
            'project': project.name,
        }])
        self._get_and_assert(project.name, 'unknown')

    def test_success(self):
        """Test redirect to success badge"""
        project = factories.ProjectFactory.create()
        Tasks.insert({
            'created': datetime(2010, 10, 10),
            'status': const.STATUS_SUCCESS,
            'project': project.name,
        })
        self._get_and_assert(project.name, 'success')

    def test_fail(self):
        """Test redirect to fail badge"""
        project = factories.ProjectFactory.create()
        Tasks.insert({
            'created': datetime(2010, 10, 10),
            'status': const.STATUS_FAILED,
            'project': project.name,
        })
        self._get_and_assert(project.name, 'fail')

    def test_get_badge_with_filtering(self):
        """Test get badge with filtering"""
        project = factories.ProjectFactory.create()
        Tasks.save({
            'status': const.STATUS_SUCCESS,
            'project': project.name,
            'commit': {'branch': 'test'}
        })
        self._get_and_assert(project.name, 'success', '?branch=test')


class RegenerateTokenViewCase(TestCase):
    """Regenerate token view case"""

    def setUp(self):
        self._create_user()
        self.project = factories.ProjectFactory(owner=self.user)
        self.url = reverse('projects_regenerate')

    def _create_user(self):
        """Create user and authorise"""
        self.user = User.objects.create_user('test', 'test@test.test', 'test')
        self.client.login(
            username='test',
            password='test',
        )

    def test_not_valid(self):
        """Test not valid data"""
        with LogCapture() as log_capture:
            response = self.client.post(self.url, {})
            list(log_capture.actual())[0].should.contain('WARNING')
        response.status_code.should.be.equal(302)

    def test_valid(self):
        """Test valid"""
        response = self.client.post(self.url, {
            'project': self.project.id,
        })
        response.status_code.should.be.equal(302)
        self.project.token.should_not.be.equal(
            Project.objects.get(id=self.project.id).token,
        )
