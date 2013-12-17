import os
from datetime import timedelta


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../"),
)


TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static_collected')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '4v62@6a8)sgacvb)b_3sy8-9v-dhqv5o!6d*a$t^pa*3!r3lcr'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'coviolations_web.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'coviolations_web.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'coviolations_web', 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'push.context_processors.push_processor',
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'south',
    'django_extensions',
    'djangobower',
    'django_rq',
    'social_auth',
    'tastypie',

    'accounts',
    'projects',
    'tasks',
    'violations',
    'services',
    'push',
    'nodes',
)

BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_ROOT, 'components')

BOWER_INSTALLED_APPS = (
    'jquery',
    'bootstrap',
    'font-awesome',
    'underscore',
    'nnnick-chartjs',
    'google-code-prettify',
    'sockjs-client',
    'favico.js',
    'jquery-waypoints',
    'angular',
    'requirejs',
    'angles',
    'angular-route',
    'angular-bootstrap',
    'ngInfiniteScroll',
    'underscore.string',
    'chai',
    'sinon',
    'ngprogress',
    'angular-ui-utils',
    'angularjs-nvd3-directives',
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.contrib.github.GithubBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/github/'

GITHUB_EXTENDED_PERMISSIONS = ['public_repo', 'repo']
GITHUB_HOOK_NAME = 'coviolations'
GITHUB_HOOK_EVENTS = ['push', 'create', 'pull_request']

PYRAX_DEFAULT_IMAGE = 'ubuntu-1204-lts-precise-pangolin'
PYRAX_DEFAULT_FLAVOR = '1-gb-performance'

PARALLEL_TASKS = 2
PARALLEL_TIMEOUT = 1
NODE_LIFETIME = timedelta(minutes=10)
NODE_KILLER_INTERVAL = 60

KEYS_TEMPORARY_ROOT = '/tmp'
