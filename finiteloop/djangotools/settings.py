import os
import random
import ConfigParser
import copy
import dateutil.parser
import urllib2
from pytz import timezone
from collections import namedtuple

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
    'redis4': 6379,
    'smtp': 25,
    'memcached': 11211,
    'smtps': 587,
}
DEFAULT_TIME_ZONE = "America/New_York"

for scheme in set(SCHEMES.keys() + DEFAULT_PORTS.keys()):
    urlparse.uses_netloc.append(scheme)

def get_time_zone(env='TIME_ZONE', default=None):
    default = default or DEFAULT_TIME_ZONE
    return os.environ.get(env, default)

def get_media_path(env='SHARED_PATH', default=None):
    shared_path = os.environ.get(env, None)

    if shared_path == None:
        return default

    return os.path.join(os.path.expanduser('~'), shared_path, 'site_media')


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

    if url.scheme == 'sqlite':
        return {
                'ENGINE': SCHEMES[url.scheme],
                'NAME': url.path
        }

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

def get_allowed_hosts(env='ALLOWED_HOSTS', default=''):
    return [h.strip() for h in os.environ.get(env, default).split(',')]

def get_raven_config(env='SENTRY_DSN'):
    dsn = os.environ.get(env)
    return { 'dsn': dsn, 'register_signals': True } if dsn else {}


class MailConfig(object):
    """This is used for telling django what email server to
    connect with to send email.  To correctly used this
    add the following to your settings.py or settings_local.py:

        import sys
        from finiteloop.djangotools.settings import MailConfig

        # This loads and sets the email configuration
        MailConfig.set(sys.modules[__name__])

    This object will read the environment variable EMAIL_SERVER
    which should be formatted like:

        smtp://<username>:<password>@<hostname>:<port>
    or the following for TLS:
        smtps://<username>:<password>@<hostname>:<port>

    """
    DEFAULT = 'smtp://:@localhost:25'
    BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    def __init__(self, env='EMAIL_SERVER', default=None):
        default = default or self.DEFAULT
        self.url = urlparse.urlparse(os.environ.get(env, default))
        self._data = {}

    @property
    def data(self):
        if not self._data:
            if self.url.scheme in ('smtp', 'smtps',):
                self._data['EMAIL_BACKEND'] = self.BACKEND
                self._data['EMAIL_HOST'] = self.url.hostname
                self._data['EMAIL_HOST_PASSWORD'] = urllib2.unquote(self.url.password)
                self._data['EMAIL_HOST_USER'] = urllib2.unquote(self.url.username)
                self._data['EMAIL_PORT'] = self.url.port
                self._data['EMAIL_USE_TLS'] = self.url.scheme == 'smtps'
            else:
                msg = "unknown scheme '{}'".format(url.scheme)
                raise ValueError(msg)
        return self._data

    def set_settings(self, the_module):
        keys = self.data.keys()
        keys.sort()
        for key in keys:
            setattr(the_module, key, self.data[key])

    @classmethod
    def set(cls, the_module, env='EMAIL_SERVER', default=None):
        obj = cls(env=env, default=default)
        obj.set_settings(the_module)


def get_secret_key(env='SECRET_KEY'):
    key = os.environ.get(env)

    if key:
        return key
    else:
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join([random.choice(chars) for i in range(50)])

class ReleaseInfo(object):

    DEFAULT_TZ = "America/New_York"
    FILENAME = "manifest.cfg"
    RELEASE_OPTIONS = ['app', 'ref', 'sha', 'date', 'type', 'by']
    TEMPLATE = {'release': {}, 'migrations': []}

    def __init__(self, filename, tz):
        self.filename = filename
        self.tz = tz
        self._config_ = None
        self._build_output = namedtuple('ReleaseInfo', 'release migrations')
        self._build_release = namedtuple('ReleaseData', self.RELEASE_OPTIONS)

    @classmethod
    def get(cls, dirname, filename=None, tz=None):
        """Returns a named tuple containing the release information
        :param dirname: is the directory where the release file may exist
        :param filename: is the name of the file to load. Default: manifest.cfg
        :param tz: is the text description of the timezone needed to display.
                   Default: America/New_York
        """
        if not os.path.exists(dirname) or not os.path.isdir(dirname):
            raise Exception("{} does not exist".format(dirname))

        filename = filename or cls.FILENAME
        filename = os.path.join(dirname, filename)

        tz = tz or timezone(cls.DEFAULT_TZ)
        if isinstance(tz, basestring):
            tz = timezone(tz)

        obj = cls(filename, tz)
        return obj()

    def __call__(self):
        data = copy.copy(self.TEMPLATE)
        self.release_info(data)
        self.migration_info(data)

        data['migrations'].sort()

        args = []
        for key in self.RELEASE_OPTIONS:
            args.append(data['release'][key])

        release_info = self._build_release(*args)
        out = self._build_output(release_info, data['migrations'])
        return out

    @property
    def config(self):
        if not self._config_:
            self._config_ = ConfigParser.RawConfigParser()
            if (os.path.exists(self.filename) and
                        os.path.isfile(self.filename)):
                self._config_.read(self.filename)
        return self._config_

    def release_info(self, data):
        for key in self.RELEASE_OPTIONS:
            val = None
            if self.config.has_option('release', key):
                if key == 'date':
                    date = dateutil.parser.parse(self.config.get('release',
                           key))
                    val = date.astimezone(self.tz)
                else:
                    val = self.config.get('release', key)

            data['release'][key] = val

    def migration_info(self, data):
        for section in self.config.sections():
            if section.startswith('migrations'):
                app = section.split(':')[1]
                for option in self.config.options(section):
                    if self.config.get(section, option) == 'true':
                        data['migrations'].append("{} {}".format(app, option))

