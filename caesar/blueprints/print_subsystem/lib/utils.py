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
from flask import g
from ..models.models_all import rbPrintTemplate, Action, Actiontype

__author__ = 'mmalkov'


def getPrintTemplates(context):
    return [
        (r.name, r.id, r.dpdAgreement, r.fileName, r.code)
        for r in g.printing_session.query(rbPrintTemplate).filter(rbPrintTemplate.context == context)
    ] if context else []


def get_action(event, flat_code, one=True):
    """
    Поиск и создание действия внутри обращения
    :param event: Обращение
    :param flat_code: flat code типа действия
    :param create: создавать ли, если нет?
    :type event: application.models.event.Event
    :type flat_code: list|tuple|basestring|None
    :type create: bool
    :return: действие
    :rtype: Action | None
    """
    query = g.printing_session.query(Action).join(Actiontype).filter(Action.event == event, Action.deleted == 0)
    if isinstance(flat_code, (list, tuple)):
        query = query.filter(Actiontype.flatCode.in_(flat_code))
    elif isinstance(flat_code, basestring):
        query = query.filter(Actiontype.flatCode == flat_code)
    elif flat_code is None:
        return
    else:
        raise TypeError('flat_code must be list|tuple|basestring|None')
    action = query.first() if one else query.all()
    return action
