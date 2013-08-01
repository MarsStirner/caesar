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


class Role(db.Model):
    __tablename__ = '%s_role' % TABLE_PREFIX

    id = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(20), unique=True)
    name = db.Column(db.Unicode(80), unique=True)
    description = db.Column(db.Unicode(255))


class User(db.Model):
    __tablename__ = '%s_user' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    roles = db.relationship('Role',
                            secondary='%s_users_roles' % TABLE_PREFIX,
                            backref=db.backref('users', lazy='dynamic'))


class UsersRoles(db.Model):
    __tablename__ = '%s_users_roles' % TABLE_PREFIX

    user_id = db.Column(db.Integer, db.ForeignKey(User.id)),
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id)),