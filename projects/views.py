from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin


class ManageProjectsView(LoginRequiredMixin, TemplateView):
    """Manage projects view"""
    template_name = 'projects/manage.html'
