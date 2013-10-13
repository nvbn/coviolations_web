from django.conf.urls import patterns, url
from .views import IndexView


urlpatterns = patterns(
    'app.views',
    url(r'^logout/$', 'logout_with_redirect', name='logout'),
    url(r'^', IndexView.as_view(), name='home'),
)
