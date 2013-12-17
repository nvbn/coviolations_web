from tastypie.api import Api
from projects.resources import ProjectsResource
from tasks.resources import TaskResource, RawTaskResource, TaskStatusResource
from nodes.resources import NodeTaskHookResource


v1_api = Api(api_name='v1')
v1_api.register(ProjectsResource())
v1_api.register(TaskResource())
v1_api.register(RawTaskResource())
v1_api.register(TaskStatusResource())
v1_api.register(NodeTaskHookResource())
