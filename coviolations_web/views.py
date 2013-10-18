from datetime import datetime, timedelta
from django.views.generic import TemplateView, RedirectView
from django.contrib.sites.models import Site
from django.conf import settings
from tasks.const import STATUS_FAILED, STATUS_SUCCESS
from tasks.models import Tasks


class IndexView(TemplateView):
    """Index page view"""
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        """Get day statistic"""
        success = Tasks.find({'created': {
            '$gte': datetime.now() - timedelta(days=1)
        }, 'status': STATUS_SUCCESS}).count()

        failed = Tasks.find({'created': {
            '$gte': datetime.now() - timedelta(days=1)
        }, 'status': STATUS_FAILED}).count()

        if failed:
            failed_percent = failed * 100 / (success + failed)
        else:
            failed_percent = 0

        return {
            'failed': failed_percent,
            'success': 100 - failed_percent,
            'debug': settings.DEBUG,
            'site': Site.objects.get_current(),
        }


class RedirectToHashView(RedirectView):
    """Redirect to url with hash"""

    def get_redirect_url(self, **kwargs):
        """Return url with hash"""
        return '/#{}'.format(self.request.path)
