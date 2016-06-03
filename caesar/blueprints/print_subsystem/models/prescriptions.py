# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Date, Float, DateTime, String, Integer
from sqlalchemy.orm import relationship, backref

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

    createPerson = relationship(u'Person', foreign_keys=[createPerson_id])
    modifyPerson = relationship(u'Person', foreign_keys=[modifyPerson_id])

    action = relationship(
        u'Action',
        backref=backref(
            'medication_prescriptions',
            primaryjoin='and_(MedicalPrescription.action_id == Action.id, MedicalPrescription.status_id == 1)'
        )
    )
    rls = relationship(u'rlsNomen', lazy='joined')
    dose_unit = relationship(u'rbUnits', foreign_keys=[dose_unit_id], lazy='joined')
    duration_unit = relationship(u'rbUnits', foreign_keys=[duration_unit_id], lazy='joined')
    frequency_unit = relationship(u'rbUnits', foreign_keys=[frequency_unit_id], lazy='joined')
    methodOfAdministration = relationship(u'rbMethodOfAdministration', lazy='joined')

    @property
    def status(self):
        from nemesis.models.enums import MedicationPrescriptionStatus
        return MedicationPrescriptionStatus(self.status_id)

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
