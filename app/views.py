from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.contrib.messages import add_message, INFO
from django.utils.translation import ugettext_lazy as _


class IndexView(TemplateView):
    """Index page view"""
    template_name = 'index.html'


def logout_with_redirect(request):
    """Logout with redirect"""
    logout(request)
    add_message(request, INFO, _('Logout success'))
    return redirect(reverse('home'))
