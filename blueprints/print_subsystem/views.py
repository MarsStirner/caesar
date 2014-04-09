# -*- encoding: utf-8 -*-

from flask import make_response
from flask import render_template, abort, request
from jinja2 import TemplateNotFound

from app import module
from application.utils import public_endpoint, jsonify
from blueprints.print_subsystem.models import Rbprinttemplate
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
        data = request.get_json()
        template_id = data['id']
        print_obj = Print_Template()
        print_obj.get_template_meta(template_id)
        return render_template('{0}/index.html'.format(module.name))
    except TemplateNotFound:
        abort(404)


@public_endpoint
@module.route('/print_template', methods=["OPTIONS"])
def print_template_options():
    return jsonify(None, extra_headers=[
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Method', 'POST'),
        ('Access-Control-Allow-Headers', 'Content-Type')
    ])


@public_endpoint
@module.route('/print_template', methods=["POST"])
def print_template_post():
    data = request.get_json()
    context_type = data['context_type']
    template_id = data['id']
    print_obj = Print_Template()

    html = print_obj.print_template(context_type, template_id, data)
    response = make_response(html, 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Method'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@module.route('/templates/')
@module.route('/templates/<context>.json')
@public_endpoint
def api_templates(context=None):
    # Не пора бы нам от этой ерунды избавиться?
    from .utils import get_lpu_session
    db = get_lpu_session()
    if not context:
        return jsonify(None)
    templates = db.query(Rbprinttemplate).filter(Rbprinttemplate.context == context)
    return jsonify([{
        'id': t.id,
        'code': t.code,
        'name': t.name,
        'meta': {},
    } for t in templates])