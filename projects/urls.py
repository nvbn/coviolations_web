from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns(
    '',
    url(
        r'^regenerate/$', views.RegenerateTokenView.as_view(),
        name='projects_regenerate',
    ),
    url(
        r'^(?P<slug>.*)/badge/$', views.ProjectBadge.as_view(),
        name='projects_badge',
    ),
)
