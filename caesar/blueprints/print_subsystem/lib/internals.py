# -*- coding: utf-8 -*-
import datetime

from jinja2 import FileSystemLoader, TemplateSyntaxError
from jinja2.ext import Extension
from jinja2.environment import Environment
from flask import url_for

from nemesis.app import app
from context import CTemplateHelpers
from html import escape, escapenl, HTMLRipper, date_toString, time_toString, addDays


__author__ = 'mmalkov'


class Render:
    standard = 0
    jinja2 = 1
    hamlpy = 2


class RenderTemplateException(Exception):
    class Type:
        syntax = 0
        other = 1
    def __init__(self, message, data=None):
        super(RenderTemplateException, self).__init__(message)
        self.data = data


def make_jinja_environment():
    from .filters import do_datetime_format, do_datetime_combine, do_datetime_add_days, do_sum_columns, \
        do_table_column, do_table_uniform, do_transpose_table
    env = Environment(
        loader=FileSystemLoader('blueprints/print_subsystem/templates/print_subsystem'),
        finalize=finalizer,
    )
    env.filters.update({
        'datetime_format': do_datetime_format,
        'datetime_combine': do_datetime_combine,
        'datetime_add_days': do_datetime_add_days,
        'transpose_table': do_transpose_table,
        'sum_columns': do_sum_columns,
        'table_column': do_table_column,
        'table_uniform': do_table_uniform,
    })
    return env


def prepare_context(data):
    from blueprints.print_subsystem.models.models_utils import DateInfo

    context = dict(globals())
    now = datetime.datetime.now()
    context.update(prepare_globals())
    context.update({
        'now': now,
        'currentDate': DateInfo(now.date()),
        'currentTime': now.time().strftime("%H:%M:%S"),
        'helpers': CTemplateHelpers,
        "date_toString": date_toString,
        "time_toString": time_toString,
        "addDays": addDays,
        "images": url_for(".static", filename="i/", _external=True),
        "trfu_service": app.config['TRFU_URL'],
    })
    context.update(data)
    return context


def prepare_globals():
    return {
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
    }


def renderTemplate(template, data, render=1):
    if render == Render.jinja2:
        return render_jinja_template(template, data)
    elif render == Render.hamlpy:
        return render_haml_template(template, data)
    else:
        result = u"<HTML><HEAD></HEAD><BODY>Не удалось выполнить шаблон</BODY></HTML>"
    return result


def render_jinja_template(template, data):
    global_vars = prepare_globals()
    try:
        context = prepare_context(data)
        env = make_jinja_environment()
        macros = "{% import '_macros.html' as macros %}"
        return env.from_string(macros + template, globals=global_vars).render(context)
    except Exception:
        print "ERROR: template.render(data)"
        raise


def render_haml_template(template, data):
    global_vars = prepare_globals()
    try:
        context = prepare_context(data)
        env = make_jinja_environment()
        env.add_extension(HamlExtension)
        macros = "{% import '_macros.html' as macros %}"
        return env.from_string(macros + template, globals=global_vars).render(context)
    except Exception:
        print "ERROR: template.render(data)"
        raise


class HamlExtension(Extension):
    """Implementation of HAML pre-processing extension."""

    DEFAULT_INDENT_STRING = '  '
    DEFAULT_NEWLINE_STRING = '\n'

    def __init__(self, environment):
        """Configures the extension and environment."""

        super(HamlExtension, self).__init__(environment)

        environment.extend(haml_indent_string=self.DEFAULT_INDENT_STRING,
                           haml_newline_string=self.DEFAULT_NEWLINE_STRING)

    def preprocess(self, source, name, filename=None):
        """Preprocesses the template from HAML to Jinja-style HTML."""
        try:
            from pyhaml_jinja.renderer import Renderer

            renderer = Renderer(
                source,
                indent_string=self.environment.haml_indent_string,
                newline_string=self.environment.haml_newline_string
            )
        except TemplateSyntaxError, e:
            raise TemplateSyntaxError(e.message, e.lineno, name=name, filename=filename)
        except ImportError:
            return u'<HTML><HEAD></HEAD><BODY>Не установлен пакет pyhaml_jinja</BODY></HTML>'
        return renderer.render()


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
