from django.shortcuts import redirect
from django.contrib.messages import add_message, INFO
from django.utils.translation import ugettext_lazy as _
from django.templatetags.static import static
from django.views.generic import (
    DetailView,
    RedirectView,
    FormView,
)
from braces.views import LoginRequiredMixin
from tasks import const
from tasks.exceptions import TaskDoesNotExists
from .models import Project
from .forms import RegenerateTokenForm, FindTaskForBadgeForm
from .utils import logger, ProjectAccessMixin


class ProjectView(ProjectAccessMixin, DetailView):
    """Project view"""
    template_name = 'projects/project.html'
    context_object_name = 'project'
    model = Project
    slug_field = 'name'
    get_project = lambda self, **kwargs: self.get_object()


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
        form = FindTaskForBadgeForm(dict(
            project=kwargs['slug'], **self.request.GET.dict()
        ))
        if form.is_valid():
            try:
                last_task = form.get_task()
            except TaskDoesNotExists:
                return 'unknown'
            return {
                const.STATUS_NEW: 'unknown',
                const.STATUS_FAILED: 'fail',
                const.STATUS_SUCCESS: 'success',
            }[last_task['status']]
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
