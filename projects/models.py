from django.core.urlresolvers import reverse
from github import Github
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django_extensions.db.fields import UUIDField
from tools.short import make_https


class ProjectManager(models.Manager):
    """Project manager"""

    def _get_remote_projects(self, user):
        """Get remote projects"""
        token = user.social_auth.get().extra_data['access_token']
        github = Github(token)
        github_user = github.get_user()
        return github_user.get_repos('public')

    def get_or_create_for_user(self, user):
        """Get or create for user"""
        for repo in self._get_remote_projects(user):
            Project.objects.get_or_create(
                owner=user,
                name=repo.full_name,
                url=repo.url,
            )
        return self.filter(owner=user)

    def get_enabled_for_user(self, user):
        """Get enabled projects available for user"""
        return self.filter(owner=user, is_enabled=True)


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

    objects = ProjectManager()

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ('-last_use', 'name')
        get_latest_by = ('-last_use',)

    def __unicode__(self):
        return self.name

    def get_badge_url(self):
        """Get or create https badge url"""
        if not self.badge_url:
            self.badge_url = make_https(
                reverse('projects_badge', args=(self.name,)),
            )
            self.save()
        return self.badge_url
