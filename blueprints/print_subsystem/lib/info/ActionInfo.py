  # -*- coding: utf-8 -*-
# from Events.Action import *
from PyQt4 import QtGui
from tempfile import mkstemp

from PyQt4.QtCore import *

from Events.Action import CActionTypeCache, CAction
from Events.ContractTariffCache import CContractTariffCache
from Events.Service import CServiceInfo
from ..info.OrgInfo import CClientInfo
from ..info.PersonInfo import CPersonInfo
from ..info.PrintInfo import CInfo, CTemplatableInfoMixin, CInfoProxyList, CDateTimeInfo
from library.Utils import *
from library.exception import CException
from library.InfoProvider import TakenTissueJournalInfoProvider, RBCache, EventInfoProvider
from library.barcode import code128C


class CActionTypeInfo(CInfo):
    def __init__(self, context, actionType):
        CInfo.__init__(self, context)
        self._actionType = actionType


    def _getGroup(self):
        groupId = self._actionType.groupId if self._actionType else None
        actionType = CActionTypeCache.getById(groupId) if groupId else None
        return self.getInstance(CActionTypeInfo, actionType)


    def __nonzero__(self):
        return bool(self._actionType)


    group   = property(_getGroup)
    class_  = property(lambda self: self._actionType.class_ if self._actionType else None)
    code    = property(lambda self: self._actionType.code  if self._actionType else None)
    flatCode= property(lambda self: self._actionType.flatCode if self._actionType else None)
    name    = property(lambda self: self._actionType.name  if self._actionType else None)
    title   = property(lambda self: self._actionType.title if self._actionType else None)
    service = property(lambda self: self.getInstance(CServiceInfo, self._actionType.serviceId if self._actionType else None))
    showTime= property(lambda self: self._actionType.showTime if self._actionType else None)
    isMes  = property(lambda self: self._actionType.isMes if self._actionType else None)
    nomenclatureService = property(lambda self: self.getInstance(CServiceInfo, self._actionType.nomenclatureServiceId if self._actionType else None))
    isHtml  = property(lambda self: self._actionType.isHtml() if self._actionType else None)

