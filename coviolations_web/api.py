from tastypie.api import Api
from projects.resources import UserProjectsResource


v1_api = Api(api_name='v1')
v1_api.register(UserProjectsResource())
