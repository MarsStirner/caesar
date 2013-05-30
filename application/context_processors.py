# -*- coding: utf-8 -*-
import sys
from application.app import app
from werkzeug.utils import import_string


@app.context_processor
def general_menu():
    mod_names = list()
    blueprints = app.blueprints
    for k, v in blueprints.items():
        try:
            config = import_string('%s.config' % import_string(v.import_name).__package__)
        except ImportError, e:
            print e
        else:
            if hasattr(config, 'RUS_NAME'):
                mod_names.append(dict(url=v.name, name=config.RUS_NAME))
            else:
                mod_names.append(dict(url=v.name, name=v.name))

    return dict(main_menu=mod_names)