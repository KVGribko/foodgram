import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-no*ifnwb+@-ote%17t*6iem#xj!fteu_q1lgq!g$fiev5y+u79",
)

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "import_export",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "djoser",
    "users.apps.UsersConfig",
    "api.apps.ApiConfig",
    "recipes.apps.RecipesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

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

WSGI_APPLICATION = "foodgram.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", default="postgres"),
        "USER": os.getenv("POSTGRES_USER", default="postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", default="postgres"),
        "HOST": os.getenv("DB_HOST", default="localhost"),
        "PORT": os.getenv("DB_PORT", default="32702"),
    }
}

AUTH_USER_MODEL = "users.User"

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
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
}

DJOSER = {
    "HIDE_USERS": False,
    "LOGIN_FIELD": "email",
    "PERMISSIONS": {
        "user_list": ["rest_framework.permissions.AllowAny"],
        "user": ["djoser.permissions.CurrentUserOrAdminOrReadOnly"],
    },
    "SERIALIZERS": {
        "user_create": "api.serializers.UsersCreateSerializerForDjoser",
        "user": "api.serializers.UserSerializer",
        "current_user": "api.serializers.UserSerializer",
        "user_list": "api.serializers.UserSerializer",
    },
}


LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static/")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_PAGE_SIZE = 10
