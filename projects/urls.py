from django.conf.urls import patterns, url
from .views import ManageProjectsView, ProjectView


urlpatterns = patterns(
    '',
    url(r'^manage/$', ManageProjectsView.as_view(), name='projects_manage'),
    url(r'^(?P<slug>.*)/$', ProjectView.as_view(), name='projects_project'),
)
