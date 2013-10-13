from django.conf.urls import patterns, url
from .views import RawViolationView


urlpatterns = patterns(
    '',
    url(
        r'^(?P<pk>.*)/raw/(?P<violation>\d*)/$',
        RawViolationView.as_view(), name='tasks_raw',
    ),
)
