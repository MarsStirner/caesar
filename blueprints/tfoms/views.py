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


@module.route('/<string:page>.html')
def show_page(page):
    try:
        return render_template('/%s.html' % page)
    except TemplateNotFound:
        abort(404)