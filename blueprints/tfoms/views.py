# -*- encoding: utf-8 -*-
from flask import render_template, abort
from jinja2 import TemplateNotFound
from app import module


@module.route('/')
def index():
    try:
        return render_template('index.html')
    except TemplateNotFound:
        abort(404)
    return render_template('index.html')