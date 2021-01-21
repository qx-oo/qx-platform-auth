"""
Django settings for qx_test project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$tt5-+tnu8g63n1)77s_zikqy1fvbmy03y1x4nnotgh2s#j%^@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'qx_base.qx_core',
    'qx_base.qx_rest',
    'qx_base.qx_user',
    'qx_platform_auth',
    'qx_test.user',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'qx_test.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'qx_test.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'qx_test',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# RestFramework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'qx_base.qx_user.auth.JwtAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS':
        'qx_base.qx_rest.paginations.Pagination',
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ),
    'EXCEPTION_HANDLER': 'qx_base.qx_rest.handlers.rest_exception_handler',
    'PAGE_SIZE': 15,
}

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = ""
REDIS_URL = "redis://:{}@{}:{}".format(
    REDIS_PASSWORD,
    REDIS_HOST,
    REDIS_PORT)

AUTH_USER_MODEL = 'user.User'

JWT_TOKEN_KEYWORD = 'token'

PRODUCTION = True

QX_BASE_SETTINGS = {
    'SEND_MOBILE_MSG_CLASS': 'qx_test.msg.TestMsg',
    'SEND_EMAIL_MSG_CLASS': 'qx_test.msg.TestMsg',
    'USERINFO_MODEL': "user.UserInfo",
    'USERINFO_SERIALIZER_CLASS': "qx_test.user.serializers.UserinfoSerializer",  # noqa
}

QX_PLATFORM_AUTH_SETTINGS = {
    "APPLE_AUTH": {
        "APPLE_KEY_ID": 'test',
        "APPLE_TEAM_ID": 'test',
        "APPLE_CLIENT_ID": 'test',
        "APPLE_CLIENT_SECRET": '-----BEGIN PUBLIC KEY-----MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDdlatRjRjogo3WojgGHFHYLugdUWAY9iR3fy4arWNA1KoS8kVw33cJibXr8bvwUAUparCwlvdbH6dvEOfou0/gCFQsHUfQrSDv+MuSUMAe8jzKE4qW+jK+xQU9a03GUnKHkkle+Q0pX/g6jXZ7r1/xAK5Do2kQ+X5xK9cipRgEKwIDAQAB-----END PUBLIC KEY-----',  # noqa
        "APPLE_REDIRECT_URI": 'test',
    },
    "PLATFORM_AUTH_MODEL": 'user.UserPlatform',
    "MINIAPP_TOKEN_KEY": "test_key",
    "MINIAPP_TOKEN_SECRET": "test_secret",
    "MINIAPP_TOKEN_PROD_URL": "https://127.0.0.1:8000/user/miniapp/accesstoken/",  # noqa
    "MINIAPP_PLATFORM_MAP": {
        "testapp": "qx_test.user.miniapps.WXTestApp",
    }
}
