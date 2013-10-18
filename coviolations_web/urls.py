from django.conf.urls import patterns, include, url
from django.contrib import admin
from .api import v1_api
from .views import IndexView, RedirectToHashView


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^', include('accounts.urls')),
    url(r'^projects/', include('projects.urls')),
    url(r'^tasks/', include('tasks.urls')),
    url(r'^api/', include(v1_api.urls)),
    url(r'^', include('social_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', RedirectToHashView.as_view()),
)
