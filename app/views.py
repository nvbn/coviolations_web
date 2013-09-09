from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.contrib.messages import add_message, INFO
from django.utils.translation import ugettext_lazy as _
from tasks.const import STATUS_FAILED, STATUS_SUCCESS
from tasks.models import Tasks


class IndexView(TemplateView):
    """Index page view"""
    template_name = 'index.html'

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
        }


def logout_with_redirect(request):
    """Logout with redirect"""
    logout(request)
    add_message(request, INFO, _('Logout success'))
    return redirect(reverse('home'))
