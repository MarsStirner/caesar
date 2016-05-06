# -*- coding: utf-8 -*-
import datetime

import six
import sqlalchemy
from UserDict import IterableUserDict
from blueprints.print_subsystem.models.models_utils import Info, RBInfo, DateInfo, ReadProxy, Query
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text, Table, or_
from sqlalchemy.orm import relationship
from ..database import metadata

__author__ = 'viruzzz-kun'


def get_client_diagnostics(client, beg_date, end_date=None, including_closed=False):
    """
    :type beg_date: datetime.date
    :type end_date: datetime.date | NoneType
    :type including_closed: bool
    :param beg_date:
    :param end_date:
    :param including_closed:
    :return:
    """
    query = Query(Diagnostic).join(
        Diagnosis
    ).filter(
        Diagnosis.client == client,
        Diagnosis.deleted == 0,
        Diagnostic.deleted == 0,
    )
    if end_date is not None:
        query = query.filter(
            Diagnostic.createDatetime <= end_date,
            Diagnosis.setDate_raw <= end_date,
        )
    if not including_closed:
        query = query.filter(
            or_(
                Diagnosis.endDate_raw.is_(None),
                Diagnosis.endDate_raw >= beg_date,
            )
        )
    query = query.group_by(
        Diagnostic.diagnosis_id
    )
    query = query.with_entities(sqlalchemy.func.max(Diagnostic.id).label('zid')).subquery()
    query = Query(Diagnostic).join(query, query.c.zid == Diagnostic.id)
    return query.all()


class NoInfo(object):
    def __cmp__(self, x):
        ss = unicode(self)
        sx = unicode(x)
        if ss > sx:
            return 1
        elif ss < sx:
            return -1
        else:
            return 0

    def __add__(self, x):
        return unicode(self) + unicode(x)

    def __radd__(self, x):
        return unicode(x) + unicode(self)


class DiagnosticInfo(NoInfo):
    def __init__(self, diagnostic, dt, dk):
        self._diagnostic = diagnostic
        self._dt = dt
        self._dk = dk

    def __getattr__(self, item):
        if item in ['action', 'diagnosis', 'mkb', 'mkb2', 'mkb_ex', 'character', 'stage', 'phase', 'traumaType',
                    'rbAcheResult', 'person', 'dispanser', 'healthGroup', 'modifyPerson', 'createPerson', 'setDate',
                    'endDate', 'diagnosis_description', 'notes', 'MKB', 'MKB2', 'MKBEx']:
            return getattr(
                object.__getattribute__(self, '_diagnostic'),
                item
            )
        if item == 'type':
            return object.__getattribute__(self, '_dt')
        if item == 'kind':
            return object.__getattribute__(self, '_dk')
        if item == 'diagnostic':
            return object.__getattribute__(self, '_diagnostic')
        return object.__getattribute__(self, item)

    def __unicode__(self):
        return u'%s, %s %s' % (
            object.__getattribute__(self, '_diagnostic'),
            object.__getattribute__(self, '_dk'),
            object.__getattribute__(self, '_dt'),
        )


class ActionDiagnosesInfo(NoInfo, IterableUserDict):
    def __init__(self, action):
        """
        @type action: blueprints.print_subsystem.models.models_all.Action
        @param action:
        """
        self.__data = {}
        self.action = action
        self.__loaded = False
        self.__diagnosis_types = []
        self.__diagnostics = []
        self.__associations = []
        IterableUserDict.__init__(self)

    @property
    def data(self):
        if not self.__loaded:
            self.__load_raw_data()
        return self.__data

    @data.setter
    def data(self, value):
        self.__loaded = False
        self.__diagnosis_types = []
        self.__diagnostics = []
        self.__associations = []
        self.__data = value

    def __load_raw_data(self):
        dk_codes = {dk.code: dk for dk in Query(rbDiagnosisKind)}
        dt_codes = {dt.code: dt for dt in Query(rbDiagnosisTypeN)}
        self.__diagnosis_types = diagnosis_types = self.action.actionType.diagnosis_types
        self.__diagnostics = diagnostics = get_client_diagnostics(
            self.action.event.client,
            self.action.begDate_raw,
            self.action.endDate_raw,
        )
        self.__associations = associations = Query(Action_Diagnosis).filter(
            Action_Diagnosis.action == self.action,
            Action_Diagnosis.deleted == 0,
        ).all()

        diag_id_2_diagnostic = {
            diagnostic.diagnosis_id: diagnostic
            for diagnostic in diagnostics
        }

        diag_id_2_dk_code = {
            dt.code: {
                dic.diagnosis_id: u'associated'
                for dic in diagnostics
            }
            for dt in diagnosis_types
        }
        for assoc in associations:
            try:
                diag_id_2_dk_code[assoc.diagnosisType.code][assoc.diagnosis_id] = assoc.diagnosisKind.code
            except KeyError:
                pass

        self.__data = {
            dt_code: {
                dk_code: [
                    DiagnosticInfo(
                        diag_id_2_diagnostic[diagnosis_id],
                        dk,
                        dt_codes[dt_code],
                    )
                    for diagnosis_id, code in six.iteritems(dt_value)
                    if code == dk_code
                ]
                for dk_code, dk in six.iteritems(dk_codes)
            }
            for dt_code, dt_value in six.iteritems(diag_id_2_dk_code)
        }
        self.__loaded = True


