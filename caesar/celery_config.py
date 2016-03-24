
# main settings
CELERY_BROKER_URL = ''  # redis://:password@hostname:port/db_number / redis+socket:///path/to/redis.sock
CELERY_RESULT_BACKEND = None

# tuning
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Europe/Moscow'
CELERYD_CONCURRENCY = 2
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 * 3  # in seconds, default 1 day

# sql database for celery application task (CAT) info and results
CAT_DB_DRIVER = 'mysql'
CAT_DB_HOST = 'localhost'
CAT_DB_PORT = 3306
CAT_DB_NAME = 'celery_tasks'
CAT_DB_USER = 'user'
CAT_DB_PASSWORD = 'password'
CAT_DB_CONNECT_OPTIONS = '?charset=utf8'


try:
    from celery_config_local import *
except ImportError:
    print('no local config')