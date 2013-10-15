from django.conf.urls import patterns, url
from .views import IndexView


urlpatterns = patterns(
    'app.views',
    url(r'^$', IndexView.as_view(), name='home'),
)
