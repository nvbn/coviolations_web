from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class Project(models.Model):
    """Github project"""
    owner = models.ForeignKey(User, verbose_name=_('owner'))
    name = models.CharField(max_length=300, verbose_name=_('name'))
    url = models.URLField(verbose_name=_('url'))
    is_enabled = models.BooleanField(
        default=False, verbose_name=_('is enabled'),
    )

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')


class Branch(models.Model):
    """Github project branch"""
    name = models.CharField(max_length=300, verbose_name=_('name'))
    project = models.ForeignKey(
        Project, related_name='branches', verbose_name=_('project'),
    )

    class Meta:
        verbose_name = _('Branch')
        verbose_name_plural = _('Branches')

    def __unicode__(self):
        return '{}: {}'.format(self.project, self.name)


class Commit(models.Model):
    """Github project commit"""
    name = models.CharField(max_length=300, verbose_name=_('name'))
    branch = models.ForeignKey(
        Branch, related_name='commits', verbose_name=_('branch'),
    )

    class Meta:
        verbose_name = _('Commit')
        verbose_name_plural = _('Commits')
