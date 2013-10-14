from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django_extensions.db.fields import UUIDField
from tools.short import make_https
from tasks.models import Tasks


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
                url=repo.url,
                is_private=repo.private,
            )
        except Project.DoesNotExist:
            project = Project(
                owner=user,
                name=repo.full_name,
                url=repo.url,
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
