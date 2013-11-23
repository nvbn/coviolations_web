from datetime import datetime
from pymongo import DESCENDING
import numpy as np
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django_extensions.db.fields import UUIDField
from tools.short import make_https
from tools.mongo import db
from tasks.models import Tasks
from tasks.exceptions import TaskDoesNotExists
from tasks.const import STATUS_SUCCESS
from . import const


WeekStatistic = db.week_statistic
DayTimeStatistic = db.day_time_statistic
QualityGame = db.quality_game


class OrganizationManager(models.Manager):
    """Organization manager"""

    def get_with_user(self, name, user):
        """Get and add user if need"""
        organisation = self.get_or_create(name=name)[0]
        if not organisation.users.filter(id=user.id).exists():
            organisation.users.add(user)
        return organisation


class Organization(models.Model):
    """Organization model"""
    name = models.CharField(max_length=300, verbose_name=_('name'))
    users = models.ManyToManyField(
        User, related_name='organizations', verbose_name=_('users'),
    )

    objects = OrganizationManager()

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organization')

    def __unicode__(self):
        return self.name


class ProjectManager(models.Manager):
    """Project manager"""

    def update_user_projects(self, user):
        """Alias for get_or_create_for_user but without return"""
        self.get_or_create_for_user(user)

    def get_or_create_for_user(self, user):
        """Get or create for user"""
        github_user = user.github.get_user()
        projects = [self._get_or_create_and_update(
            repo, user, str(github_user.avatar_url),
        ) for repo in github_user.get_repos('owner')]
        projects += self._get_for_user_organizations(
            user, github_user,
        )
        self.filter(owner=user).exclude(id__in=projects).delete()
        return self.get_for_user(user).order_by('-last_use')

    def _get_for_user_organizations(self, user, github_user):
        """Get for user organizations"""
        project_ids = []
        for github_organization in github_user.get_orgs():
            organization = Organization.objects.get_with_user(
                github_organization.login, user,
            )
            avatar = str(github_organization.avatar_url)
            project_ids += [self._get_or_create_and_update(
                repo, user, avatar, organization,
            ) for repo in github_organization.get_repos('owner')]
        return project_ids

    def _get_or_create_and_update(self, repo, user, icon, organization=None):
        """Get or create and update"""
        try:
            project = Project.objects.get(
                name=repo.full_name,
                url=repo.html_url,
                is_private=repo.private,
            )
        except Project.DoesNotExist:
            project = Project(
                owner=user,
                name=repo.full_name,
                url=repo.html_url,
                is_private=repo.private,
            )
        project.organization = organization
        project.icon = icon
        project.save()
        return project.id

    def get_enabled_for_user(self, user):
        """Get enabled projects available for user"""
        return self.get_for_user(user).filter(is_enabled=True)

    def get_for_user(self, user):
        """Get for user"""
        return self.filter(
            Q(owner=user) | Q(organization__users=user)
        ).distinct()


