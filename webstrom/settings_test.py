# pylint: disable=wildcard-import,unused-wildcard-import

from .settings import *

DEBUG = True

ALLOWED_HOSTS = [
    "test.strom.sk",
]

USE_X_FORWARDED_HOST = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'webstrom-test',
        'USER': 'webstrom',
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
