# -*- coding: utf-8 -*-
from .config import MODULE_NAME
from flask import Blueprint, g

module = Blueprint(MODULE_NAME, __name__, template_folder='templates', static_folder='static')


def _config(code):
    """Возвращает значение конфигурационной переменной, полученной из таблицы tfoms_config_variables"""
    config = g.get('%s_config' % module.name, None)
    if not config:
        values = db.session.query(ConfigVariables).all()
        setattr(g, '%s_config' % module.name, dict())
        config = g.get('%s_config' % module.name, None)
        for value in values:
            config[value.code] = value.value
    return config.get(code, None)


from .views import *