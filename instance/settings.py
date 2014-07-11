# -*- encoding: utf-8 -*-

"""
    App instance specific settings
"""


STORAGE = {
    'prototype': 'memcache',
    'hosts': ['localhost:11211']
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'georest.restapi': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'gunicornish',
        },
    },
    'formatters': {
        'gunicornish': {
            'format': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
        },
    },
}
