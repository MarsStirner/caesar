# -*- coding: utf-8 -*-
# from PyQt4 import QtGui, QtCore
import codecs
import logging
import os
# import sip
# from library.Journaling import CJournaling
# from library.TextDocument import CTextDocument
# from library.Utils import forceString, forceInt, forceRef
# from internals import renderTemplate, CPageFormat
#from specialvars import getSpVarsUsedInTempl, getSpecialVariableValue, SpecialVariable
from ..utils import get_lpu_session
from ..models.models_all import Rbprinttemplate

__author__ = 'mmalkov'


def getPrintTemplates(context):
    result = []
    if context:
        try:
            db = QtGui.qApp.db
            table = db.table('rbPrintTemplate')
            for record in db.getRecordList(table, 'name, id, dpdAgreement, fileName, code', table['context'].eq(context),'code, name, id'):
                name = forceString(record.value('name'))
                id = forceInt(record.value('id'))
                dpdAgreement = forceInt(record.value('dpdAgreement'))
                fileName = forceString(record.value('fileName'))
                code = forceString(record.value('code'))
                result.append((name, id, dpdAgreement, fileName, code))
        except:
            QtGui.qApp.logCurrentException()
    return result


def getPrintTemplatesDict(context):
    result = {}
    if not context:
        return result
    db = QtGui.qApp.db
    table = db.table('rbPrintTemplate')
    fields = (table['id'], table['code'], table['name'], table['fileName'], table['default'], table['render'])
    cond = (table['context'].eq(context),)
    records = db.getRecordList(table, fields, cond)
    if not records:
        return result
    for record in records:
        fileName = forceString(record.value('fileName'))
        html = forceString(record.value('default'))
        code = forceString(record.value('code'))
        renderer = forceInt(record.value('render'))
        _id = forceRef(record.value('id'))
        name = forceString(record.value('name'))
        if fileName:
            try:
                with open(fileName) as infile:
                    html = infile.read()
            except:
                pass
        result[code] = {'code': code,
                        'name': name,
                        'html': html,
                        'id': _id,
                        'renderer': renderer,
                        }
    return result


def getTemplate(templateId):
    u"""Получает код шаблона печати"""
    logging.debug(u'template_id: %s', templateId)
    record = Rbprinttemplate.query.get(templateId)
    logging.debug(u'record: %s', record)
    fileName = record.fileName
    name = record.name
    context = record.context
    result = record.templateText
    # if fileName: из файла
    #     fullPath = os.path.join(QtGui.qApp.getTemplateDir(), fileName)
    #     if os.path.isfile(fullPath):
    #         for enc in ['utf-8', 'cp1251']:
    #             try:
    #                 with codecs.open(fullPath, encoding=enc, mode='r') as f:
    #                     result = f.read()
    #                     #return JinjaEnv.get_template(fileName), render
    #             except:
    #                 pass
    # result = u''.join(map(unicode.rstrip, result.splitlines()))
    if not result:
        result = u'<HTML><BODY>шаблон документа пуст или испорчен</BODY></HTML>'
    #CJournaling.newLogRecord(u"notice", u"Печать документа '%s' из %s"%(name, context), ["print document"])
    return result


def applyTemplateNoPrint(templateId, data):
    name = forceString(QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'name'))
    template, render = getTemplate(templateId)
    spvars = getSpVarsUsedInTempl(templateId)#находим, используемые в шаблоне спец. переменные
    if spvars:
        for i in spvars:
            data[i] = getSpecialVariableValue(i, params = None)
    data['SpecialVariable'] = SpecialVariable
    pageFormat = CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5)
    html, canvases = renderTemplate(template, data, pageFormat, render)
    return html, name, pageFormat, canvases


def printTextDocument(document, documentName, pageFormat, printer):
    printer.setCreator(u'КОРУС Консалтинг')
    printer.setDocName(documentName)
    outDocument = document
    if pageFormat:
        pageFormat.updateFromPrinter(printer)
        outDocument = document.clone(document)
        pd = document.documentLayout().paintDevice()
        if pd is None:
            pd = QtGui.qApp.desktop()
            document.documentLayout().setPaintDevice(pd)
        pd_logicalDpiX = pd.logicalDpiX()
        pd_logicalDpiY = pd.logicalDpiY()
        p_logicalDpiX = printer.logicalDpiX()
        p_logicalDpiY = printer.logicalDpiY()

        pageRect = printer.pageRect() # in pixels
        paperRect = printer.paperRect() # in pixels

        # hardware defined margins, in printer pixels
        hl = (pageRect.left()   - paperRect.left())
        ht = (pageRect.top()    - paperRect.top())
        hr = (paperRect.right() - pageRect.right())
        hb = (paperRect.bottom() -pageRect.bottom())

        # software defined margins, in printer pixels
        sl = pageFormat.leftMargin * p_logicalDpiX / 25.4 # 25.4 mm = 1 inch
        st = pageFormat.topMargin * p_logicalDpiY / 25.4
        sr = pageFormat.rightMargin * p_logicalDpiX / 25.4
        sb = pageFormat.bottomMargin * p_logicalDpiY / 25.4

        # margins
        ml = max(0, sl-hl)
        mt = max(0, st-ht)
        mr = max(0, sr-hr)
        mb = max(0, sb-hb)

        fmt = outDocument.rootFrame().frameFormat()
        fmt.setLeftMargin(ml / p_logicalDpiX * pd_logicalDpiX) #Sets the frame's left margin in in some parrots (screen pixels?)
        fmt.setTopMargin(mt/ p_logicalDpiY * pd_logicalDpiY)
        fmt.setRightMargin(mr / p_logicalDpiX * pd_logicalDpiX)
        fmt.setBottomMargin(mb / p_logicalDpiY * pd_logicalDpiY)
        outDocument.rootFrame().setFrameFormat(fmt)
        # Calculate page width and height, in screen pixels
        pw = float(pageRect.width()) / p_logicalDpiX * pd_logicalDpiX
        ph = float(pageRect.height()) / p_logicalDpiY * pd_logicalDpiY
        # setup page size
        outDocument.setPageSize(QtCore.QSizeF(pw, ph))
    outDocument.print_(printer)
    if outDocument != document:
        sip.delete(outDocument)


def directPrintTemplateInt(name, template, data, printer, render=0):
    pageFormat = CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5)
    html, canvases = renderTemplate(template, data, pageFormat, render)
    document = CTextDocument()
    document.setHtml(html)
    document.setCanvases(canvases)
    pageFormat.setupPrinter(printer)
    printTextDocument(document, name, pageFormat, printer)


def directPrintTemplate(templateId, data, printer):
    name = forceString(QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'name'))
    template, render = getTemplate(templateId)
    directPrintTemplateInt(name, template, data, printer, render)