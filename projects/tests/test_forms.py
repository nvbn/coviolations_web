import sure
from django.test import TestCase
from django.contrib.auth.models import User
from tools.mongo import MongoFlushMixin
from tasks.exceptions import TaskDoesNotExists
from tasks.models import Tasks
from tasks.const import STATUS_SUCCESS, STATUS_FAILED
from ..forms import RegenerateTokenForm, FindTaskForBadgeForm
from . import factories


class RegenerateTokenFormCase(TestCase):
    """Regenerate token form case"""

    def setUp(self):
        self.user = User.objects.create_user('test')

    def test_valid_with_self(self):
        """Test valid with self owner"""
        project = factories.ProjectFactory(owner=self.user)
        form = RegenerateTokenForm(self.user, {
            'project': project.id,
        })
        form.is_valid().should.be.true

    def test_invalid_with_other_user(self):
        """Test invalid with other user"""
        project = factories.ProjectFactory()
        form = RegenerateTokenForm(self.user, {
            'project': project.id,
        })
        form.is_valid().should.be.false

    def test_regenerating(self):
        """Test regenerating"""
        project = factories.ProjectFactory(owner=self.user)
        initial_token = project.token
        form = RegenerateTokenForm(self.user, {
            'project': project.id,
        })
        form.is_valid().should.be.true
        initial_token.should_not.be.equal(form.save().token)


class FindTaskForBadgeFormCase(MongoFlushMixin, TestCase):
    """Find task for badge form case"""
    mongo_flush = ['tasks']

    def setUp(self):
        super(FindTaskForBadgeFormCase, self).setUp()
        self.project = factories.ProjectFactory()

    def _get_form(self, **kwargs):
        defaults = {
            'project': self.project.name,
        }
        defaults.update(kwargs)
        form = FindTaskForBadgeForm(defaults)
        form.is_valid().should.be.true
        return form

    def _create_task(self, **kwargs):
        defaults = {
            'project': self.project.name,
            'status': STATUS_SUCCESS,
        }
        defaults.update(kwargs)
        return Tasks.save(defaults)

    def test_task_not_found(self):
        """Test task not found"""
        form = self._get_form()
        form.get_task.when.called_with().should.throw(TaskDoesNotExists)

    def test_find_by_project(self):
        """Test find by project"""
        self._create_task()
        form = self._get_form()
        form.get_task()['status'].should.be.equal(STATUS_SUCCESS)

    def test_find_by_commit(self):
        """Test find by commit"""
        self._create_task(status=STATUS_FAILED, commit={'hash': 'test'})
        for n in range(10):
            self._create_task(commit={'hash': 'test{}'.format(n)})
        form = self._get_form(commit='test')
        form.get_task()['status'].should.be.equal(STATUS_FAILED)

    def test_find_by_branch(self):
        """Test find by branch"""
        self._create_task(status=STATUS_FAILED, commit={'branch': 'test'})
        for n in range(10):
            self._create_task(commit={'branch': 'test{}'.format(n)})
        form = self._get_form(branch='test')
        form.get_task()['status'].should.be.equal(STATUS_FAILED)
