# -*- coding: utf-8 -*-

from sqlalchemy import Column, Unicode, ForeignKey, DateTime, Text
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from ..database import Base
from nemesis.models.utils import UUIDColumn


class ExpertProtocol(Base):
    __tablename__ = u'ExpertProtocol'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(16), index=True)
    name = Column(Unicode(255), nullable=False)
    sex = Column(Integer, nullable=False, server_default="'0'")
    age = Column(Unicode(9), nullable=False, server_default="''")
    deleted = Column(Integer, nullable=False, server_default="'0'")

    schemes = relationship('ExpertScheme', backref='protocol')


class ExpertProtocol_ActionTypeAssoc(Base):
    __tablename__ = u'ExpertProtocol_ActionType'

    id = Column(Integer, primary_key=True)
    protocol_id = Column(Integer, ForeignKey('ExpertProtocol.id'), nullable=False)
    actionType_id = Column(Integer, ForeignKey('ActionType.id'), nullable=False)


class ExpertScheme(Base):
    __tablename__ = u'ExpertScheme'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    name = Column(Unicode(255), nullable=False)
    code = Column(Unicode(16), index=True)
    number = Column(Unicode(16), nullable=False, index=True)
    deleted = Column(Integer, nullable=False, server_default="'0'")
    protocol_id = Column(Integer, ForeignKey('ExpertProtocol.id'), nullable=False, index=True)

    mkbs = relationship('Mkb', secondary='ExpertSchemeMKB')
    scheme_measures = relationship('ExpertSchemeMeasureAssoc', backref='scheme')


class ExpertSchemeMKBAssoc(Base):
    __tablename__ = u'ExpertSchemeMKB'

    id = Column(Integer, primary_key=True)
    mkb_id = Column(Integer, ForeignKey('MKB.id'), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey('ExpertScheme.id'), nullable=False, index=True)
    deleted = Column(Integer, nullable=False, server_default="'0'")

    mkb = relationship('Mkb')


class ExpertSchemeMeasureAssoc(Base):
    __tablename__ = u'ExpertSchemeMeasure'

    id = Column(Integer, primary_key=True)
    scheme_id = Column(Integer, ForeignKey('ExpertScheme.id'), nullable=False, index=True)
    measure_id = Column(Integer, ForeignKey('Measure.id'), nullable=False, index=True)
    schedule_id = Column(Integer, ForeignKey('MeasureSchedule.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default="'0'")

    measure = relationship('Measure')
    schedule = relationship('MeasureSchedule', backref='scheme_measure', uselist=False)


class Measure(Base):
    __tablename__ = u'Measure'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    measureType_id = Column(Integer, ForeignKey('rbMeasureType.id'), nullable=False, index=True)
    code = Column(Unicode(16), index=True)
    name = Column(Unicode(512), nullable=False)
    deleted = Column(Integer, nullable=False, server_default=u"'0'", default=0)
    uuid = Column(UUIDColumn(), nullable=False)
    appointmentAt_id = Column(Integer, ForeignKey('ActionType.id'), index=True)
    resultAt_id = Column(Integer, ForeignKey('ActionType.id'), index=True)
    templateAction_id = Column(Integer, ForeignKey('Action.id'), index=True)

    measure_type = relationship('rbMeasureType')
    appointment_at = relationship('Actiontype', foreign_keys=[appointmentAt_id])
    result_at = relationship('Actiontype', foreign_keys=[resultAt_id])
    template_action = relationship('Action')


class MeasureSchedule_ScheduleTypeAssoc(Base):
    __tablename__ = u'MeasureSchedule_ScheduleType'

    id = Column(Integer, primary_key=True)
    measureSchedule_id = Column(Integer, ForeignKey('MeasureSchedule.id'), nullable=False)
    scheduleType_id = Column(Integer, ForeignKey('rbMeasureScheduleType.id'), nullable=False, index=True)


class MeasureScheduleAdditionalMKBAssoc(Base):
    __tablename__ = u'MeasureScheduleAdditionalMKB'

    id = Column(Integer, primary_key=True)
    measureSchedule_id = Column(Integer, ForeignKey('MeasureSchedule.id'), nullable=False, index=True)
    mkb_id = Column(Integer, ForeignKey('MKB.id'), nullable=False)

    mkb = relationship('Mkb')


class rbMeasureType(Base):
    __tablename__ = u'rbMeasureType'
    _table_description = u'Типы мероприятий'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(16), index=True, nullable=False)
    name = Column(Unicode(64), nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }


class rbMeasureScheduleApplyType(Base):
    __tablename__ = u'rbMeasureScheduleApplyType'
    _table_description = u'Типы мероприятий'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(16), index=True, nullable=False)
    name = Column(Unicode(64), nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }


