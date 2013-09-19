from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from push.base import sender
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
        else:
            return Project.objects.get_enabled_for_user(bundle.request.user)

    def read_detail(self, object_list, bundle):
        if bundle.obj.owner != bundle.request.user:
            return False
        else:
            return super(ProjectsAuthorization, self).read_detail(
                object_list, bundle,
            )

    def update_list(self, object_list, bundle):
        return False

    def update_detail(self, object_list, bundle):
        sender.send(
            type='project', owner=bundle.request.user.id,
        )
        return self.read_detail(object_list, bundle)


class ProjectsResource(ModelResource):
    """Projects resource"""
    id = fields.CharField(attribute='id', readonly=True)
    name = fields.CharField(attribute='name', readonly=True)
    url = fields.CharField(attribute='url', readonly=True)
    is_private = fields.BooleanField(attribute='is_private', readonly=True)
    branches = fields.ListField(attribute='branches', readonly=True)
    icon = fields.CharField(attribute='icon', readonly=True, null=True)

    class Meta:
        queryset = Project.objects.all()
        authentication = Authentication()
        authorization = ProjectsAuthorization()
        resource_name = 'projects/project'
        fields = ('name', 'is_enabled', 'id', 'is_private', 'icon')
