# -*- coding: utf-8 -*-

from flask import render_template, abort
from application.app import app
from application.context_processors import general_menu


@app.route('/')
def index():
    return render_template('base.html')
