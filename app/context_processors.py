from django.contrib.sites.models import Site


def request_site(request):
    """Current site instalnce processor"""
    return {
        'SITE': Site.objects.get_current(),
    }
