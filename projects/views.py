from django.templatetags.static import static
from django.views.generic import RedirectView
from tasks import const
from tasks.exceptions import TaskDoesNotExists
from .forms import FindTaskForBadgeForm


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
        return static('images/badge_{}.png'.format(badge_type))
