from .base import *

DEBUG = env.str('DEBUG') in ['1', 'true']

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {
    "default": {
        "ENGINE": env.str("POSTGRES_ENGINE"),
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT"),
    }
}
