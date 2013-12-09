from django.db import models
from django.utils.translation import ugettext_lazy as _
from projects.models import Project


class NodeTask(models.Model):
    """Node task"""
    STATE_NEW = 0
    STATE_ACTIVE = 1
    STATE_FINISHED = 2
    STATE_FAILED = 3
    STATES = (
        (STATE_NEW, _('new')),
        (STATE_ACTIVE, _('active')),
        (STATE_FINISHED, _('finished')),
        (STATE_FAILED, _('failed'))
    )

    project = models.ForeignKey(Project, verbose_name=_('project'))
    revision = models.CharField(max_length=42, verbose_name=_('revision'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created'),
    )
    finished = models.DateTimeField(
        blank=True, null=True, verbose_name=_('finished'),
    )
    state = models.PositiveSmallIntegerField(
        choices=STATES, default=STATE_NEW, verbose_name=_('state'),
    )
    input = models.TextField(blank=True, null=True, verbose_name=_('input'))
    stdout = models.TextField(blank=True, null=True, verbose_name=_('stdout'))
    stderr = models.TextField(blank=True, null=True, verbose_name=_('stderr'))
    node = models.CharField(
        max_length=30, blank=True, null=True, verbose_name=_('node'),
    )

    class Meta:
        verbose_name = _('Node Task')
        verbose_name_plural = _('Node Tasks')

    def __unicode__(self):
        return '{}: {}'.format(self.project, self.node)
