from django.views.generic import TemplateView, DetailView
from braces.views import LoginRequiredMixin
from .models import Project


class ManageProjectsView(LoginRequiredMixin, TemplateView):
    """Manage projects view"""
    template_name = 'projects/manage.html'


class ProjectView(DetailView):
    """Project view"""
    template_name = 'projects/project.html'
    context_object_name = 'project'
    model = Project
    slug_field = 'name'