class CCookedActionInfoEx(CActionTypeInfo, CTemplatableInfoMixin):
    def __init__(self, context, action):
        CActionTypeInfo.__init__(self, context, action.getType() if action else None)
        self._action = action
        self._eventInfo = None
        self._loaded = True
        self._ok = True
        self._price = None
        self.currentPropertyIndex = -1

    def getPrintTemplateContext(self):
        return self._action.getType().context

    def getEventInfo(self):
        if not self._eventInfo:
            from library.printing.info.EventInfo import CEventInfo
            eventId = forceRef(self._action._record.value('event_id')) if self._action._record else None
            self._eventInfo = self.getInstance(CEventInfo, eventId)
        return self._eventInfo

    def getData(self):
        itemId = forceRef(self._action._record.value('id')) if self._action._record else None
        eventInfo = self.getEventInfo()
        eventActions = eventInfo.actions
        eventActions._idList = [itemId]
        eventActions._items  = [self]
        eventActions._loaded = True
        return { 'event'  : eventInfo,
                 'action' : self,
                 'client' : eventInfo.client,
                 'actions': eventActions,
                 'currentActionIndex': 0,
                 'tempInvalid': None
               }

    def setCurrentPropertyIndex(self, currentPropertyIndex):
        self.currentPropertyIndex = currentPropertyIndex

    def getPrice(self, tariffCategoryId = None):
        if self._price is None:
            self.load()
            event = self.getEventInfo()
            tariffDescr = event.getTariffDescr()
            tariffList = tariffDescr.actionTariffList
            serviceId = self.service.id
            tariffCategoryId = self.person.tariffCategory.id
            self._price = CContractTariffCache.getPrice(tariffList, serviceId, tariffCategoryId)
        return self._price

    def getFinanceInfo(self):
        financeId = forceRef(self._action._record.value('finance_id'))
        if financeId:
            from library.printing.info.EventInfo import CFinanceInfo
            return self.getInstance(CFinanceInfo, financeId)
        elif self.getEventInfo():
            return self.getEventInfo().finance
        else:
            return self.getInstance(CFinanceInfo, None)

    event = property(getEventInfo)
    directionDate = property(lambda self: CDateTimeInfo(forceDateTime(self._action._record.value('directionDate'))))
    begDate = property(lambda self: CDateTimeInfo(forceDateTime(self._action._record.value('begDate'))))
    plannedEndDate = property(lambda self: CDateTimeInfo(forceDateTime(self._action._record.value('plannedEndDate'))))
    endDate = property(lambda self: CDateTimeInfo(forceDateTime(self._action._record.value('endDate'))))
    isUrgent = property(lambda self: forceBool(self._action._record.value('isUrgent')))
    coordDate = property(lambda self: CDateTimeInfo(forceDate(self._action._record.value('coordDate'))))
    coordAgent = property(lambda self: forceString(self._action._record.value('coordAgent')))
    coordInspector = property(lambda self: forceString(self._action._record.value('coordInspector')))
    coordText = property(lambda self: forceString(self._action._record.value('coordText')))
    status = property(lambda self: forceInt(self._action._record.value('status')))
    office = property(lambda self: forceString(self._action._record.value('office')))
    note = property(lambda self: forceString(self._action._record.value('note')))
    amount = property(lambda self: forceDouble(self._action._record.value('amount')))
    setPerson = property(lambda self: self.getInstance(CPersonInfo, forceRef(self._action._record.value('setPerson_id'))))
    person = property(lambda self: self.getInstance(CPersonInfo, forceRef(self._action._record.value('person_id'))))
    expose = property(lambda self: forceBool(self._action._record.value('expose')))
    account = property(lambda self: forceBool(self._action._record.value('account')))
    price = property(getPrice)
    finance = property(getFinanceInfo)
    action_id = property(lambda self: forceInt(self._action._record.value('id')))
    takenTissueJournal_id = property(lambda self: forceInt(self._action._record.value('takenTissueJournal_id')))
    takenTissue = property(lambda self: self.getInstance(CTakenTissueJournalInfo, forceInt(self._action._record.value('takenTissueJournal_id'))))

    def __len__(self):
        self.load()
        return len(self._action.getProperties())

    def __getitem__(self, key):
        if isinstance(key, (basestring, QString)):
            try:
                return self.getInstance(CPropertyInfo, self._action.getProperty(unicode(key)))
            except KeyError:
                actionType = self._action.getType()
                QtGui.qApp.log('!!!!!!!!!!!', actionType.name)
                QtGui.qApp.log('!!!!!!!!!!!', key)
                raise CException(u'Действие типа "%s" не имеет свойства "%s"' % (actionType.name, unicode(key)))
        elif isinstance(key, (int, long)):
            try:
                return self.getInstance(CPropertyInfo, self._action.getPropertyByIndex(key))
            except IndexError:
                actionType = self._action.getType()
                raise CException(u'Действие типа "%s" не имеет свойства c индексом "%s"' % (actionType.name, unicode(key)))
        elif isinstance(key, tuple):
            try:
                return self.getInstance(CPropertyInfo, self._action.getPropertyByCode(unicode(key[0])))
            except KeyError:
                actionType = self._action.getType()
                raise CException(u'Действие типа "%s" не имеет свойства "%s"' % (actionType.name, unicode(key)))
        else:
            raise TypeError, u'Action property subscription must be string or integer'

    def __iter__(self):
        for property in self._action.getProperties():
            yield self.getInstance(CPropertyInfo, property)

    def __contains__(self, key):
        if isinstance(key, (basestring, QString)):
            return unicode(key) in self._action._propertiesByName
        if isinstance(key, (int, long)):
            return 0<=key<len(self._action._propertiesById)
        else:
            raise TypeError, u'Action property subscription must be string or integer'

    def has_key(self, key):
        return self.__contains__(key)

    def rmCacheImages(self):
        for property in self._action.getProperties():
            if property.getImgFileName() is not None:
                try:
                    os.remove(property.getImgFileName())
                except:
                    pass


