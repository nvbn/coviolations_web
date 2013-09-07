from pymongo import DESCENDING
from django.http import Http404
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie import fields
from services.base import library
from tools.mongo import Document
from .jobs import create_task
from .models import Tasks


class TaskResource(Resource):
    """Task resource"""
    service = fields.DictField(attribute='service', null=True)
    project = fields.CharField(attribute='project', null=True)
    commit = fields.DictField(attribute='commit', null=True)
    violations = fields.ListField(attribute='violations', null=True)
    plot = fields.DictField(attribute='plot', null=True)
    created = fields.DateTimeField(attribute='created', null=True)
    status = fields.IntegerField(attribute='status', null=True)

    class Meta:
        list_allowed_methods = ['get', 'post']
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

    def obj_get_list(self, bundle, **kwargs):
        """Get object list"""
        find_kwargs = {
            'fields': {},
            'spec': {},
            'sort': [('created', DESCENDING)],
        }

        if bundle.request.GET.get('with_full_violations'):
            find_kwargs['fields']['violations'] = True
        elif bundle.request.GET.get('with_violations'):
            find_kwargs['fields']['violations.name'] = True
            find_kwargs['fields']['violations.status'] = True
        else:
            find_kwargs['fields']['violations'] = False

        if bundle.request.GET.get('project'):
            find_kwargs['spec']['project'] = bundle.request.GET['project']

        return map(Document, Tasks.find(**find_kwargs))

    def detail_uri_kwargs(self, bundle_or_obj):
        """Get kwargs for detailed uri"""
        if isinstance(bundle_or_obj, Bundle):
            pk = bundle_or_obj.obj._id
        else:
            pk = bundle_or_obj._id
        return {'pk': pk}