class EventDiagnosesInfo(NoInfo, IterableUserDict):
    def __init__(self, event):
        """
        @type event: blueprints.print_subsystem.models.models_all.event
        @param event:
        """
        self.__data = {}
        self.event = event
        self.__loaded = False
        self.__diagnosis_types = []
        self.__diagnostics = []
        self.__associations = []
        IterableUserDict.__init__(self)

    @property
    def data(self):
        if not self.__loaded:
            self.__load_raw_data()
        return self.__data

    @data.setter
    def data(self, value):
        self.__loaded = False
        self.__diagnosis_types = []
        self.__diagnostics = []
        self.__associations = []
        self.__data = value

    def __load_raw_data(self):
        dk_codes = {dk.code: dk for dk in Query(rbDiagnosisKind)}
        dt_codes = {dt.code: dt for dt in Query(rbDiagnosisTypeN)}
        self.__diagnostics = diagnostics = get_client_diagnostics(
            self.event.client,
            self.event.begDate_raw,
            self.event.endDate_raw,
        )
        self.__associations = associations = Query(Event_Diagnosis).filter(
            Event_Diagnosis.event == self.event,
            Event_Diagnosis.deleted == 0,
        ).all()
        self.__diagnosis_types = diagnosis_types = sorted(
            set(self.event.eventType.diagnosis_types) | set(e_d.diagnosisType for e_d in associations),
            key=lambda dt: dt.rank
        )

        diag_id_2_diagnostic = {
            diagnostic.diagnosis_id: diagnostic
            for diagnostic in diagnostics
        }

        diag_id_2_dk_code = {
            dt.code: {
                dic.diagnosis_id: u'associated'
                for dic in diagnostics
            }
            for dt in diagnosis_types
        }
        for assoc in associations:
            try:
                diag_id_2_dk_code[assoc.diagnosisType.code][assoc.diagnosis_id] = assoc.diagnosisKind.code
            except KeyError:
                pass

        self.__data = {
            dt_code: {
                dk_code: [
                    DiagnosticInfo(
                        diag_id_2_diagnostic[diagnosis_id],
                        dk,
                        dt_codes[dt_code],
                    )
                    for diagnosis_id, code in six.iteritems(dt_value)
                    if code == dk_code
                ]
                for dk_code, dk in six.iteritems(dk_codes)
            }
            for dt_code, dt_value in six.iteritems(diag_id_2_dk_code)
        }
        self.__loaded = True


class Diagnosis(Info):
    __tablename__ = u'Diagnosis'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False, default=datetime.datetime.now)
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False, default=datetime.datetime.now)
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'", default=0)

    client_id = Column(ForeignKey('Client.id'), index=True, nullable=False)
    person_id = Column(ForeignKey('Person.id'), index=True)
    setDate_raw = Column('setDate', Date, default=datetime.date.today)
    endDate_raw = Column('endDate', Date)

    setDate = ReadProxy('setDate_raw', DateInfo)
    endDate = ReadProxy('endDate_raw', DateInfo)

    client = relationship('Client')
    person = relationship('Person', foreign_keys=[person_id], lazy=False, innerjoin=True)
    modifyPerson = relationship('Person', foreign_keys=[modifyPerson_id])
    createPerson = relationship('Person', foreign_keys=[createPerson_id])

    def __int__(self):
        return self.id


