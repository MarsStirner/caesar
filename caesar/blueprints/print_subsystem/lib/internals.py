# -*- coding: utf-8 -*-
import datetime

from jinja2 import FileSystemLoader, FunctionLoader, PrefixLoader
from jinja2.environment import Environment
from flask import url_for
import jinja2.ext

from .query import Query
from .specialvars import StoredSql, SpecialVariable, SP, InlineSql
from ..models.models_all import rbPrintTemplate
from nemesis.app import app
from .context import CTemplateHelpers, ModelGetterProxy
from .html import escape, escapenl, HTMLRipper, date_toString, time_toString, addDays

__author__ = 'mmalkov'


class Render:
    standard = 0
    jinja2   = 1


class RenderTemplateException(Exception):
    class Type:
        syntax = 0
        other = 1

    def __init__(self, message, data=None):
        super(RenderTemplateException, self).__init__(message)
        self.data = data


def get_template_by_id(template_id):
    try:
        template_id = int(template_id)
    except (ValueError, TypeError):
        return
    template_data = Query(rbPrintTemplate).get(template_id)
    if template_data:
        if template_data.render != Render.jinja2:
            return u"<HTML><HEAD></HEAD><BODY>Шаблон имеет устаревший формат. Пожалуйста, переведите его в Jinja2</BODY></HTML>"
        if not template_data.templateText:
            return u"<HTML><HEAD></HEAD><BODY>Шаблон пуст</BODY></HTML>"
        macros = "{% import 'fs/_macros.html' as macros %}"
        return macros + template_data.templateText


def make_jinja_environment():
    from . import filters
    env = Environment(
        loader=PrefixLoader({
            'fs': FileSystemLoader('blueprints/print_subsystem/templates/print_subsystem'),
            'db': FunctionLoader(get_template_by_id),
        }),
        finalize=finalizer,
        extensions=(
            jinja2.ext.with_,
            jinja2.ext.do,
            jinja2.ext.loopcontrols,
        )
    )
    env.filters.update(
        (name[3:], getattr(filters, name))
        for name in dir(filters)
        if name.startswith('do_')
    )
    env.globals.update({
        'escape': escape,
        'escapenl': escapenl,
        'HTMLRipper': HTMLRipper,
        'hard_rip': HTMLRipper.hard_rip,
        'soft_rip': HTMLRipper.soft_rip,
        'setPageSize': setPageSize,
        'setOrientation': setOrientation,
        'setPageOrientation': setOrientation,
        'setMargins': setMargins,
        'setLeftMargin': setLeftMargin,
        'setTopMargin': setTopMargin,
        'setRightMargin': setRightMargin,
        'setBottomMargin': setBottomMargin,
        'helpers': CTemplateHelpers,
        "date_toString": date_toString,
        "time_toString": time_toString,
        "addDays": addDays,
        "images": url_for(".static", filename="i/", _external=True),
        "trfu_service": app.config['TRFU_URL'],
        'SpecialVariable': SpecialVariable,
        'SP': SP(),
        'StoredSql': StoredSql,
        'InlineSql': InlineSql,
        'Model': ModelGetterProxy(),
    })
    return env


def finalizer(obj):
    if obj is None:
        return ''
    elif isinstance(obj, datetime.datetime):
        return obj.strftime('%d.%m.%Y %H:%M')
    elif isinstance(obj, datetime.date):
        return obj.strftime('%d.%m.%Y')
    elif isinstance(obj, datetime.time):
        return obj.strftime('%H:%M')
    return obj


def setPageSize(page_size):
    return ''


def setOrientation(orientation):
    return ''


def setMargins(margin):
    return ''


def setLeftMargin(left_margin):
    return ''


def setTopMargin(top_margin):
    return ''


def setRightMargin(right_margin):
    return ''


def setBottomMargin(bottom_margin):
    return ''
