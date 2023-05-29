import os
from pathlib import Path

from decouple import config, Csv
from dj_database_url import parse as dburl
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)

BASE_URL = config("BASE_URL", default="http://localhost:8000")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django_extensions",
    'rest_framework',
    'rest_framework.authtoken',
    "ai_experiment.core.apps.CoreConfig",
    "ai_experiment.user.apps.UserConfig",
    "ai_experiment.mega_api.apps.MegaApiConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


ROOT_URLCONF = "ai_experiment.urls"

WSGI_APPLICATION = "ai_experiment.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
default_dburl = "sqlite:///" / BASE_DIR / "db.sqlite3"
DATABASES = {"default": config("DATABASE_URL", default=default_dburl, cast=dburl)}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    #  'DEFAULT_THROTTLE_CLASSES': [
        #  'rest_framework.throttling.AnonRateThrottle',
        #  'rest_framework.throttling.UserRateThrottle'
    #  ],
    #  'DEFAULT_THROTTLE_RATES': {
        #  'anon': '60/min',
        #  'user': '10/second'
    #  }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "pt-BR"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True

USE_L10N = True


# Sentry
SENTRY_DSN = config("SENTRY_DSN", default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/usuario/login"

AUTH_USER_MODEL = "user.UserModel"

# Celery
CELERY_BROKER_URL = config("CELERY_URL", default="redis://localhost:6379")
accept_content = ["application/json"]
result_serializer = "json"
timezone = TIME_ZONE

SEND_CHECKIN_LINK__MAX_RETRIES = config("SEND_CHECKIN_LINK__MAX_RETRIES", default=2)
SEND_CHECKIN_LINK__DEFAULT_RETRY_DELAY = config(
    "SEND_CHECKIN_LINK__DEFAULT_RETRY_DELAY", default=1
)

OPENAI_API_KEY = config("OPENAI_API_KEY")

LOCAL_TRANSCRIPTION = config("LOCAL_TRANSCRIPTION", cast=bool, default=True)

# Mega API

MEGA_API_HOST_TEST = config("MEGA_API_HOST_TEST")
MEGA_API_INSTANCE_KEY_TEST = config("MEGA_API_INSTANCE_KEY_TEST")
