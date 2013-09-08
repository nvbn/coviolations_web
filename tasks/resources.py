from datetime import datetime
from pymongo import DESCENDING
from django.shortcuts import get_object_or_404
from django.http import Http404
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie import fields
from services.base import library
from projects.models import Project
from tools.mongo import Document
from .jobs import create_task
from .models import Tasks


class TaskResource(Resource):
    """Task resource"""
    service = fields.DictField(attribute='service', null=True)
    project = fields.CharField(attribute='project', null=True)
    commit = fields.DictField(attribute='commit', null=True)
    violations = fields.ListField(attribute='violations', null=True)
    created = fields.DateTimeField(attribute='created', null=True)
    status = fields.IntegerField(attribute='status', null=True)
    id = fields.CharField(attribute='_id', null=True)

    class Meta:
        list_allowed_methods = ['get', 'post']
        resource_name = 'tasks'

    def obj_create(self, bundle, **kwargs):
        """Create object"""
        project = get_object_or_404(
            Project, name=bundle.data['project'], is_enabled=True,
        )

        if library.has(bundle.data['service']['name']):
            bundle.data['owner_id'] = project.owner.id
            task_id = Tasks.insert(bundle.data)
            create_task.delay(task_id)
            bundle.data['_id'] = task_id

            project.last_use = datetime.now()
            project.save()
        else:
            raise Http404()
        return bundle

    def obj_get_list(self, bundle, **kwargs):
        """Get object list"""
        find_kwargs = {
            'fields': {name: True for name in (
                'service', 'project', 'commit', 'plot',
                'created', 'status',
            )},
            'spec': {},
            'sort': [('created', DESCENDING)],
        }

        if bundle.request.GET.get('with_full_violations'):
            find_kwargs['fields']['violations'] = True
        elif bundle.request.GET.get('with_violations'):
            find_kwargs['fields']['violations.name'] = True
            find_kwargs['fields']['violations.status'] = True
            find_kwargs['fields']['violations.preview'] = True
            find_kwargs['fields']['violations.plot'] = True

        if bundle.request.GET.get('project'):
            find_kwargs['spec']['project'] = bundle.request.GET['project']

        if bundle.request.GET.get('self'):
            find_kwargs['spec']['owner_id'] = bundle.request.user.id

        print find_kwargs

        return map(Document, Tasks.find(**find_kwargs))

    def detail_uri_kwargs(self, bundle_or_obj):
        """Get kwargs for detailed uri"""
        if isinstance(bundle_or_obj, Bundle):
            if '_id' in bundle_or_obj.data:
                pk = bundle_or_obj.data['_id']
            elif bundle_or_obj.obj:
                pk = bundle_or_obj.obj._id
        else:
            pk = bundle_or_obj.id
        return {'pk': pk}
