"""
Contains every configuration variable for the application.
"""

import time
from os import getenv
from typing import List

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

load_dotenv("environments/staging.env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DEBUG_MODE") == "true"

ALLOWED_HOSTS: List[str] = ["*"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "core",
    "apps.raw_data",
    "apps.stocks",
    "apps.transactions",
    "apps.dashboard",
    "apps.cash",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": getenv("DATABASE_NAME"),
        "USER": getenv("DATABASE_USER"),
        "PASSWORD": getenv("DATABASE_PASSWORD"),
        "HOST": getenv("DATABASE_HOST"),
        "PORT": getenv("DATABASE_PORT"),
    }
}


# Password validation
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


# Internationalization
LANGUAGE_CODE = getenv("LANGUAGE")

TIME_ZONE = getenv("TIME_ZONE")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files
STATIC_URL = "/static/"


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

TEST_RUNNER = "core.test.runner.PostgresSchemaTestRunner"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]

# We only want to report and configure logging in non-development environments.
environment = getenv("PYTHON_ENV")

# Logging config
if environment != "ci":
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": f"[%(asctime)s{time.strftime('%z')}] %(levelname)s - %(message)s",
            },
            "verbose": {
                "format": f"""
                    %(asctime)s{
                        time.strftime('%z (%Z)')
                    } | %(levelname)s | %(message)s | %(module)s | %(process)d | %(thread)d
                """,
            },
        },
        "handlers": {
            "console": {
                "level": getenv("LOG_LEVEL"),
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "info_file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "filename": getenv("LOG_INFO_PATH"),
                "formatter": "verbose",
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "filename": getenv("LOG_ERROR_PATH"),
                "formatter": "verbose",
            },
        },
        "loggers": {
            "": {"level": "DEBUG", "handlers": ["console", "info_file", "error_file"]},
        },
    }


if environment in ("staging", "production"):
    # pylint: disable=abstract-class-instantiated
    sentry_sdk.init(
        dsn="https://7eb17183206c490f9f6283b1707cec07@o1120245.ingest.sentry.io/6155939",
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.0,
        send_default_pii=True,
        environment=environment,
    )
