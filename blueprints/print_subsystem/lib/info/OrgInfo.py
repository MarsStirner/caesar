# -*- coding: utf-8 -*-
# from PyQt4 import QtGui
# from PyQt4.QtCore import QDate
# from KLADR.KLADRModel import getCityName, getStreetName
# from Orgs.Utils import getOrgStructureFullName
# from Registry.Utils import getAddress, getClientAddress, getClientWork, getAttachRecord, getClientSocStatusIds, getSocStatusTypeClasses, getClientPolicyEx, getClientDocument, getClientPhonesEx
from ..info.PrintInfo import CRBInfo, CInfo, CInfoList, CDateInfo
from ..utils import get_lpu_session
from blueprints.print_subsystem.models import *
# from library.Utils import forceString, forceInt, formatSex, forceRef, forceBool, forceDate, calcAgeTuple, formatAgeTuple, formatSNILS, formatShortNameInt, formatNameInt

__author__ = 'mmalkov'


class CBankInfo(object):
    def __init__(self,  id):
        self.id = id
        self._bik = None
        self._name = None
        self._corAccount = None
        self._branchName = None
        self._subAccount = None

    def load(self):
        db = QtGui.qApp.db
        record = db.getRecord('Bank', '*', self.id) if self.id else None
        if record:
            self.bik = forceString(record.value('BIK'))
            self.name = forceString(record.value('name'))
            self.corAccount = forceString(record.value('corAccount'))
            self.branchName = forceString(record.value('branchName'))
            self.subAccount = forceString(record.value('subAccount'))

    """bik = property(lambda self: self.load()._bik)
    name = property(lambda self: self.load()._name)
    corAccount = property(lambda self: self.load()._corAccount)
    branchName = property(lambda self: self.load()._branchName)
    subAccount = property(lambda self: self.load()._subAccount)"""


class COKPFInfo(CRBInfo):
    tableName = 'rbOKPF'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


class CNetInfo(CRBInfo):
    tableName = 'rbNet'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


    def _initByRecord(self, record):
        self._sexCode = forceInt(record.value('sex'))
        self._age = forceString(record.value('age'))


    def _initByNull(self):
        self._sexCode = 0
        self._age = ''


    sexCode = property(lambda self: self.load()._sexCode)
    sex = property(lambda self: formatSex(self.load()._sexCode))
    age = property(lambda self: self.load()._age)


class COrgInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self._fullName = ''
        self._shortName = ''
        self._title = ''
        self._net = None
        self._infisCode = ''
        self._miacCode = ''
        self._OKVED = ''
        self._INN = ''
        self._KPP = ''
        self._OGRN = ''
        self._OKATO = ''
        self._OKPF = None
        self._OKFS = None
        self._OKPO = ''
        self._FSS = ''
        self._region = ''
        self._address = ''
        self._chief = ''
        self._phone = ''
        self._accountant = ''
        self._notes = ''
        self._bank = []


    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('Organisation', '*', self.id) if self.id else None
        if record:
            self._fullName = forceString(record.value('fullName'))
            self._shortName = forceString(record.value('shortName'))
            self._title = forceString(record.value('title'))
            self._net = self.getInstance(CNetInfo, record.value('net_id'))
            self._infisCode = forceString(record.value('infisCode'))
            self._miacCode = forceString(record.value('miacCode'))
            self._OKVED = forceString(record.value('OKVED'))
            self._INN = forceString(record.value('INN'))
            self._KPP = forceString(record.value('KPP'))
            self._OGRN = forceString(record.value('OGRN'))
            self._OKATO = forceString(record.value('OKATO'))
#            self._OKPF = forceString(db.translate('rbOKPF', 'id', forceRef(record.value('OKPF_id')), 'name'))
            self._OKPF = self.getInstance(COKPFInfo, forceRef(record.value('OKPF_id')))
            self._OKFS = self.getInstance(COKFSInfo, forceRef(record.value('OKFS_id')))
            self._OKPO = forceString(record.value('OKPO'))
            self._FSS = forceString(record.value('FSS'))
            self._region = forceString(record.value('region'))
            self._address = forceString(record.value('Address'))
            self._chief = forceString(record.value('chief'))
            self._phone = forceString(record.value('phone'))
            self._accountant = forceString(record.value('accountant'))
            self._notes = forceString(record.value('notes'))
            self.loadbanks(self.id)
            return True
        else:
            self._OKPF = self.getInstance(COKPFInfo, None)
            self._OKFS = self.getInstance(COKFSInfo, None)
            return False

    def loadbanks(self,  id):
        bid = QtGui.qApp.db.getIdList('Organisation_Account',  'bank_id',  'organisation_id=%i'% id)
        for i in bid:
            bi = CBankInfo(i)
            bi.load()
            self._bank.append(bi)

