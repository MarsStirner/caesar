# -*- coding: utf-8 -*-
from PyQt4 import QtGui

from library.Utils              import *

from ..info.PrintInfo import CInfo, CDateInfo, CRBInfo
from ..info.OrgInfo import COrgStructureInfo


class CHospitalBedInfo(CInfo):
    tableName = 'OrgStructure_HospitalBed'

    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def _load(self):
        if self.id:
            record = QtGui.qApp.db.getRecord(self.tableName, '*', self.id)
            if record:
                self._initByRecord(record)
                return True
        self._initByNull()
        return True

    def _initByRecord(self, record):
        self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('master_id')))
        self._isPermanent  = forceBool(record.value('isPermanent'))
        self._type         = self.getInstance(CHospitalBedTypeInfo, forceRef(record.value('type_id')))
        self._profile      = self.getInstance(CHospitalBedProfileInfo, forceRef(record.value('profile_id')))
        self._relief       = forceInt(record.value('relief'))
        self._schedule     = self.getInstance(CHospitalBedScheduleInfo, forceRef(record.value('schedule_id')))
        self._begDate      = CDateInfo(forceDate(record.value('begDate')))
        self._endDate      = CDateInfo(forceDate(record.value('endDate')))
        self._name         = forceString(record.value('name'))


    def _initByNull(self):
        self._orgStructure = self.getInstance(COrgStructureInfo, None)
        self._isPermanent  = None
        self._type         = self.getInstance(CHospitalBedTypeInfo, None)
        self._profile      = self.getInstance(CHospitalBedProfileInfo, None)
        self._relief       = None
        self._schedule     = self.getInstance(CHospitalBedScheduleInfo, None)
        self._begDate      = CDateInfo()
        self._endDate      = CDateInfo()
        self._name         = u''


    orgStructure = property(lambda self: self.load()._orgStructure)
    isPermanent  = property(lambda self: self.load()._isPermanent)
    type         = property(lambda self: self.load()._type)
    profile      = property(lambda self: self.load()._profile)
    relief       = property(lambda self: self.load()._relief)
    schedule     = property(lambda self: self.load()._schedule)
    begDate      = property(lambda self: self.load()._begDate)
    endDate      = property(lambda self: self.load()._endDate)
    name         = property(lambda self: self.load()._name)


class CHospitalBedTypeInfo(CRBInfo):
    tableName = 'rbHospitalBedType'


class CHospitalBedProfileInfo(CRBInfo):
    tableName = 'rbHospitalBedProfile'


class CHospitalBedScheduleInfo(CRBInfo):
    tableName = 'rbHospitalBedSchedule'

