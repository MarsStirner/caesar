# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
PROFILE = False
PROJECT_NAME = 'Caesar'

# DB connecting params
DB_DRIVER = 'mysql'
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'db_user'
DB_PASSWORD = 'db_password'
DB_NAME = 'db_name'
DB_CONNECT_OPTIONS = ''

DB_CAESAR_NAME = 'caesar'
DB_KLADR_NAME = 'kladr'
DB_LPU_NAME = 'lpu_db_name'

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

SYSTEM_USER = 'hippo'

WTF_CSRF_ENABLED = True
SECRET_KEY = ''

BLUEPRINTS_DIR = 'blueprints'

BABEL_DEFAULT_LOCALE = 'ru_RU'

BEAKER_SESSION = {'session.type': 'file',
                  'session.data_dir': '/tmp/session/data',
                  'session.lock_dir': '/tmp/session/lock',
                  'session.key': '{0}.beaker.session.id'.format(os.path.basename(os.path.abspath('..')))}

TIME_ZONE = 'Europe/Moscow'

SIMPLELOGS_URL = 'http://127.0.0.1:8080'

SEARCHD_CONNECTION = {
    'host': '127.0.0.1',
    'port': 9306,
}

ORGANISATION_INFIS_CODE = 500
PRINT_SUBSYSTEM_URL = ''
VESTA_URL = ''
TRFU_URL = ''
WEBMIS10_URL = ''
COLDSTAR_URL = ''
SIMARGL_URL = ''
CASTIEL_AUTH_TOKEN = 'CastielAuthToken'

TITLE = u'Администрирование ЛПУ'
COPYRIGHT_COMPANY = u''
LPU_STYLE = 'FNKC'

INDEX_HTML = 'caesar_index.html'
FILE_STORAGE_PATH = ''


CELERY_ENABLED = False
from celery_config import *


try:
    from config_local import *
except ImportError:
    print('no local config')

db_uri_format = '{0}://{1}:{2}@{3}:{4}/{5}{6}'

SQLALCHEMY_DATABASE_URI = db_uri_format.format(
    DB_DRIVER,
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_CONNECT_OPTIONS
)

SQLALCHEMY_BINDS = {
    'caesar': db_uri_format.format(
        DB_DRIVER,
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT,
        DB_CAESAR_NAME,
        DB_CONNECT_OPTIONS),
    'kladr': db_uri_format.format(
        DB_DRIVER,
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT,
        DB_KLADR_NAME,
        DB_CONNECT_OPTIONS),
    'celery_tasks': db_uri_format.format(
        CAT_DB_DRIVER, CAT_DB_USER, CAT_DB_PASSWORD, CAT_DB_HOST, CAT_DB_PORT, CAT_DB_NAME, CAT_DB_CONNECT_OPTIONS
    ),
}
