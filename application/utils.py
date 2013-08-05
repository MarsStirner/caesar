# -*- coding: utf-8 -*-
from flask import g
from flask.ext.principal import identity_loaded, Principal, Permission, RoleNeed, UserNeed
from flask.ext.login import LoginManager, current_user
from database import db
from models import Settings, Users, Roles
from app import app


def create_config_func(module_name, config_table):

    #Remember app_settings to globals
    with app.app_context():
        with app.app_context():
            app_settings = dict()
            try:
                app_settings = {item.code: item.value for item in db.session.query(Settings).all()}
            except Exception, e:
                print e

    def _config(code):
        """Возвращает значение конфигурационной переменной, полученной из таблицы config_table"""
        config = getattr(g, '%s_config' % module_name, None)
        if not config:
            values = db.session.query(config_table).all()
            config = dict()
            for value in values:
                config[value.code] = value.value
            setattr(g, '%s_config' % module_name, config)
        config.update(app_settings)
        return config.get(code, None)

    return _config

with app.app_context():
    permissions = dict()
    login_manager = LoginManager()
    try:
        roles = db.session.query(Roles).all()
    except Exception, e:
        print e
        permissions['admin'] = Permission(RoleNeed('admin'))
    else:
        for role in roles:
            permissions[role.code] = Permission(RoleNeed(role.code))
            permissions[role.code].description = role.description

# TODO: разобратсья как покрасивше сделать
admin_permission = permissions.get('admin')
user_permission = permissions.get('user')
