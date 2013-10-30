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
    'memcached': 'django.core.cache.backends.memcached.MemcachedCache',
    'dummycache': 'django.core.cache.backends.dummy.DummyCache',
}

for scheme in SCHEMES.keys():
    urlparse.uses_netloc.append(scheme)


def get_database_url(env='DATABASE_URL'):
    url = os.environ[env]

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
        'PORT': url.port,
    }


def get_cache_url(env='DEFAULT_CACHE_URL', default='dummycache://'):
    url = urlparse.urlparse(os.environ.get(env, default))
    config = { 'BACKEND': SCHEMES[url.scheme] }

    if url.hostname and url.port:
        config['LOCATION'] = '{}:{}'.format(url.hostname, url.port)

    # The redis client has some stupid behavior
    if url.scheme == 'redis2':
        config['OPTIONS'] = { 'DB': url.path[1:] }
    elif url.scheme == 'redis3':
        config['LOCATION'] = '{}:{}:{}'.format(
                url.hostname, url.port, url.path[1:])

    return config


def get_debug_flag(env='DJANGO_DEBUG', default='false'):
    return os.environ.get(env, default).lower() == 'true'


def get_raven_config(env='SENTRY_DSN'):
    dsn = os.environ.get(env)
    return { 'dsn': dsn, 'register_signals': True } if dsn else None


def get_secret_key(env='SECRET_KEY'):
    key = os.environ.get(env)

    if key:
        return key
    else:
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join([random.choice(chars) for i in range(50)])
