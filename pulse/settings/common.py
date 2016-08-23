"""
Glossary of settings/common.py:

- Hosting + Authentication
- Email
- Internationalization
- Installed applications
- Middleware
- Password validation
- Templates
- Sessions
- File uploads
- API
"""

import os
import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


############################
# HOSTING + AUTHENTICATION #
############################
SECRET_KEY = '$_a8js0o91wk)4qjz_se%b#q47n%mzm^=ubwe+^9uu_ig%t2)4'
LOGIN_URL = "/login/"
LOGOUT_REDIRECT_URL = "/"
AUTH_USER_MODEL = 'accounts.MyUser'


#########
# EMAIL #
#########
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None


########################
# INTERNATIONALIZATION #
########################
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ','
USE_TZ = False


##########################
# INSTALLED APPLICATIONS #
##########################
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',

    'accounts',
    'api',
    'notifications',
    'parties',
)


##############
# MIDDLEWARE #
##############
MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)


ROOT_URLCONF = 'pulse.urls'
WSGI_APPLICATION = 'pulse.wsgi.application'


#######################
# PASSWORD VALIDATION #
#######################
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


#############
# TEMPLATES #
#############
CRISPY_TEMPLATE_PACK = "bootstrap3"


############
# SESSIONS #
############
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'


################
# FILE UPLOADS #
################
FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB

# A P I
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.AllowAny',
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'SEARCH_PARAM': 'q',
}
JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'core.utils.jwt_response_payload_handler',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=180),
    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=30),
    'JWT_SECRET_KEY': '=*jui$tj=89_99eqg0qqsrpe01ze4&n$(lr3ed&n0mtys9+t6!',
}
