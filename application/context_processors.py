# -*- coding: utf-8 -*-
from application.app import app
from werkzeug.utils import import_string
from application.utils import current_user


@app.context_processor
def general_menu():
    menu_items = list()
    blueprints = app.blueprints
    for k, v in blueprints.items():
        try:
            config = import_string('%s.config' % import_string(v.import_name).__package__)
        except ImportError, e:
            print e
        else:
            menu_items.append(dict(module=v.name,
                                   name=getattr(config, 'RUS_NAME', v.name),
                                   descr=getattr(config, 'DESCR', u'Нет описания'),
                                   ))
    return dict(main_menu=menu_items)


@app.context_processor
def user_role():
    roles = getattr(current_user, 'roles', [])
    if len(roles):
        current_user.role = roles[0].code
    else:
        current_user.role = None
    return dict()