# -*- coding: utf-8 -*-
from .query import Query

from ..models.models_all import rbPrintTemplate, Action, Actiontype

__author__ = 'mmalkov'


def getPrintTemplates(context):
    return [
        (r.name, r.id, r.dpdAgreement, r.fileName, r.code)
        for r in Query(rbPrintTemplate).filter(rbPrintTemplate.context == context)
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
    query = Query(Action).join(Actiontype).filter(Action.event == event, Action.deleted == 0)
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