class Project(models.Model):
    """Github project"""
    owner = models.ForeignKey(User, verbose_name=_('owner'))
    name = models.CharField(max_length=300, verbose_name=_('name'))
    url = models.URLField(verbose_name=_('url'))
    is_enabled = models.BooleanField(
        default=False, verbose_name=_('is enabled'),
    )
    last_use = models.DateTimeField(
        auto_now_add=True, verbose_name=_('last use'),
    )
    badge_url = models.CharField(
        blank=True, null=True,
        max_length=300, verbose_name=_('badge url'),
    )
    token = UUIDField(null=True, auto=True, verbose_name=_('token'))
    is_private = models.BooleanField(
        default=False, verbose_name=_('is private'),
    )
    icon = models.CharField(
        blank=True, null=True, max_length=300, verbose_name=_('icon'),
    )
    organization = models.ForeignKey(
        Organization, blank=True, null=True, verbose_name=_('organization'),
    )
    comment_from_owner_account = models.BooleanField(
        default=False, verbose_name=_('comment from owner account'),
    )
    default_branch = models.CharField(
        max_length=300, blank=True, null=True,
        verbose_name=_('default branch'),
    )
    dashboard_branch = models.CharField(
        max_length=300, blank=True, null=True,
        verbose_name=_('dashboard branch'),
    )

    objects = ProjectManager()

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ('-last_use', 'name')
        get_latest_by = ('-last_use',)

    def __unicode__(self):
        return self.name

    def get_badge_url(self, **kwargs):
        """Get or create https badge url"""
        if not self.badge_url:
            local_url = reverse('projects_badge', args=(self.name,))
            local_url += '?{}'.format('&'.join(
                '{}={}'.format(key, value) for key, value in kwargs.items(),
            ))
            self.badge_url = make_https(local_url)
            self.save()
        return self.badge_url

    def can_access(self, user):
        """Can access"""
        if self.is_private:
            if self.organization:
                if self.organization.users.filter(
                    id=user.id,
                ).exists():
                    return True
            return self.owner == user
        else:
            return True

    def can_change(self, user):
        """Can change project"""
        return self.can_access(user) and self.owner == user

    def get_allowed_users(self):
        """Get allowed users"""
        if self.organization:
            users = list(self.organization.users.all())
        else:
            users = []
        return [self.owner] + users

    @property
    def branches(self):
        """Get project branches"""
        return Tasks.find({'project': self.name}).distinct('commit.branch')

    @property
    def repo(self):
        """Github repo of project with read access"""
        if not hasattr(self, '_repo'):
            self._repo = self.owner.github.get_repo(self.name)
        return self._repo

    def get_success_percents(self, count, branch=None):
        """Get project last success percents"""
        if branch is None:
            branch = self.dashboard_branch
        spec = {
            'project': self.name,
        }
        if branch:
            spec['commit.branch'] = branch
        return [
            task.get('success_percent', 0) for task in Tasks.find(
                spec, sort=[('created', DESCENDING)], fields={
                    'success_percent': True,
                }, limit=count)
        ]

    def get_last_task(self):
        """Get last task"""
        task = Tasks.find_one({
            'project': self.name,
        }, sort=[('created', DESCENDING)], fields={
            name: True for name in (
                'service', 'project', 'commit', 'plot',
                'created', 'status', 'success_percent',
            )
        })
        if task:
            return task
        else:
            raise TaskDoesNotExists()

    def get_trend(self, branch=None):
        """Get project trend"""
        percents = self.get_success_percents(const.TREND_CHUNK, branch)[::-1]
        if len(percents) > 1:
            times = range(len(percents))
            percents_matrix = np.matrix(percents).T
            times_matrix = np.matrix([times, [1 for _ in times]]).T
            return (
                (times_matrix.T * times_matrix).I
                * times_matrix.T * percents_matrix
            )[0, 0]
        else:
            return 0

    def _fill_statistic_parts(self, parts, grouper):
        """Fill statistic parts"""
        for task in Tasks.find({
            'project': self.name,
            'created': {'$exists': True},
            'success_percent': {'$exists': True},
        }):
            if type(task['created']) is datetime:
                group = grouper(task)
                parts[group]['count'] += 1
                parts[group]['sum_percent'] +=\
                    task['success_percent']
                parts[group][
                    'success' if task['status'] == STATUS_SUCCESS else 'failed'
                ] += 1

    def _calculate_statistic_percent(self, parts):
        """Calculate statistic percent"""
        for part in parts.keys():
            parts[part]['percent'] =\
                parts[part]['sum_percent'] / parts[part]['count']\
                if parts[part]['count'] else 0

    def _get_initial_statistic(self):
        """Get initial statistic"""
        return {
            'count': 0,
            'sum_percent': 0,
            'success': 0,
            'failed': 0,
        }

    def _recreate_statistic_obj(self, collection, field, parts):
        """Recreate statistic obj"""
        collection.remove({'project': self.name})
        collection.save({
            'project': self.name,
            field: {
                str(part): values for part, values in parts.items()
            },
        })

    def update_week_statistic(self):
        """Update week statistic"""
        days = {day: self._get_initial_statistic() for day in range(0, 7)}
        self._fill_statistic_parts(
            days, lambda task: task['created'].weekday(),
        )
        self._calculate_statistic_percent(days)
        self._recreate_statistic_obj(WeekStatistic, 'days', days)

    def _get_statistic(self, collection):
        """Get statistic"""
        statistic = collection.find_one({'project': self.name})
        if statistic:
            return statistic
        else:
            return {}

    @property
    def week_statistic(self):
        """Get week statistic"""
        return self._get_statistic(WeekStatistic)

    def update_day_time_statistic(self):
        """Update day time statistic"""
        parts = {part: self._get_initial_statistic() for part in range(6)}
        self._fill_statistic_parts(
            parts, lambda task: task['created'].hour / 4,
        )
        self._calculate_statistic_percent(parts)
        self._recreate_statistic_obj(DayTimeStatistic, 'parts', parts)

    @property
    def day_time_statistic(self):
        """Get day time statistic"""
        return self._get_statistic(DayTimeStatistic)

    @property
    def quality_game(self):
        """Get project quality statistic"""
        return self._get_statistic(QualityGame)

    def _get_or_create_quality_game(self):
        """Get or create quality game for project"""
        if self.quality_game:
            return self.quality_game
        else:
            return {
                'project': self.name,
                'total': {},
                'violations': {},
            }

    def _prepare_author(self, author):
        """Prepare author to key"""
        return author['url'].replace('.', '__')

    def _get_quality_object(self, game_part, task):
        """Get quality object"""
        author = self._prepare_author(task['commit']['inner'][-1]['author'])
        if author in game_part:
            return game_part[author]
        else:
            return {
                'user': task['commit']['inner'][-1]['author'],
                'value': 0,
            }

    def _update_quality_object(self, game_part, task, is_better):
        """Update quality object"""
        obj = self._get_quality_object(game_part, task)
        if is_better:
            obj['value'] += 1
        else:
            obj['value'] = 0
        game_part[self._prepare_author(
            task['commit']['inner'][-1]['author'],
        )] = obj
        return game_part

    def _get_violation_success_percent(self, task, name):
        """Get violation success percent"""
        for violation in task['violations']:
            if violation['name'] == name:
                return violation.get('success_percent', 0)

    def update_quality_game(self, task):
        """Update quality game"""
        previous = Tasks.find_one({
            'commit.branch': task['commit']['branch'],
            'created': {'$lt': task['created']},
        })
        if not previous:
            return

        game = self._get_or_create_quality_game()
        game['total'] = self._update_quality_object(
            game['total'], task,
            task.get('success_percent', 0) >=
            previous.get('success_percent', 0),
        )
        for violation in task['violations']:
            is_better = violation.get('success_percent', 0) >=\
                self._get_violation_success_percent(task, violation['name'])
            game['violations'][violation['name']] =\
                self._update_quality_object(
                    game.get(violation['name'], {}), task, is_better,
                )
        QualityGame.save(game)
