from django.conf.urls import patterns, url
from .views import CreateTaskView


urlpatterns = patterns(
    'tasks',
    url(r'^create/$', CreateTaskView.as_view(), name='tasks_create'),
)