from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns(
    '',
    url(
        r'^manage/$', views.ManageProjectsView.as_view(),
        name='projects_manage',
    ),
    url(
        r'^regenerate/$', views.RegenerateTokenView.as_view(),
        name='projects_regenerate',
    ),
    url(
        r'^(?P<slug>.*)/badge/$', views.ProjectBadge.as_view(),
        name='projects_badge',
    ),
    url(
        r'^(?P<slug>.*)/$', views.ProjectView.as_view(),
        name='projects_project',
    ),
)
