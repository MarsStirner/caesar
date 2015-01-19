# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

DB_DRIVER = 'postgresql+psycopg2'
DB_HOST = 'localhost'
DB_PORT = 5432
DB_USER = 'db_user'
DB_PASSWORD = 'db_password'

DB_CAESAR_NAME = 'db_name'
DB_KLADR_NAME = 'kladr'
DB_LPU_NAME = 'lpu_db_name'

DB_CONNECT_OPTIONS = ''

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

SYSTEM_USER = 'caesar'

WTF_CSRF_ENABLED = True
SECRET_KEY = ''

BLUEPRINTS_DIR = 'blueprints'

BEAKER_SESSION = {'session.type': 'file',
                  'session.data_dir': '/tmp/session/data',
                  'session.lock_dir': '/tmp/session/lock'}

TIME_ZONE = 'Europe/Moscow'
VESTA_URL = ''

try:
    from config_local import *
except ImportError:
    # no local config found
    pass

db_uri_format = '{0}://{1}:{2}@{3}:{4}/{5}{6}'

SQLALCHEMY_DATABASE_URI = db_uri_format.format(
    DB_DRIVER,
    DB_USER, DB_PASSWORD,
    DB_HOST, DB_PORT,
    DB_LPU_NAME, DB_CONNECT_OPTIONS
)

SQLALCHEMY_BINDS = {
    'kladr': db_uri_format.format(
        DB_DRIVER,
        DB_USER, DB_PASSWORD,
        DB_HOST, DB_PORT,
        DB_KLADR_NAME, DB_CONNECT_OPTIONS
    ),
    'caesar': db_uri_format.format(
        DB_DRIVER,
        DB_USER, DB_PASSWORD,
        DB_HOST, DB_PORT,
        DB_CAESAR_NAME, DB_CONNECT_OPTIONS
    )

}