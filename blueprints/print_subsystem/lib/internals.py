# -*- coding: utf-8 -*-
from jinja2 import Template
from jinja2 import FileSystemLoader
from jinja2.environment import Environment

from context import CTemplateContext
from html import escape, escapenl, HTMLRipper, date_toString, time_toString, addDays
from flask import url_for

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


def renderTemplate(template, data, render=1):
    # Формируем execContext
    global_vars = {
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
        'setBottomMargin': setBottomMargin
    }
    #
    # useful_builtins = dict((key, __builtins__[key]) for key in (
    #     'abs', 'all', 'any', 'bin', 'bool', 'bytes', 'chr', 'complex', 'dict', 'enumerate', 'filter',
    #     'float', 'hash', 'hex', 'id', 'int', 'iter', 'len', 'list', 'long', 'map', 'max', 'min', 'next',
    #     'oct', 'ord', 'pow', 'range', 'reduce', 'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum',
    #     'tuple', 'unichr', 'unicode', 'xrange', 'zip'))
    # global_vars.update(useful_builtins)

    execContext = CTemplateContext(global_vars, data)

    if render == Render.jinja2:
        try:
            context = {}
            context.update(execContext.builtin)
            context.update(execContext.globals)
            context.update(execContext.data)
            context.update({"now": execContext.now,
                            "date_toString": date_toString,
                            "time_toString": time_toString,
                            "addDays": addDays,
                            "images": url_for(".static", filename="i/", _external=True)
                            })
            env = Environment()
            env.loader = FileSystemLoader('blueprints/print_subsystem/templates/print_subsystem')
            macros = "{% import '_macros.html' as macros %}"
            result = env.from_string(macros+template, globals=global_vars).render(context)
        except Exception:
            print "ERROR: template.render(data)"
            # QtGui.qApp.log('Template code failed', str(context))
            # QtGui.qApp.logCurrentException()
            raise
    else:
        result = u"<HTML><HEAD></HEAD><BODY>Не удалось выполнить шаблон</BODY></HTML>"
    # canvases = execContext.getCanvases()
    # for k in canvases:
    #     print k, canvases[k]
    return result


def suppress_nones(obj):
    return obj if obj is not None else ''


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
