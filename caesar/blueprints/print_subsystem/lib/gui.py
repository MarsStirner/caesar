# -*- coding: utf-8 -*-

import logging
import traceback
from flask import g
from jinja2 import TemplateSyntaxError
from caesar.blueprints.print_subsystem.lib.internals import RenderTemplateException
from caesar.blueprints.print_subsystem.models.models_all import rbPrintTemplate
from internals import renderTemplate
from html import HTMLRipper


__author__ = 'mmalkov'


simple_logger = logging.getLogger('simple')


def applyTemplate(templateId, data):
    u"""Выводит на печать шаблон печати номер templateId с данными data"""
    template_data = g.printing_session.query(rbPrintTemplate).get(templateId)
    if not template_data:
        simple_logger.error(u'Шаблон с id=%s не найден' % templateId)
        raise RenderTemplateException(u'Шаблон с id=%s не найден' % templateId, {
            'type': RenderTemplateException.Type.other,
            'template_name': '<unknown>',
            'trace': '',
        })
    try:
        return renderTemplate(template_data.templateText, data)
    except TemplateSyntaxError, e:
        simple_logger.critical(u'Синтаксическая ошибка в шаблоне id = %s', templateId, exc_info=True)
        logging.error(u'syntax error in template id = %s', templateId, exc_info=True)
        raise RenderTemplateException(e.message, {
            'type': RenderTemplateException.Type.syntax,
            'template_name': template_data.name,
            'lineno': e.lineno
        })
    except Exception, e:
        simple_logger.critical(u'Ошибка при генерации шаблона id = %s', templateId, exc_info=True)
        logging.critical(u'erroneous template id = %s', templateId, exc_info=True)
        tb = traceback.format_exc()
        if isinstance(tb, str):
            tb = tb.decode('utf-8')
        raise RenderTemplateException(e.message, {
            'type': RenderTemplateException.Type.other,
            'template_name': template_data.name,
            'trace': tb,
        })


def applyExternTemplate(template_name, templateText, data):
    try:
        return renderTemplate(templateText, data)
    except TemplateSyntaxError, e:
        simple_logger.critical(u'Синтаксическая ошибка в шаблоне "%s"', template_name, exc_info=True)
        logging.error(u'syntax error in template "%s"', template_name, exc_info=True)
        raise RenderTemplateException(e.message, {
            'type': RenderTemplateException.Type.syntax,
            'template_name': template_name,
            'lineno': e.lineno
        })
    except Exception, e:
        simple_logger.critical(u'Ошибка при генерации шаблона "%s"', template_name, exc_info=True)
        logging.critical(u'erroneous template "%s"', template_name, exc_info=True)
        tb = traceback.format_exc()
        if isinstance(tb, str):
            tb = tb.decode('utf-8')
        raise RenderTemplateException(e.message, {
            'type': RenderTemplateException.Type.other,
            'template_name': template_name,
            'trace': tb,
        })


def applyInnerTemplate(context, code, data):
    u"""Рендерит вложенный шаблон печати по context и code с данными data.
    Используется через тег include_rb_template, который добавляется в
    расширении IncludeRbTemplateExtension."""
    if data is None:
        data = {}
    template_data = g.printing_session.query(rbPrintTemplate).filter(
        rbPrintTemplate.context == context,
        rbPrintTemplate.code == code
    ).first()
    if not template_data:
        return u'Не найден шаблон по context={0} и code={1}'.format(context, code)
    try:
        template_string = renderTemplate(template_data.templateText, data)
    except TemplateSyntaxError, e:
        logging.error(u'syntax error in template id = %s', template_data.id, exc_info=True)
        raise RenderTemplateException(e.message, {
            'type': RenderTemplateException.Type.syntax,
            'template_name': template_data.name,
            'lineno': e.lineno
        })
    except Exception, e:
        logging.critical(u'erroneous template id = %s', template_data.id, exc_info=True)
        tb = traceback.format_exc()
        if isinstance(tb, str):
            tb = tb.decode('utf-8')
        raise RenderTemplateException(e.message, {
            'type': RenderTemplateException.Type.other,
            'template_name': template_data.name,
            'trace': tb,
        })

    template_string = HTMLRipper.gentlest_rip(template_string)
    return template_string