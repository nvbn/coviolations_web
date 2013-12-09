import sure
from datetime import timedelta, datetime
from mock import MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from accounts.tests.factories import UserFactory
from tools.mongo import MongoFlushMixin
from tools.tests import MockGithubMixin
from tasks.models import Tasks
from tasks.exceptions import TaskDoesNotExists
from tasks.const import STATUS_SUCCESS
from .. import models
from . import factories


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
        projects.count().should.be.equal(10)

    def test_get(self):
        """Test get without creating new"""
        for n in range(10):
            factories.ProjectFactory(
                owner=self.user, url='http://test{}.com'.format(n),
                name='project {}'.format(n),
            )
        User.github.get_user.return_value.get_repos.return_value =\
            map(self._create_repo, range(10))
        User.github.get_user.return_value.get_repos.get_orgs = []
        projects = models.Project.objects.get_or_create_for_user(self.user)
        projects.count().should.be.equal(10)

    def test_get_enabled_for_user(self):
        """"Test get enabled for user"""
        enabled = factories.ProjectFactory.create_batch(
            10, owner=self.user, is_enabled=True,
        )
        factories.ProjectFactory.create_batch(
            30, owner=self.user, is_enabled=False,
        )
        set(enabled).should.be.equal(
            set(models.Project.objects.get_enabled_for_user(self.user)),
        )

    def test_get_for_user_in_organization(self):
        """Test get for user in organization"""
        organization = factories.OrganizationFactory(users=[self.user])
        factories.ProjectFactory.create_batch(10)
        projects = factories.ProjectFactory.create_batch(
            10, organization=organization,
        )
        set(projects).should.be.equal(
            set(models.Project.objects.get_for_user(self.user)),
        )

    def test_get_with_owner(self):
        """Test get projects with github owner"""
        projects = factories.ProjectFactory.create_batch(
            5, name='cat/dog', is_enabled=True,
        )
        factories.ProjectFactory.create_batch(
            5, name='test/dog', is_enabled=True,
        )
        set(projects).should.be.equal(
            set(models.Project.objects.get_with_owner('cat')),
        )


