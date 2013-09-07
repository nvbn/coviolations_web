from django.conf.urls import patterns, url
from .views import DetailTaskView, RawViolationView


urlpatterns = patterns(
    '',
    url(
        r'^(?P<pk>.*)/raw/(?P<violation>\d*)/$',
        RawViolationView.as_view(), name='tasks_raw',
    ),
    url(r'^(?P<pk>.*)/$', DetailTaskView.as_view(), name='tasks_detail'),
)
