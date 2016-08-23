"""
Glossary of settings/prod.py:

- Hosting + Authentication
- Email
- SSL Security
- Installed applications
- Database
- Templates
- HTML minification
- Cache
- Staticfiles
- Logging
"""

from pulse.settings.common import *

import dj_database_url


# HOSTING + AUTHENTICATION
ADMINS = (
    # Uncomment lines below if you want email about server errors.
    # ("Luke Aprile", ""),
    # ("TJ Magno", ""),
    # ("Frank Szucs", ""),
)
MANAGERS = ADMINS
ALLOWED_HOSTS = [
    'www.domain.com',
    'domain.com',
    '*.domain.com',
    '127.0.0.1',
]
CORS_URLS_REGEX = r'^/hidden/secure/pulse/api/.*$'
FULL_DOMAIN_NAME = ''  # NEED TO ENTER THIS VALUE


# E M A I L
DEFAULT_FROM_EMAIL = ''
DEFAULT_HR_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587


# S S L  S E C U R I T Y
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_SECONDS = 0
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_HOST = None
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


# A P P L I C A T I O N S
INSTALLED_APPS += (
    'storages',
)


# D A T A B A S E
DATABASES = {
    'default': {  # get credentials from Heroku database creation
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432',
    },
}
DATABASES['default'] = dj_database_url.config()  # Heroku
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['default']['NAME'] = ''
DATABASES['default']['USER'] = ''
DATABASES['default']['PASSWORD'] = ''
DATABASES['default']['HOST'] = ''
DATABASES['default']['PORT'] = '5432'


# T E M P L A T E S
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join('templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]


# H T M L  M I N I F I C A T I O N
KEEP_COMMENTS_ON_MINIFYING = False
EXCLUDE_FROM_MINIFYING = ('^hidden/secure/pulse/admin/',)


# C A C H E
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': [
#             '127.0.0.1:11211',
#         ],
#         'OPTIONS': {
#             'MAX_ENTRIES': 1000
#         }
#     }
# }
# CACHE_MIDDLEWARE_ALIAS = 'default'
# CACHE_MIDDLEWARE_SECONDS = 12
# CACHE_MIDDLEWARE_KEY_PREFIX = ''


# A W S
# STATICFILES_DIRS = (
#     os.path.join(os.path.dirname(BASE_DIR), 'static', 'static_dirs'),
# )
# AWS_ACCESS_KEY_ID = ''
# AWS_SECRET_ACCESS_KEY = ''
# AWS_STORAGE_BUCKET_NAME = ''
# S3DIRECT_REGION = 'us-east-1'
# AWS_CLOUDFRONT_DOMAIN = ''
# STATICFILES_STORAGE = 'wipp.s3utils.StaticRootS3BotoStorage'  # static files
# STATIC_S3_PATH = 'media/'
# DEFAULT_FILE_STORAGE = 'wipp.s3utils.MediaRootS3BotoStorage'  # media uploads
# DEFAULT_S3_PATH = 'static/'
# S3_URL = '//{}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)

# # Without cloudfront
# MEDIA_URL = S3_URL + STATIC_S3_PATH
# STATIC_URL = S3_URL + DEFAULT_S3_PATH
# MEDIA_ROOT = '/home/ubuntu/domain.com/wipp/static/media'  # change to specific
# STATIC_ROOT = '/home/ubuntu/domain.com/wipp/static/static'  # change to specific

# # With cloudfront
# # MEDIA_URL = '//{}/{}'.format(AWS_CLOUDFRONT_DOMAIN, STATIC_S3_PATH)
# # STATIC_URL = '//{}/{}'.format(AWS_CLOUDFRONT_DOMAIN, DEFAULT_S3_PATH)

# AWS_FILE_EXPIRE = 200
# AWS_PRELOAD_METADATA = True
# AWS_S3_SECURE_URLS = True
# date_three_months_later = datetime.date.today() + datetime.timedelta(3 * 365 / 12)
# expires = date_three_months_later.strftime('%A, %d %B %Y 20:00:00 EST')
# AWS_HEADERS = {
#     'Expires': expires,
#     'Cache-Control': 'max-age=31536000',  # 365 days
# }

# H E R O K U
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static', 'static')
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(BASE_DIR), 'static', 'static_dirs'),
)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static', 'media')


# L O G G I N G
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}
