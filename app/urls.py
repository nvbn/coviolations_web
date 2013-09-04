from django.conf.urls import patterns, url
from .views import IndexView


urlpatterns = patterns(
    '',
    url(
        r'^logout/$', 'django.contrib.auth.views.logout',
        name='logout', kwargs={
            'template_name': 'logout.html'
        },
    ),
    url(r'^$', IndexView.as_view(), name='home'),
)
