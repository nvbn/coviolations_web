from bson import ObjectId
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from .models import Tasks


class DetailTaskView(TemplateView):
    """Detail task"""
    template_name = 'tasks/detail_task.html'

    def get_context_data(self, **kwargs):
        """Get context data"""
        context = dict(Tasks.find_one(ObjectId(kwargs['pk'])))
        context['pk'] = kwargs['pk']
        return context


class RawViolationView(View):
    """Raw violation view"""

    def get(self, request, *args, **kwargs):
        """Return raw violation"""
        task = Tasks.find_one(ObjectId(kwargs['pk']))
        return HttpResponse(
            task['violations'][int(kwargs['violation'])]['raw'],
            content_type='text/plain',
        )
