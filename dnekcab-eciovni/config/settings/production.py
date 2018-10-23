# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

from .common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'invoice_api',
        'USER': 'invoice_api',
        'PASSWORD': 'xWU7yZ0fX4xA97r6',
        'HOST': 'drop.in.ceptro.br',
        'PORT': 3306,
        }
}

