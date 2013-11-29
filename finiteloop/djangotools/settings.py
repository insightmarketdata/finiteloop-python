import os
import random

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


SCHEMES = {
    'postgres': 'django.db.backends.postgresql_psycopg2',
    'postgresql': 'django.db.backends.postgresql_psycopg2',
    'postgis': 'django.contrib.gis.db.backends.postgis',
    'mysql': 'django.db.backends.mysql',
    'mysql2': 'django.db.backends.mysql',
    'sqlite': 'django.db.backends.sqlite3',
    'redis2': 'redis_cache.cache.RedisCache',
    'redis3': 'redis_cache.cache.RedisCache',
    'redis4': 'redis_cache.cache.RedisCache',
    'memcached': 'django.core.cache.backends.memcached.MemcachedCache',
    'dummycache': 'django.core.cache.backends.dummy.DummyCache',
}

DEFAULT_PORTS = {
    'postgres': 5432,
    'postgresql': 5432,
    'postgis': 5432,
    'mysql': 3306,
    'mysql2': 3306,
    'redis2': 6379,
    'redis3': 6379,
    'smtp': 25,
    'memcached': 11211,
    'smtps': 587,
}

for scheme in set(SCHEMES.keys() + DEFAULT_PORTS.keys()):
    urlparse.uses_netloc.append(scheme)


def get_database_url(env='DATABASE_URL', default=None):
    url = os.environ.get(env, default)

    if url is None:
        return

    if url == 'sqlite://:memory:' or url == 'sqlite://':
        return {
            'ENGINE': SCHEMES['sqlite'],
            'NAME': ':memory:',
        }

    url = urlparse.urlparse(url)

    return {
        'ENGINE': SCHEMES[url.scheme],
        'NAME': url.path[1:].split('?', 2)[0],
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname,
        'PORT': url.port or DEFAULT_PORTS.get(url.scheme),
    }


def get_cache_url(env='DEFAULT_CACHE_URL', default='dummycache://'):
    url = urlparse.urlparse(os.environ.get(env, default))
    config = { 'BACKEND': SCHEMES[url.scheme] }

    if url.hostname and url.port:
        config['LOCATION'] = '{}:{}'.format(url.hostname,
                url.port or DEFAULT_PORTS.get(url.scheme))

    # The redis client has some stupid behavior
    if url.scheme == 'redis2':
        config['OPTIONS'] = { 'DB': url.path[1:] }
    elif url.scheme == 'redis3':
        config['LOCATION'] = '{}:{}:{}'.format(
                url.hostname, url.port or DEFAULT_PORTS.get(url.scheme),
                url.path[1:])
    elif url.scheme == 'redis4':
        config['LOCATION'] = '{}:{}:{}'.format(
                url.hostname, url.port or DEFAULT_PORTS.get(url.scheme),
                url.path[1:])
        config['OPTIONS'] = {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        }

    return config


def get_debug_flag(env='DJANGO_DEBUG', default='false'):
    return os.environ.get(env, default).lower() == 'true'


def get_raven_config(env='SENTRY_DSN'):
    dsn = os.environ.get(env)
    return { 'dsn': dsn, 'register_signals': True } if dsn else None


def get_mail_config(env='EMAIL_SERVER', default=None):
    url = os.environ.get(env, default)

    if url is None:
        return {}

    url = urlparse.urlparse(url)
    return {
        'EMAIL_USE_TLS': url.scheme == 'smtps',
        'EMAIL_HOST': url.hostname,
        'EMAIL_PORT': url.port or DEFAULT_PORTS.get(url.scheme),
        'EMAIL_HOST_USER': url.username,
        'EMAIL_HOST_PASSWORD': url.password,
    }


def get_secret_key(env='SECRET_KEY'):
    key = os.environ.get(env)

    if key:
        return key
    else:
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join([random.choice(chars) for i in range(50)])