#    def __unicode__(self):
    def __str__(self):
        return self.load()._shortName

    fullName    = property(lambda self: self.load()._fullName)
    shortName   = property(lambda self: self.load()._shortName)
    title       = property(lambda self: self.load()._title)
    net         = property(lambda self: self.load()._net)
    infisCode   = property(lambda self: self.load()._infisCode)
    miacCode    = property(lambda self: self.load()._miacCode)
    OKVED       = property(lambda self: self.load()._OKVED)
    INN         = property(lambda self: self.load()._INN)
    KPP         = property(lambda self: self.load()._KPP)
    OGRN        = property(lambda self: self.load()._OGRN)
    OKATO       = property(lambda self: self.load()._OKATO)
    OKPF        = property(lambda self: self.load()._OKPF)
    OKFS        = property(lambda self: self.load()._OKFS)
    OKPO        = property(lambda self: self.load()._OKPO)
    FSS         = property(lambda self: self.load()._FSS)
    region      = property(lambda self: self.load()._region)
    address     = property(lambda self: self.load()._address)
    chief       = property(lambda self: self.load()._chief)
    phone       = property(lambda self: self.load()._phone)
    accountant  = property(lambda self: self.load()._accountant)
    notes       = property(lambda self: self.load()._notes)
    note        = property(lambda self: self.load()._notes)
    bank        = property(lambda self: self.load()._bank)


class COrgStructureInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self._name = ''
        self._code = ''
        self._net = None
        self._parent = None
        self._address = None
        self._organisation = None


    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('OrgStructure', '*', self.id) if self.id else None
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            netId = forceRef(record.value('net_id'))
            self._net = self.getInstance(CNetInfo, netId) if netId else None
            self._infisInternalCode = forceString(record.value('infisInternalCode'))
            self._infisDepTypeCode = forceString(record.value('infisDepTypeCode'))
            parentId = forceRef(record.value('parent_id'))
            self._parent = self.getInstance(COrgStructureInfo, parentId) if parentId else None
            organisationId = forceRef(record.value('organisation_id'))
            self._organisation = self.getInstance(COrgInfo, organisationId) if organisationId else None
            address = forceString(record.value('address'))
            if address:
                self._address = address
            return True
        else:
            return False


    def getNet(self):
        self.load()
        if self._net is None:
            if self._parent:
                self._net = self._parent.getNet()
            elif self._organisation:
                self._net = self._organisation.net
            else:
                self._net = self.getInstance(CNetInfo, None)
        return self._address


    def getFullName(self):
#        self.load()
        return getOrgStructureFullName(self.id)


    def getAddress(self):
        self.load()
        if self._address is None:
            if self._parent:
                self._address = self._parent.getAddress()
            elif self._organisation:
                self._address = self._organisation.address
            else:
                self._address = ''
        return self._address



    def __str__(self):
        return self.getFullName()


    code              = property(lambda self: self.load()._code)
    name              = property(lambda self: self.load()._name)
    net               = property(getNet)
    infisInternalCode = property(lambda self: self.load()._infisInternalCode)
    infisDepTypeCode  = property(lambda self: self.load()._infisDepTypeCode)
    fullName          = property(getFullName)
    organisation      = property(lambda self: self.load()._organisation)
    parent            = property(lambda self: self.load()._parent)
    address           = property(getAddress)


class COKFSInfo(CRBInfo):
    tableName = 'rbOKFS'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


    def _initByRecord(self, record):
        self._ownership = forceInt(record.value('ownership'))


    def _initByNull(self):
        self._ownership = None

    ownership = property(lambda self: self.load()._ownership)


class CAddressInfo(CInfo):
    def __init__(self, context, addressId):
        CInfo.__init__(self, context)
        self._addressId = addressId
        self._KLADRCode = ''
        self._KLADRStreetCode = ''
        self._city = ''
        self._street = ''
        self._number = ''
        self._corpus = ''
        self._flat = ''
        self._text = ''

    def _load(self):
        parts = []
        address = getAddress(self._addressId)
        self._KLADRCode = address.KLADRCode
        self._KLADRStreetCode = address.KLADRStreetCode
        if self._KLADRCode:
            self._city = getCityName(self._KLADRCode)
            parts.append(self._city)
        else:
            self._city = ''
        if self._KLADRStreetCode:
            self._street = getStreetName(self._KLADRStreetCode)
            parts.append(self._street)
        else:
            self._street = ''
        self._number = address.number
        self._corpus = address.corpus
        self._flat = address.flat
        if self._number:
            parts.append(u'д.'+self._number)
        if self._corpus:
            parts.append(u'к.'+self._corpus)
        if self._flat:
            parts.append(u'кв.'+self._flat)
        self._text = (', '.join(parts)).strip()
        return bool(self._text)

    KLADRCode       = property(lambda self: self.load()._KLADRCode)
    KLADRStreetCode = property(lambda self: self.load()._KLADRStreetCode)
    city            = property(lambda self: self.load()._city)
    town            = city
    street          = property(lambda self: self.load()._street)
    number          = property(lambda self: self.load()._number)
    corpus          = property(lambda self: self.load()._corpus)
    flat            = property(lambda self: self.load()._flat)

#    def __unicode__(self):
    def __str__(self):
        self.load()
        return self._text


