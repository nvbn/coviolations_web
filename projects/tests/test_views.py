import sure
from datetime import datetime
from django.test import TestCase
from django.core.urlresolvers import reverse
from tools.mongo import MongoFlushMixin
from tasks.models import Tasks
from tasks import const
from . import factories


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
