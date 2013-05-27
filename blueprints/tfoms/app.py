# -*- coding: utf-8 -*-
from flask import Blueprint

module = Blueprint('tfoms', __name__, template_folder='templates', static_folder='static')

from views import *