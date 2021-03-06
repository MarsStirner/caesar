# -*- coding: utf-8 -*-
from .config import MODULE_NAME, RUS_NAME
from flask import Blueprint
from .utils import _config

module = Blueprint(MODULE_NAME, __name__, template_folder='templates', static_folder='static')


@module.context_processor
def module_name():
    return dict(module_name=RUS_NAME)


from .views import *