class CClientAddressInfo(CAddressInfo):
    def __init__(self, context, clientId, addrType):
        CAddressInfo.__init__(self, context, None)
        self._clientId = clientId
        self._addrType = addrType
        self._freeInput = ''

    def _load(self):
        record = getClientAddress(self._clientId, self._addrType)
        if record:
            self._addressId = record.value('address_id')
            self._freeInput = forceString(record.value('freeInput'))
            if self._addressId:
                return CAddressInfo._load(self)
            else:
                return True
        else:
            self._addressId = None
            self._freeInput = ''
            return False

    freeInput  = property(lambda self: self.load()._freeInput)

#    def __unicode__(self):
    def __nonzero__(self):
        return bool(self.__str__())

    def __str__(self):
        self.load()
        if self._addressId and len(self._text):
            return CAddressInfo.__str__(self)
        else:
            return self.freeInput


class CClientWorkInfo(COrgInfo):
    def __init__(self, context, clientId):
        COrgInfo.__init__(self, context, None)
        self.clientId = clientId
        self._post = ''
        self._OKVED = ''
        self._hurts = []

    def _load(self):
        workRecord = getClientWork(self.clientId)
        if workRecord:
#            self.orgId = forceRef(workRecord.value('org_id'))
            self.id = forceRef(workRecord.value('org_id'))
            if self.id:
                COrgInfo._load(self)
            else:
                self._shortName = forceString(workRecord.value('freeInput'))
            self._post = forceString(workRecord.value('post'))
            self._OKVED = forceString(workRecord.value('OKVED'))
            self._hurts = self.getInstance(CClientWorkHurtInfoList, forceRef(workRecord.value('id')))
            return True
        else:
            return False

#    def __unicode__(self):
    def __str__(self):
        self.load()
        parts = []
        if self._shortName:
            parts.append(self._shortName)
        if self._post:
            parts.append(self._post)
        if self._OKVED:
            parts.append(u'ОКВЭД: '+self._OKVED)
        return ', '.join(parts)

    shortName  = property(lambda self: self.load()._shortName)
    post       = property(lambda self: self.load()._post)
    OKVED      = property(lambda self: self.load()._OKVED)
    hurts      = property(lambda self: self.load()._hurts)


class CClientWorkHurtInfoList(CInfoList):
    def __init__(self, context, workId):
        CInfoList.__init__(self, context)
        self.workId = workId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientWork_Hurt')
        idList = db.getIdList(table, 'id', table['master_id'].eq(self.workId), 'id')
        self._items = [ self.getInstance(CClientWorkHurtInfo, id) for id in idList ]
        return True


class CClientWorkHurtInfo(CInfo):
    def __init__(self, context, clientWorkHurtId):
        CInfo.__init__(self, context)
        self.clientWorkHurtId = clientWorkHurtId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientWork_Hurt')
        tableHurtType = db.table('rbHurtType')

        record = db.getRecordEx(table.leftJoin(tableHurtType, tableHurtType['id'].eq(table['hurtType_id'])),
                                [table['id'], tableHurtType['code'], tableHurtType['name'], table['stage']],
                                table['id'].eq(self.clientWorkHurtId))
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._stage = forceInt(record.value('stage'))
            self._factors = self.getInstance(CClientWorkHurtFactorInfoList, forceRef(record.value('id')))
            return True
        else:
            self._code = ''
            self._name = ''
            self._stage = 0
            self._factors = []
            return False

    code  = property(lambda self: self.load()._code)
    name  = property(lambda self: self.load()._name)
    stage = property(lambda self: self.load()._stage)
    factors = property(lambda self: self.load()._factors)

#    def __unicode__(self):
    def __str__(self):
        return self.load()._name


class CClientWorkHurtFactorInfoList(CInfoList):
    def __init__(self, context, hurtId):
        CInfoList.__init__(self, context)
        self.hurtId = hurtId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientWork_Hurt_Factor')
        idList = db.getIdList(table, 'id', table['master_id'].eq(self.hurtId), 'id')
        self._items = [ self.getInstance(CClientWorkHurtFactorInfo, id) for id in idList ]


class CClientWorkHurtFactorInfo(CInfo):
    def __init__(self, context, clientWorkHurtFactorId):
        CInfo.__init__(self, context)
        self.clientWorkHurtFactorId = clientWorkHurtFactorId
        self._code = ''
        self._name = ''

    def _load(self):
        db_session = get_lpu_session()
        record = db_session.query(Client).get(id)
        db_session.close()
        table = db.table('ClientWork_Hurt_Factor')
        tableHurtFactorType = db.table('rbHurtFactorType')
        record = db.getRecordEx(table.leftJoin(tableHurtFactorType, tableHurtFactorType['id'].eq(table['factorType_id'])),
                                [tableHurtFactorType['name'], tableHurtFactorType['code']],
                                table['id'].eq(self.clientWorkHurtFactorId))
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            return True
        return False