class CCookedActionInfo(CActionTypeInfo, CTemplatableInfoMixin):
    def __init__(self, context, record, action):
        CActionTypeInfo.__init__(self, context, action.getType() if action else None)
        self._record = record
        self._action = action
        self._eventInfo = None
        self._loaded = True
        self._ok = True
        self._price = None
        self.currentPropertyIndex = -1


    def getPrintTemplateContext(self):
        return self._action.getType().context


    def getEventInfo(self):
        if not self._eventInfo:
            from library.printing.info.EventInfo import CEventInfo
            eventId = forceRef(self._record.value('event_id')) if self._record else None
            self._eventInfo = self.getInstance(CEventInfo, eventId)
        return self._eventInfo


    def getData(self):
        itemId = forceRef(self._record.value('id')) if self._record else None
        eventInfo = self.getEventInfo()
        eventActions = eventInfo.actions
        eventActions._idList = [itemId]
        eventActions._items  = [self]
        eventActions._loaded = True

        return { 'event'  : eventInfo,
                 'action' : self,
                 'client' : eventInfo.client,
                 'actions': eventActions,
                 'currentActionIndex': 0,
                 'tempInvalid': None
               }


    def setCurrentPropertyIndex(self, currentPropertyIndex):
        self.currentPropertyIndex = currentPropertyIndex


    def getPrice(self, tariffCategoryId = None):
        if self._price is None:
            self.load()
            event = self.getEventInfo()
            tariffDescr = event.getTariffDescr()
            tariffList = tariffDescr.actionTariffList
            serviceId = self.service.id
            tariffCategoryId = self.person.tariffCategory.id
            self._price = CContractTariffCache.getPrice(tariffList, serviceId, tariffCategoryId)
        return self._price


    def getFinanceInfo(self):
        financeId = forceRef(self._record.value('finance_id'))
        if financeId:
            from library.printing.info.EventInfo import CFinanceInfo
            return self.getInstance(CFinanceInfo, financeId)
        elif self.getEventInfo():
            return self.getEventInfo().finance
        else:
            return self.getInstance(CFinanceInfo, None)


    event = property(getEventInfo)
    directionDate = property(lambda self: CDateTimeInfo(forceDateTime(self._record.value('directionDate'))))
    begDate = property(lambda self: CDateTimeInfo(forceDateTime(self._record.value('begDate'))))
    plannedEndDate = property(lambda self: CDateTimeInfo(forceDateTime(self._record.value('plannedEndDate'))))
    endDate = property(lambda self: CDateTimeInfo(forceDateTime(self._record.value('endDate'))))
    isUrgent = property(lambda self: forceBool(self._record.value('isUrgent')))
    coordDate = property(lambda self: CDateTimeInfo(forceDate(self._record.value('coordDate'))))
    coordAgent = property(lambda self: forceString(self._record.value('coordAgent')))
    coordInspector = property(lambda self: forceString(self._record.value('coordInspector')))
    coordText = property(lambda self: forceString(self._record.value('coordText')))
    status = property(lambda self: forceInt(self._record.value('status')))
    office = property(lambda self: forceString(self._record.value('office')))
    note = property(lambda self: forceString(self._record.value('note')))
    amount = property(lambda self: forceDouble(self._record.value('amount')))
    setPerson = property(lambda self: self.getInstance(CPersonInfo, forceRef(self._record.value('setPerson_id'))))
    person = property(lambda self: self.getInstance(CPersonInfo, forceRef(self._record.value('person_id'))))
    expose = property(lambda self: forceBool(self._record.value('expose')))
    account = property(lambda self: forceBool(self._record.value('account')))
    price = property(getPrice)
    finance = property(getFinanceInfo)
    action_id = property(lambda self: forceInt(self._record.value('id')))
    takenTissueJournal_id = property(lambda self: forceInt(self._record.value('takenTissueJournal_id')))
    takenTissue = property(lambda self: self.getInstance(CTakenTissueJournalInfo, forceInt(self._record.value('takenTissueJournal_id'))))


    def __len__(self):
        self.load()
        return len(self._action.getProperties())


    def __getitem__(self, key):
        if isinstance(key, (basestring, QString)):
            try:
                return self.getInstance(CPropertyInfo, self._action.getProperty(unicode(key)))
            except KeyError:
                actionType = self._action.getType()
                QtGui.qApp.log('!!!!!!!!!!!', actionType.name)
                QtGui.qApp.log('!!!!!!!!!!!', key)
                raise CException(u'Действие типа "%s" не имеет свойства "%s"' % (actionType.name, unicode(key)))
        elif isinstance(key, tuple):
            try:
                return self.getInstance(CPropertyInfo, self._action.getPropertyByCode(unicode(key[0])))
            except KeyError:
                actionType = self._action.getType()
                raise CException(u'Действие типа "%s" не имеет свойства "%s"' % (actionType.name, unicode(key)))
        elif isinstance(key, (int, long)):
            try:
                return self.getInstance(CPropertyInfo, self._action.getPropertyByIndex(key))
            except IndexError:
                actionType = self._action.getType()
                raise CException(u'Действие типа "%s" не имеет свойства c индексом "%s"' % (actionType.name, unicode(key)))
        else:
            raise TypeError, u'Action property subscription must be string or integer'


    def __iter__(self):
        for property in self._action.getProperties():
            yield self.getInstance(CPropertyInfo, property)


    def __contains__(self, key):
        if isinstance(key, (basestring, QString)):
            return self._action.hasProperty(unicode(key))
        elif isinstance(key, (int, long)):
            return 0<=key<len(self._action.getPropertiesById())
        elif isinstance(key, (tuple, list)):
            return self._action.hasProperty(key)
        else:
            raise TypeError, u'Action property subscription must be string or integer'

    def rmCacheImages(self):
        for property in self._action.getProperties():
            if property.getImgFileName() is not None:
                try:
                    os.remove(property.getImgFileName())
                except:
                    pass


