# -*- coding: utf-8 -*-
from database import db

TABLE_PREFIX = 'app'


class Settings(db.Model):
    __tablename__ = '%s_settings' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(25), unique=True, nullable=False)
    name = db.Column(db.Unicode(50), unique=True, nullable=False)
    value = db.Column(db.Unicode(100))

    def __unicode__(self):
        return self.name