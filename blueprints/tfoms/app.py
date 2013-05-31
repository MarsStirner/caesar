# -*- coding: utf-8 -*-
import os
from flask import Blueprint

# Определяем название модуля по имени директории
MODULE_NAME = os.path.basename(os.path.dirname(__file__))
module = Blueprint(MODULE_NAME, __name__, template_folder='templates', static_folder='static')

from views import *