from django.http import Http404
from tastypie.resources import Resource
from tastypie import fields
from projects.models import Project
from .models import NodeTask
from .jobs import run_node_task
from .utils import logger


class NodeTaskHookResource(Resource):
    """Node task hook resource"""
    before = fields.CharField()
    after = fields.CharField()
    ref = fields.CharField()
    commits = fields.ListField()
    repository = fields.DictField()

    class Meta:
        allowed_methods = ['post']
        resource_name = 'nodes/hook'

    def obj_create(self, bundle, **kwargs):
        """Create task from received data"""
        logger.info('Node task started: {}'.format(bundle.data['ref']))
        project_name = '{}/{}'.format(
            bundle.data['repository']['owner']['name'],
            bundle.data['repository']['name'],
        )
        try:
            project = Project.objects.get(
                name=project_name, is_enabled=True, run_here=True,
            )
        except Project.DoesNotExist:
            logger.warning(
                'Project for node task not found: {}'.
                format(project_name),
            )
            raise Http404('Project not found')
        task = NodeTask.objects.create(
            project=project,
            revision=bundle.data['after'],
            branch=self._get_branch(bundle.data['ref']),
        )
        run_node_task.delay(task.id)

    def _get_branch(self, ref):
        """Get branch from ref"""
        return ref.replace('refs/heads/', '')
