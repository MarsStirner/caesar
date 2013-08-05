# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask.ext.principal import Principal
from database import db
from autoload import load_blueprints
import config

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
from models import *


from utils import login_manager
Principal(app)
login_manager.init_app(app)

#Register blueprints
blueprints_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', app.config['BLUEPRINTS_DIR']))
load_blueprints(app, apps_path=blueprints_path)

# Import all views
from views import *