from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth import logout


def logout_with_redirect(request):
    """Logout with redirect"""
    logout(request)
    return redirect(reverse('home'))
