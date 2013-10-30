DEBUG = TEMPLATE_DEBUG = get_debug_flag()
DATABASES = { 'default': get_database_url() }
RAVEN_CONFIG = get_raven_config()

CACHES = {
  'default': get_cache_url('DEFAULT_CACHE_URL'),
}
