# -*- coding: utf-8 -*-
import json
import datetime
from datetime import timedelta

from flask import g
from flask.ext.principal import identity_loaded, Principal, Permission, RoleNeed, UserNeed
from flask.ext.login import LoginManager, current_user
from flask import make_response, request, current_app
from database import db
from models import Settings, Users, Roles
from app import app
from functools import update_wrapper


def public_endpoint(function):
    function.is_public = True
    return function


def create_config_func(module_name, config_table):

    def _config(code):
        """Возвращает значение конфигурационной переменной, полученной из таблицы %module_name%_config"""
        #Get app_settings
        app_settings = dict()
        try:
            for item in db.session.query(Settings).all():
                app_settings.update({item.code: item.value})
            # app_settings = {item.code: item.value for item in db.session.query(Settings).all()}
        except Exception, e:
            print e

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
        if roles:
            for role in roles:
                permissions[role.code] = Permission(RoleNeed(role.code))
                permissions[role.code].description = role.description
        else:
            permissions['admin'] = Permission(RoleNeed('admin'))

# TODO: разобратсья как покрасивше сделать
admin_permission = permissions.get('admin')
user_permission = permissions.get('user')


# TODO: разобратсья c декоратором @crossdomain
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


class WebMisJsonEncoder(json.JSONEncoder):
    def default(self, o):
        from decimal import Decimal
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()
        elif isinstance(o, Decimal):
            return float(o)
        elif hasattr(o, '__json__'):
            return o.__json__()
        elif isinstance(o, db.Model) and hasattr(o, '__unicode__'):
            return unicode(o)
        return json.JSONEncoder.default(self, o)


def jsonify(obj, result_code=200, result_name='OK', extra_headers=None):
    indent = None
    headers = [('content-type', 'application/json; charset=utf-8')]
    if extra_headers:
        headers.extend(extra_headers)
    return (
        json.dumps({
            'result': obj,
            'meta': {
                'code': result_code,
                'name': result_name,
            }
        }, indent=indent, cls=WebMisJsonEncoder, encoding='utf-8', ensure_ascii=False),
        result_code,
        headers
    )