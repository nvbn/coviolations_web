from django.conf.urls import patterns, url
from .views import ManageProjectsView


urlpatterns = patterns(
    '',
    url(r'^manage/$', ManageProjectsView.as_view(), name='projects_manage'),
)
