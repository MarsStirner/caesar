# -*- coding: utf-8 -*-
import sqlalchemy
import sqlalchemy.orm.session
from sqlalchemy.ext.declarative import declarative_base
from config import SQLALCHEMY_DATABASE_URI

__author__ = 'viruzzz-kun'


db = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
session_maker = sqlalchemy.orm.session.sessionmaker(bind=db)

Base = declarative_base()
metadata = Base.metadata
