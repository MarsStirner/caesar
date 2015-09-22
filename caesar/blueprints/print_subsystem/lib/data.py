# -*- coding: utf-8 -*-
import datetime

from .query import Query
from sqlalchemy import and_

from nemesis.lib.utils import safe_date
from ..models.models_all import (Orgstructure, Action, ActionProperty, ActionProperty_OrgStructure, Actionpropertytype, Actiontype,
    ActionProperty_HospitalBed, OrgstructureHospitalbed, ActionProperty_Integer)
from nemesis.lib.const import (STATIONARY_ORG_STRUCT_STAY_CODE, STATIONARY_HOSP_BED_CODE, STATIONARY_MOVING_CODE,
    STATIONARY_HOSP_LENGTH_CODE, STATIONARY_ORG_STRUCT_TRANSFER_CODE, STATIONARY_LEAVED_CODE)
from nemesis.models.enums import ActionStatus


def current_patient_orgStructure(event_id):
    return Query(Orgstructure).\
        join(ActionProperty_OrgStructure, Orgstructure.id == ActionProperty_OrgStructure.value_).\
        join(ActionProperty, ActionProperty.id == ActionProperty_OrgStructure.id).\
        join(Action).\
        join(Actionpropertytype).\
        filter(
            Actionpropertytype.code == 'orgStructStay',
            Action.event_id == event_id,
            Action.deleted == 0).\
        order_by(Action.begDate_raw.desc()).\
        first()


def get_patient_location(event, dt=None):
    if event.is_stationary:
        query = _get_stationary_location_query(event, dt)
        query = query.with_entities(
            Orgstructure
        )
        current_os = query.first()
    else:
        current_os = event.orgStructure
    return current_os


def _get_stationary_location_query(event, dt=None):
    query = _get_moving_query(event, dt, False)
    query = query.join(
        ActionProperty
    ).join(
        Actionpropertytype, and_(ActionProperty.type_id == Actionpropertytype.id,
                                 Actionpropertytype.actionType_id == Actiontype.id)
    ).join(
        ActionProperty_OrgStructure, ActionProperty.id == ActionProperty_OrgStructure.id
    ).join(
        Orgstructure
    ).filter(
        Actionpropertytype.code == STATIONARY_ORG_STRUCT_STAY_CODE
    )
    return query


def get_patient_hospital_bed(event, dt=None):
    query = _get_moving_query(event, dt, False)
    query = query.join(
        ActionProperty
    ).join(
        Actionpropertytype, and_(ActionProperty.type_id == Actionpropertytype.id,
                                 Actionpropertytype.actionType_id == Actiontype.id)
    ).join(
        ActionProperty_HospitalBed, ActionProperty.id == ActionProperty_HospitalBed.id
    ).join(
        OrgstructureHospitalbed
    ).filter(
        Actionpropertytype.code == STATIONARY_HOSP_BED_CODE
    ).with_entities(
        OrgstructureHospitalbed
    )
    hb = query.first()
    return hb


def _get_moving_query(event, dt=None, finished=None):
    query = Query(Action).join(
        Actiontype
    ).filter(
        Action.event_id == event.id,
        Action.deleted == 0,
        Actiontype.flatCode == STATIONARY_MOVING_CODE
    )
    if dt:
        query = query.filter(Action.begDate_raw <= dt)
    elif finished is not None:
        if finished:
            query = query.filter(Action.status == ActionStatus.finished[0])
        else:
            query = query.filter(Action.status != ActionStatus.finished[0])
    query = query.order_by(Action.begDate_raw.desc())
    return query


def get_hosp_length(event):
    def from_hosp_release():
        query = _get_hosp_release_query(event)
        query = query.join(
            ActionProperty
        ).join(
            Actionpropertytype, and_(ActionProperty.type_id == Actionpropertytype.id,
                                     Actionpropertytype.actionType_id == Actiontype.id)
        ).join(
            ActionProperty_Integer, ActionProperty.id == ActionProperty_Integer.id
        ).filter(
            Actionpropertytype.code == STATIONARY_HOSP_LENGTH_CODE
        ).with_entities(
            ActionProperty_Integer
        )
        hosp_length = query.first()
        return hosp_length.value if hosp_length else None

    def _get_start_date_from_moving():
        query = _get_moving_query(event)
        start_date = query.with_entities(
            Action.begDate_raw
        ).order_by(None).order_by(Action.begDate_raw).first()
        return safe_date(start_date[0]) if start_date else None

    def _get_finish_date_from_moving():
        last_moving_q = _get_moving_query(event, finished=True)
        final_moving_q = last_moving_q.join(
            ActionProperty
        ).join(
            Actionpropertytype, and_(ActionProperty.type_id == Actionpropertytype.id,
                                     Actionpropertytype.actionType_id == Actiontype.id)
        ).outerjoin(
            ActionProperty_Integer, ActionProperty.id == ActionProperty_Integer.id
        ).filter(
            Actionpropertytype.code == STATIONARY_ORG_STRUCT_TRANSFER_CODE,
            ActionProperty_Integer.id == None
        )
        end_date = final_moving_q.with_entities(
            Action.endDate_raw
        ).first()
        return safe_date(end_date[0]) if end_date else None

    def calculate_not_finished():
        date_start = _get_start_date_from_moving() or event.setDate_raw.date()
        date_to = _get_finish_date_from_moving()
        if not date_to:
            date_to = datetime.date.today()
        hosp_length = (date_to - date_start).days
        if event.is_day_hospital:
            hosp_length += 1
        return hosp_length

    # 1) from hospital release document
    duration = from_hosp_release()
    if duration is not None:
        hosp_length = duration
    else:
        # 2) calculate not yet finished stay length
        hosp_length = calculate_not_finished()
    return hosp_length


def _get_hosp_release_query(event):
    query = Query(Action).join(
        Actiontype
    ).filter(
        Action.event_id == event.id,
        Action.deleted == 0,
        Actiontype.flatCode == STATIONARY_LEAVED_CODE
    ).filter(
        Action.status == ActionStatus.finished[0]
    ).order_by(Action.begDate_raw.desc())
    return query
