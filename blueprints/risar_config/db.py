# -*- coding: utf-8 -*-
import sqlalchemy
import sqlalchemy.orm

__author__ = 'viruzzz-kun'


url = 'mysql://tmis:q1w2e3r4t5@10.1.2.11/hospital1?charset=utf8'

db = sqlalchemy.create_engine(url)
Session = sqlalchemy.orm.sessionmaker(bind=db)


