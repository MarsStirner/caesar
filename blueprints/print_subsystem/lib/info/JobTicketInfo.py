# -*- coding: utf-8 -*-
u"""
Объект печати Job_Ticket
"""

from library.Utils     import *
from ..info.PrintInfo import CInfo, CDateTimeInfo, CRBInfo
from ..info.OrgInfo import COrgStructureInfo
from Resources.JobTicketChooser import CJobTicketChooserComboBox


class CJobTypeInfo(CRBInfo):
    tableName = 'rbJobType'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


class CJobTicketInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id


    def _load(self):
        record = CJobTicketChooserComboBox.getTicketRecord(self.id) if self.id else None
        if record:
            self._initByRecord(record)
            return True
        else:
            self._initByNull()
            return False


    def _initByRecord(self, record):
        self._datetime     = CDateTimeInfo(forceDateTime(record.value('datetime')))
        self._idx          = forceInt(record.value('idx'))
        self._jobType      = self.getInstance(CJobTypeInfo, forceRef(record.value('jobType_id')))
        self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('orgStructure_id')))
        self._status       = forceInt(record.value('status'))
        self._label        = forceString(record.value('label'))
        self._note         = forceString(record.value('note'))
        self._begDateTime  = CDateTimeInfo(forceDateTime(record.value('begDateTime')))
        self._endDateTime  = CDateTimeInfo(forceDateTime(record.value('endDateTime')))


    def _initByNull(self):
        self._datetime     = CDateTimeInfo()
        self._idx          = None
        self._jobType      = self.getInstance(CJobTypeInfo, None)
        self._orgStructure = self.getInstance(COrgStructureInfo, None)
        self._status       = 0
        self._label        = ''
        self._note         = ''
        self._begDateTime  = CDateTimeInfo()
        self._endDateTime  = CDateTimeInfo()


    def __str__(self):
        self.load()
        if self._ok:
            return u'%s, %s, %s' % ( unicode(self._jobType),
                                     unicode(self._datetime),
                                     unicode(self._orgStructure) )
        else:
            return ''


    datetime     = property(lambda self: self.load()._datetime)
    idx          = property(lambda self: self.load()._idx)
    jobType      = property(lambda self: self.load()._jobType)
    orgStructure = property(lambda self: self.load()._orgStructure)

    status       = property(lambda self: self.load()._status)
    label        = property(lambda self: self.load()._label)
    note         = property(lambda self: self.load()._note)
    note         = property(lambda self: self.load()._note)
    begDateTime  = property(lambda self: self.load()._begDateTime)
    endDateTime  = property(lambda self: self.load()._endDateTime)
