# -*- encoding: utf-8 -*-
import re
import os
from datetime import datetime

from flask import render_template, abort, request, redirect, jsonify, send_from_directory, url_for, json, current_app
from flask.ext.sqlalchemy import Pagination

from jinja2 import TemplateNotFound, Environment, PackageLoader
from app import module

from application.database import db
from application.utils import public_endpoint
from lib.data import Print_Template


PER_PAGE = 20
xml_encodings = ['windows-1251', 'utf-8']

@module.route('/')
def index():
    try:
        return render_template('{0}/index.html'.format(module.name))
    except TemplateNotFound:
        abort(404)


@module.route('/template_meta', methods=["POST"])
def template_meta():
    try:
        data = json.loads(request.data)
        template_id = data['id']
        print_obj = Print_Template()
        print_obj.get_template_meta(template_id)
        return render_template('{0}/index.html'.format(module.name))
    except TemplateNotFound:
        abort(404)

@public_endpoint
@module.route('/print_template', methods=["POST", "GET"])
def print_template():
    try:
        data = json.loads(request.data)
        context_type = data['context_type']
        template_id = data['id']
        print_obj = Print_Template()
        return print_obj.print_template(context_type, template_id, data), 200, [('Access-Control-Allow-Origin', '*')]
    except TemplateNotFound:
        abort(404)