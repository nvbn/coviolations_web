from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns(
    '',
    url(
        r'^(?P<slug>.*)/badge/$', views.ProjectBadge.as_view(),
        name='projects_badge',
    ),
)
