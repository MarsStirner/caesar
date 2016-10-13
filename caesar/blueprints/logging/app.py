# -*- coding: utf-8 -*-
from flask import Blueprint, redirect
from nemesis.app import app

module = Blueprint('logging', __name__)


@module.route('/')
def index():
    return redirect(app.config['SIMPLELOGS_URL'])
