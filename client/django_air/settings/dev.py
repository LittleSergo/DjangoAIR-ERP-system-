from .base import *

DEBUG = True

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {
    "default": {
        "ENGINE": env.str("SQL_ENGINE"),
        "NAME": env.str("SQL_DATABASE"),
        "USER": env.str("SQL_USER"),
        "PASSWORD": env.str("SQL_PASSWORD"),
        "HOST": env.str("SQL_HOST"),
        "PORT": env.str("SQL_PORT"),
    }
}
