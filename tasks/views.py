import json
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
from .jobs import create_task


class CreateTaskView(View):
    """Create task view"""

    def post(self, request, *args, **kwargs):
        """Create task from data"""
        data = json.loads(request.body)
        if data.get('service') in settings.ENABLED_SERVICES:
            create_task(data)
            ok = True
        else:
            ok = False
        return HttpResponse(content=json.dumps({'ok': ok}))
