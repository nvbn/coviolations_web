from django.http import Http404
from tastypie.resources import Resource
from tastypie import fields
from services.base import library
from .jobs import create_task
from .models import Tasks


class TaskResource(Resource):
    """Task resource"""
    service = fields.DictField()
    project = fields.CharField()
    commit = fields.DictField()
    violations = fields.ListField()

    class Meta:
        list_allowed_methods = ['post']
        resource_name = 'tasks'

    def obj_create(self, bundle, **kwargs):
        """Create object"""
        if library.has(bundle.data['service']['name']):
            task_id = Tasks.insert(bundle.data)
            create_task(task_id)
            bundle.data['_id'] = task_id
        else:
            raise Http404()
        return bundle

    def detail_uri_kwargs(self, bundle_or_obj):
        """Get kwargs for detailed uri"""
        return {}
