from django.conf.urls import patterns, url
from .views import DetailTask


urlpatterns = patterns(
    '',
    url(r'^(?P<pk>.*)/$', DetailTask.as_view(), name='tasks_detail'),
)
