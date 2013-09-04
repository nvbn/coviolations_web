import json
from django.views.generic import View
from django.conf import settings
from braces.views import JSONResponseMixin
from .jobs import create_task


class CreateTaskView(JSONResponseMixin, View):
    """Create task view"""

    def post(self, request, *args, **kwargs):
        """Create task from data"""
        data = json.loads(request.body)
        if data.get('service') in settings.ENABLED_SERVICES:
            create_task(data)
            ok = True
        else:
            ok = False
        return self.render_json_response({
            'ok': ok,
        })
