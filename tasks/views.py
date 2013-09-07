from bson import ObjectId
from django.views.generic import TemplateView
from .models import Tasks


class DetailTask(TemplateView):
    """Detail task"""
    template_name = 'tasks/detail_task.html'

    def get_context_data(self, **kwargs):
        """Get context data"""
        return Tasks.find_one(ObjectId(kwargs['pk']))
