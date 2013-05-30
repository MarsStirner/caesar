# -*- coding: utf-8 -*-
from flask import Blueprint
from .config import MODULE_NAME

module = Blueprint(MODULE_NAME, __name__, template_folder='templates', static_folder='static')

from views import *