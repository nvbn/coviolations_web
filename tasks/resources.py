from datetime import datetime
from copy import copy
from pymongo import DESCENDING
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie import fields
from services.base import library
from projects.models import Project
from tools.mongo import Document
from tools.filters import FiltersAccumulator
from .jobs import create_task
from .models import Tasks
from .utils import logger
from .exceptions import ServiceNotFound


class BaseTaskResource(Resource):
    """Base task resource"""

    def get_resource_uri(
        self, bundle_or_obj=None, url_name='api_dispatch_list',
    ):
        """Get resource uri"""
        url_kwargs = {
            'resource_name': 'tasks/task',
            'api_name': 'v1',
        }
        if bundle_or_obj:
            url_name = 'api_dispatch_detail'
            url_kwargs.update(
                self.detail_uri_kwargs(bundle_or_obj)
            )
        return reverse(url_name, kwargs=url_kwargs)

    def detail_uri_kwargs(self, bundle_or_obj):
        """Get kwargs for detailed uri"""
        if isinstance(bundle_or_obj, Bundle):
            if '_id' in bundle_or_obj.data:
                pk = bundle_or_obj.data['_id']
            elif bundle_or_obj.obj:
                pk = bundle_or_obj.obj._id
        else:
            pk = bundle_or_obj.id
        return {
            'pk': str(pk),
        }


class RawTaskResource(BaseTaskResource):
    """Raw task resource, for creating tasks from remote service"""
    service = fields.DictField(attribute='service', null=True)
    project = fields.CharField(attribute='project', null=True)
    commit = fields.DictField(attribute='commit', null=True)
    violations = fields.ListField(attribute='violations', null=True)
    id = fields.CharField(attribute='_id', null=True)

    class Meta:
        resource_name = 'tasks/raw'
        list_allowed_methods = ['post']
        detail_allowed_methods = []

    def obj_create(self, bundle, **kwargs):
        """Create object"""
        project = get_object_or_404(
            Project, name=bundle.data['project'],
            is_enabled=True,
        )
        try:
            service = self._get_service(bundle.data)
        except ServiceNotFound:
            logger.info(
                'Service not found', exc_info=True, extra={
                    'request': bundle.request,
                    'task': bundle.data,
                },
            )
            raise Http404('Service not found')
        task_id = self._create_task(bundle.data, project, service)
        bundle.data['_id'] = task_id
        logger.info(
            'Task received: {}'.format(task_id), exc_info=True, extra={
                'request': bundle.request,
            },
        )
        self._update_project(project)
        return bundle

    def _get_service(self, data):
        """Get service"""
        try:
            service = data['service']['name']
        except KeyError:
            raise ServiceNotFound()
        if not library.has(service):
            raise ServiceNotFound()
        return library.get(service)

    def _create_task(self, data, project, service):
        """Create service"""
        task_data = copy(data)
        task_data.update({
            'owner_id': project.owner.id,
            'is_private': project.is_private,
        })
        if project.is_private:
            task_data['allowed_users'] = [
                user.id for user in project.get_allowed_users()
            ]
        task_id = Tasks.insert(task_data)
        create_task.delay(task_id)
        return task_id

    def _update_project(self, project):
        """Update project"""
        project.last_use = datetime.now()
        project.save()


class TaskResource(BaseTaskResource):
    """Task resource"""
    service = fields.DictField(attribute='service', null=True)
    created = fields.DateTimeField(attribute='created', null=True)
    status = fields.IntegerField(attribute='status', null=True)
    project = fields.CharField(attribute='project', null=True)
    commit = fields.DictField(attribute='commit', null=True)
    violations = fields.ListField(attribute='violations', null=True)
    id = fields.CharField(attribute='_id', null=True)

    filters = FiltersAccumulator()

    class Meta:
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = 'tasks/task'
        detail_uri_name = 'pk'

    def obj_get_list(self, bundle, **kwargs):
        """Get object list"""
        return map(Document, Tasks.find(**self.filters.get_spec(
            self, bundle, self._get_initial_filters(),
        )))

    def _get_initial_filters(self):
        """Get initial filters"""
        return {
            'fields': {name: True for name in (
                'service', 'project', 'commit', 'plot',
                'created', 'status',
            )},
            'spec': {},
            'sort': [('created', DESCENDING)],
        }

    @filters.add
    def _add_permission_filters(self, find_kwargs, bundle):
        """Add permission filters"""
        if bundle.request.user.is_authenticated():
            find_kwargs['spec']['$or'] = [{
                'is_private': {'$ne': True},
            }, {
                'allowed_users': bundle.request.user.id,
            }]
        else:
            find_kwargs['spec']['is_private'] = {'$ne': True}
        return find_kwargs

    @filters.add
    def _show_hide_violations_fields(self, find_kwargs, bundle):
        """Show/hide violations fields"""
        if bundle.request.GET.get('with_full_violations'):
            find_kwargs['fields']['violations'] = True
        elif bundle.request.GET.get('with_violations'):
            find_kwargs['fields']['violations.name'] = True
            find_kwargs['fields']['violations.status'] = True
            find_kwargs['fields']['violations.preview'] = True
            find_kwargs['fields']['violations.plot'] = True
        return find_kwargs

    @filters.add
    def _add_project_filters(self, find_kwargs, bundle):
        """Add project filters"""
        if bundle.request.GET.get('project'):
            find_kwargs['spec']['project'] = bundle.request.GET['project']
        return find_kwargs

    @filters.add
    def _add_owner_filters(self, find_kwargs, bundle):
        """Add owner filters"""
        if bundle.request.GET.get('self'):
            find_kwargs['spec']['owner_id'] = bundle.request.user.id
        return find_kwargs
