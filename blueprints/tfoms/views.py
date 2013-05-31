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


@module.route('/download/')
def download():
    try:
        return render_template('download.html')
    except TemplateNotFound:
        abort(404)


@module.route('/upload/')
def upload():
    try:
        return render_template('upload.html')
    except TemplateNotFound:
        abort(404)


@module.route('/reports/')
def reports():
    try:
        return render_template('reports.html')
    except TemplateNotFound:
        abort(404)


@module.route('/settings/')
def settings():
    try:
        return render_template('settings.html')
    except TemplateNotFound:
        abort(404)


@module.route('/settings_template/')
@module.route('/settings_template/<string:template_type>/')
def settings_template(template_type='xml_patient'):
    try:
        return render_template('settings_templates/%s.html' % template_type)
    except TemplateNotFound:
        abort(404)


@module.route('/<string:page>.html')
def show_page(page):
    try:
        return render_template('/%s.html' % page)
    except TemplateNotFound:
        abort(404)