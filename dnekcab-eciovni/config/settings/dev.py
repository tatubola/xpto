from .common import *
from .common import env


DEBUG = True

SECRET_KEY = env(
    'DJANGO_SECRET_KEY',
    default='MQMhxeAlTYk9inSJoAt7WyLGX37P39NA1B7N3BXFrLRoQky7WkWCy1Tri4CqRiua'
)
ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'invoice_api',
        'USER': 'invoice_api',
        'PASSWORD': 'EulerInvoiceMaker@18651',
        'HOST': 'db',
        'PORT': 3360,
    }
}