class MeasureSchedule(Base):
    __tablename__ = u'MeasureSchedule'

    id = Column(Integer, primary_key=True)
    additionalText = Column(Text)
    applyType_id = Column(Integer, ForeignKey('rbMeasureScheduleApplyType.id'))
    applyBoundRangeLow = Column(Integer)
    applyBoundRangeLowUnits_id = Column(Integer, ForeignKey('rbUnits.id'))
    applyBoundRangeLowMax = Column(Integer)
    applyBoundRangeLowMaxUnits_id = Column(Integer, ForeignKey('rbUnits.id'))
    applyBoundRangeHigh = Column(Integer)
    applyBoundRangeHighUnits_id = Column(Integer, ForeignKey('rbUnits.id'))
    period = Column(Integer)
    periodUnits_id = Column(Integer, ForeignKey('rbUnits.id'))
    frequency = Column(Integer)
    count = Column(Integer)

    apply_type = relationship('rbMeasureScheduleApplyType')
    apply_bound_range_low_unit = relationship('rbUnits', foreign_keys=[applyBoundRangeLowUnits_id])
    apply_bound_range_low_max_unit = relationship('rbUnits', foreign_keys=[applyBoundRangeLowMaxUnits_id])
    apply_bound_range_high_unit = relationship('rbUnits', foreign_keys=[applyBoundRangeHighUnits_id])
    period_unit = relationship('rbUnits', foreign_keys=[periodUnits_id])
    schedule_types = relationship('rbMeasureScheduleType', secondary='MeasureSchedule_ScheduleType')
    additional_mkbs = relationship('Mkb', secondary='MeasureScheduleAdditionalMKB')


class rbMeasureScheduleType(Base):
    __tablename__ = u'rbMeasureScheduleType'
    _table_description = u'Типы расписаний мероприятий'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(16), index=True, nullable=False)
    name = Column(Unicode(64), nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }


class rbMeasureStatus(Base):
    __tablename__ = u'rbMeasureStatus'
    _table_description = u'Типы статусов мероприятий'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(32), index=True, nullable=False)
    name = Column(Unicode(64), nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }


class EventMeasure(Base):
    __tablename__ = u'EventMeasure'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, ForeignKey('Person.id'), index=True)
    event_id = Column(Integer, ForeignKey('Event.id'), nullable=False, index=True)
    schemeMeasure_id = Column(Integer, ForeignKey('ExpertSchemeMeasure.id'), nullable=False, index=True)
    measure_id = Column(Integer, ForeignKey('Measure.id'), nullable=True, index=True)
    begDateTime = Column(DateTime)
    endDateTime = Column(DateTime)
    status = Column(Integer, nullable=False)
    deleted = Column(Integer, nullable=False, server_default=u"'0'", default=0)
    sourceAction_id = Column(Integer, ForeignKey('Action.id'), index=True)
    appointmentAction_id = Column(Integer, ForeignKey('Action.id'), index=True)
    resultAction_id = Column(Integer, ForeignKey('Action.id'), index=True)
    is_actual = Column(Integer, server_default="'1'")

    event = relationship('Event')
    _scheme_measure = relationship('ExpertSchemeMeasureAssoc')
    _measure = relationship('Measure')
    source_action = relationship('Action', foreign_keys=[sourceAction_id])
    result_action = relationship('Action', foreign_keys=[resultAction_id])
    appointment_action = relationship('Action', foreign_keys=[appointmentAction_id])

    @property
    def scheme_measure(self):
        return self._scheme_measure if self.schemeMeasure_id is not None else None

    @property
    def manual_measure(self):
        return self._measure if self.measure_id is not None else None

    @property
    def measure(self):
        return self.scheme_measure.measure if self.schemeMeasure_id is not None else self.manual_measure
