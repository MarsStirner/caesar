# -*- coding: utf-8 -*-
from config import MODULE_NAME
from flask import Blueprint

module = Blueprint(MODULE_NAME, __name__, template_folder='templates', static_folder='static')

from views import *