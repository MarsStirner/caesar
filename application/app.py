# -*- coding: utf-8 -*-
import os
from flask import Flask, request, session
from flask.ext.babelex import Babel
from database import db
from autoload import load_blueprints
import config

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)

#Register blueprints
blueprints_path = os.path.abspath(app.config['BLUEPRINTS_DIR'])
load_blueprints(app, apps_path=blueprints_path)


# Initialize babel
# TODO: delete if not used
babel = Babel(app)


@babel.localeselector
def get_locale():
    override = request.args.get('lang')
    if override:
        session['lang'] = override
    return session.get('lang', 'ru')


# Import all views
from views import *