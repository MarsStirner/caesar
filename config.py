# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

DB_DRIVER = 'mysql'
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = ''
DB_PASSWORD = ''
DB_NAME = ''
DB_CONNECT_OPTIONS = '?charset=utf8'

SYSTEM_USER = ''

CSRF_ENABLED = True
SECRET_KEY = ''

BLUEPRINTS_DIR = 'blueprints'

try:
    from config_local import *
except ImportError:
    # no local config found
    pass

SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(DB_DRIVER,
                                                       DB_USER,
                                                       DB_PASSWORD,
                                                       DB_HOST,
                                                       DB_PORT,
                                                       DB_NAME,
                                                       DB_CONNECT_OPTIONS)