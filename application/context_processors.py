# -*- coding: utf-8 -*-
from application.app import app
from werkzeug.utils import import_string


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
            if hasattr(config, 'RUS_NAME'):
                menu_items.append(dict(module=v.name, name=config.RUS_NAME))
            else:
                menu_items.append(dict(module=v.name, name=v.name))

    return dict(main_menu=menu_items)