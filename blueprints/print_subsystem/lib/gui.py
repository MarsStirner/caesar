# -*- coding: utf-8 -*-
# from PyQt4 import QtGui, QtCore
# from PyQt4.QtCore import pyqtSignal, QVariant, QDate, Qt
# from Reports.ReportView import CReportViewDialog
# from library.Utils import forceRef, forceString
from internals import renderTemplate
#from specialvars import getSpVarsUsedInTempl, getSpecialVariableValue, SpecialVariable
from utils import getTemplate

__author__ = 'mmalkov'


# class CPrintAction(QtGui.QAction):
#     printByTemplate = pyqtSignal(int)
#     def __init__(self, name, id, emitter,  parent):
#         QtGui.QAction.__init__(self, name, parent)
#         self.id = id
#         self.emitter = emitter
#         self.dpdAgreement = None
#         self.triggered.connect(self.onTriggered)
#
#     def setDpdAgreement(self, dpdAgreement):
#         self.dpdAgreement = dpdAgreement
#
#     def onTriggered(self):
#         if self.dpdAgreement:
#             self.changeClientDpdAgreement(QtGui.qApp.currentClientId())
#         emitter = self.emitter or self
#         if self.id:
#             emitter.printByTemplate.emit(self.id)
#
#     def changeClientDpdAgreement(self, clientId):
#         if not clientId:
#             return
#         db = QtGui.qApp.db
#         dpdAccountingSystemId = forceRef(db.translate('rbAccountingSystem', 'code', u'ДПД', 'id'))
#         record = db.getRecordEx('ClientIdentification', '*', 'deleted=0 AND accountingSystem_id=%d AND client_id=%d'%(dpdAccountingSystemId, clientId))
#         if not record:
#             record = db.table('ClientIdentification').newRecord()
#             record.setValue('accountingSystem_id', QVariant(dpdAccountingSystemId))
#             record.setValue('client_id', QVariant(clientId))
#         value = u'Да' if self.dpdAgreement == 1 else u'Нет'
#         record.setValue('identifier', QVariant(value))
#         record.setValue('checkDate', QVariant(QDate.currentDate()))
#         db.insertOrUpdate('ClientIdentification', record)
#
#
# class CPrintButton(QtGui.QPushButton):
#     __pyqtSignals__ = ('printByTemplate(int)',
#                       )
#
#     def __init__(self, parent, name='', id=None):
#         QtGui.QPushButton.__init__(self, name, parent)
#         self.setId(id)
#         self.connect(self, QtCore.SIGNAL('clicked()'), self.onClicked)
#
#     def setId(self, id):
#         self.id = id
# #       if id:
# #            self.fileName = template[1]
# #            self.connect(self, QtCore.SIGNAL('clicked()'), self.onClicked)
# #        else:
# #            self.fileName = ''
#
#         self.actions = []
#         self.setMenu(None)
#
#
#     def addAction(self, action):
#         menu = self.menu()
#         if not menu:
#             menu = QtGui.QMenu(self)
#             self.setMenu(menu)
#         self.actions.append(action)
#         menu.addAction(action)
#
#
#     def onClicked(self):
#         if self.id:
#             self.emit(QtCore.SIGNAL('printByTemplate(int)'), self.id)
#
#
# def getPrintAction(parent, context, name=u'Печать'):
#     templates = getPrintTemplates(context)
#     actions = []
#     if not templates:
#         result = CPrintAction(name, None, None, parent)
#         result.setEnabled(False)
# #        result.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
#     elif len(templates) == 1:
#         result = CPrintAction(name, templates[0][1], None, parent)
#         result.setDpdAgreement(templates[0][2])
#         actions.append(result)
#         result.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
#     else:
#         result = CPrintAction(name, None, None, parent)
#         menu = QtGui.QMenu(parent)
#         for i, template in enumerate(templates):
#             action = CPrintAction(template[0], template[1], result, menu)
#             action.setDpdAgreement(template[2])
#             menu.addAction(action)
#             actions.append(action)
#             if i == 0:
#                 action.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
#         result.setMenu(menu)
# #        result.setShortcut(QtGui.QKeySequence(Qt.ALT+Qt.Key_F6))
#     return result
#
#
# def customizePrintButton(btn, context):
#     templates = getPrintTemplates(context)
#     if not templates:
#         btn.setId(None)
#         btn.setEnabled(False)
#         btn.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
#     elif len(templates) == 1:
#         btn.setId(templates[0][1])
#         btn.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
#         btn.setEnabled(True)
#     else:
#         btn.setId(None)
#         btn.setEnabled(True)
#         for i, template in enumerate(templates):
#             action = CPrintAction(template[0], template[1], btn, btn)
#             btn.addAction(action)
#             if i == 0:
#                 btn.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
#         btn.setShortcut(QtGui.QKeySequence(Qt.ALT+Qt.Key_F6))
#
#
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
    except Exception as e:
        raise


def applyTemplateInt(template, data, render=1):
    u"""Выводит на печать шаблон печати по имени name с кодом template и данными data"""
    html = renderTemplate(template, data, render)
    return html


# def getPrintButton(parent, context='', name=u'Печать'):
#     result = CPrintButton(parent, name, None)
#     customizePrintButton(result, context)
#     return result