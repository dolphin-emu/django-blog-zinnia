"""Settings for Zinnia documentation"""

DATABASES = {'default': {'NAME': ':memory:',
                         'ENGINE': 'django.db.backends.sqlite3'}}

SITE_ID = 1

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

STATIC_URL = '/static/'

SECRET_KEY = 'secret-key'
INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.auth',
    'mptt', 'tagging', 'zinnia']

SILENCED_SYSTEM_CHECKS = ['1_7.W001']