class Diagnostic(Info):
    __tablename__ = u'Diagnostic'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False, default=datetime.datetime.now)
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False, default=datetime.datetime.now)
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'", default=0)

    # Roots
    diagnosis_id = Column(ForeignKey('Diagnosis.id'), index=True)
    action_id = Column(Integer, ForeignKey('Action.id'), index=True)

    # Basic data
    MKB = Column(String(8), ForeignKey('MKB.DiagID'), index=True)
    MKB2 = Column(String(8), ForeignKey('MKB.DiagID'), index=True)
    MKBEx = Column(String(8), ForeignKey('MKB.DiagID'), index=True)
    notes = Column(Text, nullable=False, default='')
    diagnosis_description = Column(Text)
    setDate_raw = Column('setDate', Date, default=datetime.date.today)
    endDate_raw = Column('endDate', Date)

    setDate = ReadProxy('setDate_raw', DateInfo)
    endDate = ReadProxy('endDate_raw', DateInfo)

    # Extended data
    character_id = Column(ForeignKey('rbDiseaseCharacter.id'), index=True)
    stage_id = Column(ForeignKey('rbDiseaseStage.id'), index=True)
    phase_id = Column(ForeignKey('rbDiseasePhases.id'), index=True)
    traumaType_id = Column(ForeignKey('rbTraumaType.id'), index=True)
    rbAcheResult_id = Column(ForeignKey('rbAcheResult.id'), index=True)

    # Auxiliary data
    person_id = Column(ForeignKey('Person.id'), index=True)
    dispanser_id = Column(ForeignKey('rbDispanser.id'), index=True)
    healthGroup_id = Column(ForeignKey('rbHealthGroup.id'), nullable=False)
    sanatorium = Column(Integer, nullable=False, default=0)
    hospital = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=0)

    action = relationship('Action', backref='diagnostics')
    diagnosis = relationship('Diagnosis', backref='diagnostics')

    mkb = relationship('Mkb', foreign_keys=[MKB])
    mkb2 = relationship('Mkb', foreign_keys=[MKB2])
    mkb_ex = relationship('Mkb', foreign_keys=[MKBEx])

    character = relationship('rbDiseaseCharacter', lazy=False)
    stage = relationship('rbDiseaseStage', lazy=False)
    phase = relationship('rbDiseasePhases', lazy=False)
    traumaType = relationship('rbTraumaType', lazy=False)
    rbAcheResult = relationship(u'rbAcheResult', lazy=False)

    person = relationship('Person', foreign_keys=[person_id])
    dispanser = relationship('rbDispanser')
    healthGroup = relationship('rbHealthGroup', lazy=False)
    modifyPerson = relationship('Person', foreign_keys=[modifyPerson_id])
    createPerson = relationship('Person', foreign_keys=[createPerson_id])

    def __int__(self):
        return self.id

    def __unicode__(self):
        return self.MKB

    @property
    def date(self):
        return self.action.begDate


class Event_Diagnosis(Info):
    __tablename__ = "Event_Diagnosis"

    id = Column(Integer, primary_key=True)
    event_id = Column(ForeignKey('Event.id'), nullable=False)
    diagnosis_id = Column(ForeignKey('Diagnosis.id'), nullable=False)
    diagnosisType_id = Column(ForeignKey('rbDiagnosisTypeN.id'), nullable=False)
    diagnosisKind_id = Column(ForeignKey('rbDiagnosisKind.id'), nullable=False)
    createDatetime = Column(DateTime, nullable=False, default=datetime.datetime.now)
    deleted = Column(Integer, nullable=False, server_default=u"'0'", default=0)

    event = relationship('Event', lazy=True, backref="diagnoses")
    diagnosis = relationship('Diagnosis')
    diagnosisType = relationship('rbDiagnosisTypeN', lazy=False)
    diagnosisKind = relationship('rbDiagnosisKind', lazy=False)


class Action_Diagnosis(Info):
    __tablename__ = "Action_Diagnosis"

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False)
    diagnosis_id = Column(ForeignKey('Diagnosis.id'), nullable=False)
    diagnosisType_id = Column(ForeignKey('rbDiagnosisTypeN.id'), nullable=False)
    diagnosisKind_id = Column(ForeignKey('rbDiagnosisKind.id'), nullable=False)
    createDatetime = Column(DateTime, nullable=False, default=datetime.datetime.now)
    deleted = Column(Integer, nullable=False, server_default=u"'0'", default=0)

    action = relationship('Action', lazy=True, backref="diagnoses")
    diagnosis = relationship('Diagnosis')
    diagnosisType = relationship('rbDiagnosisTypeN', lazy=False)
    diagnosisKind = relationship('rbDiagnosisKind', lazy=False)


class rbDiagnosisTypeN(RBInfo):
    __tablename__ = "rbDiagnosisTypeN"

    id = Column(Integer, primary_key=True)
    code = Column(String(128), unique=True, nullable=False)
    name = Column(String(256), nullable=False)
    requireResult = Column(Integer)
    rank = Column(Integer)

    def __unicode__(self):
        return self.name


class rbDiagnosisKind(RBInfo):
    __tablename__ = "rbDiagnosisKind"

    id = Column(Integer, primary_key=True)
    code = Column(String(128), unique=True, nullable=False)
    name = Column(String(256), nullable=False)

    def __unicode__(self):
        return self.name


EventType_rbDiagnosisType = Table(
    "EventType_DiagnosisType", metadata,
    Column('eventType_id', ForeignKey('EventType.id')),
    Column('diagnosisType_id', ForeignKey('rbDiagnosisTypeN.id')),
)


ActionType_rbDiagnosisType = Table(
    "ActionType_DiagnosisType", metadata,
    Column('actionType_id', ForeignKey('ActionType.id')),
    Column('diagnosisType_id', ForeignKey('rbDiagnosisTypeN.id')),
)


