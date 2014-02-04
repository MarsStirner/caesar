# -*- coding: utf-8 -*-
from datetime import date

from ..app import module, _config
from ..utils import get_lpu_session
from ..models import Client, Orgstructure, Person, Organisation
from gui import applyTemplate
from info.OrgInfo import CClientInfo
from info.PrintInfo import CInfoContext


class Print_Template(object):

    def __init__(self):
        self.db_session = get_lpu_session()
        self.today = date.today()

    def __del__(self):
        self.db_session.close()

    def get_template_meta(self, template_id):
        query = '''{0}'''.format(template_id)

        return self.db_session.execute(query)

    def print_template(self, template_id, client_id, additional_context):
        #template_record = self.get_template(template_id)
        # context = CInfoContext()
        client = self.db_session.query(Client).get(18)
        currentOrganisation = self.db_session.query(Organisation).get(additional_context['currentOrganisation']) if \
            additional_context['currentOrganisation'] else ""
        currentOrgStructure = self.db_session.query(Orgstructure).get(additional_context['currentOrgStructure']) if \
            additional_context['currentOrgStructure'] else ""
        currentPerson = self.db_session.query(Person).get(additional_context['currentPerson']) if \
            additional_context['currentPerson'] else ""
        data = {'currentOrganisation': currentOrganisation,
                'currentOrgStructure': currentOrgStructure,
                'currentPerson': currentPerson,
                'client': client,
                'currentActionIndex': 0,  # на самом деле мы ничего не знаем о текущем индексе действия
                }
        return applyTemplate(template_id, data)


# class OrgsructureFull(Orgstructure):


# def getTemplate(templateId):
#     u"""Получает код шаблона печати"""
#     db = QtGui.qApp.db
#     table = db.table('rbPrintTemplate')
#     record = db.getRecordEx(table,
#                             [table['default'], table['render'], table['fileName'], table['name'], table['context']],
#                             table['id'].eq(templateId))
#     logging.debug(u'record: %s', record)
#     fileName = forceString(record.value(2))
#     name = forceString(record.value(3))
#     context = forceString(record.value(4))
#     render = forceInt(record.value(1))
#     result = forceString(record.value(0))
#     # if fileName:  чтение текста шаблона из файла
#     #     fullPath = os.path.join(QtGui.qApp.getTemplateDir(), fileName)
#     #     if os.path.isfile(fullPath):
#     #         for enc in ['utf-8', 'cp1251']:
#     #             try:
#     #                 with codecs.open(fullPath, encoding=enc, mode='r') as f:
#     #                     result = f.read()
#     #                     #return JinjaEnv.get_template(fileName), render
#     #             except:
#     #                 pass
#     result = u''.join(map(unicode.rstrip, result.splitlines()))
#     if not result:
#         result = u'<HTML><BODY>шаблон документа пуст или испорчен</BODY></HTML>'
#     #CJournaling.newLogRecord(u"notice", u"Печать документа '%s' из %s"%(name, context), ["print document"])
#     return result, render
#
#
# def renderTemplate(template, data, pageFormat=None, render=1):
#     # Формируем infoContext
#     infoContext = None
#     for item in data.itervalues():
#         if isinstance(item, CInfo):
#             infoContext = item.context
#             if infoContext:
#                 break
#     if not infoContext:
#         infoContext = CInfoContext()
#     if not pageFormat:
#         pageFormat = CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5)
#     # Формируем execContext
#     global_vars = {
#         'escape': escape,
#         'escapenl': escapenl,
#         'HTMLRipper': HTMLRipper,
#         'hard_rip': HTMLRipper.hard_rip,
#         'soft_rip': HTMLRipper.soft_rip,
#         'setPageSize': pageFormat.setPageSize,
#         'setOrientation': pageFormat.setOrientation,
#         'setPageOrientation': pageFormat.setOrientation,
#         'setMargins': pageFormat.setMargins,
#         'setLeftMargin': pageFormat.setLeftMargin,
#         'setTopMargin': pageFormat.setTopMargin,
#         'setRightMargin': pageFormat.setRightMargin,
#         'setBottomMargin': pageFormat.setBottomMargin,
#     }
#
#     # useful_builtins = dict((key, __builtins__[key]) for key in (
#     #     'abs', 'all', 'any', 'bin', 'bool', 'bytes', 'chr', 'complex', 'dict', 'enumerate', 'filter',
#     #     'float', 'hash', 'hex', 'id', 'int', 'iter', 'len', 'list', 'long', 'map', 'max', 'min', 'next',
#     #     'oct', 'ord', 'pow', 'range', 'reduce', 'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum',
#     #     'tuple', 'unichr', 'unicode', 'xrange', 'zip'))
#     # global_vars.update(useful_builtins)
#
#     execContext = CTemplateContext(global_vars, data, infoContext)
#
#     if render == 1:
#         try:
#             context = {}
#             context.update(execContext.builtin)
#             context.update(execContext.globals)
#             context.update(execContext.data)
#             context.update({"now": execContext.now,
#                             "page": pageFormat,
#                             "date_toString": date_toString,
#                             "time_toString": time_toString,
#                             })
#             result = Template(template).render(context)
#         except Exception:
#             print "ERROR: template.render(data)"
#             # QtGui.qApp.log('Template code failed', str(context))
#             # QtGui.qApp.logCurrentException()
#             raise
#     else:
#         result = u"<HTML><HEAD></HEAD><BODY>Не удалось выполнить шаблон</BODY></HTML>"
#     canvases = execContext.getCanvases()
#     for k in canvases:
#         print k, canvases[k]
#     return result, canvases
#
#
# def date_toString(object_QDate, format):
#     return QDate.toString(object_QDate, format)
#
#
# def time_toString(object_QTime, format):
#     return QTime.toString(object_QTime, format)
#
#
# def date(self, date):
#     date = forceDate(date)
#     if type(date) == CDateInfo:
#         date = date.date
#     if type(date) != QDate:
#         date = QDate.fromString(unicode(date), u"dd.MM.yyyy")
#     return CDateProxy(date)
#
#
# def applyTemplate(templateId, data):
#     u"""Выводит на печать шаблон печати номер templateId с данными data"""
#     try:
#         name = forceString(QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'name'))
#         template, render = getTemplate(templateId)
#         #spvars = getSpVarsUsedInTempl(templateId)#находим, используемые в шаблоне спец. переменные
#         # if spvars:
#         #     for i in spvars:
#         #         data[i] = getSpecialVariableValue(i, params = None,  parent = widget)
#         # data['SpecialVariable'] = SpecialVariable
#         applyTemplateInt(name, template, data, render)
#     except Exception as e:
#         QtGui.QMessageBox.critical(None, u"Ошибка печати", u"Не могу сформировать документ для печати.\n\n%s" % e)
#         raise
#
#
# def applyTemplateInt(name, template, data, render=0):
#     u"""Выводит на печать шаблон печати по имени name с кодом template и данными data"""
#     pageFormat = CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5)
#     html, canvases = renderTemplate(template, data, pageFormat, render)