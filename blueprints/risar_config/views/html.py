# -*- coding: utf-8 -*-
from ..app import module
from flask import render_template, abort
from jinja2 import TemplateNotFound
from application.utils import public_endpoint

__author__ = 'viruzzz-kun'


@module.route('/')
@public_endpoint
def index():
    try:
        return render_template('risar_config/index.html')
    except TemplateNotFound:
        abort(404)