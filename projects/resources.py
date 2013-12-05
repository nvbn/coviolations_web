from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tools.decorators import attach_field
from push.base import sender
from tasks.exceptions import TaskDoesNotExists
from .models import Project


class ProjectsAuthorization(Authorization):
    """Projects authorization"""

    def create_detail(self, object_list, bundle):
        return False

    def create_list(self, object_list, bundle):
        return False

    def delete_detail(self, object_list, bundle):
        return False

    def delete_list(self, object_list, bundle):
        return False

    def read_list(self, object_list, bundle):
        """Return only user resources"""
        if bundle.request.GET.get('fetch'):
            return Project.objects.get_or_create_for_user(bundle.request.user)
        elif bundle.request.GET.get('owner'):
            return Project.objects.get_with_owner(bundle.request.GET['owner'])
        else:
            return Project.objects.get_enabled_for_user(bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.obj.can_access(bundle.request.user)

    def update_list(self, object_list, bundle):
        return False

    def update_detail(self, object_list, bundle):
        sender.send(
            type='project', owner=bundle.request.user.id,
        )
        return bundle.obj.can_change(bundle.request.user)


class ProjectsResource(ModelResource):
    """Projects resource"""
    id = fields.CharField(attribute='id', readonly=True)
    name = fields.CharField(attribute='name', readonly=True)
    url = fields.CharField(attribute='url', readonly=True)
    is_private = fields.BooleanField(attribute='is_private', readonly=True)
    branches = fields.ListField(attribute='branches', readonly=True)
    icon = fields.CharField(attribute='icon', readonly=True, null=True)
    badge_url = fields.CharField(attribute='get_badge_url', readonly=True)
    owner_id = fields.CharField(attribute='owner_id', readonly=True)
    token = fields.CharField(attribute='token', blank=True, null=True)
    default_branch = fields.CharField(
        attribute='default_branch', blank=True, null=True,
    )
    dashboard_branch = fields.CharField(
        attribute='dashboard_branch', blank=True, null=True,
    )
    can_change = fields.BooleanField(default=False)
    success_percents = fields.ListField(blank=True, null=True)
    last_task = fields.DictField(blank=True, null=True)
    trend = fields.FloatField(blank=True, null=True)
    week_statistic = fields.DictField(
        attribute='week_statistic', blank=True, null=True, readonly=True,
    )
    day_time_statistic = fields.DictField(
        attribute='day_time_statistic', blank=True, null=True, readonly=True,
    )
    quality_game = fields.DictField(
        attribute='quality_game', blank=True, null=True, readonly=True,
    )

    class Meta:
        queryset = Project.objects.all()
        authentication = Authentication()
        authorization = ProjectsAuthorization()
        resource_name = 'projects/project'
        detail_uri_name = 'name'
        fields = (
            'name', 'is_enabled', 'id',
            'is_private', 'icon',
            'comment_from_owner_account',
        )

    def dehydrate(self, bundle):
        """Attach token to bundle if owner"""
        if (
            bundle.request.user.is_authenticated()
            and bundle.obj.can_change(bundle.request.user)
        ):
            bundle.data['can_change'] = True
        else:
            bundle.data['token'] = ''
        self._attach_success_percent(bundle)
        self._attach_last_task(bundle)
        self._attach_trend(bundle)
        return bundle

    @attach_field('with_success_percent', 'success_percents')
    def _attach_success_percent(self, bundle):
        """Attach success percent"""
        return bundle.obj.get_success_percents(
            100, bundle.request.GET.get('branch'),
        )

    @attach_field('with_last_task', 'last_task')
    def _attach_last_task(self, bundle):
        """Attach last task to project"""
        try:
            return bundle.obj.get_last_task()
        except TaskDoesNotExists:
            return None

    @attach_field('with_trend', 'trend')
    def _attach_trend(self, bundle):
        """Attach trend to project"""
        return bundle.obj.get_trend(bundle.request.GET.get('branch'))
