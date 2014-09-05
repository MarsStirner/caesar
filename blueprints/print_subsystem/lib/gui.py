# -*- coding: utf-8 -*-

import logging
import traceback
from jinja2 import TemplateSyntaxError
from blueprints.print_subsystem.lib.internals import RenderTemplateException
from blueprints.print_subsystem.lib.utils import getTemplateName
from internals import renderTemplate
from utils import getTemplate
#from specialvars import getSpVarsUsedInTempl, getSpecialVariableValue, SpecialVariable

__author__ = 'mmalkov'


# def printTeleMed(widget, clientInfo, eventInfo, context, act_context, data, actionsInfo, unloadingType, person):
#     templates = getPrintTemplates(context)
#     templatesInfo = templates
#     def tryApply(templateInfo):
#         try:
#             return applyTemplateNoPrint(templateInfo[1], data)
#         except:
#             return (u'', u'',
#                 CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5),
#                 {})
#     def tryApply_actions(index):
#         data['action'] = actionsInfo[index]
#         templatesInfo.extend(getPrintTemplates(act_context[index]))
#         return map(tryApply, getPrintTemplates(act_context[index]))
#
#     allRendered = map(tryApply, templates)
#     map(lambda index: allRendered.extend(tryApply_actions(index)), xrange(len(act_context)))
#     allHtml = u"\n<br style='page-break-after: always;'>\n".join(map(lambda item: item[0], allRendered))
#     allCanvases = {}
#     map(lambda item: allCanvases.update(item[3]), allRendered)
#
#     reportView = CReportViewDialog(widget)
#
#     reportView.setText(allHtml)
#     reportView.setCanvases(allCanvases)
#     reportView.setPageFormat(CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5))
#     #templatesInfo.extend(templates)
#     if unloadingType == u"TeleMed":
#         reportView.setWindowTitle(u"Телемедицинская консультация")
#         reportView.saveAsFile()
#     elif unloadingType == u"EMK":
#         reportView.setWindowTitle(u"Выгрузка в ЭМК")
#         reportView.saveAsTelemedFile(clientInfo, eventInfo, templatesInfo, person)


def applyTemplate(templateId, data):
    u"""Выводит на печать шаблон печати номер templateId с данными data"""
    try:
        template = getTemplate(templateId)
        #spvars = getSpVarsUsedInTempl(templateId)#находим, используемые в шаблоне спец. переменные
        # if spvars:
        #     for i in spvars:
        #         data[i] = getSpecialVariableValue(i, params = None,  parent = widget)
        # data['SpecialVariable'] = SpecialVariable
        return applyTemplateInt(template, data)
    except TemplateSyntaxError, e:
        print e
        logging.error('syntax error in template id = %s', templateId, exc_info=True)
        raise RenderTemplateException(e.message, {
            'type': RenderTemplateException.Type.syntax,
            'template_name': getTemplateName(templateId),
            'lineno': e.lineno
        })
    except Exception, e:
        print unicode(traceback.format_exc(), 'utf-8')
        logging.critical('erroneous template id = %s', templateId, exc_info=True)
        raise RenderTemplateException(e.message, {
            'type': RenderTemplateException.Type.other,
            'template_name': getTemplateName(templateId),
            'trace': unicode(traceback.format_exc(), 'utf-8')
        })


def applyTemplateInt(template, data, render=1):
    u"""Выводит на печать шаблон печати по имени name с кодом template и данными data"""
    html = renderTemplate(template, data, render)
    return html