#    def __unicode__(self):
    def __str__(self):
        return self.load()._name

    code  = property(lambda self: self.load()._code)
    name  = property(lambda self: self.load()._name)


class CClientAttachInfo(CInfo):
    def __init__(self, context, clientId, temporary):
        CInfo.__init__(self, context)
        self.clientId = clientId
        self.temporary = temporary
        self._document = None

    def _load(self):
        attach = getAttachRecord(self.clientId, self.temporary)
        if attach:
            self._code = attach['code']
            self._name = attach['name']
            self._outcome = attach['outcome']
            self._org = self.getInstance(COrgInfo, attach['LPU_id'])
            self._orgStructure = self.getInstance(COrgStructureInfo, attach['orgStructure_id'])
            self._begDate = CDateInfo(attach['begDate'])
            self._endDate = CDateInfo(attach['endDate'])
            self._document = self.getInstance(CClientDocumentInfo, documentId=attach['document_id'])
            return True
        else:
            self._code = ''
            self._name = ''
            self._outcome = ''
            self._org = self.getInstance(COrgInfo, None)
            self._orgStructure = self.getInstance(COrgStructureInfo, None)
            self._begDate = CDateInfo()
            self._endDate = CDateInfo()
            self._document = None
            return False

    def __str__(self):
        self.load()
        if self._ok:
            result = self._name
            if self._outcome:
                result += ' '+ unicode(self._endDate)
            elif self.temporary:
                result += ' ' + self._org.shortName
                if self._begDate:
                    result += u' c ' + unicode(self._begDate)
                if self.endDate:
                    result += u' по ' + unicode(self._endDate)
            else:
                result += ' ' + self._org.shortName
        else:
            result = ''
        return result

    code    = property(lambda self: self.load()._code)
    name    = property(lambda self: self.load()._name)
    outcome = property(lambda self: self.load()._outcome)
    begDate = property(lambda self: self.load()._begDate)
    endDate = property(lambda self: self.load()._endDate)
    org    = property(lambda self: self.load()._org)
    orgStructure = property(lambda self: self.load()._orgStructure)
    document = property(lambda self: self.load()._document)


class CClientSocStatusInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        idList = getClientSocStatusIds(self.clientId)
        self._items = [ self.getInstance(CClientSocStatusInfo, id) for id in idList ]


