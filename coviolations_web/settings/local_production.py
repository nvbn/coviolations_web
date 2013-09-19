from .base import INSTALLED_APPS

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['coviolations.io']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}

VIOLATIONS = (
    'violations.pep8',
    'violations.sloccount',
    'violations.py_unittest',
    'violations.pip_review',
    'violations.testem',
    'violations.coverage',
)

SERVICES = (
    'services.travis_ci',
    'services.token',
)

PUSH_BIND = 'http://coviolations.io/sub'

INSTALLED_APPS += ('raven.contrib.django.raven_compat',)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'ERROR',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'INFO',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.request': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'coviolations_tasks': {
            'level': 'DEBUG',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'coviolations_services': {
            'level': 'DEBUG',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'coviolations_projects': {
            'level': 'DEBUG',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
    },
}

USE_SSL = True
