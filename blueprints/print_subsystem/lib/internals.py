# -*- coding: utf-8 -*-
from StringIO import StringIO
# from PyQt4 import QtGui
import re
import sys

from jinja2 import Environment, FileSystemLoader, Template
# from PyQt4.QtCore import QSizeF

from info.PrintInfo import CInfo, CInfoContext
from context import CTemplateContext
#from html import escape, escapenl, HTMLRipper, date_toString, time_toString
#from renderer import CTemplateParser


__author__ = 'mmalkov'


class Render:
    standard = 0
    jinja2   = 1


class JinjaEnv(object):
    """jinja environment"""

    jinja_environment = None

    @classmethod
    def get_template(cls, template_name):
        if not cls.jinja_environment:
            cls.jinja_environment = Environment(
                loader=FileSystemLoader(QtGui.qApp.getTemplateDir()))
        return cls.jinja_environment.get_template(template_name)


def renderTemplate(template, data, pageFormat=None, render=1):
    # Формируем infoContext
    infoContext = None
    for item in data.itervalues():
        if isinstance(item, CInfo):
            infoContext = item.context
            if infoContext:
                break
    if not infoContext:
        infoContext = CInfoContext()
    # if not pageFormat:
    #     pageFormat = CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5)
    # Формируем execContext
    # global_vars = {
    #     'escape': escape,
    #     'escapenl': escapenl,
    #     'HTMLRipper': HTMLRipper,
    #     'hard_rip': HTMLRipper.hard_rip,
    #     'soft_rip': HTMLRipper.soft_rip,
    #     'setPageSize': pageFormat.setPageSize,
    #     'setOrientation': pageFormat.setOrientation,
    #     'setPageOrientation': pageFormat.setOrientation,
    #     'setMargins': pageFormat.setMargins,
    #     'setLeftMargin': pageFormat.setLeftMargin,
    #     'setTopMargin': pageFormat.setTopMargin,
    #     'setRightMargin': pageFormat.setRightMargin,
    #     'setBottomMargin': pageFormat.setBottomMargin,
    # }
    #
    # useful_builtins = dict((key, __builtins__[key]) for key in (
    #     'abs', 'all', 'any', 'bin', 'bool', 'bytes', 'chr', 'complex', 'dict', 'enumerate', 'filter',
    #     'float', 'hash', 'hex', 'id', 'int', 'iter', 'len', 'list', 'long', 'map', 'max', 'min', 'next',
    #     'oct', 'ord', 'pow', 'range', 'reduce', 'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum',
    #     'tuple', 'unichr', 'unicode', 'xrange', 'zip'))
    # global_vars.update(useful_builtins)

    # execContext = CTemplateContext(global_vars, data, infoContext)
    execContext = CTemplateContext(data)

    if render == Render.jinja2:
        try:
            context = {}
            context.update(execContext.builtin)
            # context.update(execContext.globals)
            context.update(execContext.data)
            # context.update({"now": execContext.now,
            #                 "page": pageFormat,
            #                 "date_toString": date_toString,
            #                 "time_toString": time_toString,
            #                 })
            result = Template(template).render(context)
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


# class CPageFormat(object):
#     # page size
#     A3 = QtGui.QPrinter.A3
#     A4 = QtGui.QPrinter.A4
#     A5 = QtGui.QPrinter.A5
#     A6 = QtGui.QPrinter.A6
#     # page orientation
#     Portrait = QtGui.QPrinter.Portrait
#     Landscape = QtGui.QPrinter.Landscape
#     #
#     validPageSizes = { A3: A3, 'A3': A3,
#                        A4: A4, 'A4': A4,
#                        A5: A5, 'A5': A5,
#                        A6: A6, 'A6': A6
#                      }
#     validOrientations = { Portrait: Portrait,  'PORTRAIT': Portrait,  'P':Portrait,
#                           Landscape:Landscape, 'LANDSCAPE':Landscape, 'L':Landscape
#                      }
#
#     def __init__(self, pageSize=QtGui.QPrinter.A4,
#                         orientation=QtGui.QPrinter.Portrait,
#                         leftMargin=10,
#                         topMargin=10,
#                         rightMargin=10,
#                         bottomMargin=10
#                 ):
#         self.pageSize = pageSize
#         self.pageRect = None # для custom size
#         self.orientation = orientation
#         self.leftMargin = leftMargin
#         self.topMargin = topMargin
#         self.rightMargin = rightMargin
#         self.bottomMargin = bottomMargin
#
#
#     def setupPrinter(self, printer):
#         printer.setPageSize(self.pageSize)
#         printer.setPageMargins(self.leftMargin, self.topMargin,
#                                self.rightMargin, self.bottomMargin, QtGui.QPrinter.Millimeter)
#         if self.pageSize == QtGui.QPrinter.Custom and self.pageRect:
#             printer.setPaperSize(self.pageRect, QtGui.QPrinter.Millimeter)
#         printer.setOrientation(self.orientation)
#
#
#     def updateFromPrinter(self, printer):
#         self.pageSize = printer.pageSize()
#         if self.pageSize == QtGui.QPrinter.Custom:
#             self.pageRect = printer.paperSize(QtGui.QPrinter.Millimeter)
#         else:
#             self.pageRect = None
#         self.orientation = printer.orientation()
#
#
#     def setPageSize(self, size):
#         if isinstance(size, basestring):
#             size = size.upper().strip()
#             customSize = re.match(r'^(\d+)\s*[xX]\s*(\d+)$', size)
#             if customSize:
#                 self.pageSize = QtGui.QPrinter.Custom
#                 sizes = customSize.groups()
#                 self.pageRect = QSizeF(float(sizes[0]), float(sizes[1]))
#                 return ''
#         validPageSize = self.validPageSizes.get(size, None)
#         if validPageSize is not None:
#             self.pageSize = validPageSize
#             self.pageRect = None
#             return ''
#         else:
#             return u'[Invalid page size "%s"]' % size
#
#
#     def setOrientation(self, orientation):
#         if isinstance(orientation, basestring):
#             orientation = orientation.upper().strip()
#         validOrientation = self.validOrientations.get(orientation, None)
#         if validOrientation != None:
#             self.orientation = validOrientation
#             return ''
#         else:
#             return u'[Invalid orientation "%s"]' % orientation
#
#
#     def setMargins(self, margin):
#         if isinstance(margin, (int, float)):
#             self.leftMargin = margin
#             self.topMargin = margin
#             self.rightMargin = margin
#             self.bottomMargin = margin
#             return ''
#         else:
#             return u'[Invalid margin "%s"]' % margin
#
#
#     def setLeftMargin(self, margin):
#         if isinstance(margin, (int, float)):
#             self.leftMargin = margin
#             return ''
#         else:
#             return u'[Invalid left margin "%s"]' % margin
#
#
#     def setTopMargin(self, margin):
#         if isinstance(margin, (int, float)):
#             self.topMargin = margin
#             return ''
#         else:
#             return u'[Invalid top margin "%s"]' % margin
#
#
#     def setRightMargin(self, margin):
#         if isinstance(margin, (int, float)):
#             self.rightMargin = margin
#             return ''
#         else:
#             return u'[Invalid right margin "%s"]' % margin
#
#
#     def setBottomMargin(self, margin):
#         if isinstance(margin, (int, float)):
#             self.bottomMargin = margin
#             return ''
#         else:
#             return u'[Invalid bottom margin "%s"]' % margin