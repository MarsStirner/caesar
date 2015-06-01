# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.orm.session import sessionmaker
from .config import MODULE_NAME, RUS_NAME
from flask import Blueprint, g
from nemesis.app import app

module = Blueprint(MODULE_NAME, __name__, template_folder='templates', static_folder='static')


@module.context_processor
def module_name():
    return dict(module_name=RUS_NAME)


@module.before_request
def setup_database():
    db = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], pool_recycle=3600, echo=app.config['SQLALCHEMY_ECHO'])
    session_maker = sessionmaker(bind=db, autoflush=False, autocommit=False)
    g.printing_session = session_maker()
    g.printing_session._model_changes = {}

@module.after_request
def teardown_database(response):
    g.printing_session.rollback()
    del g.printing_session
    return response

from .views import *
from .models import *