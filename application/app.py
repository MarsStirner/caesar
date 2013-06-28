# -*- coding: utf-8 -*-
import os
from flask import Flask
from database import db
from autoload import load_blueprints
import config

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)

#Register blueprints
blueprints_path = os.path.abspath(app.config['BLUEPRINTS_DIR'])
load_blueprints(app, apps_path=blueprints_path)


# Import all views
from views import *