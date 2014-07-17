# -*- encoding: utf-8 -*-

from flask import render_template, abort, request, url_for, send_file
from jinja2 import TemplateNotFound

from app import module
from application.utils import public_endpoint, jsonify, crossdomain, string_to_datetime
from blueprints.print_subsystem.models.models_all import Rbprinttemplate
from lib.data import Print_Template


PER_PAGE = 20
xml_encodings = ['windows-1251', 'utf-8']


@module.route('/')
def index():
    try:
        return render_template('{0}/index.html'.format(module.name))
    except TemplateNotFound:
        abort(404)


@public_endpoint
@module.route('/print_template', methods=["POST", "OPTIONS"])
@crossdomain('*', methods=['POST', 'OPTIONS'], headers='Content-Type')
def print_templates_post():
    data = request.get_json()
    if data.get('separate', True):
        separator = '\n\n<div style="page-break-after: always" ></div>\n\n'
    else:
        separator = '\n\n'
    result = [
        Print_Template().print_template(doc)
        for doc in data.get('documents', [])
    ]
    font_url_ttf = url_for(".fonts", filename="Code39Azalea.ttf", _external=True)
    font_url_eot = url_for(".fonts", filename="Code39Azalea.eot", _external=True)
    font_url_woff = url_for(".fonts", filename="Code39Azalea.woff", _external=True)
    font_url_svg = url_for(".fonts", filename="Code39Azalea.svg", _external=True)
    template_style = url_for(".static", filename="css/template_style.css", _external=True)
    style = u'''
                <style>
                        @font-face{font-family:Code39AzaleaFont;
                                    src:url('%s') format('embedded-opentype'),
                                    url('%s') format('woff'),
                                    url('%s') format('truetype'),
                                    url('%s') format('svg');
                                    font-weight:normal;font-style:normal}
                </style>
                <link rel="stylesheet" href="%s"/>
                        ''' % (font_url_eot, font_url_woff, font_url_ttf, font_url_svg, template_style)
    return style + separator.join(result)

@public_endpoint
@module.route('/fonts')
@module.route('/fonts/<filename>')
@crossdomain('*', methods=['GET'])
def fonts(filename=None):
    return send_file('../blueprints/print_subsystem/static/%s' % filename)


@module.route('/templates/')
@module.route('/templates/<context>.json')
@public_endpoint
@crossdomain('*', methods=['GET'])
def api_templates(context=None):
    # Не пора бы нам от этой ерунды избавиться?
    # Неа, нам нужно подключение к разным БД (http://stackoverflow.com/questions/7923966/flask-sqlalchemy-with-dynamic-database-connections)
    # А в Гиппократе всё работает. Там те же две БД.
    if not context:
        return jsonify(None)
    templates = Rbprinttemplate.query.filter(Rbprinttemplate.context == context)
    return jsonify([{
        'id': t.id,
        'code': t.code,
        'name': t.name,
        'meta': t.meta_data,
    } for t in templates])
