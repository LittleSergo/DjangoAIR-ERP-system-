from .base import *

DEBUG = True

ALLOWED_HOSTS = [env.str('ALLOWED_HOSTS')]

DATABASES = {
    'default': env.db('DATABASE_URL')
}
