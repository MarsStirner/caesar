# -*- coding: utf-8 -*-
from caesar.blueprints.utils import check_admin_profile
from .config import MODULE_NAME, RUS_NAME
from flask import Blueprint

module = Blueprint(MODULE_NAME, __name__, template_folder='templates', static_folder='static')


@module.context_processor
def module_name():
    return dict(module_name=RUS_NAME)


@module.before_request
def admin_profile_requirement():
    check_admin_profile()


from .views import *