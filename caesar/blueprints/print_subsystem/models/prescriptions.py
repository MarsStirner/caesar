# -*- coding: utf-8 -*-
from sqlalchemy import Column, Unicode, ForeignKey, Date, Float, DateTime, SmallInteger, Numeric, String
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy import orm

from ..database import Base

__author__ = 'viruzzz-kun'


class MedicalPrescription(Base):
    __tablename__ = 'MedicalPrescription'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    modifyDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(ForeignKey(u'Person.id'), nullable=False, index=True)
    modifyPerson_id = Column(ForeignKey(u'Person.id'), nullable=False, index=True)
    action_id = Column(ForeignKey(u'Action.id'), nullable=False, index=True)
    rls_id = Column(ForeignKey(u'rlsNomen.id'), nullable=False, index=True)
    status_id = Column(Integer, nullable=False)
    dose_amount = Column(Float(asdecimal=True), nullable=False)
    dose_unit_id = Column(ForeignKey(u'rbUnits.id'), nullable=False, index=True)
    frequency_value = Column(Float(asdecimal=True), nullable=False)
    frequency_unit_id = Column(ForeignKey(u'rbUnits.id'), nullable=False, index=True)
    duration_value = Column(Integer, nullable=False)
    duration_unit_id = Column(ForeignKey(u'rbUnits.id'), nullable=False, index=True)
    begDate = Column(Date)
    methodOfAdministration_id = Column(ForeignKey(u'rbMethodOfAdministration.id'), nullable=False, index=True)
    reasonOfCancel = Column(String(256))
    note = Column(String(256))

    createPerson = relationship(u'Person', primaryjoin='MedicalPrescription.createPerson_id == Person.id')
    modifyPerson = relationship(u'Person', primaryjoin='MedicalPrescription.modifyPerson_id == Person.id')

    action = relationship(u'Action', backref='medication_prescriptions')
    rls = relationship(u'rlsNomen')
    dose_unit = relationship(u'rbUnits', primaryjoin='MedicalPrescription.dose_unit_id == rbUnits.id')
    duration_unit = relationship(u'rbUnits', primaryjoin='MedicalPrescription.duration_unit_id == rbUnits.id')
    frequency_unit = relationship(u'rbUnits', primaryjoin='MedicalPrescription.frequency_unit_id == rbUnits.id')
    methodOfAdministration = relationship(u'rbMethodOfAdministration')

    # @property
    # def status(self):
    #     return MedicationPrescriptionStatus(self.status_id)

    def __json__(self):
        return {
            'id': self.id,
            'rls': self.rls,
            'method': self.methodOfAdministration,
            'note': self.note,
            'reason': self.reasonOfCancel,
            'status': self.status,
            'dose': {
                'value': self.dose_amount,
                'unit': self.dose_unit,
            },
            'frequency': {
                'value': self.frequency_value,
                'unit': self.frequency_unit,
            },
            'duration': {
                'value': self.duration_value,
                'unit': self.duration_unit,
            },
            'related': {
                'action_person_id': self.action.person_id,
                'action_set_person_id': self.action.setPerson_id,
                'event_exec_person_id': self.action.event.execPerson_id,
            },
            'closed': self.action.status >= 2 or self.status_id >= 3,
            'create_person': self.createPerson,
            'modify_person': self.modifyPerson,
            'create_datetime': self.createDatetime,
            'modify_datetime': self.modifyDatetime,
        }
