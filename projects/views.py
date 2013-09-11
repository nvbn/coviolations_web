from django.http import Http404
from pymongo import DESCENDING
from django.shortcuts import redirect
from django.contrib.messages import add_message, INFO
from django.utils.translation import ugettext_lazy as _
from django.templatetags.static import static
from django.views.generic import (
    TemplateView,
    DetailView,
    RedirectView,
    FormView,
)
from braces.views import LoginRequiredMixin
from tasks import const
from tasks.models import Tasks
from .models import Project
from .forms import RegenerateTokenForm
from .utils import logger


class ManageProjectsView(LoginRequiredMixin, TemplateView):
    """Manage projects view"""
    template_name = 'projects/manage.html'


class ProjectView(DetailView):
    """Project view"""
    template_name = 'projects/project.html'
    context_object_name = 'project'
    model = Project
    slug_field = 'name'

    def get_object(self, queryset=None):
        """Get object"""
        obj = super(ProjectView, self).get_object(queryset)
        if not obj.can_access(self.request.user):
            raise Http404()
        return obj


class ProjectBadge(RedirectView):
    """Project badge view"""
    permanent = False

    def get_redirect_url(self, **kwargs):
        """Redirect to badge"""
        return self._get_badge_url(
            self._get_badge_type(**kwargs),
        )

    def _get_badge_type(self, **kwargs):
        """Get badge type"""
        try:
            project = Project.objects.get(name=kwargs['slug'])
            last_task = Tasks.find_one({
                'project': project.name,
            }, sort=[('created', DESCENDING)], fields={
                'status': True,
            })

            return {
                const.STATUS_NEW: 'unknown',
                const.STATUS_FAILED: 'fail',
                const.STATUS_SUCCESS: 'success',
            }[last_task['status']]
        except (Project.DoesNotExist, TypeError) as e:
            return 'unknown'

    def _get_badge_url(self, badge_type):
        """Get badge url"""
        return static('img/badge_{}.png'.format(badge_type))


class RegenerateTokenView(LoginRequiredMixin, FormView):
    """Regenerate token view"""
    form_class = RegenerateTokenForm

    def get_form(self, form_class):
        """Get initialised form"""
        return form_class(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        """Save form and go back"""
        project = form.save()
        logger.info('Token of project {} changed'.format(
            project.name,
        ), exc_info=True, extra={
            'request': self.request,
        })
        add_message(self.request, INFO, _('Token changed success'))
        return self._redirect_back()

    def form_invalid(self, form):
        """Redirect back"""
        logger.warning(
            'Attempt to change now self-owned project',
            exc_info=True, extra={
                'request': self.request,
            },
        )
        return self._redirect_back()

    def _redirect_back(self):
        """Redirect back"""
        return redirect(self.request.META.get('HTTP_REFERER', '/'))
