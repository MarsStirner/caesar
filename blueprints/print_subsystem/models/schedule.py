# -*- coding: utf-8 -*-
import datetime

from application.database import db
from models_all import Person, Client, Rbreasonofabsence, Organisation, Orgstructure


class rbReceptionType(db.Model):
    __tablename__ = 'rbReceptionType'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.Unicode(32), nullable=False)
    name = db.Column(db.Unicode(64), nullable=False)

    def __unicode__(self):
        return u'(%s) %s' % (self.code, self.name)

    def __json__(self):
        return {
            'code': self.code,
            'name': self.name,
        }


class rbAttendanceType(db.Model):
    __tablename__ = 'rbAttendanceType'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.Unicode(32), nullable=False)
    name = db.Column(db.Unicode(64), nullable=False)

    def __unicode__(self):
        return u'(%s) %s' % (self.code, self.name)

    def __json__(self):
        return {
            'code': self.code,
            'name': self.name,
        }


class Office(db.Model):
    __tablename__ = 'Office'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.Unicode(32), nullable=False)
    name = db.Column(db.Unicode(64), nullable=False)
    orgStructure_id = db.Column(db.ForeignKey('OrgStructure.id'))

    orgStructure = db.relationship('Orgstructure')

    def __unicode__(self):
        return self.code

    def __json__(self):
        return {
            'code': self.code,
            'name': self.name,
            'org_structure': self.orgStructure
        }


class rbAppointmentType(db.Model):
    __tablename__ = 'rbAppointmentType'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.Unicode(32), nullable=False)
    name = db.Column(db.Unicode(64), nullable=False)

    def __unicode__(self):
        return u'(%s) %s' % (self.code, self.name)

    def __json__(self):
        return {
            'code': self.code,
            'name': self.name,
        }


class Schedule(db.Model):
    __tablename__ = 'Schedule'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('Person.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    begTime = db.Column(db.Time, nullable=False)
    endTime = db.Column(db.Time, nullable=False)
    numTickets = db.Column(db.Integer, doc=u'Запланированное количество талонов на данный день')
    office_id = db.Column(db.ForeignKey('Office.id'))
    reasonOfAbsence_id = db.Column(db.Integer, db.ForeignKey('rbReasonOfAbsence.id'))
    receptionType_id = db.Column(db.Integer, db.ForeignKey('rbReceptionType.id'))
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.SmallInteger, nullable=False, server_default='0')

    person = db.relationship('Person', foreign_keys=person_id)
    reasonOfAbsence = db.relationship('Rbreasonofabsence', lazy='joined')
    receptionType = db.relationship('rbReceptionType', lazy='joined')
    tickets = db.relationship(
        'ScheduleTicket', lazy=False, primaryjoin=
        "and_(ScheduleTicket.schedule_id == Schedule.id, ScheduleTicket.deleted == 0)")
    office = db.relationship('Office', lazy='joined')
    

class ScheduleTicket(db.Model):
    __tablename__ = 'ScheduleTicket'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('Schedule.id'), nullable=False)
    begTime = db.Column(db.Time)
    endTime = db.Column(db.Time)
    attendanceType_id = db.Column(db.Integer, db.ForeignKey('rbAttendanceType.id'), nullable=False)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.SmallInteger, nullable=False, server_default='0')

    attendanceType = db.relationship('rbAttendanceType', lazy=False)
    client_ticket = db.relationship(
        'ScheduleClientTicket', lazy=False, primaryjoin=
        "and_(ScheduleClientTicket.ticket_id == ScheduleTicket.id, ScheduleClientTicket.deleted == 0)",
        uselist=False)

    schedule = db.relationship(
        'Schedule', lazy="joined", innerjoin=True, uselist=False,
        primaryjoin='and_('
                    'Schedule.deleted == 0, ScheduleTicket.deleted == 0, ScheduleTicket.schedule_id == Schedule.id)'
    )

    @property
    def client(self):
        ct = self.client_ticket
        return ct.client if ct else None

    @property
    def begDateTime(self):
        return datetime.datetime.combine(self.schedule.date, self.begTime) if self.begTime is not None else None

    @property
    def endDateTime(self):
        return datetime.datetime.combine(self.schedule.date, self.endTime) if self.endTime is not None else None


class ScheduleClientTicket(db.Model):
    __tablename__ = 'ScheduleClientTicket'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('Client.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ScheduleTicket.id'), nullable=False)
    isUrgent = db.Column(db.Boolean)
    note = db.Column(db.Unicode(256))
    appointmentType_id = db.Column(db.Integer, db.ForeignKey('rbAppointmentType.id'))
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.SmallInteger, nullable=False, server_default='0')
    event_id = db.Column(db.ForeignKey('Event.id'))
    
    client = db.relationship('Client', lazy='joined', uselist=False)
    appointmentType = db.relationship('rbAppointmentType', lazy=False, innerjoin=True)
    createPerson = db.relationship('Person', foreign_keys=[createPerson_id])
    event = db.relationship('Event')

    ticket = db.relationship(
        'ScheduleTicket', lazy="joined", innerjoin=True, uselist=False,
        primaryjoin='and_('
                    'ScheduleClientTicket.deleted == 0, '
                    'ScheduleTicket.deleted == 0, '
                    'ScheduleClientTicket.ticket_id == ScheduleTicket.id)'
    )


    @property
    def org_from(self):
        if not self.infisFrom:
            return
        from models_all import Organisation
        org = Organisation.query.filter(Organisation.infisCode == self.infisFrom).first()
        if not org:
            return self.infisFrom
        return org.title

    @property
    def date(self):
        return self.ticket.schedule.date

    @property
    def time(self):
        attendance_type_code = self.ticket.attendanceType.code
        if attendance_type_code == 'planned':
            time = self.ticket.begDateTime.time()
        elif attendance_type_code == 'CITO':
            time = "CITO"
        elif attendance_type_code == 'extra':
            time = u"сверх очереди"
        else:
            time = '--:--'

        return time

    @property
    def typeText(self):
        toHome = self.ticket.schedule.receptionType.code == 'home'
        if toHome:
            typeText = u'Вызов на дом'
        else:
            typeText = u'Направление на приём к врачу'
        return typeText