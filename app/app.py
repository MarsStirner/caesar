# -*- coding: utf-8 -*-
from flask import Flask, request, session
from flask.ext.babelex import Babel
from models import db
from autoload import register_blueprints

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

#Register blueprints
register_blueprints(app, apps_package="blueprints", module_name="app", blueprint_name="module")


# Initialize babel
babel = Babel(app)


@babel.localeselector
def get_locale():
    override = request.args.get('lang')
    if override:
        session['lang'] = override
    return session.get('lang', 'ru')