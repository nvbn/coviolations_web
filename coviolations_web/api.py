from tastypie.api import Api
from projects.resources import UserProjectsResource
from tasks.resources import TaskResource, RawTaskResource


v1_api = Api(api_name='v1')
v1_api.register(UserProjectsResource())
v1_api.register(TaskResource())
v1_api.register(RawTaskResource())
