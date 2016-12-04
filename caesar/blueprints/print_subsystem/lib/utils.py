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
from sqlalchemy import or_

from caesar.blueprints.print_subsystem.lib.risar_config import request_type_pregnancy
from caesar.blueprints.print_subsystem.models.expert_protocol import EventMeasure, ExpertSchemeMeasureAssoc, Measure
from nemesis.models.event import EventType
from ..models.models_all import rbPrintTemplate, Action, Actiontype, Event, rbRequestType, RisarFetusState

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
    :rtype: Action | None | sqlalchemy.query
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
    action = query
    if one is not None:
        action = query.first() if one else query.all()
    return action


def get_event(event_id):
    if not event_id:
        return None
    return g.printing_session.query(Event).filter(Event.id == event_id, Event.deleted == 0).first()


def get_latest_pregnancy_event(client_id):
    return g.printing_session.query(Event).join(EventType, rbRequestType).filter(
        Event.client_id == client_id,
        Event.deleted == 0,
        rbRequestType.code == request_type_pregnancy,
        Event.execDate_raw.is_(None)
    ).order_by(Event.setDate_raw.desc()).first()


def get_fetuses(action_id):
    if not action_id:
        return []
    return g.printing_session.query(RisarFetusState).filter(
        RisarFetusState.action_id == action_id,
        RisarFetusState.deleted == 0,
    ).order_by(RisarFetusState.id).all()


def get_measures_list(event_id, measure_code, with_result=False):
    query = g.printing_session.query(EventMeasure).outerjoin(
        ExpertSchemeMeasureAssoc
    ).join(Measure, or_(
        Measure.id == ExpertSchemeMeasureAssoc.measure_id,
        Measure.id == EventMeasure.measure_id,)
    ).filter(
        EventMeasure.event_id == event_id,
        EventMeasure.deleted == 0,
        Measure.code == measure_code
    )

    if with_result:
        query = query.filter(EventMeasure.resultAction_id.isnot(None))

    return query.order_by(EventMeasure.begDateTime).all()


def get_latest_measure(event_id, measure_code, with_result=False):
    query = g.printing_session.query(EventMeasure).outerjoin(
        ExpertSchemeMeasureAssoc
    ).join(Measure, or_(
        Measure.id == ExpertSchemeMeasureAssoc.measure_id,
        Measure.id == EventMeasure.measure_id,)
    ).filter(
        EventMeasure.event_id == event_id,
        EventMeasure.deleted == 0,
        Measure.code == measure_code
    )

    if with_result:
        query = query.filter(EventMeasure.resultAction_id.isnot(None))

    return query.order_by(EventMeasure.begDateTime.desc()).first()
