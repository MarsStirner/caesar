# -*- coding: utf-8 -*-

from PyQt4 import QtGui
#from PyQt4.QtCore import *
from ..info.PrintInfo import CInfo, CRBInfo
from ..info.OrgInfo import COrgInfo, COrgStructureInfo
#from Events.Service import CServiceInfo
from library.Utils import *


class CQuotingInfo(CInfo):
    def __init__(self, context, quotaId):
        CInfo.__init__(self, context)
        self.quotaId = quotaId # id в Client_Quoting (и vClient_Quoting)
        self._identifier = ''
        self._quotaTicket = ''
        self._stage = ''
        self._directionDate = ''
        self._freeInput = ''
        self._amount = ''
        self._mkb = ''
        self._status = ''
        self._request = ''
        self._statement = ''
        self._dateRegistration = ''
        self._dateEnd = ''
        self._regionCode = ''
        
        self._quotaType = self.getInstance(CQuotaTypeInfo, None)
        self._organisation = self.getInstance(COrgInfo, None)
        self._orgStructure = self.getInstance(COrgStructureInfo, None)        
        self._patientModel = self.getInstance(CPatientModelInfo, None)
        self._treatment = self.getInstance(CTreatmentInfo, None)
        
        self._clientId = None
        self._eventId = None


    def _load(self):
        db = QtGui.qApp.db
        if not self.exists():
            return False
        record = db.getRecordEx('vClient_Quoting', '*', 'id=%s AND deleted=0' % self.quotaId)
        if record:
            self._identifier = forceString(record.value('identifier'))
            self._quotaTicket = forceString(record.value('quotaTicket'))
            self._stage = forceString(record.value('stage'))
            self._directionDate = forceString(record.value('directionDate'))
            self._freeInput = forceString(record.value('freeInput'))
            self._amount = forceString(record.value('amount'))
            self._mkb = forceString(record.value('MKB'))
            self._status = forceString(record.value('status'))
            self._request = forceString(record.value('request'))
            self._statement = forceString(record.value('statment'))
            self._dateRegistration = forceString(record.value('dateRegistration'))
            self._dateEnd = forceString(record.value('dateEnd'))
            self._regionCode = forceString(record.value('regionCode'))
            
            self._quotaType = self.getInstance(CQuotaTypeInfo, forceRef(record.value('quotaType_id')))
            self._organisation = self.getInstance(COrgInfo, forceRef(record.value('org_id')))
            self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('orgStructure_id')))
            self._patientModel = self.getInstance(CPatientModelInfo, forceRef(record.value('pacientModel_id')))
            self._treatment = self.getInstance(CTreatmentInfo, forceRef(record.value('treatment_id')))
            return True
        else:
            return False
        
    
    def exists(self):
        return bool(self.quotaId)


#    def __str__(self):
#        self.load()
#        result = formatShortNameInt(self._lastName, self._firstName, self._patrName)
#        if self._speciality:
#            result += ', ' + self._speciality.name
#        return unicode(result)

    identifier = property(lambda self: self.load()._identifier)
    quotaTicket = property(lambda self: self.load()._quotaTicket)# if self.load()._quotaTicket else u"Нет")
    stage = property(lambda self: self.load()._stage)
    directionDate = property(lambda self: self.load()._directionDate)
    freeInput = property(lambda self: self.load()._freeInput)
    amount = property(lambda self: self.load()._amount)
    MKB = property(lambda self: self.load()._mkb)
    status = property(lambda self: self.load()._status)
    request = property(lambda self: self.load()._request)
    statement = property(lambda self: self.load()._statment)
    dateRegistration = property(lambda self: self.load()._dateRegistration)
    dateEnd = property(lambda self: self.load()._dateEnd)
    regionCode = property(lambda self: self.load()._regionCode)
    quotaType = property(lambda self: self.load()._quotaType)
    organisation = property(lambda self: self.load()._organisation)
    orgStructure = property(lambda self: self.load()._orgStructure)
    patientModel = property(lambda self: self.load()._patientModel)
    treatment = property(lambda self: self.load()._treatment)


class CQuotaTypeInfo(CInfo):
    def __init__(self, context, quotaTypeId):
        CInfo.__init__(self, context)
        self.quotaTypeId = quotaTypeId
        self._class = ''
        self._group_code = ''
        self._code = ''
        self._name = ''
        self._mkb = ''
        self._teenOlder = ''


    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('QuotaType', '*', self.quotaTypeId)
        if record:
            self._class = forceString(record.value('class'))
            self._group_code = forceString(record.value('group_code'))
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._mkb = forceString(record.value('MKB'))
            self._teenOlder = forceString(record.value('teenOlder'))
            return True
        else:
            return False


    def __str__(self):
        return self.load()._name

    class_ = property(lambda self: self.load()._class)
    group_code = property(lambda self: self.load()._group_code)
    code = property(lambda self: self.load()._code)
    name = property(lambda self: self.load()._name)
    MKB = property(lambda self: self.load()._mkb)
    teenOlder = property(lambda self: self.load()._teenOlder)
    

class CPatientModelInfo(CRBInfo):
    tableName = 'rbPacientModel'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)
        
        
class CTreatmentInfo(CRBInfo):
    tableName = 'rbTreatment'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

