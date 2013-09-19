from bson import ObjectId
from django.views.generic import TemplateView, View
from django.http import HttpResponse, Http404
from projects.models import Project
from projects.utils import ProjectAccessMixin
from .models import Tasks


class TaskViewMixin(ProjectAccessMixin):
    """Task view mixin"""

    def get_project(self, task):
        """Get project"""
        project = Project.objects.get(name=task['project'])
        if not self.check_can_access(project):
            raise Http404()
        return project

    def get_task(self, **kwargs):
        """Get task"""
        return Tasks.find_one(ObjectId(kwargs['pk']))


class DetailTaskView(TaskViewMixin, TemplateView):
    """Detail task"""
    template_name = 'tasks/detail_task.html'

    def get_context_data(self, **kwargs):
        """Get context data"""
        task = self.get_task(**kwargs)
        context = dict(task)
        context['pk'] = kwargs['pk']
        context['project'] = self.get_project(task)
        return context


class RawViolationView(TaskViewMixin, View):
    """Raw violation view"""

    def get(self, request, *args, **kwargs):
        """Return raw violation"""
        task = Tasks.find_one(ObjectId(kwargs['pk']))
        self.get_project(task)
        return HttpResponse(
            task['violations'][int(kwargs['violation'])]['raw'],
            content_type='text/plain',
        )
