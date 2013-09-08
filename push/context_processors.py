from django.conf import settings


def push_processor(request):
    """Push context processor"""
    return {
        'push_bind': settings.PUSH_BIND,
    }