class ProjectModelCase(MongoFlushMixin, TestCase):
    """Project model case"""
    mongo_flush = [
        'tasks', 'week_statistic', 'day_time_statistic', 'quality_game',
    ]

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
        set(project.branches).should.be.equal({'master', 'develop'})

    def test_owner_can_access(self):
        """Test owner can access project"""
        project = factories.ProjectFactory()
        project.can_access(project.owner).should.be.true

    def test_organization_member_can_access(self):
        """Test organization member can access project"""
        project = factories.ProjectFactory()
        project.can_access(
            project.organization.users.all()[0],
        ).should.be.true

    def test_other_user_cant_access(self):
        """Test other user can't access"""
        project = factories.ProjectFactory(is_private=True)
        user = UserFactory()
        project.can_access(user).should.be.false

    def test_get_allowed_users_only_owner(self):
        """Test get allowed users only owner"""
        project = factories.ProjectFactory(
            organization=None, is_private=True,
        )
        set(project.get_allowed_users()).should.be.equal({project.owner})

    def test_get_allowed_users_with_organization(self):
        """Test get allowed users with organization"""
        project = factories.ProjectFactory(is_private=True)
        set(project.get_allowed_users()).should.be.equal(
            set([project.owner] + list(project.organization.users.all())),
        )

    def test_owner_can_change(self):
        """Test owner can change project"""
        project = factories.ProjectFactory()
        project.can_change(project.owner).should.be.true

    def test_third_user_cant_change(self):
        """Test third user can't change project"""
        project = factories.ProjectFactory()
        user = UserFactory()
        project.can_change(user).should.be.false

    def test_get_success_percents(self):
        """Test get success percents"""
        project = factories.ProjectFactory()
        Tasks.save({
            'project': project.name,
            'commit': {'branch': 'branch'},
            'success_percent': 92,
        })
        project.get_success_percents(10).should.be.equal([92])

    def test_get_last_task(self):
        """Test get last task"""
        project = factories.ProjectFactory()
        task_id = Tasks.save({
            'project': project.name,
            'commit': {'branch': 'branch'},
        })
        project.get_last_task()['_id'].should.be.equal(task_id)

    def test_last_task_not_exists(self):
        """Test last task not exists"""
        project = factories.ProjectFactory()
        project.get_last_task.when.called_with().should.throw(
            TaskDoesNotExists,
        )

    def test_get_positive_trend(self):
        """Test get positive trend"""
        project = factories.ProjectFactory()
        Tasks.insert([{
            'project': project.name,
            'commit': {'branch': 'branch'},
            'success_percent': n,
            'created': num,
        } for num, n in enumerate(range(1, 5))])
        project.get_trend().should.be.greater_than(0)

    def test_get_negative_trend(self):
        """Test get negative trend"""
        project = factories.ProjectFactory()
        Tasks.insert([{
            'project': project.name,
            'commit': {'branch': 'branch'},
            'success_percent': n,
            'created': num,
        } for num, n in enumerate(range(5, 1, -1))])
        project.get_trend().should.be.lower_than(0)

    def test_get_neutral_trend(self):
        """Test get neutral trend"""
        project = factories.ProjectFactory()
        Tasks.save({
            'project': project.name,
            'commit': {'branch': 'branch'},
            'success_percent': 0,
        })
        project.get_trend().should.be.equal(0)

    def test_update_week_statistic_without_tasks(self):
        """Test update week statistic without tasks"""
        project = factories.ProjectFactory()
        project.update_week_statistic()
        project.week_statistic['days'].should.be.equal({
            unicode(n): {
                u'count': 0,
                u'sum_percent': 0,
                u'success': 0,
                u'failed': 0,
                u'percent': 0,
            } for n in range(7)
        })

    def test_update_week_statistic(self):
        """Test update week statistic"""
        project = factories.ProjectFactory()
        Tasks.insert([{
            'project': project.name,
            'success_percent': 10,
            'status': STATUS_SUCCESS,
            'created': datetime.now() + timedelta(days=day),
        } for day in range(7)])
        project.update_week_statistic()
        len(project.week_statistic).should.be.ok

    def test_update_day_time_statistic_without_tasks(self):
        """Test update day time statistic without tasks"""
        project = factories.ProjectFactory()
        project.update_day_time_statistic()
        project.day_time_statistic['parts'].should.be.equal({
            unicode(n): {
                u'count': 0,
                u'sum_percent': 0,
                u'success': 0,
                u'failed': 0,
                u'percent': 0,
            } for n in range(6)
        })

    def test_update_day_time_statistic(self):
        """Test update day time statistic"""
        project = factories.ProjectFactory()
        Tasks.insert([{
            'project': project.name,
            'success_percent': 10,
            'status': STATUS_SUCCESS,
            'created': datetime.now() + timedelta(hours=4 * part),
        } for part in range(6)])
        project.update_day_time_statistic()
        len(project.day_time_statistic).should.be.ok

    def test_update_quality_game_without_previous_task(self):
        """Test update quality game without previous task"""
        project = factories.ProjectFactory()
        task = {
            'project': project.name,
            'success_percent': 10,
            'status': STATUS_SUCCESS,
            'created': datetime.now(),
            'commit': {
                'branch': 'test',
                'author': 'test',
                'inner': [{'author': {'url': 'test'}}]
            }
        }
        project.update_quality_game(task)
        project.quality_game.should.be.equal({})

    def test_update_quality_game_with_previous_tasks(self):
        """Test update quality game with previous tasks"""
        project = factories.ProjectFactory()
        Tasks.save({
            'project': project.name,
            'success_percent': 10,
            'status': STATUS_SUCCESS,
            'created': datetime.now() - timedelta(hours=5),
            'commit': {
                'branch': 'test',
                'author': 'test',
                'inner': [{'author': {'url': 'test'}}]
            },
            'violations': [],
        })
        project.update_quality_game({
            'project': project.name,
            'success_percent': 15,
            'status': STATUS_SUCCESS,
            'created': datetime.now(),
            'commit': {
                'branch': 'test',
                'author': 'test',
                'inner': [{'author': {'url': 'test'}}]
            },
            'violations': [],
        })
        project.quality_game['total']['test']['value'].should.be.equal(1)

    def test_update_quality_game_with_violations(self):
        """Test update quality game with violations"""
        project = factories.ProjectFactory()
        Tasks.save({
            'project': project.name,
            'success_percent': 10,
            'status': STATUS_SUCCESS,
            'created': datetime.now() - timedelta(hours=5),
            'commit': {
                'branch': 'test',
                'author': 'test',
                'inner': [{'author': {'url': 'test'}}]
            },
            'violations': [
                {'name': 'cat', 'success_percent': 10},
            ],
        })
        project.update_quality_game({
            'project': project.name,
            'success_percent': 15,
            'status': STATUS_SUCCESS,
            'created': datetime.now(),
            'commit': {
                'branch': 'test',
                'author': 'test',
                'inner': [{'author': {'url': 'test'}}]
            },
            'violations': [
                {'name': 'cat', 'success_percent': 15},
            ],
        })
        project.quality_game['violations']['cat']['test']['value']\
            .should.be.equal(1)

    def test_update_quality_game_with_new_violation(self):
        """Test update quality game with new violation"""
        project = factories.ProjectFactory()
        Tasks.save({
            'project': project.name,
            'success_percent': 10,
            'status': STATUS_SUCCESS,
            'created': datetime.now() - timedelta(hours=5),
            'commit': {
                'branch': 'test',
                'author': 'test',
                'inner': [{'author': {'url': 'test'}}]
            },
            'violations': [],
        })
        project.update_quality_game({
            'project': project.name,
            'success_percent': 15,
            'status': STATUS_SUCCESS,
            'created': datetime.now(),
            'commit': {
                'branch': 'test',
                'author': 'test',
                'inner': [{'author': {'url': 'test'}}]
            },
            'violations': [
                {'name': 'cat', 'success_percent': 15},
            ],
        })
        project.quality_game['violations']['cat']['test']['value']\
            .should.be.equal(1)

    def test_get_covio(self):
        """Test get covio.yml decoded content"""
        project = factories.ProjectFactory()
        project._repo = MagicMock()
        project.repo.get_file_contents.return_value = 'dmlvbGF0aW9uczoKICBwZ' \
            'XA4OiBwZXA4IC4gLS1leGNsdWRlPScqbWlncmF0\naW9ucyosKnNldHRpbmdzKi' \
            'wqY29tcG9uZW50cyosKmRvY3MqJwogIHNsb2Nj\nb3VudDogc2xvY2NvdW50IC4' \
            'KICBweV91bml0dGVzdDogY2F0IHRlc3Rfb3V0\nCiAgY292ZXJhZ2U6IGNvdmVy' \
            'YWdlIHJlcG9ydAogIHBpcF9yZXZpZXc6CiAg\nICBjb21tYW5kOiBwaXAtcmV2a' \
            'WV3CiAgICBub2ZhaWw6IHRydWUK\n'
        project.get_covio()['violations'].should.be.ok


class OrganizationManagerCase(TestCase):
    """Organization manager case"""

    def setUp(self):
        self.user = User.objects.create_user('user')

    def test_create_and_add_user(self):
        """Test create and add user"""
        organization =\
            models.Organization.objects.get_with_user('test', self.user)
        organization.users.count().should.be.equal(1)
        models.Organization.objects.count().should.be.equal(1)

    def test_create_with_exists_user(self):
        """Test create with exists user"""
        factories.OrganizationFactory(
            name='test', users=[self.user],
        )
        organization =\
            models.Organization.objects.get_with_user('test', self.user)
        set(organization.users.all()).should.be.equal({self.user})
        models.Organization.objects.count().should.be.equal(1)

    def test_add_user_to_exists(self):
        """Test add user to exists"""
        factories.OrganizationFactory(
            name='test', users=[self.user],
        )
        user = UserFactory()
        organization =\
            models.Organization.objects.get_with_user('test', user)
        set(organization.users.all()).should.be.equal({self.user, user})
