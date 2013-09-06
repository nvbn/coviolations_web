from django.db import models
from django.utils.translation import ugettext_lazy as _
from projects.models import Project
from violations.base import library
from violations.exceptions import ViolationDoesNotExists
from . import const
from .utils import logger


class TaskManager(models.Manager):
    """Task manager"""

    def create_task(self, data):
        """Create task from data dict"""
        project = Project.objects.get(
            name=data['project'],
        )
        task = Task.objects.create(
            project=project,
            commit=data['commit'],
            branch=data['branch'],
        )
        for violation in data['violations']:
            Violation.objects.create(
                task=task,
                violation=violation['name'],
                raw_data=violation['data'],
            )
        return task


class Task(models.Model):
    """Task"""
    commit = models.CharField(
        blank=True, null=True, max_length=300, verbose_name=_('commit'),
    )
    branch = models.CharField(
        blank=True, null=True, max_length=300, verbose_name=_('branch'),
    )
    project = models.ForeignKey(
        Project, blank=True, null=True, verbose_name=_('project'),
    )
    status = models.PositiveSmallIntegerField(
        choices=const.STATUSES, default=const.STATUS_NEW,
        verbose_name=_('status'),
    )

    objects = TaskManager()

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def __unicode__(self):
        return '{}: {}'.format(self.commit, self.id)


class Violation(models.Model):
    """Task violation"""
    task = models.ForeignKey(
        Task, related_name='violations', verbose_name=_('task'),
    )
    violation = models.CharField(
        max_length=300, verbose_name=_('violation'),
    )
    raw_data = models.TextField(verbose_name=_('raw data'))
    prepared_data = models.TextField(
        blank=True, null=True, verbose_name=_('prepared data'),
    )
    status = models.PositiveSmallIntegerField(
        choices=const.STATUSES, default=const.STATUS_NEW,
        verbose_name=_('status'),
    )

    class Meta:
        verbose_name = _('Violation')
        verbose_name_plural = _('Violations')

    def __unicode__(self):
        return '{}: {}'.format(self.task, self.violation)

    def prepare(self):
        """Prepare violation result"""
        try:
            violation = library.get(self.violation)
            self.prepared_data = violation(self.raw_data)
            self.status = const.STATUS_SUCCESS
        except ViolationDoesNotExists:
            self.status = const.STATUS_FAILED
            logger.warning('Prepare violation failed')