class CClientSocStatusInfo(CInfo):
    def __init__(self, context, socStatusId):
        CInfo.__init__(self, context)
        self.socStatusId = socStatusId
        self._code = ''
        self._name = ''
        self._document = None
        self._classes = []

    def _load(self):
        db = QtGui.qApp.db
        tableClientSocStatus = db.table('ClientSocStatus')
        tableSocStatusType = db.table('rbSocStatusType')
        record = QtGui.qApp.db.getRecord(tableClientSocStatus.leftJoin(tableSocStatusType,
                                                                       tableSocStatusType['id'].eq(tableClientSocStatus['socStatusType_id'])),
                                         'code, name, document_id, socStatusType_id',
                                         self.socStatusId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._document = self.getInstance(CClientDocumentInfo, documentId=forceRef(record.value('document_id')))
            self._classes = self.getInstance(CSocStatusClassInfoList, forceRef(record.value('socStatusType_id')))
            return True
        return False

    code    = property(lambda self: self.load()._code)
    name    = property(lambda self: self.load()._name)
    document= property(lambda self: self.load()._document)
    classes = property(lambda self: self.load()._classes)

#    def __unicode__(self):
    def __str__(self):
        return self.load()._name


class CSocStatusClassInfoList(CInfoList):
    def __init__(self, context, socStatusTypeId):
        CInfoList.__init__(self, context)
        self.socStatusTypeId = socStatusTypeId

    def _load(self):
        idList = getSocStatusTypeClasses(self.socStatusTypeId)
        self._items = [ self.getInstance(CSocStatusClassInfo, id) for id in idList ]


class CSocStatusClassInfo(CInfo):
    def __init__(self, context, socStatusClassId):
        CInfo.__init__(self, context)
        self.socStatusClassId = socStatusClassId
        self._code = ''
        self._name = ''
        self._group = None

    def _load(self):
        record = QtGui.qApp.db.getRecord('rbSocStatusClass', 'code, name, group_id', self.socStatusClassId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            groupId = forceRef(record.value('group_id'))
            self._group = self.getInstance(CSocStatusClassInfo, groupId) if groupId else None
            return True
        return False

    code    = property(lambda self: self.load()._code)
    name    = property(lambda self: self.load()._name)
    group   = property(lambda self: self.load()._group)

#    def __unicode__(self):
    def __str__(self):
        return self.load()._name

    def isPartOf(self, name):
        return self._isPartOf(name.lower(), set([]))

    def _isPartOf(self, name, seen):
        self.load()
        if self._name.lower() == name:
            return True
        if self.socStatusClassId in seen:
            return None
        elif self._group:
            seen.add(self.socStatusClassId)
            return self._group._isPartOf(name, seen)
        else:
            return False


class CClientIntoleranceMedicamentInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientIntoleranceMedicament')
        idList = db.getIdList(table, 'id', table['client_id'].eq(self.clientId), 'id')
        self._items = [ self.getInstance(CClientIntoleranceMedicamentInfo, id) for id in idList ]
        return True


class CClientIntoleranceMedicamentInfo(CInfo):
    def __init__(self, context, itemId):
        CInfo.__init__(self, context)
        self.itemId = itemId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientIntoleranceMedicament')
        record = db.getRecord(table, ['nameMedicament', 'power', 'createDate', 'notes'], self.itemId)
        if record:
            self._name  = forceString(record.value('nameMedicament'))
            self._power = forceInt(record.value('power'))
            self._date  = CDateInfo(record.value('createDate'))
            self._notes = forceString(record.value('notes'))
            return True
        else:
            self._name  = ''
            self._power = 0
            self._date  = CDateInfo(None)
            self._notes = ''
            return False

    name  = property(lambda self: self.load()._name)
    power = property(lambda self: self.load()._power)
    date  = property(lambda self: self.load()._date)
    notes = property(lambda self: self.load()._notes)

#    def __unicode__(self):
    def __str__(self):
        return self.load()._name


class CClientAllergyInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientAllergy')
        idList = db.getIdList(table, 'id', table['client_id'].eq(self.clientId), 'id')
        self._items = [ self.getInstance(CClientAllergyInfo, id) for id in idList ]
        return True


class CClientAllergyInfo(CInfo):
    def __init__(self, context, itemId):
        CInfo.__init__(self, context)
        self.itemId = itemId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientAllergy')
        record = db.getRecord(table, ['nameSubstance', 'power', 'createDate', 'notes'], self.itemId)
        if record:
            self._name  = forceString(record.value('nameSubstance'))
            self._power = forceInt(record.value('power'))
            self._date  = CDateInfo(record.value('createDate'))
            self._notes = forceString(record.value('notes'))
            return True
        else:
            self._name  = ''
            self._power = 0
            self._date  = CDateInfo(None)
            self._notes = ''
            return False

    name   = property(lambda self: self.load()._name)
    power  = property(lambda self: self.load()._power)
    date   = property(lambda self: self.load()._date)
    notes  = property(lambda self: self.load()._notes)

#    def __unicode__(self):
    def __str__(self):
        return self.load()._name


class CClientIdentificationInfo(CInfo):
    def __init__(self, context, clientId):
        CInfo.__init__(self, context)
        self._clientId = clientId
        self._byCode = {}
#        self._byName = {}
        self._nameDict = {}


    def _load(self):
        db = QtGui.qApp.db
        tableCI = db.table('ClientIdentification')
        tableAS = db.table('rbAccountingSystem')
        stmt = db.selectStmt(tableCI.leftJoin(tableAS, tableAS['id'].eq(tableCI['accountingSystem_id'])),
                             ['code', 'name', 'identifier'],
                             db.joinAnd([tableCI['client_id'].eq(self._clientId),
                                         tableCI['deleted'].eq(0),
                                        ])
                            )
        query = db.query(stmt)
        while query.next():
            record = query.record()
            code = forceString(record.value('code'))
            name = forceString(record.value('name'))
            identifier = forceString(record.value('identifier'))
            self._byCode[code] = identifier
#            self._byName[name] = identifier
            self._nameDict[code] = name
        return True

    def has_key(self, key):
        return key in self.byCode

    def get(self, key, default=None):
        return self.byCode.get(key, default)

    def iter(self):
        return self.byCode.iter()

    def iteritems(self):
        return self.byCode.iteritems()

    def iterkeys(self):
        return self.byCode.iterkeys()

    def itervalues(self):
        return self.byCode.itervalues()

    def items(self):
        return self.byCode.items()

    def keys(self):
        return self.byCode.keys()

    def values(self):
        return self.byCode.values()

    def __nonzero__(self):
        return bool(self.byCode)

    def __len__(self):
        return len(self.byCode)

    def __contains__(self, key):
        return key in self.byCode

    def __getitem__(self, key):
        return self.byCode.get(key, '')

    def __iter__(self):
        return self.byCode.iterkeys()

    def __str__(self):
        self.load()
        l = [ u'%s (%s): %s' % (self._nameDict[code], code, identifier)
              for code, identifier in self.byCode.iteritems()
            ]
        l.sort()
        return ', '.join(l)

    byCode = property(lambda self: self.load()._byCode)
#    byName = property(lambda self: self.load()._byName)
    nameDict = property(lambda self: self.load()._nameDict)


class CClientRelationInfoList(CInfoList):
    def __init__(self, context, clientId, date):
        CInfoList.__init__(self, context)
        self.clientId = clientId
        self.date = date

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientRelation')
        directIdList = db.getIdList(table,
                              'id',
                              db.joinAnd([table['deleted'].eq(0),
                                          table['relativeType_id'].isNotNull(),
                                          table['client_id'].eq(self.clientId)
                                         ]),
                              'id')
        reversedIdList = db.getIdList(table,
                              'id',
                              db.joinAnd([table['deleted'].eq(0),
                                          table['relativeType_id'].isNotNull(),
                                          table['relative_id'].eq(self.clientId)
                                         ]),
                              'id')

        self._items = ([ self.getInstance(CClientRelationInfo, id, self.date, True) for id in directIdList ] +
                       [ self.getInstance(CClientRelationInfo, id, self.date, False) for id in reversedIdList ])
        return True


class CClientRelationInfo(CInfo):
    def __init__(self, context, itemId, date, isDirect):
        CInfo.__init__(self, context)
        self._itemId = itemId
        self._date = date
        self._isDirect = isDirect

    def _load(self):
        db = QtGui.qApp.db
        tableCR = db.table('ClientRelation')
        tableRT = db.table('rbRelationType')
        tableCR['relativeType_id']
        record = db.getRecord(tableCR.leftJoin(tableRT, tableRT['id'].eq(tableCR['relativeType_id'])),
                              ['client_id', 'relative_id',
                               'leftName', 'rightName',
                               'code',
                               'isDirectGenetic', 'isBackwardGenetic',
                               'isDirectRepresentative',  'isBackwardRepresentative',
                               'isDirectEpidemic', 'isBackwardEpidemic',
                               'isDirectDonation',  'isBackwardDonation',
                               'regionalCode', 'regionalReverseCode'],
                              self._itemId)
        if record:
            leftName  = forceString(record.value('leftName'))
            rightName = forceString(record.value('rightName'))
            code = forceString(record.value('code'))

            isDirectGenetic = forceBool(record.value('isDirectGenetic'))
            isBackwardGenetic = forceBool(record.value('isBackwardGenetic'))
            isDirectRepresentative = forceBool(record.value('isDirectRepresentative'))
            isBackwardRepresentative = forceBool(record.value('isBackwardRepresentative'))
            isDirectEpidemic = forceBool(record.value('isDirectEpidemic'))
            isBackwardEpidemic = forceBool(record.value('isBackwardEpidemic'))
            isDirectDonation = forceBool(record.value('isDirectDonation'))
            isBackwardDonation = forceBool(record.value('isBackwardDonation'))

            if self._isDirect:
                clientId = forceRef(record.value('relative_id'))
                role, otherRole = leftName, rightName
                regionalCode = forceString(record.value('regionalCode'))
            else:
                clientId = forceRef(record.value('client_id'))
                role, otherRole = rightName, leftName
                regionalCode = forceString(record.value('regionalReverseCode'))
                isDirectGenetic, isBackwardGenetic = isBackwardGenetic, isDirectGenetic
                isDirectRepresentative, isBackwardRepresentative = isBackwardRepresentative, isDirectRepresentative
                isDirectEpidemic, isBackwardEpidemic = isBackwardEpidemic, isDirectEpidemic
                isDirectDonation, isBackwardDonation = isBackwardDonation, isDirectDonation

            self._role = role
            self._otherRole = otherRole
            self._other = self.getInstance(CClientInfo, clientId, self._date)
            self._name = role + ' -> ' + otherRole
            self._code = code
            self._regionalCode = regionalCode
            self._isDirectGenetic = isDirectGenetic
            self._isBackwardGenetic = isBackwardGenetic
            self._isDirectRepresentative = isDirectRepresentative
            self._isBackwardRepresentative = isBackwardRepresentative
            self._isDirectEpidemic = isDirectEpidemic
            self._isBackwardEpidemic = isBackwardEpidemic
            self._isDirectDonation = isDirectDonation
            self._isBackwardDonation = isBackwardDonation
            return True
        else:
            self._role = ''
            self._otherRole = ''
            self._other = None
            self._name = ''
            self._code = ''
            self._regionalCode = ''
            self._isDirectGenetic = False
            self._isBackwardGenetic = False
            self._isDirectRepresentative = False
            self._isBackwardRepresentative = False
            self._isDirectEpidemic = False
            self._isBackwardEpidemic = False
            self._isDirectDonation = False
            self._isBackwardDonation = False
            return False


    role      = property(lambda self: self.load()._role)
    otherRole = property(lambda self: self.load()._otherRole)
    other     = property(lambda self: self.load()._other)
    name      = property(lambda self: self.load()._name)
    code      = property(lambda self: self.load()._code)
    regionalCode = property(lambda self: self.load()._regionalCode)
    isDirectGenetic          = property(lambda self: self.load()._isDirectGenetic)
    isBackwardGenetic        = property(lambda self: self.load()._isBackwardGenetic)
    isDirectRepresentative   = property(lambda self: self.load()._isDirectRepresentative)
    isBackwardRepresentative = property(lambda self: self.load()._isBackwardRepresentative)
    isDirectEpidemic         = property(lambda self: self.load()._isDirectEpidemic)
    isBackwardEpidemic       = property(lambda self: self.load()._isBackwardEpidemic)
    isDirectDonation         = property(lambda self: self.load()._isDirectDonation)
    isBackwardDonation       = property(lambda self: self.load()._isBackwardDonation)

    def __str__(self):
        return self.name + ' ' + self.other


class CClientPolicyInfo(CInfo):
    def __init__(self, context, clientId, isCompulsory=True):
        CInfo.__init__(self, context)
        self.clientId = clientId
        self.isCompulsory = isCompulsory

    def _load(self):
        record = getClientPolicyEx(self.clientId, self.isCompulsory)
        if record:
            policyTypeId  = forceRef(record.value('policyType_id'))
            self._policyType = forceString(QtGui.qApp.db.translate('rbPolicyType', 'id', policyTypeId, 'name'))
            self._insurer = self.getInstance(COrgInfo, forceRef(record.value('insurer_id')))
            self._serial  = forceString(record.value('serial'))
            self._number  = forceString(record.value('number'))
            self._name    = forceString(record.value('name'))
            self._note    = forceString(record.value('note'))
            self._begDate = CDateInfo(record.value('begDate'))
            self._endDate = CDateInfo(record.value('endDate'))
            return True
        else:
            self._policyType = u'-'
            self._insurer = self.getInstance(COrgInfo, None)
            self._serial  = ''
            self._number  = ''
            self._name    = ''
            self._note    = ''
            self._begDate = CDateInfo()
            self._endDate = CDateInfo()
            return False

#    def __unicode__(self):
    def __str__(self):
        self.load()
        return (' '.join([self._policyType, unicode(self._insurer), self._serial, self._number])).strip()

    policyType  = property(lambda self: self.load()._policyType)
    type        = property(lambda self: self.load()._policyType)
    insurer     = property(lambda self: self.load()._insurer)
    serial      = property(lambda self: self.load()._serial)
    number      = property(lambda self: self.load()._number)
    name        = property(lambda self: self.load()._name)
    note        = property(lambda self: self.load()._note)
#    notes       = note
    begDate     = property(lambda self: self.load()._begDate)
    endDate     = property(lambda self: self.load()._endDate)


class CClientDocumentInfo(CInfo):
    def __init__(self, context, clientId=None, documentId=None):
        CInfo.__init__(self, context)
        self._clientId = clientId
        self._documentId = documentId
        self._documentType = u'-'
        self._serial = ''
        self._number = ''
        self._date = CDateInfo()
        self._origin = ''

    def _load(self):
        if self._documentId:
            record = QtGui.qApp.db.getRecord('ClientDocument', '*', self._documentId)
        elif self._clientId:
            record = getClientDocument(self._clientId)
        else:
            record = None
        if record:
            documentTypeId = forceRef(record.value('documentType_id'))
            self._documentType = forceString(QtGui.qApp.db.translate('rbDocumentType', 'id', documentTypeId, 'name'))
            self._documentTypeCode = forceString(QtGui.qApp.db.translate('rbDocumentType', 'id', documentTypeId,
                                                                         'regionalCode'))
            self._serial = forceString(record.value('serial'))
            self._number = forceString(record.value('number'))
            self._date = CDateInfo(forceDate(record.value('date')))
            self._origin = forceString(record.value('origin'))
            return True
        else:
            return False

#    def __unicode__(self):
    def __str__(self):
        self.load()
        return (' '.join([self._documentType, self._serial, self._number])).strip()

    documentType = property(lambda self: self.load()._documentType)
    type         = property(lambda self: self.load()._documentType)
    documentTypeCode = property(lambda self: self.load()._documentTypeCode)
    serial       = property(lambda self: self.load()._serial)
    number       = property(lambda self: self.load()._number)
    date         = property(lambda self: self.load()._date)
    origin       = property(lambda self: self.load()._origin)


class CBloodTypeInfo(CRBInfo):
    tableName = 'rbBloodType'


class CClientInfo(CInfo):
    def __init__(self, context, id, date=None):
        CInfo.__init__(self, context)
        self._id = id
        self._loaded = True
        self._ok = id
        #sself.date = date if date is not None else QDate.currentDate()

        db_session = get_lpu_session()
        record = db_session.query(Client).get(id)
        db_session.close()
        if record:
            self._initByRecord(record)
        else:
            self._initByNone()

    def getInstance(self, infoClass, id):
        db_session = get_lpu_session()
        record = db_session.query(infoClass).get(id)
        db_session.close()
        return record

    def _initByNone(self):
        self._lastName  = ''
        self._firstName = ''
        self._patrName  = ''
        self._nameText  = ''
        self._sexCode   = None
        self._sex       = None
        #self._birthDate = CDateInfo(None)
        self._birthPlace = ''
        self._ageTuple  = None
        self._age       = None
        self._SNILS     = ''
        self._notes     = ''
        # self._permanentAttach = self.getInstance(CClientAttachInfo, None, False)
        # self._temporaryAttach = self.getInstance(CClientAttachInfo, None, True)
        # self._socStatuses = self.getInstance(CClientSocStatusInfoList, None)
        # self._document  = self.getInstance(CClientDocumentInfo, None)
        # self._compulsoryPolicy = self.getInstance(CClientPolicyInfo, None, True)
        # self._voluntaryPolicy  = self.getInstance(CClientPolicyInfo, None, False)
        # self._policy     = self._compulsoryPolicy
        # self._policyDMS  = self._voluntaryPolicy
        # self._regAddress = self.getInstance(CClientAddressInfo, None, 0)
        # self._locAddress = self.getInstance(CClientAddressInfo, None, 1)
        # self._work       = self.getInstance(CClientWorkInfo, None)
        # self._phones     = getClientPhonesEx(None)
        # self._bloodType  = None
        # self._intolerances = self.getInstance(CClientIntoleranceMedicamentInfoList, None)
        # self._allergies    = self.getInstance(CClientAllergyInfoList, None)
        # self._identification = self.getInstance(CClientIdentificationInfo, None)
        # self._relations    = self.getInstance(CClientRelationInfoList, None, self.date)

    def _initByRecord(self, record):
        self._lastName  = record.lastName
        self._firstName = record.firstName
        self._patrName  = record.patrName
        self._nameText  = u' '.join((u'%s %s %s' % (self._lastName, self._firstName, self._patrName)).split())
        self._sexCode   = record.sex
        # self._sex       = formatSex(self._sexCode)
        # self._birthDate = CDateInfo(record.value('birthDate'))
        self._birthPlace = forceString(record.value('birthPlace'))
        # self._ageTuple  = calcAgeTuple(self._birthDate.date, self.date)
        # self._age       = formatAgeTuple(self._ageTuple, self._birthDate.date, self.date)
        self._SNILS     = formatSNILS(forceString(record.value('SNILS')))
        self._notes     = forceString(record.value('notes'))
        # self._permanentAttach = self.getInstance(CClientAttachInfo, self._id, False)
        # self._temporaryAttach = self.getInstance(CClientAttachInfo, self._id, True)
        # self._socStatuses = self.getInstance(CClientSocStatusInfoList, self._id)
        self._document  = self.getInstance(CClientDocumentInfo, clientId=self._id)
        # self._compulsoryPolicy = self.getInstance(CClientPolicyInfo, self._id, True)
        # self._voluntaryPolicy  = self.getInstance(CClientPolicyInfo, self._id, False)
        # self._policy     = self._compulsoryPolicy
        # self._policyDMS  = self._voluntaryPolicy
        # self._regAddress = self.getInstance(CClientAddressInfo, self._id, 0)
        # self._locAddress = self.getInstance(CClientAddressInfo, self._id, 1)
        # self._work       = self.getInstance(CClientWorkInfo, self._id)
        # self._phones     = getClientPhonesEx(self._id)
        #self._bloodType = self.getInstance(Rbbloodtype, record.bloodType_id)
        # self._intolerances = self.getInstance(CClientIntoleranceMedicamentInfoList, self._id)
        # self._allergies    = self.getInstance(CClientAllergyInfoList, self._id)
        # self._identification = self.getInstance(CClientIdentificationInfo, self._id)
        # self._relations    = self.getInstance(CClientRelationInfoList, self._id, self.date)

    # def __str__(self):
    #     self.load()
    #     return formatShortNameInt(self._lastName, self._firstName, self._patrName)
    #
    # fullName = property(lambda self: formatNameInt(self._lastName, self._firstName,self._patrName))
    # shortName = property(lambda self: formatShortNameInt(self._lastName, self._firstName,self._patrName))

    id = property(lambda self: self._id)
    lastName  = property(lambda self: self._lastName)
    firstName = property(lambda self: self._firstName)
    patrName  = property(lambda self: self._patrName)
    nameText  = property(lambda self: self._nameText)
    sexCode   = property(lambda self: self._sexCode)
    # sex       = property(lambda self: self._sex)
    # birthDate = property(lambda self: self._birthDate)
    # birthPlace = property(lambda self: self._birthPlace)
    # ageTuple  = property(lambda self: self._ageTuple)
    # age       = property(lambda self: self._age)
    # SNILS     = property(lambda self: self._SNILS)
    # notes     = property(lambda self: self._notes)
    # permanentAttach = property(lambda self: self._permanentAttach)
    # temporaryAttach = property(lambda self: self._temporaryAttach)
    # socStatuses = property(lambda self: self._socStatuses)
    # document  = property(lambda self: self._document)
    # compulsoryPolicy = property(lambda self: self._compulsoryPolicy)
    # voluntaryPolicy  = property(lambda self: self._voluntaryPolicy)
    # policy     = property(lambda self: self._policy)
    # policyDMS  = property(lambda self: self._policyDMS)
    # regAddress = property(lambda self: self._regAddress)
    # locAddress = property(lambda self: self._locAddress)
    # work       = property(lambda self: self._work)
    # phones     = property(lambda self: self._phones)
    # bloodType = property(lambda self: self._bloodType)
    # intolerances = property(lambda self: self._intolerances)
    # allergies    = property(lambda self: self._allergies)
    # identification = property(lambda self: self._identification)
    # relations    = property(lambda self: self._relations)