class CActionInfo(CCookedActionInfo):
    def __init__(self, context, actionId):
        db = QtGui.qApp.db
        record = db.getRecord('Action', '*', actionId)
        action = CAction(record=record)
        CCookedActionInfo.__init__(self, context, record, action)


class CPropertyInfo(CInfo):
    def _load(self):
        super(CPropertyInfo, self)._load()

    def __init__(self, context, property):
        CInfo.__init__(self, context)
        self._property = property
        self._loaded = True
        self._ok = True
        self.imgUrl = None
        if self.image is not None:
            expectCacheDir = os.path.join(os.getcwd(),'cache')
            cacheDir = expectCacheDir if os.path.isdir(expectCacheDir) else os.getcwd()
            try:
                fName = mkstemp(suffix='.png', dir=cacheDir)[1]
                self.image.save(fName)
                self.imgUrl = fName
                property.setImgFileName(fName)
            except:
                QtGui.qApp.logCurrentException()

    def _getImageUrl(self):
        return self.imgUrl

    value = property(lambda self: self._property.getInfo(self.context))
    name  = property(lambda self: self._property._type.name)
    descr = property(lambda self: self._property._type.descr)
    unit  = property(lambda self: forceString(QtGui.qApp.db.translate('rbUnit', 'id', self._property.getUnitId(), 'code')))
    norm  = property(lambda self: self._property.getNorm())
    isAssigned = property(lambda self: self._property.isAssigned())
    evaluation = property(lambda self: self._property.getEvaluation())
    isAssignable = property(lambda self: self._property._type.isAssignable)
    image = property(lambda self: self._property.getImage())
    imageUrl = property(_getImageUrl)

    def __str__(self):
#        v = self._property.getValue()
#        return forceString(v) if v else ''
        return forceString(self.value)


class CActionInfoProxyListEx(CInfoProxyList):
    def __init__(self, context, eventInfo):
        CInfoProxyList.__init__(self, context)
        eventInfoProvider = EventInfoProvider.getById(eventInfo.id)
        eventInfoProvider.loadChildren()
        self._rawItems = eventInfoProvider.keys()
        self._items = [ None ]*len(self._rawItems)
        self._eventInfo = eventInfo


    def __getitem__(self, key):
        v = self._items[key]
        if v is None:
            actionId = self._rawItems[key]
            v = self.getInstance(CCookedActionInfoEx, CAction.getById(actionId))
            v._eventInfo = self._eventInfo
            self._items[key] = v
        return v

class CActionInfoProxyList(CInfoProxyList):
    def __init__(self, context, models, eventInfo):
        CInfoProxyList.__init__(self, context)
        self._rawItems = []
        for model in models:
            self._rawItems.extend(model.items())
        self._items = [ None ]*len(self._rawItems)
        self._eventInfo = eventInfo


    def __getitem__(self, key):
        v = self._items[key]
        if v is None:
            record, action = self._rawItems[key]
            v = self.getInstance(CCookedActionInfo, record, action)
            v._eventInfo = self._eventInfo
            self._items[key] = v
        return v

class CTissueTypeInfo(CInfo):
    def __init__(self, context, TT_id):
        CInfo.__init__(self, context)
        if TT_id:
            self.TT = RBCache.getRBId('rbTissueType', TT_id)
        else:
            self.TT = object()
            self.TT.code = u''
            self.TT.name = u''
            self.sex = 0

    code         = property(lambda self: self.TT.code)
    name         = property(lambda self: self.TT.name)
    sex          = property(lambda self: {0: u'Любой',
                                          1: u'М',
                                          2: u'Ж'} [self.TT.sex])

class CTakenTissueJournalInfo(CInfo):
    def __init__(self, context, TTJ_id):
        CInfo.__init__(self, context)
        self._TTJ = TakenTissueJournalInfoProvider.getById(TTJ_id)

    client        = property(lambda self: self.getInstance(CClientInfo, self._TTJ.client_id))
    tissueType    = property(lambda self: self.getInstance(CTissueTypeInfo, self._TTJ.tissueType_id))
    externalId    = property(lambda self: self._TTJ.externalId)
    amount        = property(lambda self: self._TTJ.amount)
    unit          = property(lambda self: RBCache.getRBId('rbUnit', self._TTJ.unit_id).code)
    datetimeTaken = property(lambda self: CDateTimeInfo(self._TTJ.datetimeTaken))
    execPerson    = property(lambda self: self.getInstance(CPersonInfo, self._TTJ.execPerson_id))
    note          = property(lambda self: self._TTJ.note)
    barcode       = property(lambda self: self._TTJ.barcode)
    barcode_s     = property(lambda self: code128C(self._TTJ.barcode).decode('windows-1252')) # Да, использует именно эту кодировку, я проверял.
    period        = property(lambda self: self._TTJ.period)
