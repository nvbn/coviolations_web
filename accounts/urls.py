from django.conf.urls import patterns, url


urlpatterns = patterns(
    'accounts.views',
    url(r'^logout/$', 'logout_with_redirect', name='logout'),
)
