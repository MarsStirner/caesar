# -*- coding: utf-8 -*-
import struct
from application.database import db
from config import MODULE_NAME
from sqlalchemy import BigInteger, Column, Date, DateTime, Enum, Float, ForeignKey, Index, Integer, SmallInteger, \
    String, Table, Text, Time, Unicode, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.base import LONGBLOB, MEDIUMBLOB
from sqlalchemy.ext.declarative import declarative_base


TABLE_PREFIX = MODULE_NAME
Base = declarative_base()
metadata = Base.metadata


class ConfigVariables(Base):
    __tablename__ = '%s_config' % TABLE_PREFIX

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(25), unique=True, nullable=False)
    name = Column(Unicode(50), unique=True, nullable=False)
    value = Column(Unicode(100))
    value_type = Column(String(30))

    def __unicode__(self):
        return self.code


class Info(object):
    u"""Базовый класс для представления объектов при передаче в шаблоны печати"""

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


class RBInfo(Info):
    def __unicode__(self):
        return self.name


class CInfoList(Info):
    u"""Базовый класс для представления списков (массивов) объектов при передаче в шаблоны печати"""

    def __len__(self):
        return len(self._items)

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __str__(self):
        return u', '.join([unicode(x) for x in self._items])

    def __nonzero__(self):
        return bool(self._items)

    # def filter(self, **kw):
    #     result = CInfoList(self.context)
    #     result._loaded = True
    #     result._ok = True
    #
    #     for item in self._items:
    #         if all([item.__getattribute__(key) == value for key, value in kw.iteritems()]):
    #             result._items.append(item)
    #     return result
    #
    # def __add__(self, right):
    #     if isinstance(right, CInfoList):
    #         right.load()
    #         rightItems = right._items
    #     elif isinstance(right, list):
    #         rightItems = right
    #     else:
    #         raise TypeError(u'can only concatenate CInfoList or list (not "%s") to CInfoList' % type(right).__name__)
    #     result = CInfoList(self.context)
    #     result._loaded = True
    #     result._ok = True
    #     result._items = self._items + rightItems
    #     return result


class Account(Base):
    __tablename__ = u'Account'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    contract_id = Column(Integer, nullable=False, index=True)
    orgStructure_id = Column(Integer)
    payer_id = Column(Integer, nullable=False, index=True)
    settleDate = Column(Date, nullable=False)
    number = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    uet = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    sum = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    exposeDate = Column(Date)
    payedAmount = Column(Float(asdecimal=True), nullable=False)
    payedSum = Column(Float(asdecimal=True), nullable=False)
    refusedAmount = Column(Float(asdecimal=True), nullable=False)
    refusedSum = Column(Float(asdecimal=True), nullable=False)
    format_id = Column(Integer, index=True)


class AccountItem(Base):
    __tablename__ = u'Account_Item'

    id = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(Integer, nullable=False, index=True)
    serviceDate = Column(Date, server_default=u"'0000-00-00'")
    event_id = Column(Integer, index=True)
    visit_id = Column(Integer, index=True)
    action_id = Column(Integer, index=True)
    price = Column(Float(asdecimal=True), nullable=False)
    unit_id = Column(Integer, index=True)
    amount = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    uet = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    sum = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    date = Column(Date)
    number = Column(String(20), nullable=False)
    refuseType_id = Column(Integer, index=True)
    reexposeItem_id = Column(Integer, index=True)
    note = Column(String(256), nullable=False)
    tariff_id = Column(Integer, index=True)
    service_id = Column(Integer)
    paymentConfirmationDate = Column(Date)


class Action(Base):
    __tablename__ = u'Action'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    actionType_id = Column(Integer, ForeignKey('ActionType.id'), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('Event.id'), index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    directionDate = Column(DateTime)
    status = Column(Integer, nullable=False)
    setPerson_id = Column(Integer, ForeignKey('Person.id'), index=True)
    isUrgent = Column(Boolean, nullable=False, server_default=u"'0'")
    begDate = Column(DateTime)
    plannedEndDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime)
    note = Column(Text, nullable=False)
    person_id = Column(Integer, ForeignKey('Person.id'), index=True)
    office = Column(String(16), nullable=False)
    amount = Column(Float(asdecimal=True), nullable=False)
    uet = Column(Float(asdecimal=True), server_default=u"'0'")
    expose = Column(Boolean, nullable=False, server_default=u"'1'")
    payStatus = Column(Integer, nullable=False)
    account = Column(Boolean, nullable=False)
    finance_id = Column(Integer, ForeignKey('rbFinance.id'), index=True)
    prescription_id = Column(Integer, index=True)
    takenTissueJournal_id = Column(ForeignKey('TakenTissueJournal.id'), index=True)
    contract_id = Column(Integer, index=True)
    coordDate = Column(DateTime)
    coordAgent = Column(String(128), nullable=False, server_default=u"''")
    coordInspector = Column(String(128), nullable=False, server_default=u"''")
    coordText = Column(String, nullable=False)
    hospitalUidFrom = Column(String(128), nullable=False, server_default=u"'0'")
    pacientInQueueType = Column(Integer, server_default=u"'0'")
    AppointmentType = Column(Enum(u'0', u'amb', u'hospital', u'polyclinic', u'diagnostics', u'portal', u'otherLPU'), nullable=False)
    version = Column(Integer, nullable=False, server_default=u"'0'")
    parentAction_id = Column(Integer, index=True)
    uuid_id = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    dcm_study_uid = Column(String(50))

    actionType = relationship(u'Actiontype')
    event = relationship(u'Event')
    person = relationship(u'Person', foreign_keys='Action.person_id')
    setPerson = relationship(u'Person', foreign_keys='Action.setPerson_id')
    takenTissueJournal = relationship(u'Takentissuejournal')
    tissues = relationship(u'Tissue', secondary=u'ActionTissue')
    properties = relationship(u'Actionproperty')

    # def getPrice(self, tariffCategoryId=None):
    #     if self.price is None:
    #         event = self.getEventInfo()
    #         tariffDescr = event.getTariffDescr()
    #         tariffList = tariffDescr.actionTariffList
    #         serviceId = self.service.id
    #         tariffCategoryId = self.person.tariffCategory.id
    #         self._price = CContractTariffCache.getPrice(tariffList, serviceId, tariffCategoryId)
    #     return self._price

    @property
    def finance(self):
        if self.finance_id:
            return relationship(u'Rbfinance')
        else:
            return self.event.eventType.finance

    def __iter__(self):
        for property in self.properties:
            yield property


class Bbtresponse(Action):
    __tablename__ = u'bbtResponse'

    id = Column(ForeignKey('Action.id'), primary_key=True)
    final = Column(Integer, nullable=False, server_default=u"'0'")
    defects = Column(Text)
    doctor_id = Column(ForeignKey('Person.id'), nullable=False, index=True)
    codeLIS = Column(String(20), nullable=False)

    doctor = relationship(u'Person')


class Actionproperty(Base, Info):
    __tablename__ = u'ActionProperty'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    action_id = Column(Integer, ForeignKey('Action.id'), nullable=False, index=True)
    type_id = Column(Integer, ForeignKey('ActionPropertyType.id'), nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey('rbUnit.id'), index=True)
    norm = Column(String(64), nullable=False)
    isAssigned = Column(Boolean, nullable=False, server_default=u"'0'")
    evaluation = Column(Integer)
    version = Column(Integer, nullable=False, server_default=u"'0'")

    type = relationship(u'Actionpropertytype')
    unit_all = relationship(u'Rbunit')

    @property
    def name(self):
        return self.type.name

    @property
    def descr(self):
        return self.type.descr

    @property
    def unit(self):
        return self.unit_all.code

    @property
    def isAssignable(self):
        return self.type.isAssignable

    @property
    def value(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        class_name = u'Actionproperty{}'.format(u"String" if (self.type.typeName == "Text" or
                                                              self.type.typeName == "Constructor" or
                                                              self.type.typeName == "Html") else self.type.typeName.capitalize())
        cl = globals()[class_name]
        values = db_session.query(cl).filter(cl.id == self.id).all()
        if values and self.type.isVector:
            return [value.value for value in values]
        elif values:
            return values[0].value
        else:
            return ""

    def __unicode__(self):
        return unicode(self.value)
    # image = property(lambda self: self._property.getImage())
    # imageUrl = property(_getImageUrl)


class Actionpropertytemplate(Base):
    __tablename__ = u'ActionPropertyTemplate'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    group_id = Column(Integer, index=True)
    parentCode = Column(String(20), nullable=False)
    code = Column(String(64), nullable=False, index=True)
    federalCode = Column(String(64), nullable=False, index=True)
    regionalCode = Column(String(64), nullable=False)
    name = Column(String(120), nullable=False, index=True)
    abbrev = Column(String(64), nullable=False)
    sex = Column(Integer, nullable=False)
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    service_id = Column(Integer, index=True)


class Actionpropertytype(Base, Info):
    __tablename__ = u'ActionPropertyType'

    id = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    actionType_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    template_id = Column(Integer, index=True)
    name = Column(String(128), nullable=False)
    descr = Column(String(128), nullable=False)
    unit_id = Column(Integer, index=True)
    typeName = Column(String(64), nullable=False)
    valueDomain = Column(Text, nullable=False)
    defaultValue = Column(String(5000), nullable=False)
    isVector = Column(Integer, nullable=False, server_default=u"'0'")
    norm = Column(String(64), nullable=False)
    sex = Column(Integer, nullable=False)
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    penalty = Column(Integer, nullable=False, server_default=u"'0'")
    visibleInJobTicket = Column(Integer, nullable=False, server_default=u"'0'")
    isAssignable = Column(Integer, nullable=False, server_default=u"'0'")
    test_id = Column(Integer, index=True)
    defaultEvaluation = Column(Integer, nullable=False, server_default=u"'0'")
    toEpicrisis = Column(Integer, nullable=False, server_default=u"'0'")
    code = Column(String(25), index=True)
    mandatory = Column(Integer, nullable=False, server_default=u"'0'")
    readOnly = Column(Integer, nullable=False, server_default=u"'0'")
    createDatetime = Column(DateTime, nullable=False, index=True)
    createPerson_id = Column(Integer)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer)


class ActionpropertyAction(Base):
    __tablename__ = u'ActionProperty_Action'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Integer, index=True)

    def __unicode__(self):
        return self.value


class ActionpropertyDate(Base):
    __tablename__ = u'ActionProperty_Date'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Date)

    def __unicode__(self):
        return self.value


class ActionpropertyDouble(Base):
    __tablename__ = u'ActionProperty_Double'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Float(asdecimal=True), nullable=False)

    def __unicode__(self):
        return self.value


class ActionpropertyFdrecord(Base):
    __tablename__ = u'ActionProperty_FDRecord'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True)
    index = Column(Integer, nullable=False, server_default=u"'0'")
    value = Column(ForeignKey('FDRecord.id'), nullable=False, index=True)

    FDRecord = relationship(u'Fdrecord')


class ActionpropertyHospitalbed(Base):
    __tablename__ = u'ActionProperty_HospitalBed'

    id = Column(ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(ForeignKey('OrgStructure_HospitalBed.id'), index=True)

    ActionProperty = relationship(u'Actionproperty')
    OrgStructure_HospitalBed = relationship(u'OrgstructureHospitalbed')


class ActionpropertyHospitalbedprofile(Base):
    __tablename__ = u'ActionProperty_HospitalBedProfile'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Integer, index=True)


class ActionpropertyImage(Base):
    __tablename__ = u'ActionProperty_Image'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(MEDIUMBLOB)


class ActionpropertyImagemap(Base):
    __tablename__ = u'ActionProperty_ImageMap'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(String)


class ActionpropertyInteger(Base):
    __tablename__ = u'ActionProperty_Integer'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Integer, nullable=False)

    def __unicode__(self):
        return self.value


class ActionpropertyJobTicket(Base):
    __tablename__ = u'ActionProperty_Job_Ticket'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Integer, index=True)


class ActionpropertyMkb(Base):
    __tablename__ = u'ActionProperty_MKB'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Integer, index=True)


class ActionpropertyOrgstructure(Base):
    __tablename__ = u'ActionProperty_OrgStructure'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Integer, index=True)

    def __unicode__(self):
        return self.value


class ActionpropertyOrganisation(Base):
    __tablename__ = u'ActionProperty_Organisation'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Integer, index=True)

    def __unicode__(self):
        return self.value


class ActionpropertyOtherlpurecord(Base):
    __tablename__ = u'ActionProperty_OtherLPURecord'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)


class ActionpropertyPerson(Base):
    __tablename__ = u'ActionProperty_Person'

    id = Column(ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, nullable=False, server_default=u"'0'")
    value = Column(ForeignKey('Person.id'), index=True)

    ActionProperty = relationship(u'Actionproperty')
    Person = relationship(u'Person')

    def __unicode__(self):
        return self.value


class ActionpropertyString(Base):
    __tablename__ = u'ActionProperty_String'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Text, nullable=False)

    def __unicode__(self):
        return self.value


class ActionpropertyTime(Base):
    __tablename__ = u'ActionProperty_Time'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Time, nullable=False)

    def __unicode__(self):
        return self.value


class ActionpropertyRbbloodcomponenttype(Base):
    __tablename__ = u'ActionProperty_rbBloodComponentType'

    id = Column(Integer, primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False)
    value = Column(Integer, nullable=False)


class ActionpropertyRbfinance(Base):
    __tablename__ = u'ActionProperty_rbFinance'

    id = Column(Integer, primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Integer, index=True)


class ActionpropertyRbreasonofabsence(Base):
    __tablename__ = u'ActionProperty_rbReasonOfAbsence'

    id = Column(Integer, primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Integer, index=True)


class Actiontemplate(Base):
    __tablename__ = u'ActionTemplate'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    group_id = Column(Integer, index=True)
    code = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    sex = Column(Integer, nullable=False)
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    owner_id = Column(Integer, index=True)
    speciality_id = Column(Integer, index=True)
    action_id = Column(Integer, index=True)


t_ActionTissue = Table(
    u'ActionTissue', metadata,
    Column(u'action_id', ForeignKey('Action.id'), primary_key=True, nullable=False, index=True),
    Column(u'tissue_id', ForeignKey('Tissue.id'), primary_key=True, nullable=False, index=True)
)


class Actiontype(Base, Info):
    __tablename__ = u'ActionType'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    hidden = Column(Integer, nullable=False, server_default=u"'0'")
    class_ = Column(u'class', Integer, nullable=False, index=True)
    group_id = Column(Integer, index=True)
    code = Column(String(25), nullable=False)
    name = Column(Unicode(255), nullable=False)
    title = Column(Unicode(255), nullable=False)
    flatCode = Column(String(64), nullable=False, index=True)
    sex = Column(Integer, nullable=False)
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    office = Column(String(32), nullable=False)
    showInForm = Column(Integer, nullable=False)
    genTimetable = Column(Integer, nullable=False)
    service_id = Column(Integer, ForeignKey('rbService.id'), index=True)
    quotaType_id = Column(Integer, index=True)
    context = Column(String(64), nullable=False)
    amount = Column(Float(asdecimal=True), nullable=False, server_default=u"'1'")
    amountEvaluation = Column(Integer, nullable=False, server_default=u"'0'")
    defaultStatus = Column(Integer, nullable=False, server_default=u"'0'")
    defaultDirectionDate = Column(Integer, nullable=False, server_default=u"'0'")
    defaultPlannedEndDate = Column(Integer, nullable=False)
    defaultEndDate = Column(Integer, nullable=False, server_default=u"'0'")
    defaultExecPerson_id = Column(Integer, index=True)
    defaultPersonInEvent = Column(Integer, nullable=False, server_default=u"'0'")
    defaultPersonInEditor = Column(Integer, nullable=False, server_default=u"'0'")
    maxOccursInEvent = Column(Integer, nullable=False, server_default=u"'0'")
    showTime = Column(Integer, nullable=False, server_default=u"'0'")
    isMES = Column(Integer)
    nomenclativeService_id = Column(Integer, ForeignKey('rbService.id'), index=True)
    isPreferable = Column(Integer, nullable=False, server_default=u"'1'")
    prescribedType_id = Column(Integer, index=True)
    shedule_id = Column(Integer, index=True)
    isRequiredCoordination = Column(Integer, nullable=False, server_default=u"'0'")
    isRequiredTissue = Column(Integer, nullable=False, server_default=u"'0'")
    testTubeType_id = Column(Integer, index=True)
    jobType_id = Column(Integer, index=True)
    mnem = Column(String(32), server_default=u"''")

    service = relationship(u'Rbservice', foreign_keys='Actiontype.service_id')
    nomenclatureService = relationship(u'Rbservice', foreign_keys='Actiontype.nomenclativeService_id')


class ActiontypeEventtypeCheck(Base):
    __tablename__ = u'ActionType_EventType_check'

    id = Column(Integer, primary_key=True)
    actionType_id = Column(ForeignKey('ActionType.id'), nullable=False, index=True)
    eventType_id = Column(ForeignKey('EventType.id'), nullable=False, index=True)
    related_actionType_id = Column(ForeignKey('ActionType.id'), index=True)
    relationType = Column(Integer)

    actionType = relationship(u'Actiontype', primaryjoin='ActiontypeEventtypeCheck.actionType_id == Actiontype.id')
    eventType = relationship(u'Eventtype')
    related_actionType = relationship(u'Actiontype', primaryjoin='ActiontypeEventtypeCheck.related_actionType_id == Actiontype.id')


class ActiontypeQuotatype(Base):
    __tablename__ = u'ActionType_QuotaType'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    quotaClass = Column(Integer)
    finance_id = Column(Integer, index=True)
    quotaType_id = Column(Integer, index=True)


class ActiontypeService(Base):
    __tablename__ = u'ActionType_Service'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    finance_id = Column(Integer, index=True)
    service_id = Column(Integer, index=True)


class ActiontypeTissuetype(Base):
    __tablename__ = u'ActionType_TissueType'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('ActionType.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    tissueType_id = Column(ForeignKey('rbTissueType.id'), index=True)
    amount = Column(Integer, nullable=False, server_default=u"'0'")
    unit_id = Column(ForeignKey('rbUnit.id'), index=True)

    master = relationship(u'Actiontype')
    tissueType = relationship(u'Rbtissuetype')
    unit = relationship(u'Rbunit')


class ActiontypeUser(Base):
    __tablename__ = u'ActionType_User'
    __table_args__ = (
        Index(u'person_id_profile_id', u'person_id', u'profile_id'),
    )

    id = Column(Integer, primary_key=True)
    actionType_id = Column(ForeignKey('ActionType.id'), nullable=False, index=True)
    person_id = Column(ForeignKey('Person.id'))
    profile_id = Column(ForeignKey('rbUserProfile.id'), index=True)

    actionType = relationship(u'Actiontype')
    person = relationship(u'Person')
    profile = relationship(u'Rbuserprofile')


class Addres(Base):
    __tablename__ = u'Address'
    __table_args__ = (
        Index(u'house_id', u'house_id', u'flat'),
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    house_id = Column(Integer, nullable=False)
    flat = Column(String(6), nullable=False)


class Addressareaitem(Base):
    __tablename__ = u'AddressAreaItem'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    LPU_id = Column(Integer, nullable=False, index=True)
    struct_id = Column(Integer, nullable=False, index=True)
    house_id = Column(Integer, nullable=False, index=True)
    flatRange = Column(Integer, nullable=False)
    begFlat = Column(Integer, nullable=False)
    endFlat = Column(Integer, nullable=False)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date)


class Addresshouse(Base):
    __tablename__ = u'AddressHouse'
    __table_args__ = (
        Index(u'KLADRCode', u'KLADRCode', u'KLADRStreetCode', u'number', u'corpus'),
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    KLADRCode = Column(String(13), nullable=False)
    KLADRStreetCode = Column(String(17), nullable=False)
    number = Column(String(8), nullable=False)
    corpus = Column(String(8), nullable=False)


class Applock(Base):
    __tablename__ = u'AppLock'

    id = Column(BigInteger, primary_key=True)
    lockTime = Column(DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    retTime = Column(DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    connectionId = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    person_id = Column(Integer)
    addr = Column(String(255), nullable=False)


t_AppLock_Detail = Table(
    u'AppLock_Detail', metadata,
    Column(u'master_id', BigInteger, nullable=False, index=True),
    Column(u'tableName', String(64), nullable=False),
    Column(u'recordId', Integer, nullable=False),
    Column(u'recordIndex', Integer, nullable=False, server_default=u"'0'"),
    Index(u'rec', u'recordId', u'tableName')
)


t_AssignmentHour = Table(
    u'AssignmentHour', metadata,
    Column(u'action_id', Integer, nullable=False),
    Column(u'createDatetime', DateTime, nullable=False),
    Column(u'hour', Integer),
    Column(u'complete', Integer, server_default=u"'0'"),
    Column(u'comments', String(120))
)


class Bank(Base, Info):
    __tablename__ = u'Bank'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    BIK = Column(String(10), nullable=False, index=True)
    name = Column(Unicode(100), nullable=False, index=True)
    branchName = Column(Unicode(100), nullable=False)
    corrAccount = Column(String(20), nullable=False)
    subAccount = Column(String(20), nullable=False)


class Blankaction(Base):
    __tablename__ = u'BlankActions'

    id = Column(Integer, primary_key=True)
    doctype_id = Column(ForeignKey('ActionType.id'), index=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    checkingSerial = Column(Integer, nullable=False)
    checkingNumber = Column(Integer, nullable=False)
    checkingAmount = Column(Integer, nullable=False)

    doctype = relationship(u'Actiontype')


class BlankactionsMoving(Base):
    __tablename__ = u'BlankActions_Moving'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    date = Column(Date, nullable=False)
    blankParty_id = Column(ForeignKey('BlankActions_Party.id'), nullable=False, index=True)
    serial = Column(String(8), nullable=False)
    orgStructure_id = Column(ForeignKey('OrgStructure.id'), index=True)
    person_id = Column(ForeignKey('Person.id'), index=True)
    received = Column(Integer, nullable=False, server_default=u"'0'")
    used = Column(Integer, nullable=False, server_default=u"'0'")
    returnDate = Column(Date)
    returnAmount = Column(Integer, nullable=False, server_default=u"'0'")

    blankParty = relationship(u'BlankactionsParty')
    createPerson = relationship(u'Person', primaryjoin='BlankactionsMoving.createPerson_id == Person.id')
    modifyPerson = relationship(u'Person', primaryjoin='BlankactionsMoving.modifyPerson_id == Person.id')
    orgStructure = relationship(u'Orgstructure')
    person = relationship(u'Person', primaryjoin='BlankactionsMoving.person_id == Person.id')


class BlankactionsParty(Base):
    __tablename__ = u'BlankActions_Party'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    date = Column(Date, nullable=False)
    doctype_id = Column(ForeignKey('rbBlankActions.id'), nullable=False, index=True)
    person_id = Column(ForeignKey('Person.id'), index=True)
    serial = Column(String(8), nullable=False)
    numberFrom = Column(String(16), nullable=False)
    numberTo = Column(String(16), nullable=False)
    amount = Column(Integer, nullable=False, server_default=u"'0'")
    extradited = Column(Integer, nullable=False, server_default=u"'0'")
    balance = Column(Integer, nullable=False, server_default=u"'0'")
    used = Column(Integer, nullable=False, server_default=u"'0'")
    writing = Column(Integer, nullable=False, server_default=u"'0'")

    createPerson = relationship(u'Person', primaryjoin='BlankactionsParty.createPerson_id == Person.id')
    doctype = relationship(u'Rbblankaction')
    modifyPerson = relationship(u'Person', primaryjoin='BlankactionsParty.modifyPerson_id == Person.id')
    person = relationship(u'Person', primaryjoin='BlankactionsParty.person_id == Person.id')


class BlanktempinvalidMoving(Base):
    __tablename__ = u'BlankTempInvalid_Moving'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    date = Column(Date, nullable=False)
    blankParty_id = Column(ForeignKey('BlankTempInvalid_Party.id'), nullable=False, index=True)
    serial = Column(String(8), nullable=False)
    orgStructure_id = Column(ForeignKey('OrgStructure.id'), index=True)
    person_id = Column(ForeignKey('Person.id'), index=True)
    received = Column(Integer, nullable=False, server_default=u"'0'")
    used = Column(Integer, nullable=False, server_default=u"'0'")
    returnDate = Column(Date)
    returnAmount = Column(Integer, nullable=False, server_default=u"'0'")

    blankParty = relationship(u'BlanktempinvalidParty')
    createPerson = relationship(u'Person', primaryjoin='BlanktempinvalidMoving.createPerson_id == Person.id')
    modifyPerson = relationship(u'Person', primaryjoin='BlanktempinvalidMoving.modifyPerson_id == Person.id')
    orgStructure = relationship(u'Orgstructure')
    person = relationship(u'Person', primaryjoin='BlanktempinvalidMoving.person_id == Person.id')


class BlanktempinvalidParty(Base):
    __tablename__ = u'BlankTempInvalid_Party'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    date = Column(Date, nullable=False)
    doctype_id = Column(ForeignKey('rbBlankTempInvalids.id'), nullable=False, index=True)
    person_id = Column(ForeignKey('Person.id'), index=True)
    serial = Column(String(8), nullable=False)
    numberFrom = Column(String(16), nullable=False)
    numberTo = Column(String(16), nullable=False)
    amount = Column(Integer, nullable=False, server_default=u"'0'")
    extradited = Column(Integer, nullable=False, server_default=u"'0'")
    balance = Column(Integer, nullable=False, server_default=u"'0'")
    used = Column(Integer, nullable=False, server_default=u"'0'")
    writing = Column(Integer, nullable=False, server_default=u"'0'")

    createPerson = relationship(u'Person', primaryjoin='BlanktempinvalidParty.createPerson_id == Person.id')
    doctype = relationship(u'Rbblanktempinvalid')
    modifyPerson = relationship(u'Person', primaryjoin='BlanktempinvalidParty.modifyPerson_id == Person.id')
    person = relationship(u'Person', primaryjoin='BlanktempinvalidParty.person_id == Person.id')


class Blanktempinvalid(Base):
    __tablename__ = u'BlankTempInvalids'

    id = Column(Integer, primary_key=True)
    doctype_id = Column(ForeignKey('rbTempInvalidDocument.id'), index=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    checkingSerial = Column(Integer, nullable=False)
    checkingNumber = Column(Integer, nullable=False)
    checkingAmount = Column(Integer, nullable=False)

    doctype = relationship(u'Rbtempinvaliddocument')


class Bloodhistory(Base):
    __tablename__ = u'BloodHistory'

    id = Column(Integer, primary_key=True)
    bloodDate = Column(Date, nullable=False)
    client_id = Column(Integer, nullable=False)
    bloodType_id = Column(Integer, nullable=False)
    person_id = Column(Integer, nullable=False)


class Calendarexception(Base):
    __tablename__ = u'CalendarExceptions'
    __table_args__ = (
        Index(u'CHANGEDAY', u'date', u'fromDate'),
        Index(u'HOLIDAY', u'date', u'startYear')
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    date = Column(Date, nullable=False)
    isHoliday = Column(Integer, nullable=False)
    startYear = Column(SmallInteger)
    finishYear = Column(SmallInteger)
    fromDate = Column(Date)
    text = Column(String(250), nullable=False)


class Client(Base, Info):
    __tablename__ = u'Client'
    __table_args__ = (
        Index(u'lastName', u'lastName', u'firstName', u'patrName', u'birthDate', u'id'),
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    lastName = Column(Unicode(30), nullable=False)
    firstName = Column(Unicode(30), nullable=False)
    patrName = Column(Unicode(30), nullable=False)
    birthDate = Column(Date, nullable=False, index=True)
    sexCode = Column("sex", Integer, nullable=False)
    SNILS = Column(String(11), nullable=False, index=True)
    bloodType_id = Column(ForeignKey('rbBloodType.id'), index=True)
    bloodDate = Column(Date)
    bloodNotes = Column(String, nullable=False)
    growth = Column(String(16), nullable=False)
    weight = Column(String(16), nullable=False)
    notes = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    birthPlace = Column(String(128), nullable=False, server_default=u"''")
    embryonalPeriodWeek = Column(String(16), nullable=False, server_default=u"''")
    uuid_id = Column(Integer, nullable=False, index=True, server_default=u"'0'")

    bloodType = relationship(u'Rbbloodtype')
    client_attachments = relationship(u'Clientattach')
    socStatusesAll = relationship(u'Clientsocstatus')
    documentsAll = relationship(u'Clientdocument')
    intolerancesAll = relationship(u'Clientintolerancemedicament')
    allergiesAll = relationship(u'Clientallergy')
    contacts = relationship(u'Clientcontact')
    direct_relations = relationship(u'DirectClientRelation', foreign_keys='Clientrelation.client_id')
    reversed_relations = relationship(u'ReversedClientRelation', foreign_keys='Clientrelation.relative_id')
    policies = relationship(u'Clientpolicy')
    works = relationship(u'Clientwork')

    # TODO: date

    @property
    def nameText(self):
        return u' '.join((u'%s %s %s' % (self.lastName, self.firstName, self.patrName)).split())

    @property
    def sex(self):
        """
        Делаем из пола строку
        sexCode - код пола (1 мужской, 2 женский)
        """
        if self.sexCode == 1:
            return u'М'
        elif self.sexCode == 2:
            return u'Ж'
        else:
            return u''

    @property
    def SNILS(self):
        if self.SNILS:
            s = self.SNILS+' '*14
            return s[0:3]+'-'+s[3:6]+'-'+s[6:9]+' '+s[9:11]
        else:
            return u''

    @property
    def permanentAttach(self):
        for attach in self.client_attachments:
            if attach.deleted == 0 and attach.attachType.temporary == 0:
                return attach

    @property
    def temporaryAttach(self):
        for attach in self.client_attachments:
            if attach.deleted == 0 and attach.attachType.temporary != 0:
                return attach

    @property
    def socStatuses(self):
        # TODO: db.joinOr([table['endDate'].isNull(), table['endDate'].ge(QDate.currentDate())])
        return [socStatus for socStatus in self.socStatusesAll if socStatus.deleted == 0]

    @property
    def document(self):
        # TODO: отстортировать по дате
        for document in self.documents:
            if document.deleted == 0 and document.documentType.group.code == '1':
                return document

    @property
    def intolerances(self):
        return [intolerance for intolerance in self.intolerancesAll if intolerance.deleted == 0]

    @property
    def allergies(self):
        return [allergie for allergie in self.allergiesAll if allergie.deleted == 0]

    @property
    def relations(self):
        return self.reversed_relations + self.direct_relations

    @property
    def phones(self):
        contacts = [(contact.name, contact.contact, contact.notes) for contact in self.contacts if contact.deleted == 0]
        return ', '.join([(phone[0]+': '+phone[1]+' ('+phone[2]+')') if phone[2] else (phone[0]+': '+phone[1])
                          for phone in contacts])

    @property
    def compulsoryPolicy(self):
        # TODO: order by date code?
        for policy in self.policies:
            if not policy.policyType or u"ОМС" in policy.policyType.name:
                return policy

    @property
    def voluntaryPolicy(self):
        # TODO: order by date code?
        for policy in self.policies:
            if policy.policyType and policy.policyType.name.startswith(u"ДМС"):
                return policy
    @property
    def policy(self):
        return self.compulsoryPolicy

    @property
    def policyDMS(self):
        return self.voluntaryPolicy

    @property
    def fullName(self):
        return formatNameInt(self.lastName, self.firstName, self.patrName)

    @property
    def shortName(self):
        return formatShortNameInt(self.lastName, self.firstName, self.patrName)

    @property
    def work(self):
        # TODO: order by date
        for work in self.works:
            if work.deleted == 0:
                return work

    def __unicode__(self):
        return self.formatShortNameInt(self.lastName, self.firstName, self.patrName)


class Patientstohs(Base):
    __tablename__ = u'PatientsToHS'

    client_id = Column(ForeignKey('Client.id'), primary_key=True)
    sendTime = Column(DateTime, nullable=False, server_default=u'CURRENT_TIMESTAMP')
    errCount = Column(Integer, nullable=False, server_default=u"'0'")
    info = Column(String(1024))


class Clientaddres(Base):
    __tablename__ = u'ClientAddress'
    __table_args__ = (
        Index(u'address_id', u'address_id', u'type'),
        Index(u'client_id', u'client_id', u'type', u'address_id')
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False)
    type = Column(Integer, nullable=False)
    address_id = Column(Integer)
    freeInput = Column(String(200), nullable=False)
    version = Column(Integer, nullable=False)
    localityType = Column(Integer, nullable=False)

    client = relationship(u'Client')


class Clientallergy(Base, Info):
    __tablename__ = u'ClientAllergy'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    power = Column(Integer, nullable=False)
    createDate = Column(Date)
    notes = Column(String, nullable=False)
    version = Column(Integer, nullable=False)

    client = relationship(u'Client')

    def __unicode__(self):
        return self.name


class Clientattach(Base, Info):
    __tablename__ = u'ClientAttach'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    attachType_id = Column(ForeignKey('rbAttachType.id'), nullable=False, index=True)
    LPU_id = Column(ForeignKey('Organisation.id'), nullable=False, index=True)
    orgStructure_id = Column(ForeignKey('OrgStructure.id'), index=True)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date)
    document_id = Column(ForeignKey('ClientDocument.id'), index=True)

    client = relationship(u'Client')
    document = relationship(u'Clientdocument')
    org = relationship(u'Organisation')
    orgStructure = relationship(u'Orgstructure')
    attachType = relationship(u'Rbattachtype')

    def __unicode__(self):
        if self._ok:
            result = self.name
            if self._outcome:
                result += ' ' + unicode(self.endDate)
            elif self.temporary:  # ??
                result += ' ' + self.org.shortName
                if self.begDate:
                    result += u' c ' + unicode(self.begDate)
                if self.endDate:
                    result += u' по ' + unicode(self.endDate)
            else:
                result += ' ' + self.org.shortName
        else:
            result = ''
        return result

    def getCode(self):
        return self.attachType.code

    def getName(self):
        return self.attachType.name

    def getOutcome(self):
        return self.attachType.outcome

    code = property(getCode)
    name = property(getName)
    outcome = property(getOutcome)


class Clientcontact(Base, Info):
    __tablename__ = u'ClientContact'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    contactType_id = Column(Integer, ForeignKey('rbContactType.id'), nullable=False, index=True)
    contact = Column(String(32), nullable=False)
    notes = Column(Unicode(64), nullable=False)
    version = Column(Integer, nullable=False)

    client = relationship(u'Client')
    contactType = relationship(u'Rbcontacttype')

    @property
    def name(self):
        return self.contactType.names


class Clientdocument(Base):
    __tablename__ = u'ClientDocument'
    __table_args__ = (
        Index(u'Ser_Numb', u'serial', u'number'),
    )

    documentId = Column("id", Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    clientId = Column("client_id", ForeignKey('Client.id'), nullable=False, index=True)
    documentType_id = Column(Integer, ForeignKey('rbDocumentType.id'), nullable=False, index=True)
    serial = Column(String(8), nullable=False)
    number = Column(String(16), nullable=False)
    date = Column(Date, nullable=False)
    origin = Column(String(256), nullable=False)
    version = Column(Integer, nullable=False)
    endDate = Column(Date)

    client = relationship(u'Client')
    documentType = relationship(u'Rbdocumenttype')

    @property
    def documentTypeCode(self):
        return self.documentType.regionalCode

    def __unicode__(self):
        return (' '.join([self.documentType, self.serial, self.number])).strip()


class Clientfdproperty(Base):
    __tablename__ = u'ClientFDProperty'

    id = Column(Integer, primary_key=True)
    flatDirectory_id = Column(ForeignKey('FlatDirectory.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    version = Column(Integer, nullable=False)

    flatDirectory = relationship(u'Flatdirectory')


class Clientflatdirectory(Base):
    __tablename__ = u'ClientFlatDirectory'

    id = Column(Integer, primary_key=True)
    clientFDProperty_id = Column(ForeignKey('ClientFDProperty.id'), nullable=False, index=True)
    fdRecord_id = Column(ForeignKey('FDRecord.id'), nullable=False, index=True)
    dateStart = Column(DateTime)
    dateEnd = Column(DateTime)
    createDateTime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, nullable=False)
    modifyDateTime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer)
    deleted = Column(Integer, nullable=False)
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    comment = Column(String)
    version = Column(Integer, nullable=False)

    clientFDProperty = relationship(u'Clientfdproperty')
    client = relationship(u'Client')
    fdRecord = relationship(u'Fdrecord')


class Clientidentification(Base, Info):
    __tablename__ = u'ClientIdentification'
    __table_args__ = (
        Index(u'accountingSystem_id', u'accountingSystem_id', u'identifier'),
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    accountingSystem_id = Column(Integer, ForeignKey('rbAccountingSystem.id'), nullable=False)
    identifier = Column(String(16), nullable=False)
    checkDate = Column(Date)
    version = Column(Integer, nullable=False)

    client = relationship(u'Client')
    accountingSystem = relationship(u'Rbaccountingsystem')

    def getAccountingSystemCode(self):
        return self.attachType.code

    def getAccountingSystemName(self):
        return self.attachType.name

    code = property(getAccountingSystemCode)
    name = property(getAccountingSystemName)
    # byCode = {code: identifier}
    # nameDict = {code: name}


class Clientintolerancemedicament(Base, Info):
    __tablename__ = u'ClientIntoleranceMedicament'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    power = Column(Integer, nullable=False)
    createDate = Column(Date)
    notes = Column(String, nullable=False)
    version = Column(Integer, nullable=False)

    client = relationship(u'Client')

    def __unicode__(self):
        return self.name


class Clientpolicy(Base, Info):
    __tablename__ = u'ClientPolicy'
    __table_args__ = (
        Index(u'Serial_Num', u'serial', u'number'),
        Index(u'client_insurer', u'client_id', u'insurer_id')
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    clientId = Column("client_id", ForeignKey('Client.id'), nullable=False)
    insurer_id = Column(Integer, ForeignKey('Organisation.id'), index=True)
    policyType_id = Column(Integer, ForeignKey('rbPolicyType.id'), index=True)
    serial = Column(String(16), nullable=False)
    number = Column(String(16), nullable=False)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date)
    name = Column(Unicode(64), nullable=False, server_default=u"''")
    note = Column(String(200), nullable=False, server_default=u"''")
    version = Column(Integer, nullable=False)

    client = relationship(u'Client')
    insurer = relationship(u'Organisation')
    policyType = relationship(u'Rbpolicytype')

    def __unicode__(self):
        return (' '.join([self.policyType, unicode(self.insurer), self.serial, self.number])).strip()


class Clientrelation(Base, Info):
    __tablename__ = u'ClientRelation'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    relativeType_id = Column(Integer, ForeignKey('rbRelationType.id'), index=True)
    relative_id = Column(Integer, ForeignKey('Client.id'), nullable=False, index=True)
    version = Column(Integer, nullable=False)

    relativeType = relationship(u'Rbrelationtype')

    @property
    def leftName(self):
        return self.relativeType.leftName

    @property
    def rightName(self):
        return self.relativeType.rightName

    @property
    def code(self):
        return self.relativeType.code

    @property
    def name(self):
        return self.role + ' -> ' + self.otherRole


class DirectClientRelation(Clientrelation):

    other = relationship(u'Client', foreign_keys='Clientrelation.relative_id')

    @property
    def role(self):
        return self.rightName

    @property
    def otherRole(self):
        return self.leftName

    @property
    def regionalCode(self):
        return self.relativeType.regionalCode

    @property
    def clientId(self):
        return self.relative_id

    @property
    def isDirectGenetic(self):
        return self.relativeType.isDirectGenetic

    @property
    def isBackwardGenetic(self):
        return self.relativeType.isBackwardGenetic

    @property
    def isDirectRepresentative(self):
        return self.relativeType.isDirectRepresentative

    @property
    def isBackwardRepresentative(self):
        return self.relativeType.isBackwardRepresentative

    @property
    def isDirectEpidemic(self):
        return self.relativeType.isDirectEpidemic

    @property
    def isBackwardEpidemic(self):
        return self.relativeType.isBackwardEpidemic

    @property
    def isDirectDonation(self):
        return self.relativeType.isDirectDonation

    @property
    def isBackwardDonation(self):
        return self.relativeType.isBackwardDonation

    def __unicode__(self):
        return self.name + ' ' + self.other


class ReversedClientRelation(Clientrelation):

    other = relationship(u'Client', foreign_keys='Clientrelation.client_id')

    @property
    def role(self):
        return self.leftName

    @property
    def otherRole(self):
        return self.rightName

    @property
    def regionalCode(self):
        return self.relativeType.regionalReverseCode

    @property
    def clientId(self):
        return self.client_id
    @property
    def isDirectGenetic(self):
        return self.relativeType.isBackwardGenetic

    @property
    def isBackwardGenetic(self):
        return self.relativeType.isDirectGenetic

    @property
    def isDirectRepresentative(self):
        return self.relativeType.isBackwardRepresentative

    @property
    def isBackwardRepresentative(self):
        return self.relativeType.isDirectRepresentative

    @property
    def isDirectEpidemic(self):
        return self.relativeType.isBackwardEpidemic

    @property
    def isBackwardEpidemic(self):
        return self.relativeType.isDirectEpidemic

    @property
    def isDirectDonation(self):
        return self.relativeType.isBackwardDonation

    @property
    def isBackwardDonation(self):
        return self.relativeType.isDirectDonation

    def __unicode__(self):
        return self.name + ' ' + self.other


class Clientsocstatus(Base, Info):
    __tablename__ = u'ClientSocStatus'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    socStatusClass_id = Column(ForeignKey('rbSocStatusClass.id'), index=True)
    socStatusType_id = Column(ForeignKey('rbSocStatusType.id'), nullable=False, index=True)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date)
    document_id = Column(ForeignKey('ClientDocument.id'), index=True)
    version = Column(Integer, nullable=False)
    note = Column(String(256), nullable=False, server_default=u"''")
    benefitCategory_id = Column(Integer)

    client = relationship(u'Client')
    socStatusType = relationship(u'Rbsocstatustype')
    document = relationship(u'Clientdocument')

    def socStatusClasses(self):
        return self.socStatusType.classes

    def getSocStatusTypeCode(self):
        return self.socStatusType.code

    def getSocStatusTypeName(self):
        return self.socStatusType.name

    code = property(getSocStatusTypeCode)
    name = property(getSocStatusTypeName)
    classes = property(socStatusClasses)

    def __unicode__(self):
        return self.name


class Clientwork(Base):
    __tablename__ = u'ClientWork'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    org_id = Column(ForeignKey('Organisation.id'), index=True)
    shortName = Column('freeInput', String(200), nullable=False)
    post = Column(String(200), nullable=False)
    stage = Column(Integer, nullable=False)
    OKVED = Column(String(10), nullable=False)
    version = Column(Integer, nullable=False)
    rank_id = Column(Integer, nullable=False)
    arm_id = Column(Integer, nullable=False)

    client = relationship(u'Client')
    organisation = relationship(u'Organisation')
    hurts = relationship(u'ClientworkHurt')

    def __unicode__(self):
        parts = []
        if self.shortName:
            parts.append(self.shortName)
        if self.post:
            parts.append(self.post)
        if self.OKVED:
            parts.append(u'ОКВЭД: '+self._OKVED)
        return ', '.join(parts)

    #TODO: насл от OrgInfo


class ClientworkHurt(Base, Info):
    __tablename__ = u'ClientWork_Hurt'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('ClientWork.id'), nullable=False, index=True)
    hurtType_id = Column(ForeignKey('rbHurtType.id'), nullable=False, index=True)
    stage = Column(Integer, nullable=False)

    clientWork = relationship(u'Clientwork')
    hurtType = relationship(u'Rbhurttype')
    factors = relationship(u'ClientworkHurtFactor')

    def hurtTypeCode(self):
        return self.hurtType.code

    def hurtTypeName(self):
        return self.hurtType.name

    code = property(hurtTypeCode)
    name = property(hurtTypeName)


class ClientworkHurtFactor(Base, Info):
    __tablename__ = u'ClientWork_Hurt_Factor'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('ClientWork_Hurt.id'), nullable=False, index=True)
    factorType_id = Column(ForeignKey('rbHurtFactorType.id'), nullable=False, index=True)

    master = relationship(u'ClientworkHurt')
    factorType = relationship(u'Rbhurtfactortype')

    def factorTypeCode(self):
        return self.factorType.code

    def factorTypeName(self):
        return self.factorType.name

    code = property(factorTypeCode)
    name = property(factorTypeName)


class ClientQuoting(Base):
    __tablename__ = u'Client_Quoting'
    __table_args__ = (
        Index(u'deleted_prevTalon_event_id', u'deleted', u'prevTalon_event_id'),
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(ForeignKey('Client.id'), index=True)
    identifier = Column(String(16))
    quotaTicket = Column(String(20))
    quotaType_id = Column(Integer)
    stage = Column(Integer)
    directionDate = Column(DateTime, nullable=False)
    freeInput = Column(String(128))
    org_id = Column(Integer)
    amount = Column(Integer, nullable=False, server_default=u"'0'")
    MKB = Column(String(8), nullable=False)
    status = Column(Integer, nullable=False, server_default=u"'0'")
    request = Column(Integer, nullable=False, server_default=u"'0'")
    statment = Column(String(255))
    dateRegistration = Column(DateTime, nullable=False)
    dateEnd = Column(DateTime, nullable=False)
    orgStructure_id = Column(Integer)
    regionCode = Column(String(13), index=True)
    pacientModel_id = Column(Integer, nullable=False)
    treatment_id = Column(Integer, nullable=False)
    event_id = Column(Integer, index=True)
    prevTalon_event_id = Column(Integer)
    version = Column(Integer, nullable=False)

    master = relationship(u'Client')


class ClientQuotingdiscussion(Base):
    __tablename__ = u'Client_QuotingDiscussion'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('Client.id'), index=True)
    dateMessage = Column(DateTime, nullable=False)
    agreementType_id = Column(Integer)
    responsiblePerson_id = Column(Integer)
    cosignatory = Column(String(25))
    cosignatoryPost = Column(String(20))
    cosignatoryName = Column(String(50))
    remark = Column(String(128))

    master = relationship(u'Client')


class Contract(Base, Info):
    __tablename__ = u'Contract'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    number = Column(String(64), nullable=False)
    date = Column(Date, nullable=False)
    recipient_id = Column(Integer, ForeignKey('Organisation.id'), nullable=False, index=True)
    recipientAccount_id = Column(Integer, ForeignKey('Organisation_Account.id'), index=True)
    recipientKBK = Column(String(30), nullable=False)
    payer_id = Column(Integer, ForeignKey('Organisation.id'), index=True)
    payerAccount_id = Column(Integer, ForeignKey('Organisation_Account.id'), index=True)
    payerKBK = Column(String(30), nullable=False)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    finance_id = Column(Integer, ForeignKey('rbFinance.id'), nullable=False, index=True)
    grouping = Column(String(64), nullable=False)
    resolution = Column(String(64), nullable=False)
    format_id = Column(Integer, index=True)
    exposeUnfinishedEventVisits = Column(Integer, nullable=False, server_default=u"'0'")
    exposeUnfinishedEventActions = Column(Integer, nullable=False, server_default=u"'0'")
    visitExposition = Column(Integer, nullable=False, server_default=u"'0'")
    actionExposition = Column(Integer, nullable=False, server_default=u"'0'")
    exposeDiscipline = Column(Integer, nullable=False, server_default=u"'0'")
    priceList_id = Column(Integer)
    coefficient = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    coefficientEx = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")

    recipient = relationship(u'Organisation', foreign_keys='Contract.recipient_id')
    payer = relationship(u'Organisation', foreign_keys='Contract.payer_id')
    finance = relationship(u'Rbfinance')
    recipientAccount = relationship(u'OrganisationAccount', foreign_keys='Contract.recipientAccount_id')
    payerAccount = relationship(u'OrganisationAccount', foreign_keys='Contract.payerAccount_id')

    def __unicode__(self):
        return self.number + ' ' + self.date


class ContractContingent(Base):
    __tablename__ = u'Contract_Contingent'

    id = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(Integer, nullable=False, index=True)
    client_id = Column(Integer, index=True)
    attachType_id = Column(Integer, index=True)
    org_id = Column(Integer, index=True)
    socStatusType_id = Column(Integer, index=True)
    insurer_id = Column(Integer, index=True)
    policyType_id = Column(Integer, index=True)
    sex = Column(Integer, nullable=False)
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)


class ContractContragent(Base):
    __tablename__ = u'Contract_Contragent'

    id = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(Integer, nullable=False, index=True)
    insurer_id = Column(Integer, nullable=False, index=True)
    payer_id = Column(Integer, nullable=False, index=True)
    payerAccount_id = Column(Integer, nullable=False, index=True)
    payerKBK = Column(String(30), nullable=False)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)


class ContractSpecification(Base):
    __tablename__ = u'Contract_Specification'

    id = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(Integer, nullable=False, index=True)
    eventType_id = Column(Integer, nullable=False, index=True)


class ContractTariff(Base):
    __tablename__ = u'Contract_Tariff'

    id = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(Integer, nullable=False, index=True)
    eventType_id = Column(Integer, index=True)
    tariffType = Column(Integer, nullable=False)
    service_id = Column(Integer, index=True)
    tariffCategory_id = Column(Integer, index=True)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    sex = Column(Integer, nullable=False)
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    unit_id = Column(Integer, index=True)
    amount = Column(Float(asdecimal=True), nullable=False)
    uet = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    price = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    limitationExceedMode = Column(Integer, nullable=False, server_default=u"'0'")
    limitation = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    priceEx = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    MKB = Column(String(8), nullable=False)
    rbServiceFinance_id = Column(ForeignKey('rbServiceFinance.id'), index=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer)

    rbServiceFinance = relationship(u'Rbservicefinance')


class Couponstransferquote(Base):
    __tablename__ = u'CouponsTransferQuotes'

    id = Column(Integer, primary_key=True)
    srcQuotingType_id = Column(ForeignKey('rbTimeQuotingType.code'), nullable=False, index=True)
    dstQuotingType_id = Column(ForeignKey('rbTimeQuotingType.code'), nullable=False, index=True)
    transferDayType = Column(ForeignKey('rbTransferDateType.code'), nullable=False, index=True)
    transferTime = Column(Time, nullable=False)
    couponsEnabled = Column(Integer, server_default=u"'0'")

    dstQuotingType = relationship(u'Rbtimequotingtype', primaryjoin='Couponstransferquote.dstQuotingType_id == Rbtimequotingtype.code')
    srcQuotingType = relationship(u'Rbtimequotingtype', primaryjoin='Couponstransferquote.srcQuotingType_id == Rbtimequotingtype.code')
    rbTransferDateType = relationship(u'Rbtransferdatetype')


class Diagnosi(Base):
    __tablename__ = u'Diagnosis'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(Integer, nullable=False, index=True)
    diagnosisType_id = Column(Integer, nullable=False, index=True)
    character_id = Column(Integer, index=True)
    MKB = Column(String(8), nullable=False)
    MKBEx = Column(String(8), nullable=False)
    dispanser_id = Column(Integer, index=True)
    traumaType_id = Column(Integer, index=True)
    setDate = Column(Date)
    endDate = Column(Date, nullable=False)
    mod_id = Column(Integer, index=True)
    person_id = Column(Integer, index=True)
    diagnosisName = Column(String(64), nullable=False)


class Diagnostic(Base):
    __tablename__ = u'Diagnostic'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    event_id = Column(Integer, nullable=False, index=True)
    diagnosis_id = Column(Integer, index=True)
    diagnosisType_id = Column(Integer, nullable=False, index=True)
    character_id = Column(Integer, index=True)
    stage_id = Column(Integer, index=True)
    phase_id = Column(Integer, index=True)
    dispanser_id = Column(Integer, index=True)
    sanatorium = Column(Integer, nullable=False)
    hospital = Column(Integer, nullable=False)
    traumaType_id = Column(Integer, index=True)
    speciality_id = Column(Integer, nullable=False, index=True)
    person_id = Column(Integer, index=True)
    healthGroup_id = Column(Integer, index=True)
    result_id = Column(Integer, index=True)
    setDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime)
    notes = Column(Text, nullable=False)
    rbAcheResult_id = Column(ForeignKey('rbAcheResult.id'), index=True)
    version = Column(Integer, nullable=False)
    action_id = Column(Integer, index=True)

    rbAcheResult = relationship(u'Rbacheresult')


class Drugchart(Base):
    __tablename__ = u'DrugChart'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    master_id = Column(ForeignKey('DrugChart.id'), index=True)
    begDateTime = Column(DateTime, nullable=False)
    endDateTime = Column(DateTime)
    status = Column(Integer, nullable=False)
    statusDateTime = Column(Integer)
    note = Column(String(256), server_default=u"''")
    uuid = Column(String(100))
    version = Column(Integer)

    action = relationship(u'Action')
    master = relationship(u'Drugchart', remote_side=[id])


class Drugcomponent(Base):
    __tablename__ = u'DrugComponent'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    nomen = Column(Integer, index=True)
    name = Column(String(255))
    dose = Column(Float)
    unit = Column(Integer)
    createDateTime = Column(DateTime, nullable=False)
    cancelDateTime = Column(DateTime)

    action = relationship(u'Action')


class Emergencybrigade(Base):
    __tablename__ = u'EmergencyBrigade'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class EmergencybrigadePersonnel(Base):
    __tablename__ = u'EmergencyBrigade_Personnel'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    person_id = Column(Integer, nullable=False, index=True)


class Emergencycall(Base):
    __tablename__ = u'EmergencyCall'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    event_id = Column(Integer, nullable=False, index=True)
    numberCardCall = Column(String(64), nullable=False)
    brigade_id = Column(Integer, index=True)
    causeCall_id = Column(Integer, index=True)
    whoCallOnPhone = Column(String(64), nullable=False)
    numberPhone = Column(String(32), nullable=False)
    begDate = Column(DateTime, nullable=False, index=True)
    passDate = Column(DateTime, nullable=False, index=True)
    departureDate = Column(DateTime, nullable=False, index=True)
    arrivalDate = Column(DateTime, nullable=False, index=True)
    finishServiceDate = Column(DateTime, nullable=False, index=True)
    endDate = Column(DateTime, index=True)
    placeReceptionCall_id = Column(Integer, index=True)
    receivedCall_id = Column(Integer, index=True)
    reasondDelays_id = Column(Integer, index=True)
    resultCall_id = Column(Integer, index=True)
    accident_id = Column(Integer, index=True)
    death_id = Column(Integer, index=True)
    ebriety_id = Column(Integer, index=True)
    diseased_id = Column(Integer, index=True)
    placeCall_id = Column(Integer, index=True)
    methodTransport_id = Column(Integer, index=True)
    transfTransport_id = Column(Integer, index=True)
    renunOfHospital = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    faceRenunOfHospital = Column(String(64), nullable=False, index=True)
    disease = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    birth = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    pregnancyFailure = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    noteCall = Column(Text, nullable=False)


class Event(Base, Info):
    __tablename__ = u'Event'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    externalId = Column(String(30), nullable=False)
    eventType_id = Column(Integer, ForeignKey('EventType.id'), nullable=False, index=True)
    org_id = Column(Integer, ForeignKey('Organisation.id'))
    client_id = Column(Integer, ForeignKey('Client.id'), index=True)
    contract_id = Column(Integer, ForeignKey('Contract.id'), index=True)
    prevEventDate = Column(DateTime)
    setDate = Column(DateTime, nullable=False, index=True)
    setPerson_id = Column(Integer, index=True)
    execDate = Column(DateTime, index=True)
    execPerson_id = Column(Integer, ForeignKey('Person.id'), index=True)
    isPrimaryCode = Column("isPrimary", Integer, nullable=False)
    order = Column(Integer, nullable=False)
    result_id = Column(Integer, ForeignKey('rbResult.id'), index=True)
    nextEventDate = Column(DateTime)
    payStatus = Column(Integer, nullable=False)
    typeAsset_id = Column(Integer, ForeignKey('rbEmergencyTypeAsset.id'), index=True)
    note = Column(Text, nullable=False)
    curator_id = Column(Integer, ForeignKey('Person.id'), index=True)
    assistant_id = Column(Integer, ForeignKey('Person.id'), index=True)
    pregnancyWeek = Column(Integer, nullable=False, server_default=u"'0'")
    MES_id = Column(Integer, index=True)
    mesSpecification_id = Column(ForeignKey('rbMesSpecification.id'), index=True)
    rbAcheResult_id = Column(ForeignKey('rbAcheResult.id'), index=True)
    version = Column(Integer, nullable=False, server_default=u"'0'")
    privilege = Column(Integer, server_default=u"'0'")
    urgent = Column(Integer, server_default=u"'0'")
    orgStructure_id = Column(Integer, ForeignKey('Person.orgStructure_id'))
    uuid_id = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    lpu_transfer = Column(String(100))

    actions = relationship(u'Action')
    eventType = relationship(u'Eventtype')
    execPerson = relationship(u'Person', foreign_keys='Event.execPerson_id')
    curator = relationship(u'Person', foreign_keys='Event.curator_id')
    assistant = relationship(u'Person', foreign_keys='Event.assistant_id')
    persons = relationship(u'Person', foreign_keys='Event.orgStructure_id')
    client = relationship(u'Client')
    contract = relationship(u'Contract')
    organisation = relationship(u'Organisation')
    mesSpecification = relationship(u'Rbmesspecification')
    rbAcheResult = relationship(u'Rbacheresult')
    result = relationship(u'Rbresult')
    typeAsset = relationship(u'Rbemergencytypeasset')
    localContract = relationship(u'EventLocalcontract')

    @property
    def isPrimary(self):
        return self.isPrimaryCode == 1

    @property
    def departmentManager(self):
        for person in self.persons:
            if person.post.flatCode == u'departmentManager':
                return person
        return None

    def __unicode__(self):
        return unicode(self.eventType)


class Hsintegration(Event):
    __tablename__ = u'HSIntegration'

    event_id = Column(ForeignKey('Event.id'), primary_key=True)
    status = Column(Enum(u'NEW', u'SENDED', u'ERROR'), nullable=False, server_default=u"'NEW'")
    info = Column(String(1024))


class Eventtype(Base, RBInfo):
    __tablename__ = u'EventType'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False)
    purpose_id = Column(Integer, ForeignKey('rbEventTypePurpose.id'), index=True)
    finance_id = Column(Integer, ForeignKey('rbFinance.id'), index=True)
    scene_id = Column(Integer, index=True)
    visitServiceModifier = Column(String(128), nullable=False)
    visitServiceFilter = Column(String(32), nullable=False)
    visitFinance = Column(Integer, nullable=False, server_default=u"'0'")
    actionFinance = Column(Integer, nullable=False, server_default=u"'0'")
    period = Column(Integer, nullable=False)
    singleInPeriod = Column(Integer, nullable=False)
    isLong = Column(Integer, nullable=False, server_default=u"'0'")
    dateInput = Column(Integer, nullable=False, server_default=u"'0'")
    service_id = Column(Integer, ForeignKey('rbService.id'), index=True)
    printContext = Column("context", String(64), nullable=False)
    form = Column(String(64), nullable=False)
    minDuration = Column(Integer, nullable=False, server_default=u"'0'")
    maxDuration = Column(Integer, nullable=False, server_default=u"'0'")
    showStatusActionsInPlanner = Column(Integer, nullable=False, server_default=u"'1'")
    showDiagnosticActionsInPlanner = Column(Integer, nullable=False, server_default=u"'1'")
    showCureActionsInPlanner = Column(Integer, nullable=False, server_default=u"'1'")
    showMiscActionsInPlanner = Column(Integer, nullable=False, server_default=u"'1'")
    limitStatusActionsInput = Column(Integer, nullable=False, server_default=u"'0'")
    limitDiagnosticActionsInput = Column(Integer, nullable=False, server_default=u"'0'")
    limitCureActionsInput = Column(Integer, nullable=False, server_default=u"'0'")
    limitMiscActionsInput = Column(Integer, nullable=False, server_default=u"'0'")
    showTime = Column(Integer, nullable=False, server_default=u"'0'")
    medicalAidType_id = Column(Integer, index=True)
    eventProfile_id = Column(Integer, index=True)
    mesRequired = Column(Integer, nullable=False, server_default=u"'0'")
    mesCodeMask = Column(String(64), server_default=u"''")
    mesNameMask = Column(String(64), server_default=u"''")
    counter_id = Column(ForeignKey('rbCounter.id'), index=True)
    isExternal = Column(Integer, nullable=False, server_default=u"'0'")
    isAssistant = Column(Integer, nullable=False, server_default=u"'0'")
    isCurator = Column(Integer, nullable=False, server_default=u"'0'")
    canHavePayableActions = Column(Integer, nullable=False, server_default=u"'0'")
    isRequiredCoordination = Column(Integer, nullable=False, server_default=u"'0'")
    isOrgStructurePriority = Column(Integer, nullable=False, server_default=u"'0'")
    isTakenTissue = Column(Integer, nullable=False, server_default=u"'0'")
    sex = Column(Integer, nullable=False, server_default=u"'0'")
    age = Column(String(9), nullable=False)
    rbMedicalKind_id = Column(ForeignKey('rbMedicalKind.id'), index=True)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    requestType_id = Column(Integer, ForeignKey('rbRequestType.id'))

    counter = relationship(u'Rbcounter')
    rbMedicalKind = relationship(u'Rbmedicalkind')
    purpose = relationship(u'Rbeventtypepurpose')
    finance = relationship(u'Rbfinance')
    service = relationship(u'Rbservice')
    requestType = relationship(u'Rbrequesttype')


class Eventtypeform(Base):
    __tablename__ = u'EventTypeForm'

    id = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    eventType_id = Column(Integer, nullable=False, index=True)
    code = Column(String(8), nullable=False)
    name = Column(String(64), nullable=False)
    descr = Column(String(64), nullable=False)
    pass_ = Column(u'pass', Integer, nullable=False)


class EventtypeAction(Base):
    __tablename__ = u'EventType_Action'

    id = Column(Integer, primary_key=True)
    eventType_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    actionType_id = Column(Integer, nullable=False, index=True)
    speciality_id = Column(Integer, index=True)
    tissueType_id = Column(ForeignKey('rbTissueType.id'), index=True)
    sex = Column(Integer, nullable=False)
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    selectionGroup = Column(Integer, nullable=False, server_default=u"'0'")
    actuality = Column(Integer, nullable=False)
    expose = Column(Integer, nullable=False, server_default=u"'1'")
    payable = Column(Integer, nullable=False, server_default=u"'0'")
    academicDegree_id = Column(Integer, index=True)

    tissueType = relationship(u'Rbtissuetype')


class EventtypeDiagnostic(Base):
    __tablename__ = u'EventType_Diagnostic'

    id = Column(Integer, primary_key=True)
    eventType_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    speciality_id = Column(Integer, index=True)
    sex = Column(Integer, nullable=False)
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    defaultHealthGroup_id = Column(Integer, index=True)
    defaultMKB = Column(String(5), nullable=False)
    defaultDispanser_id = Column(Integer, index=True)
    selectionGroup = Column(Integer, nullable=False, server_default=u"'0'")
    actuality = Column(Integer, nullable=False)
    visitType_id = Column(Integer)


class EventFeed(Base):
    __tablename__ = u'Event_Feed'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    event_id = Column(Integer, nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    mealTime_id = Column(Integer, index=True)
    diet_id = Column(Integer, index=True)


class EventLocalcontract(Base, Info):
    __tablename__ = u'Event_LocalContract'
    __table_args__ = (
        Index(u'lastName', u'lastName', u'firstName', u'patrName', u'birthDate', u'id'),
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    master_id = Column(Integer, ForeignKey('Event.id'), nullable=False, index=True)
    coordDate = Column(DateTime)
    coordAgent = Column(String(128), nullable=False, server_default=u"''")
    coordInspector = Column(String(128), nullable=False, server_default=u"''")
    coordText = Column(String, nullable=False)
    dateContract = Column(Date, nullable=False)
    numberContract = Column(Unicode(64), nullable=False)
    sumLimit = Column(Float(asdecimal=True), nullable=False)
    lastName = Column(Unicode(30), nullable=False)
    firstName = Column(Unicode(30), nullable=False)
    patrName = Column(Unicode(30), nullable=False)
    birthDate = Column(Date, nullable=False, index=True)
    documentType_id = Column(Integer, ForeignKey('rbDocumentType.id'), index=True)
    serialLeft = Column(Unicode(8), nullable=False)
    serialRight = Column(Unicode(8), nullable=False)
    number = Column(String(16), nullable=False)
    regAddress = Column(Unicode(64), nullable=False)
    org_id = Column(Integer, ForeignKey('Organisation.id'), index=True)

    org = relationship(u'Organisation')
    documentType = relationship(u'Rbdocumenttype')

    def __unicode__(self):
        parts = []
        if self.coordDate:
            parts.append(u'согласовано ' + self.coordDate)
        if self.coordText:
            parts.append(self.coordText)
        if self.number:
            parts.append(u'№ ' + self.number)
        if self.date:
            parts.append(u'от ' + self.date)
        if self.org:
            parts.append(unicode(self.org))
        else:
            parts.append(self.lastName)
            parts.append(self.firstName)
            parts.append(self.patrName)
        return ' '.join(parts)

    @property
    def document(self):
        document = Clientdocument()
        document.documentType = self.documentType
        document.serial = self.serialLeft + u' ' + self.serialRight
        document.number = self.number
        return document


class EventPayment(Base):
    __tablename__ = u'Event_Payment'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    master_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    cashOperation_id = Column(ForeignKey('rbCashOperation.id'), index=True)
    sum = Column(Float(asdecimal=True), nullable=False)
    typePayment = Column(Integer, nullable=False)
    settlementAccount = Column(String(64))
    bank_id = Column(Integer, index=True)
    numberCreditCard = Column(String(64))
    cashBox = Column(String(32), nullable=False)

    cashOperation = relationship(u'Rbcashoperation')


class EventPerson(Base):
    __tablename__ = u'Event_Persons'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False, index=True)
    person_id = Column(Integer, nullable=False, index=True)
    begDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime)


class Fdfield(Base):
    __tablename__ = u'FDField'

    id = Column(Integer, primary_key=True)
    fdFieldType_id = Column(ForeignKey('FDFieldType.id'), nullable=False, index=True)
    flatDirectory_id = Column(ForeignKey('FlatDirectory.id'), nullable=False, index=True)
    flatDirectory_code = Column(ForeignKey('FlatDirectory.code'), index=True)
    name = Column(String(4096), nullable=False)
    description = Column(String(4096))
    mask = Column(String(4096))
    mandatory = Column(Integer)
    order = Column(Integer)

    fdFieldType = relationship(u'Fdfieldtype')
    FlatDirectory = relationship(u'Flatdirectory', primaryjoin='Fdfield.flatDirectory_code == Flatdirectory.code')
    flatDirectory = relationship(u'Flatdirectory', primaryjoin='Fdfield.flatDirectory_id == Flatdirectory.id')


class Fdfieldtype(Base):
    __tablename__ = u'FDFieldType'

    id = Column(Integer, primary_key=True)
    name = Column(String(4096), nullable=False)
    description = Column(String(4096))


class Fdfieldvalue(Base):
    __tablename__ = u'FDFieldValue'

    id = Column(Integer, primary_key=True)
    fdRecord_id = Column(ForeignKey('FDRecord.id'), nullable=False, index=True)
    fdField_id = Column(ForeignKey('FDField.id'), nullable=False, index=True)
    value = Column(String)

    fdField = relationship(u'Fdfield')
    fdRecord = relationship(u'Fdrecord')


class Fdrecord(Base):
    __tablename__ = u'FDRecord'

    id = Column(Integer, primary_key=True)
    flatDirectory_id = Column(ForeignKey('FlatDirectory.id'), nullable=False, index=True)
    flatDirectory_code = Column(ForeignKey('FlatDirectory.code'), index=True)
    order = Column(Integer)
    name = Column(String(4096))
    description = Column(String(4096))
    dateStart = Column(DateTime)
    dateEnd = Column(DateTime)

    FlatDirectory = relationship(u'Flatdirectory', primaryjoin='Fdrecord.flatDirectory_code == Flatdirectory.code')
    flatDirectory = relationship(u'Flatdirectory', primaryjoin='Fdrecord.flatDirectory_id == Flatdirectory.id')


class Flatdirectory(Base):
    __tablename__ = u'FlatDirectory'

    id = Column(Integer, primary_key=True)
    name = Column(String(4096), nullable=False)
    code = Column(String(128), index=True)
    description = Column(String(4096))


class Informermessage(Base):
    __tablename__ = u'InformerMessage'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    subject = Column(String(128), nullable=False)
    text = Column(String, nullable=False)


class InformermessageReadmark(Base):
    __tablename__ = u'InformerMessage_readMark'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    person_id = Column(Integer, index=True)


class Job(Base):
    __tablename__ = u'Job'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    jobType_id = Column(Integer, nullable=False, index=True)
    orgStructure_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    begTime = Column(Time, nullable=False)
    endTime = Column(Time, nullable=False)
    quantity = Column(Integer, nullable=False)


class JobTicket(Base):
    __tablename__ = u'Job_Ticket'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    datetime = Column(DateTime, nullable=False)
    resTimestamp = Column(DateTime)
    resConnectionId = Column(Integer)
    status = Column(Integer, nullable=False, server_default=u"'0'")
    begDateTime = Column(DateTime)
    endDateTime = Column(DateTime)
    label = Column(String(64), nullable=False, server_default=u"''")
    note = Column(String(128), nullable=False, server_default=u"''")


class Lastchange(Base):
    __tablename__ = u'LastChanges'

    id = Column(Integer, primary_key=True)
    table = Column(String(32), nullable=False)
    table_key_id = Column(Integer, nullable=False)
    flags = Column(Text, nullable=False)


class Layoutattribute(Base):
    __tablename__ = u'LayoutAttribute'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1023), nullable=False)
    code = Column(String(255), nullable=False)
    typeName = Column(String(255))
    measure = Column(String(255))
    defaultValue = Column(String(1023))


class Layoutattributevalue(Base):
    __tablename__ = u'LayoutAttributeValue'

    id = Column(Integer, primary_key=True)
    actionPropertyType_id = Column(Integer, nullable=False)
    layoutAttribute_id = Column(ForeignKey('LayoutAttribute.id'), nullable=False, index=True)
    value = Column(String(1023), nullable=False)

    layoutAttribute = relationship(u'Layoutattribute')


class Licence(Base):
    __tablename__ = u'Licence'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    serial = Column(String(8), nullable=False)
    number = Column(String(16), nullable=False)
    date = Column(Date, nullable=False)
    person_id = Column(Integer, index=True)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)


class LicenceService(Base):
    __tablename__ = u'Licence_Service'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    service_id = Column(Integer, nullable=False, index=True)


class Mkb(Base):
    __tablename__ = u'MKB'
    __table_args__ = (
        Index(u'BlockID', u'BlockID', u'DiagID'),
        Index(u'ClassID_2', u'ClassID', u'BlockID', u'BlockName'),
        Index(u'ClassID', u'ClassID', u'ClassName')
    )

    id = Column(Integer, primary_key=True)
    ClassID = Column(String(8), nullable=False)
    ClassName = Column(String(150), nullable=False)
    BlockID = Column(String(9), nullable=False)
    BlockName = Column(String(160), nullable=False)
    DiagID = Column(String(8), nullable=False, index=True)
    DiagName = Column(String(160), nullable=False, index=True)
    Prim = Column(String(1), nullable=False)
    sex = Column(Integer, nullable=False)
    age = Column(String(12), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    characters = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    service_id = Column(Integer, index=True)
    MKBSubclass_id = Column(Integer)


class MkbQuotatypePacientmodel(Base):
    __tablename__ = u'MKB_QuotaType_PacientModel'

    id = Column(Integer, primary_key=True)
    MKB_id = Column(Integer, nullable=False)
    pacientModel_id = Column(Integer, nullable=False)
    quotaType_id = Column(Integer, nullable=False)


class Media(Base):
    __tablename__ = u'Media'

    id = Column(Integer, primary_key=True)
    filename = Column(String(256, u'utf8_bin'), nullable=False)
    file = Column(MEDIUMBLOB)


class Medicalkindunit(Base):
    __tablename__ = u'MedicalKindUnit'

    id = Column(Integer, primary_key=True)
    rbMedicalKind_id = Column(ForeignKey('rbMedicalKind.id'), nullable=False, index=True)
    eventType_id = Column(ForeignKey('EventType.id'), index=True)
    rbMedicalAidUnit_id = Column(ForeignKey('rbMedicalAidUnit.id'), nullable=False, index=True)
    rbPayType_id = Column(ForeignKey('rbPayType.id'), nullable=False, index=True)
    rbTariffType_id = Column(ForeignKey('rbTariffType.id'), nullable=False, index=True)

    eventType = relationship(u'Eventtype')
    rbMedicalAidUnit = relationship(u'Rbmedicalaidunit')
    rbMedicalKind = relationship(u'Rbmedicalkind')
    rbPayType = relationship(u'Rbpaytype')
    rbTariffType = relationship(u'Rbtarifftype')


class Meta(Base):
    __tablename__ = u'Meta'

    name = Column(String(100), primary_key=True)
    value = Column(Text)


class Modeldescription(Base):
    __tablename__ = u'ModelDescription'

    id = Column(Integer, primary_key=True)
    idx = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    name = Column(String(64), nullable=False)
    fieldIdx = Column(Integer, nullable=False, server_default=u"'-1'")
    tableName = Column(String(64), nullable=False)


class Notificationoccurred(Base):
    __tablename__ = u'NotificationOccurred'

    id = Column(Integer, primary_key=True)
    eventDatetime = Column(DateTime, nullable=False)
    clientId = Column(Integer, nullable=False)
    userId = Column(ForeignKey('Person.id'), nullable=False, index=True)

    Person = relationship(u'Person')


class Orgstructure(Base, Info):
    __tablename__ = u'OrgStructure'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    organisation_id = Column(Integer, ForeignKey('Organisation.id'), nullable=False, index=True)
    code = Column(Unicode(255), nullable=False)
    name = Column(Unicode(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('OrgStructure.id'), index=True)
    type = Column(Integer, nullable=False, server_default=u"'0'")
    net_id = Column(Integer, ForeignKey('rbNet.id'), index=True)
    isArea = Column(Integer, nullable=False, server_default=u"'0'")
    hasHospitalBeds = Column(Integer, nullable=False, server_default=u"'0'")
    hasStocks = Column(Integer, nullable=False, server_default=u"'0'")
    infisCode = Column(String(16), nullable=False)
    infisInternalCode = Column(String(16), nullable=False)
    infisDepTypeCode = Column(String(16), nullable=False)
    infisTariffCode = Column(String(16), nullable=False)
    availableForExternal = Column(Integer, nullable=False, server_default=u"'1'")
    Address = Column(String(255), nullable=False)
    inheritEventTypes = Column(Integer, nullable=False, server_default=u"'0'")
    inheritActionTypes = Column(Integer, nullable=False, server_default=u"'0'")
    inheritGaps = Column(Integer, nullable=False, server_default=u"'0'")
    uuid_id = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    show = Column(Integer, nullable=False, server_default=u"'1'")

    parent = relationship(u'Orgstructure', remote_side=[id])
    organisation = relationship(u'Organisation')
    Net = relationship(u'Rbnet')

    def getNet(self):
        if self.Net is None:
            if self.parent:
                self.Net = self.parent.getNet()
            elif self.organisation:
                self.Net = self.organisation.net
        return self.Net

    def get_org_structure_full_name(self, org_structure_id):
        names = [self.code]
        ids = set([self.id])
        parent_id = self.parent_id
        parent = self.parent

        while parent_id:
            if parent_id in ids:
                parent_id = None
            else:
                ids.add(parent_id)
                names.append(parent.code)
                parent_id = parent.parent_id
                parent = parent.parent
        return '/'.join(reversed(names))

    def getFullName(self):
        return self.get_org_structure_full_name(self.id)

    def getAddress(self):
        if not self.Address:
            if self.parent:
                self.Address = self.parent.getAddress()
            elif self.organisation:
                self.Address = self.organisation.address
            else:
                self.Address = ''
        return self.Address

    def __unicode__(self):
        return self.getFullName()

    net = property(getNet)
    fullName = property(getFullName)
    address = property(getAddress)


class OrgstructureActiontype(Base):
    __tablename__ = u'OrgStructure_ActionType'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    actionType_id = Column(Integer, index=True)


class OrgstructureAddres(Base):
    __tablename__ = u'OrgStructure_Address'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    house_id = Column(Integer, nullable=False, index=True)
    firstFlat = Column(Integer, nullable=False, server_default=u"'0'")
    lastFlat = Column(Integer, nullable=False, server_default=u"'0'")


class OrgstructureDisabledattendance(Base):
    __tablename__ = u'OrgStructure_DisabledAttendance'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('OrgStructure.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    attachType_id = Column(ForeignKey('rbAttachType.id'), index=True)
    disabledType = Column(Integer, nullable=False, server_default=u"'0'")

    attachType = relationship(u'Rbattachtype')
    master = relationship(u'Orgstructure')


class OrgstructureEventtype(Base):
    __tablename__ = u'OrgStructure_EventType'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    eventType_id = Column(Integer, index=True)


class OrgstructureGap(Base):
    __tablename__ = u'OrgStructure_Gap'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    begTime = Column(Time, nullable=False)
    endTime = Column(Time, nullable=False)
    speciality_id = Column(Integer, index=True)
    person_id = Column(Integer, index=True)


class OrgstructureHospitalbed(Base, Info):
    __tablename__ = u'OrgStructure_HospitalBed'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, ForeignKey('OrgStructure.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    code = Column(String(16), nullable=False, server_default=u"''")
    name = Column(String(64), nullable=False, server_default=u"''")
    isPermanentCode = Column("isPermanent", Integer, nullable=False, server_default=u"'0'")
    type_id = Column(Integer, ForeignKey('rbHospitalBedType.id'), index=True)
    profile_id = Column(Integer, ForeignKey('rbHospitalBedProfile.id'), index=True)
    relief = Column(Integer, nullable=False, server_default=u"'0'")
    schedule_id = Column(Integer, ForeignKey('rbHospitalBedShedule.id'), index=True)
    begDate = Column(Date)
    endDate = Column(Date)
    sex = Column(Integer, nullable=False, server_default=u"'0'")
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    involution = Column(Integer, nullable=False, server_default=u"'0'")
    begDateInvolute = Column(Date)
    endDateInvolute = Column(Date)

    orgStructure = relationship(u'Orgstructure')
    type = relationship(u'Rbhospitalbedtype')
    profile = relationship(u'Rbhospitalbedprofile')
    schedule = relationship(u'Rbhospitalbedshedule')

    @property
    def isPermanent(self):
        return self.isPermanentCode == 1


class OrgstructureJob(Base):
    __tablename__ = u'OrgStructure_Job'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    jobType_id = Column(Integer, index=True)
    begTime = Column(Time, nullable=False)
    endTime = Column(Time, nullable=False)
    quantity = Column(Integer, nullable=False)


class OrgstructureStock(Base):
    __tablename__ = u'OrgStructure_Stock'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('OrgStructure.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    finance_id = Column(ForeignKey('rbFinance.id'), index=True)
    constrainedQnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    orderQnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")

    finance = relationship(u'Rbfinance')
    master = relationship(u'Orgstructure')
    nomenclature = relationship(u'Rbnomenclature')


class Organisation(Base, Info):
    __tablename__ = u'Organisation'
    __table_args__ = (
        Index(u'shortName', u'shortName', u'INN', u'OGRN'),
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    fullName = Column(String(255), nullable=False)
    shortName = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    net_id = Column(Integer, ForeignKey('rbNet.id'), index=True)
    infisCode = Column(String(12), nullable=False, index=True)
    obsoleteInfisCode = Column(String(60), nullable=False)
    OKVED = Column(String(64), nullable=False, index=True)
    INN = Column(String(15), nullable=False, index=True)
    KPP = Column(String(15), nullable=False)
    OGRN = Column(String(15), nullable=False, index=True)
    OKATO = Column(String(15), nullable=False)
    OKPF_code = Column(String(4), nullable=False)
    OKPF_id = Column(Integer, ForeignKey('rbOKPF.id'), index=True)
    OKFS_code = Column(Integer, nullable=False)
    OKFS_id = Column(Integer, ForeignKey('rbOKFS.id'), index=True)
    OKPO = Column(String(15), nullable=False)
    FSS = Column(String(10), nullable=False)
    region = Column(String(40), nullable=False)
    Address = Column(String(255), nullable=False)
    chief = Column(String(64), nullable=False)
    phone = Column(String(255), nullable=False)
    accountant = Column(String(64), nullable=False)
    isInsurer = Column(Integer, nullable=False, index=True)
    compulsoryServiceStop = Column(Integer, nullable=False, server_default=u"'0'")
    voluntaryServiceStop = Column(Integer, nullable=False, server_default=u"'0'")
    area = Column(String(13), nullable=False)
    isHospital = Column(Integer, nullable=False, server_default=u"'0'")
    notes = Column(String, nullable=False)
    head_id = Column(Integer, index=True)
    miacCode = Column(String(10), nullable=False)
    isOrganisation = Column(Integer, nullable=False, server_default=u"'0'")
    uuid_id = Column(Integer, nullable=False, index=True, server_default=u"'0'")


    net = relationship(u'Rbnet')
    OKPF = relationship(u'Rbokpf')
    OKFS = relationship(u'Rbokfs')


class OrganisationAccount(Base, Info):
    __tablename__ = u'Organisation_Account'

    id = Column(Integer, primary_key=True)
    organisation_id = Column(Integer, ForeignKey('Organisation.id'), nullable=False, index=True)
    bankName = Column(Unicode(128), nullable=False)
    name = Column(String(20), nullable=False)
    notes = Column(String, nullable=False)
    bank_id = Column(Integer, ForeignKey('Bank.id'), nullable=False, index=True)
    cash = Column(Integer, nullable=False)

    org = relationship(u'Organisation')
    bank = relationship(u'Bank')


class OrganisationPolicyserial(Base):
    __tablename__ = u'Organisation_PolicySerial'

    id = Column(Integer, primary_key=True)
    organisation_id = Column(Integer, nullable=False, index=True)
    serial = Column(String(16), nullable=False)
    policyType_id = Column(Integer, index=True)


class Person(Base):
    __tablename__ = u'Person'
    __table_args__ = (
        Index(u'lastName', u'lastName', u'firstName', u'patrName'),
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    code = Column(String(12), nullable=False)
    federalCode = Column(Unicode(255), nullable=False)
    regionalCode = Column(String(16), nullable=False)
    lastName = Column(Unicode(30), nullable=False)
    firstName = Column(Unicode(30), nullable=False)
    patrName = Column(Unicode(30), nullable=False)
    post_id = Column(Integer, ForeignKey('rbPost.id'), index=True)
    speciality_id = Column(Integer, ForeignKey('rbSpeciality.id'), index=True)
    org_id = Column(Integer, ForeignKey('Organisation.id'), index=True)
    orgStructure_id = Column(Integer, ForeignKey('OrgStructure.id'), index=True)
    office = Column(Unicode(8), nullable=False)
    office2 = Column(Unicode(8), nullable=False)
    tariffCategory_id = Column(Integer, ForeignKey('rbTariffCategory.id'), index=True)
    finance_id = Column(Integer, ForeignKey('rbFinance.id'), index=True)
    retireDate = Column(Date, index=True)
    ambPlan = Column(SmallInteger, nullable=False)
    ambPlan2 = Column(SmallInteger, nullable=False)
    ambNorm = Column(SmallInteger, nullable=False)
    homPlan = Column(SmallInteger, nullable=False)
    homPlan2 = Column(SmallInteger, nullable=False)
    homNorm = Column(SmallInteger, nullable=False)
    expPlan = Column(SmallInteger, nullable=False)
    expNorm = Column(SmallInteger, nullable=False)
    login = Column(Unicode(32), nullable=False)
    password = Column(String(32), nullable=False)
    userProfile_id = Column(Integer, index=True)
    retired = Column(Integer, nullable=False)
    birthDate = Column(Date, nullable=False)
    birthPlace = Column(String(64), nullable=False)
    sex = Column(Integer, nullable=False)
    SNILS = Column(String(11), nullable=False)
    INN = Column(String(15), nullable=False)
    availableForExternal = Column(Integer, nullable=False, server_default=u"'1'")
    primaryQuota = Column(SmallInteger, nullable=False, server_default=u"'50'")
    ownQuota = Column(SmallInteger, nullable=False, server_default=u"'25'")
    consultancyQuota = Column(SmallInteger, nullable=False, server_default=u"'25'")
    externalQuota = Column(SmallInteger, nullable=False, server_default=u"'10'")
    lastAccessibleTimelineDate = Column(Date)
    timelineAccessibleDays = Column(Integer, nullable=False, server_default=u"'0'")
    typeTimeLinePerson = Column(Integer, nullable=False)
    maxOverQueue = Column(Integer, server_default=u"'0'")
    maxCito = Column(Integer, server_default=u"'0'")
    quotUnit = Column(Integer, server_default=u"'0'")
    academicdegree_id = Column(Integer, ForeignKey('rbAcademicDegree.id'))
    academicTitle_id = Column(Integer, ForeignKey('rbAcademicTitle.id'))

    post = relationship(u'Rbpost')
    speciality = relationship(u'Rbspeciality')
    organisation = relationship(u'Organisation')
    orgStructure = relationship(u'Orgstructure')
    academicDegree = relationship(u'Rbacademicdegree')
    academicTitle = relationship(u'Rbacademictitle')
    tariffCategory = relationship(u'Rbtariffcategory')

    @property
    def fullName(self):
        return formatNameInt(self.lastName, self.firstName, self.patrName)

    @property
    def shortName(self):
        return formatShortNameInt(self.lastName, self.firstName, self.patrName)

    @property
    def longName(self):
        return formatNameInt(self.lastName, self.firstName, self.patrName)

    @property
    def name(self):
        return formatShortNameInt(self.lastName, self.firstName, self.patrName)

    def __unicode__(self):
        result = formatShortNameInt(self._lastName, self._firstName, self._patrName)
        if self.speciality:
            result += ', '+self.speciality.name
        return unicode(result)


class Personaddres(Base):
    __tablename__ = u'PersonAddress'
    __table_args__ = (
        Index(u'person_id', u'person_id', u'type', u'address_id'),
    )

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    person_id = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    address_id = Column(Integer)


class Persondocument(Base):
    __tablename__ = u'PersonDocument'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    person_id = Column(Integer, nullable=False, index=True)
    documentType_id = Column(Integer, index=True)
    serial = Column(String(8), nullable=False)
    number = Column(String(16), nullable=False)
    date = Column(Date, nullable=False)
    origin = Column(String(64), nullable=False)


class Personeducation(Base):
    __tablename__ = u'PersonEducation'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    person_id = Column(Integer, nullable=False, index=True)
    documentType_id = Column(Integer, index=True)
    serial = Column(String(8), nullable=False)
    number = Column(String(16), nullable=False)
    date = Column(Date, nullable=False)
    origin = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    validFromDate = Column(Date)
    validToDate = Column(Date)
    speciality_id = Column(Integer)
    educationCost = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    cost = Column(Float(asdecimal=True))


class Personorder(Base):
    __tablename__ = u'PersonOrder'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    person_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    type = Column(String(64), nullable=False)
    documentDate = Column(Date, nullable=False)
    documentNumber = Column(String(16), nullable=False)
    documentType_id = Column(Integer, index=True)
    salary = Column(String(64), nullable=False)
    validFromDate = Column(Date)
    validToDate = Column(Date)
    orgStructure_id = Column(Integer, index=True)
    post_id = Column(Integer, index=True)


class Persontimetemplate(Base):
    __tablename__ = u'PersonTimeTemplate'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    ambBegTime = Column(Time)
    ambEndTime = Column(Time)
    ambPlan = Column(SmallInteger, nullable=False)
    office = Column(String(8), nullable=False)
    ambBegTime2 = Column(Time)
    ambEndTime2 = Column(Time)
    ambPlan2 = Column(SmallInteger, nullable=False)
    office2 = Column(String(8), nullable=False)
    homBegTime = Column(Time)
    homEndTime = Column(Time)
    homPlan = Column(SmallInteger, nullable=False)
    homBegTime2 = Column(Time)
    homEndTime2 = Column(Time)
    homPlan2 = Column(SmallInteger, nullable=False)


class PersonActivity(Base):
    __tablename__ = u'Person_Activity'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    activity_id = Column(Integer, index=True)


class PersonProfile(Base):
    __tablename__ = u'Person_Profiles'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, nullable=False, index=True)
    userProfile_id = Column(Integer, nullable=False, index=True)


class PersonTimetemplate(Base):
    __tablename__ = u'Person_TimeTemplate'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(ForeignKey('Person.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    ambBegTime = Column(Time)
    ambEndTime = Column(Time)
    ambPlan = Column(SmallInteger, nullable=False)
    office = Column(String(8), nullable=False)
    ambBegTime2 = Column(Time)
    ambEndTime2 = Column(Time)
    ambPlan2 = Column(SmallInteger, nullable=False)
    office2 = Column(String(8), nullable=False)
    homBegTime = Column(Time)
    homEndTime = Column(Time)
    homPlan = Column(SmallInteger, nullable=False)
    homBegTime2 = Column(Time)
    homEndTime2 = Column(Time)
    homPlan2 = Column(SmallInteger, nullable=False)

    createPerson = relationship(u'Person', primaryjoin='PersonTimetemplate.createPerson_id == Person.id')
    master = relationship(u'Person', primaryjoin='PersonTimetemplate.master_id == Person.id')
    modifyPerson = relationship(u'Person', primaryjoin='PersonTimetemplate.modifyPerson_id == Person.id')


class Pharmacy(Base):
    __tablename__ = u'Pharmacy'

    actionId = Column(Integer, primary_key=True)
    flatCode = Column(String(255))
    attempts = Column(Integer, server_default=u"'0'")
    status = Column(Enum(u'ADDED', u'COMPLETE', u'ERROR'), server_default=u"'ADDED'")
    uuid = Column(String(255), server_default=u"'0'")
    result = Column(String(255), server_default=u"''")
    error_string = Column(String(255))
    rev = Column(String(255), server_default=u"''")
    value = Column(Integer, server_default=u"'0'")


class Prescriptionsendingre(Base):
    __tablename__ = u'PrescriptionSendingRes'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(100))
    version = Column(Integer)
    interval_id = Column(ForeignKey('DrugChart.id'), index=True)
    drugComponent_id = Column(ForeignKey('DrugComponent.id'), index=True)

    drugComponent = relationship(u'Drugcomponent')
    interval = relationship(u'Drugchart')


class Prescriptionsto1c(Base):
    __tablename__ = u'PrescriptionsTo1C'

    interval_id = Column(Integer, primary_key=True)
    errCount = Column(Integer, nullable=False, server_default=u"'0'")
    info = Column(String(1024))
    is_prescription = Column(Integer)
    new_status = Column(Integer)
    old_status = Column(Integer)
    sendTime = Column(DateTime, nullable=False, server_default=u'CURRENT_TIMESTAMP')


class Quotatype(Base):
    __tablename__ = u'QuotaType'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    class_ = Column(u'class', Integer, nullable=False)
    group_code = Column(String(16))
    code = Column(String(16), nullable=False)
    name = Column(Unicode(255), nullable=False)
    teenOlder = Column(Integer, nullable=False)

    def __unicode__(self):
        return self.name


class Quoting(Base):
    __tablename__ = u'Quoting'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    quotaType_id = Column(Integer)
    beginDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime, nullable=False)
    limitation = Column(Integer, nullable=False, server_default=u"'0'")
    used = Column(Integer, nullable=False, server_default=u"'0'")
    confirmed = Column(Integer, nullable=False, server_default=u"'0'")
    inQueue = Column(Integer, nullable=False, server_default=u"'0'")


class Quotingbyspeciality(Base):
    __tablename__ = u'QuotingBySpeciality'

    id = Column(Integer, primary_key=True)
    speciality_id = Column(ForeignKey('rbSpeciality.id'), nullable=False, index=True)
    organisation_id = Column(ForeignKey('Organisation.id'), nullable=False, index=True)
    coupons_quote = Column(Integer)
    coupons_remaining = Column(Integer)

    organisation = relationship(u'Organisation')
    speciality = relationship(u'Rbspeciality')


class Quotingbytime(Base):
    __tablename__ = u'QuotingByTime'

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer)
    quoting_date = Column(Date, nullable=False)
    QuotingTimeStart = Column(Time, nullable=False)
    QuotingTimeEnd = Column(Time, nullable=False)
    QuotingType = Column(Integer)


class QuotingRegion(Base):
    __tablename__ = u'Quoting_Region'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(Integer, index=True)
    region_code = Column(String(13), index=True)
    limitation = Column(Integer, nullable=False, server_default=u"'0'")
    used = Column(Integer, nullable=False, server_default=u"'0'")
    confirmed = Column(Integer, nullable=False, server_default=u"'0'")
    inQueue = Column(Integer, nullable=False, server_default=u"'0'")


class Setting(Base):
    __tablename__ = u'Setting'

    id = Column(Integer, primary_key=True)
    path = Column(String(255), nullable=False, unique=True)
    value = Column(Text, nullable=False)


class Socstatu(Base):
    __tablename__ = u'SocStatus'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    socStatusClass_id = Column(Integer, nullable=False, index=True)
    socStatusType_id = Column(Integer, nullable=False, index=True)


class Stockmotion(Base):
    __tablename__ = u'StockMotion'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    deleted = Column(Integer, nullable=False)
    type = Column(Integer, server_default=u"'0'")
    date = Column(DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    supplier_id = Column(ForeignKey('OrgStructure.id'), index=True)
    receiver_id = Column(ForeignKey('OrgStructure.id'), index=True)
    note = Column(String, nullable=False)
    supplierPerson_id = Column(ForeignKey('Person.id'), index=True)
    receiverPerson_id = Column(ForeignKey('Person.id'), index=True)

    createPerson = relationship(u'Person', primaryjoin='Stockmotion.createPerson_id == Person.id')
    modifyPerson = relationship(u'Person', primaryjoin='Stockmotion.modifyPerson_id == Person.id')
    receiverPerson = relationship(u'Person', primaryjoin='Stockmotion.receiverPerson_id == Person.id')
    receiver = relationship(u'Orgstructure', primaryjoin='Stockmotion.receiver_id == Orgstructure.id')
    supplierPerson = relationship(u'Person', primaryjoin='Stockmotion.supplierPerson_id == Person.id')
    supplier = relationship(u'Orgstructure', primaryjoin='Stockmotion.supplier_id == Orgstructure.id')


class StockmotionItem(Base):
    __tablename__ = u'StockMotion_Item'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('StockMotion.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    finance_id = Column(ForeignKey('rbFinance.id'), index=True)
    qnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    sum = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    oldQnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    oldSum = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    oldFinance_id = Column(ForeignKey('rbFinance.id'), index=True)
    isOut = Column(Integer, nullable=False, server_default=u"'0'")
    note = Column(String, nullable=False)

    finance = relationship(u'Rbfinance', primaryjoin='StockmotionItem.finance_id == Rbfinance.id')
    master = relationship(u'Stockmotion')
    nomenclature = relationship(u'Rbnomenclature')
    oldFinance = relationship(u'Rbfinance', primaryjoin='StockmotionItem.oldFinance_id == Rbfinance.id')


class Stockrecipe(Base):
    __tablename__ = u'StockRecipe'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    deleted = Column(Integer, nullable=False)
    group_id = Column(ForeignKey('StockRecipe.id'), index=True)
    code = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)

    createPerson = relationship(u'Person', primaryjoin='Stockrecipe.createPerson_id == Person.id')
    group = relationship(u'Stockrecipe', remote_side=[id])
    modifyPerson = relationship(u'Person', primaryjoin='Stockrecipe.modifyPerson_id == Person.id')


class StockrecipeItem(Base):
    __tablename__ = u'StockRecipe_Item'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('StockRecipe.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    qnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    isOut = Column(Integer, nullable=False, server_default=u"'0'")

    master = relationship(u'Stockrecipe')
    nomenclature = relationship(u'Rbnomenclature')


class Stockrequisition(Base):
    __tablename__ = u'StockRequisition'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    date = Column(Date, nullable=False, server_default=u"'0000-00-00'")
    deadline = Column(DateTime)
    supplier_id = Column(ForeignKey('OrgStructure.id'), index=True)
    recipient_id = Column(ForeignKey('OrgStructure.id'), index=True)
    revoked = Column(Integer, nullable=False, server_default=u"'0'")
    note = Column(String, nullable=False)

    createPerson = relationship(u'Person', primaryjoin='Stockrequisition.createPerson_id == Person.id')
    modifyPerson = relationship(u'Person', primaryjoin='Stockrequisition.modifyPerson_id == Person.id')
    recipient = relationship(u'Orgstructure', primaryjoin='Stockrequisition.recipient_id == Orgstructure.id')
    supplier = relationship(u'Orgstructure', primaryjoin='Stockrequisition.supplier_id == Orgstructure.id')


class StockrequisitionItem(Base):
    __tablename__ = u'StockRequisition_Item'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('StockRequisition.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    finance_id = Column(ForeignKey('rbFinance.id'), index=True)
    qnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    satisfiedQnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")

    finance = relationship(u'Rbfinance')
    master = relationship(u'Stockrequisition')
    nomenclature = relationship(u'Rbnomenclature')


class Stocktran(Base):
    __tablename__ = u'StockTrans'
    __table_args__ = (
        Index(u'cre', u'creOrgStructure_id', u'creNomenclature_id', u'creFinance_id'),
        Index(u'deb', u'debOrgStructure_id', u'debNomenclature_id', u'debFinance_id')
    )

    id = Column(BigInteger, primary_key=True)
    stockMotionItem_id = Column(ForeignKey('StockMotion_Item.id'), nullable=False, index=True)
    date = Column(DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    qnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    sum = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    debOrgStructure_id = Column(ForeignKey('OrgStructure.id'), index=True)
    debNomenclature_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    debFinance_id = Column(ForeignKey('rbFinance.id'), index=True)
    creOrgStructure_id = Column(ForeignKey('OrgStructure.id'), index=True)
    creNomenclature_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    creFinance_id = Column(ForeignKey('rbFinance.id'), index=True)

    creFinance = relationship(u'Rbfinance', primaryjoin='Stocktran.creFinance_id == Rbfinance.id')
    creNomenclature = relationship(u'Rbnomenclature', primaryjoin='Stocktran.creNomenclature_id == Rbnomenclature.id')
    creOrgStructure = relationship(u'Orgstructure', primaryjoin='Stocktran.creOrgStructure_id == Orgstructure.id')
    debFinance = relationship(u'Rbfinance', primaryjoin='Stocktran.debFinance_id == Rbfinance.id')
    debNomenclature = relationship(u'Rbnomenclature', primaryjoin='Stocktran.debNomenclature_id == Rbnomenclature.id')
    debOrgStructure = relationship(u'Orgstructure', primaryjoin='Stocktran.debOrgStructure_id == Orgstructure.id')
    stockMotionItem = relationship(u'StockmotionItem')


class Takentissuejournal(Base):
    __tablename__ = u'TakenTissueJournal'
    __table_args__ = (
        Index(u'period_barcode', u'period', u'barcode'),
    )

    id = Column(Integer, primary_key=True)
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    tissueType_id = Column(ForeignKey('rbTissueType.id'), nullable=False, index=True)
    externalId = Column(String(30), nullable=False)
    amount = Column(Integer, nullable=False, server_default=u"'0'")
    unit_id = Column(ForeignKey('rbUnit.id'), index=True)
    datetimeTaken = Column(DateTime, nullable=False)
    execPerson_id = Column(ForeignKey('Person.id'), index=True)
    note = Column(String(128), nullable=False)
    barcode = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)

    client = relationship(u'Client')
    execPerson = relationship(u'Person')
    tissueType = relationship(u'Rbtissuetype')
    unit = relationship(u'Rbunit')

    @property
    def barcode_s(self):
        return code128C(self.barcode).decode('windows-1252')


class Tempinvalid(Base):
    __tablename__ = u'TempInvalid'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    type = Column(Integer, nullable=False, server_default=u"'0'")
    doctype = Column(Integer, nullable=False)
    doctype_id = Column(Integer, index=True)
    serial = Column(String(8), nullable=False)
    number = Column(String(16), nullable=False)
    client_id = Column(Integer, nullable=False, index=True)
    tempInvalidReason_id = Column(Integer, index=True)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False, index=True)
    person_id = Column(Integer, index=True)
    diagnosis_id = Column(Integer, index=True)
    sex = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    notes = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    closed = Column(Integer, nullable=False)
    prev_id = Column(Integer, index=True)
    insuranceOfficeMark = Column(Integer, nullable=False, server_default=u"'0'")
    caseBegDate = Column(Date, nullable=False)
    event_id = Column(Integer)


class Tempinvalidduplicate(Base):
    __tablename__ = u'TempInvalidDuplicate'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    tempInvalid_id = Column(Integer, nullable=False, index=True)
    person_id = Column(Integer, index=True)
    date = Column(Date, nullable=False)
    serial = Column(String(8), nullable=False)
    number = Column(String(16), nullable=False)
    destination = Column(String(128), nullable=False)
    reason_id = Column(Integer, index=True)
    note = Column(String, nullable=False)
    insuranceOfficeMark = Column(Integer, nullable=False, server_default=u"'0'")


class TempinvalidPeriod(Base):
    __tablename__ = u'TempInvalid_Period'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    diagnosis_id = Column(Integer, index=True)
    begPerson_id = Column(Integer, index=True)
    begDate = Column(Date, nullable=False)
    endPerson_id = Column(Integer, index=True)
    endDate = Column(Date, nullable=False)
    isExternal = Column(Integer, nullable=False)
    regime_id = Column(Integer, index=True)
    break_id = Column(Integer, index=True)
    result_id = Column(Integer, index=True)
    note = Column(String(256), nullable=False)


class Tissue(Base):
    __tablename__ = u'Tissue'

    id = Column(Integer, primary_key=True)
    type_id = Column(ForeignKey('rbTissueType.id'), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    barcode = Column(String(255), nullable=False, index=True)
    event_id = Column(ForeignKey('Event.id'), nullable=False, index=True)

    event = relationship(u'Event')
    type = relationship(u'Rbtissuetype')


class Uuid(Base):
    __tablename__ = u'UUID'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(100), nullable=False, unique=True)


class Variablesforsql(Base):
    __tablename__ = u'VariablesforSQL'

    id = Column(Integer, primary_key=True)
    specialVarName_id = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False)
    var_type = Column(String(64), nullable=False)
    label = Column(String(64), nullable=False)


class Version(Base):
    __tablename__ = u'Versions'

    id = Column(Integer, primary_key=True)
    table = Column(String(64), nullable=False, unique=True)
    version = Column(Integer, nullable=False, server_default=u"'0'")


class Visit(Base):
    __tablename__ = u'Visit'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    event_id = Column(Integer, nullable=False, index=True)
    scene_id = Column(Integer, nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    visitType_id = Column(Integer, nullable=False, index=True)
    person_id = Column(Integer, nullable=False, index=True)
    isPrimary = Column(Integer, nullable=False)
    finance_id = Column(Integer, nullable=False, index=True)
    service_id = Column(Integer, index=True)
    payStatus = Column(Integer, nullable=False)


class ActionDocument(Base):
    __tablename__ = u'action_document'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    modify_date = Column(DateTime, nullable=False)
    template_id = Column(ForeignKey('rbPrintTemplate.id'), nullable=False, index=True)
    document = Column(MEDIUMBLOB, nullable=False)

    action = relationship(u'Action')
    template = relationship(u'Rbprinttemplate')


class BbtorganismSensvalue(Base):
    __tablename__ = u'bbtOrganism_SensValues'
    __table_args__ = (
        Index(u'bbtResult_Organism_id_index', u'bbtResult_Organism_id', u'idx'),
    )

    id = Column(Integer, primary_key=True)
    bbtResult_Organism_id = Column(ForeignKey('bbtResult_Organism.id'), nullable=False)
    idx = Column(Integer)
    antibiotic_id = Column(ForeignKey('rbAntibiotic.id'), index=True)
    MIC = Column(String(20), nullable=False)
    activity = Column(String(5), nullable=False)

    antibiotic = relationship(u'Rbantibiotic')
    bbtResult_Organism = relationship(u'BbtresultOrganism')


class BbtresultImage(Base):
    __tablename__ = u'bbtResult_Image'
    __table_args__ = (
        Index(u'action_id_index', u'action_id', u'idx'),
    )

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False)
    idx = Column(Integer, nullable=False)
    description = Column(String(256))
    image = Column(LONGBLOB, nullable=False)

    action = relationship(u'Action')


class BbtresultOrganism(Base):
    __tablename__ = u'bbtResult_Organism'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    organism_id = Column(ForeignKey('rbMicroorganism.id'), nullable=False, index=True)
    concentration = Column(String(256), nullable=False)

    action = relationship(u'Action')
    organism = relationship(u'Rbmicroorganism')


class BbtresultTable(Base):
    __tablename__ = u'bbtResult_Table'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    indicator_id = Column(ForeignKey('rbBacIndicator.id'), nullable=False, index=True)
    normString = Column(String(256))
    normalityIndex = Column(Float)
    unit = Column(String(20))
    signDateTime = Column(DateTime, nullable=False)
    status = Column(Text)
    comment = Column(Text)

    action = relationship(u'Action')
    indicator = relationship(u'Rbbacindicator')


class BbtresultText(Base):
    __tablename__ = u'bbtResult_Text'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    valueText = Column(Text)

    action = relationship(u'Action')


class Mrbmodelagegroup(Base):
    __tablename__ = u'mrbModelAgeGroup'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelaidcase(Base):
    __tablename__ = u'mrbModelAidCase'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelaidpurpose(Base):
    __tablename__ = u'mrbModelAidPurpose'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelcategory(Base):
    __tablename__ = u'mrbModelCategory'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelcontinuation(Base):
    __tablename__ = u'mrbModelContinuation'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodeldiseaseclas(Base):
    __tablename__ = u'mrbModelDiseaseClass'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelexpectedresult(Base):
    __tablename__ = u'mrbModelExpectedResult'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelinstitutiontype(Base):
    __tablename__ = u'mrbModelInstitutionType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelsertificationrequirement(Base):
    __tablename__ = u'mrbModelSertificationRequirement'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelstatebadnes(Base):
    __tablename__ = u'mrbModelStateBadness'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class NewTable(Base):
    __tablename__ = u'new_table'

    idnew_table = Column(Integer, primary_key=True)


class Rb64district(Base):
    __tablename__ = u'rb64District'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    code_tfoms = Column(Integer, nullable=False)
    socr = Column(String(10), nullable=False)
    code = Column(String(15), nullable=False)
    index = Column(Integer)
    gninmb = Column(Integer, nullable=False)
    uno = Column(Integer)
    ocatd = Column(String(15), nullable=False)
    status = Column(Integer, nullable=False, server_default=u"'0'")
    parent = Column(Integer, nullable=False)
    infis = Column(String(15))
    prefix = Column(Integer, nullable=False)


class Rb64placetype(Base):
    __tablename__ = u'rb64PlaceType'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class Rb64reason(Base):
    __tablename__ = u'rb64Reason'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class Rb64streettype(Base):
    __tablename__ = u'rb64StreetType'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class Rbaptable(Base):
    __tablename__ = u'rbAPTable'

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(256), nullable=False)
    tableName = Column(String(256), nullable=False)
    masterField = Column(String(256), nullable=False)


class Rbaptablefield(Base):
    __tablename__ = u'rbAPTableField'

    id = Column(Integer, primary_key=True)
    idx = Column(Integer, nullable=False)
    master_id = Column(ForeignKey('rbAPTable.id'), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    fieldName = Column(String(256), nullable=False)
    referenceTable = Column(String(256))

    master = relationship(u'Rbaptable')


class Rbacademicdegree(Base, RBInfo):
    __tablename__ = u'rbAcademicDegree'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False)
    name = Column(Unicode(64), nullable=False)


class Rbacademictitle(Base, RBInfo):
    __tablename__ = u'rbAcademicTitle'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class Rbaccountexportformat(Base):
    __tablename__ = u'rbAccountExportFormat'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    prog = Column(String(128), nullable=False)
    preferentArchiver = Column(String(128), nullable=False)
    emailRequired = Column(Integer, nullable=False)
    emailTo = Column(String(64), nullable=False)
    subject = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)


class Rbaccountingsystem(Base, RBInfo):
    __tablename__ = u'rbAccountingSystem'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    isEditable = Column(Integer, nullable=False, server_default=u"'0'")
    showInClientInfo = Column(Integer, nullable=False, server_default=u"'0'")


class Rbacheresult(Base, RBInfo):
    __tablename__ = u'rbAcheResult'

    id = Column(Integer, primary_key=True)
    eventPurpose_id = Column(ForeignKey('rbEventTypePurpose.id'), nullable=False, index=True)
    code = Column(String(3, u'utf8_unicode_ci'), nullable=False)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)

    eventPurpose = relationship(u'Rbeventtypepurpose')


class Rbactionshedule(Base):
    __tablename__ = u'rbActionShedule'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, server_default=u"''")
    name = Column(String(64), nullable=False, server_default=u"''")
    period = Column(Integer, nullable=False, server_default=u"'1'")


class RbactionsheduleItem(Base):
    __tablename__ = u'rbActionShedule_Item'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    offset = Column(Integer, nullable=False, server_default=u"'0'")
    time = Column(Time, nullable=False, server_default=u"'00:00:00'")


class Rbactivity(Base):
    __tablename__ = u'rbActivity'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    regionalCode = Column(String(8), nullable=False, index=True)


class Rbagreementtype(Base):
    __tablename__ = u'rbAgreementType'

    id = Column(Integer, primary_key=True)
    code = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)
    quotaStatusModifier = Column(Integer, server_default=u"'0'")


class Rbanalysisstatu(Base):
    __tablename__ = u'rbAnalysisStatus'

    id = Column(Integer, primary_key=True)
    statusName = Column(String(80), nullable=False, unique=True)


class Rbanalyticalreport(Base):
    __tablename__ = u'rbAnalyticalReports'

    id = Column(Integer, primary_key=True)
    name = Column(String(45))
    PrintTemplate_id = Column(Integer)


class Rbantibiotic(Base):
    __tablename__ = u'rbAntibiotic'

    id = Column(Integer, primary_key=True)
    code = Column(String(128), nullable=False)
    name = Column(String(256), nullable=False)


class Rbattachtype(Base):
    __tablename__ = u'rbAttachType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    temporary = Column(Integer, nullable=False)
    outcome = Column(Integer, nullable=False)
    finance_id = Column(Integer, nullable=False, index=True)


class Rbbacindicator(Base):
    __tablename__ = u'rbBacIndicator'

    id = Column(Integer, primary_key=True)
    code = Column(String(128), nullable=False)
    name = Column(String(256), nullable=False)


class Rbblankaction(Base):
    __tablename__ = u'rbBlankActions'

    id = Column(Integer, primary_key=True)
    doctype_id = Column(ForeignKey('ActionType.id'), nullable=False, index=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    checkingSerial = Column(Integer, nullable=False)
    checkingNumber = Column(Integer, nullable=False)
    checkingAmount = Column(Integer, nullable=False)

    doctype = relationship(u'Actiontype')


class Rbblanktempinvalid(Base):
    __tablename__ = u'rbBlankTempInvalids'

    id = Column(Integer, primary_key=True)
    doctype_id = Column(ForeignKey('rbTempInvalidDocument.id'), nullable=False, index=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    checkingSerial = Column(Integer, nullable=False)
    checkingNumber = Column(Integer, nullable=False)
    checkingAmount = Column(Integer, nullable=False)

    doctype = relationship(u'Rbtempinvaliddocument')


class Rbbloodtype(Base, RBInfo):
    __tablename__ = u'rbBloodType'

    id = Column(Integer, primary_key=True)
    code = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)


class Rbcashoperation(Base):
    __tablename__ = u'rbCashOperation'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(64), nullable=False)


class Rbcomplain(Base):
    __tablename__ = u'rbComplain'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, index=True)
    code = Column(String(64), nullable=False, index=True)
    name = Column(String(120), nullable=False, index=True)


class Rbcontacttype(Base, RBInfo):
    __tablename__ = u'rbContactType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class Rbcoreactionproperty(Base):
    __tablename__ = u'rbCoreActionProperty'

    id = Column(Integer, primary_key=True)
    actionType_id = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False)
    actionPropertyType_id = Column(Integer, nullable=False)


class Rbcounter(Base):
    __tablename__ = u'rbCounter'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False)
    name = Column(String(64), nullable=False)
    value = Column(Integer, nullable=False, server_default=u"'0'")
    prefix = Column(String(32))
    separator = Column(String(8), server_default=u"' '")
    reset = Column(Integer, nullable=False, server_default=u"'0'")
    startDate = Column(DateTime, nullable=False)
    resetDate = Column(DateTime)
    sequenceFlag = Column(Integer, nullable=False, server_default=u"'0'")


class Rbdiagnosistype(Base):
    __tablename__ = u'rbDiagnosisType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    replaceInDiagnosis = Column(String(8), nullable=False)
    flatCode = Column(String(64), nullable=False)


class Rbdiet(Base):
    __tablename__ = u'rbDiet'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class Rbdiseasecharacter(Base):
    __tablename__ = u'rbDiseaseCharacter'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    replaceInDiagnosis = Column(String(8), nullable=False)


class Rbdiseasephase(Base):
    __tablename__ = u'rbDiseasePhases'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    characterRelation = Column(Integer, nullable=False, server_default=u"'0'")


class Rbdiseasestage(Base):
    __tablename__ = u'rbDiseaseStage'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    characterRelation = Column(Integer, nullable=False, server_default=u"'0'")


class Rbdispanser(Base, RBInfo):
    __tablename__ = u'rbDispanser'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    observed = Column(Integer, nullable=False)


class Rbdocumenttype(Base, RBInfo):
    __tablename__ = u'rbDocumentType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    regionalCode = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey('rbDocumentTypeGroup.id'), nullable=False, index=True)
    serial_format = Column(Integer, nullable=False)
    number_format = Column(Integer, nullable=False)
    federalCode = Column(String(16), nullable=False)
    socCode = Column(String(8), nullable=False, index=True)
    TFOMSCode = Column(Integer)

    group = relationship(u'Rbdocumenttypegroup')


class Rbdocumenttypegroup(Base, RBInfo):
    __tablename__ = u'rbDocumentTypeGroup'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class Rbemergencyaccident(Base):
    __tablename__ = u'rbEmergencyAccident'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencycausecall(Base):
    __tablename__ = u'rbEmergencyCauseCall'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)
    typeCause = Column(Integer, nullable=False, server_default=u"'0'")


class Rbemergencydeath(Base):
    __tablename__ = u'rbEmergencyDeath'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencydiseased(Base):
    __tablename__ = u'rbEmergencyDiseased'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencyebriety(Base):
    __tablename__ = u'rbEmergencyEbriety'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencymethodtransportation(Base):
    __tablename__ = u'rbEmergencyMethodTransportation'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencyplacecall(Base):
    __tablename__ = u'rbEmergencyPlaceCall'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencyplacereceptioncall(Base):
    __tablename__ = u'rbEmergencyPlaceReceptionCall'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencyreasonddelay(Base):
    __tablename__ = u'rbEmergencyReasondDelays'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencyreceivedcall(Base):
    __tablename__ = u'rbEmergencyReceivedCall'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencyresult(Base):
    __tablename__ = u'rbEmergencyResult'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencytransferredtransportation(Base):
    __tablename__ = u'rbEmergencyTransferredTransportation'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbemergencytypeasset(Base, RBInfo):
    __tablename__ = u'rbEmergencyTypeAsset'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class Rbeventprofile(Base):
    __tablename__ = u'rbEventProfile'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    regionalCode = Column(String(16), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class Rbeventtypepurpose(Base, RBInfo):
    __tablename__ = u'rbEventTypePurpose'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    codePlace = Column(String(2))


class Rbfinance(Base, RBInfo):
    __tablename__ = u'rbFinance'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class Rbfinance1c(Base):
    __tablename__ = u'rbFinance1C'

    id = Column(Integer, primary_key=True)
    code1C = Column(String(127), nullable=False)
    finance_id = Column(ForeignKey('rbFinance.id'), nullable=False, index=True)

    finance = relationship(u'Rbfinance')


class Rbhealthgroup(Base):
    __tablename__ = u'rbHealthGroup'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class Rbhospitalbedprofile(Base, RBInfo):
    __tablename__ = u'rbHospitalBedProfile'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    service_id = Column(Integer, index=True)


class RbhospitalbedprofileService(Base):
    __tablename__ = u'rbHospitalBedProfile_Service'

    id = Column(Integer, primary_key=True)
    rbHospitalBedProfile_id = Column(ForeignKey('rbHospitalBedProfile.id'), nullable=False, index=True)
    rbService_id = Column(ForeignKey('rbService.id'), nullable=False, index=True)

    rbHospitalBedProfile = relationship(u'Rbhospitalbedprofile')
    rbService = relationship(u'Rbservice')


class Rbhospitalbedshedule(Base, RBInfo):
    __tablename__ = u'rbHospitalBedShedule'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class Rbhospitalbedtype(Base, RBInfo):
    __tablename__ = u'rbHospitalBedType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class Rbhurtfactortype(Base):
    __tablename__ = u'rbHurtFactorType'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(250), nullable=False, index=True)


class Rbhurttype(Base, RBInfo):
    __tablename__ = u'rbHurtType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(256), nullable=False, index=True)


class Rbimagemap(Base):
    __tablename__ = u'rbImageMap'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False)
    name = Column(String(64), nullable=False)
    image = Column(MEDIUMBLOB, nullable=False)
    markSize = Column(Integer)


class Rbjobtype(Base):
    __tablename__ = u'rbJobType'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, index=True)
    code = Column(String(64), nullable=False)
    regionalCode = Column(String(64), nullable=False)
    name = Column(String(128), nullable=False)
    laboratory_id = Column(Integer, index=True)
    isInstant = Column(Integer, nullable=False, server_default=u"'0'")


class Rblaboratory(Base):
    __tablename__ = u'rbLaboratory'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    protocol = Column(Integer, nullable=False)
    address = Column(String(128), nullable=False)
    ownName = Column(String(128), nullable=False)
    labName = Column(String(128), nullable=False)


class RblaboratoryTest(Base):
    __tablename__ = u'rbLaboratory_Test'
    __table_args__ = (
        Index(u'code', u'book', u'code'),
    )

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    test_id = Column(Integer, nullable=False, index=True)
    book = Column(String(64), nullable=False)
    code = Column(String(64), nullable=False)


class Rbmkbsubclas(Base):
    __tablename__ = u'rbMKBSubclass'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False)
    name = Column(String(128), nullable=False)


class RbmkbsubclassItem(Base):
    __tablename__ = u'rbMKBSubclass_Item'
    __table_args__ = (
        Index(u'master_id', u'master_id', u'code'),
    )

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False)
    code = Column(String(8), nullable=False)
    name = Column(String(128), nullable=False)


class Rbmealtime(Base):
    __tablename__ = u'rbMealTime'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    begTime = Column(Time, nullable=False)
    endTime = Column(Time, nullable=False)


class Rbmedicalaidprofile(Base):
    __tablename__ = u'rbMedicalAidProfile'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    regionalCode = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)


class Rbmedicalaidtype(Base):
    __tablename__ = u'rbMedicalAidType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False)


class Rbmedicalaidunit(Base):
    __tablename__ = u'rbMedicalAidUnit'

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    descr = Column(String(64), nullable=False)
    regionalCode = Column(String(1), nullable=False)


class Rbmedicalkind(Base):
    __tablename__ = u'rbMedicalKind'

    id = Column(Integer, primary_key=True)
    code = Column(String(1, u'utf8_unicode_ci'), nullable=False)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)


class Rbmenu(Base):
    __tablename__ = u'rbMenu'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class RbmenuContent(Base):
    __tablename__ = u'rbMenu_Content'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    mealTime_id = Column(Integer, nullable=False, index=True)
    diet_id = Column(Integer, nullable=False, index=True)


class Rbmesspecification(Base):
    __tablename__ = u'rbMesSpecification'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    regionalCode = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    done = Column(Integer, nullable=False)


class Rbmethodofadministration(Base):
    __tablename__ = u'rbMethodOfAdministration'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class Rbmicroorganism(Base):
    __tablename__ = u'rbMicroorganism'

    id = Column(Integer, primary_key=True)
    code = Column(String(128), nullable=False)
    name = Column(String(256), nullable=False)


class Rbnet(Base, RBInfo):
    __tablename__ = u'rbNet'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    sex = Column(Integer, nullable=False, server_default=u"'0'")
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)


class Rbnomenclature(Base):
    __tablename__ = u'rbNomenclature'

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    code = Column(String(64), nullable=False)
    regionalCode = Column(String(64), nullable=False)
    name = Column(String(128), nullable=False)

    group = relationship(u'Rbnomenclature', remote_side=[id])


class Rbokfs(Base, RBInfo):
    __tablename__ = u'rbOKFS'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    ownership = Column(Integer, nullable=False, server_default=u"'0'")


class Rbokpf(Base, RBInfo):
    __tablename__ = u'rbOKPF'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class Rbokved(Base):
    __tablename__ = u'rbOKVED'

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, index=True)
    div = Column(String(10), nullable=False)
    class_ = Column(u'class', String(2), nullable=False)
    group_ = Column(String(2), nullable=False)
    vid = Column(String(2), nullable=False)
    OKVED = Column(String(8), nullable=False, index=True)
    name = Column(String(250), nullable=False, index=True)


class Rboperationtype(Base):
    __tablename__ = u'rbOperationType'

    id = Column(Integer, primary_key=True)
    cd_r = Column(Integer, nullable=False)
    cd_subr = Column(Integer, nullable=False)
    code = Column(String(8), nullable=False, index=True)
    ktso = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False, index=True)


class Rbpacientmodel(Base, RBInfo):
    __tablename__ = u'rbPacientModel'

    id = Column(Integer, primary_key=True)
    code = Column(String(32), nullable=False)
    name = Column(Text, nullable=False)
    quotaType_id = Column(ForeignKey('QuotaType.id'), nullable=False, index=True)

    quotaType = relationship(u'Quotatype')


class Rbpayrefusetype(Base):
    __tablename__ = u'rbPayRefuseType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    finance_id = Column(Integer, nullable=False, index=True)
    rerun = Column(Integer, nullable=False)


class Rbpaytype(Base):
    __tablename__ = u'rbPayType'

    id = Column(Integer, primary_key=True)
    code = Column(String(2, u'utf8_unicode_ci'), nullable=False)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)


class Rbpolicytype(Base, RBInfo):
    __tablename__ = u'rbPolicyType'

    id = Column(Integer, primary_key=True)
    code = Column(String(64), nullable=False, unique=True)
    name = Column(Unicode(256), nullable=False, index=True)
    TFOMSCode = Column(String(8))


class Rbpost(Base, RBInfo):
    __tablename__ = u'rbPost'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    regionalCode = Column(String(8), nullable=False)
    key = Column(String(6), nullable=False, index=True)
    high = Column(String(6), nullable=False)
    flatCode = Column(String(65), nullable=False)


class Rbprinttemplate(Base):
    __tablename__ = u'rbPrintTemplate'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    context = Column(String(64), nullable=False)
    fileName = Column(String(128), nullable=False)
    default = Column(String, nullable=False)
    dpdAgreement = Column(Integer, nullable=False, server_default=u"'0'")
    render = Column(Integer, nullable=False, server_default=u"'0'")


class Rbquotastatu(Base):
    __tablename__ = u'rbQuotaStatus'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(50), nullable=False, index=True)


class Rbreasonofabsence(Base, RBInfo):
    __tablename__ = u'rbReasonOfAbsence'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class Rbrelationtype(Base, RBInfo):
    __tablename__ = u'rbRelationType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    leftName = Column(String(64), nullable=False)
    rightName = Column(String(64), nullable=False)
    isDirectGenetic = Column(Integer, nullable=False, server_default=u"'0'")
    isBackwardGenetic = Column(Integer, nullable=False, server_default=u"'0'")
    isDirectRepresentative = Column(Integer, nullable=False, server_default=u"'0'")
    isBackwardRepresentative = Column(Integer, nullable=False, server_default=u"'0'")
    isDirectEpidemic = Column(Integer, nullable=False, server_default=u"'0'")
    isBackwardEpidemic = Column(Integer, nullable=False, server_default=u"'0'")
    isDirectDonation = Column(Integer, nullable=False, server_default=u"'0'")
    isBackwardDonation = Column(Integer, nullable=False, server_default=u"'0'")
    leftSex = Column(Integer, nullable=False, server_default=u"'0'")
    rightSex = Column(Integer, nullable=False, server_default=u"'0'")
    regionalCode = Column(String(64), nullable=False)
    regionalReverseCode = Column(String(64), nullable=False)


class Rbrequesttype(Base, RBInfo):
    __tablename__ = u'rbRequestType'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    relevant = Column(Integer, nullable=False, server_default=u"'1'")


class Rbresult(Base, RBInfo):
    __tablename__ = u'rbResult'

    id = Column(Integer, primary_key=True)
    eventPurpose_id = Column(Integer, nullable=False, index=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    continued = Column(Integer, nullable=False)
    regionalCode = Column(String(8), nullable=False)


class Rbscene(Base):
    __tablename__ = u'rbScene'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    serviceModifier = Column(String(128), nullable=False)


class Rbservice(Base, RBInfo):
    __tablename__ = u'rbService'
    __table_args__ = (
        Index(u'infis', u'infis', u'eisLegacy'),
        Index(u'group_id_idx', u'group_id', u'idx')
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(31), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    eisLegacy = Column(Boolean, nullable=False)
    nomenclatureLegacy = Column(Integer, nullable=False, server_default=u"'0'")
    license = Column(Boolean, nullable=False)
    infis = Column(String(31), nullable=False)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    medicalAidProfile_id = Column(ForeignKey('rbMedicalAidProfile.id'), index=True)
    adultUetDoctor = Column(Float(asdecimal=True), server_default=u"'0'")
    adultUetAverageMedWorker = Column(Float(asdecimal=True), server_default=u"'0'")
    childUetDoctor = Column(Float(asdecimal=True), server_default=u"'0'")
    childUetAverageMedWorker = Column(Float(asdecimal=True), server_default=u"'0'")
    rbMedicalKind_id = Column(ForeignKey('rbMedicalKind.id'), index=True)
    UET = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    departCode = Column(String(3))
    group_id = Column(ForeignKey('rbService.id'))
    idx = Column(Integer, nullable=False, server_default=u"'0'")

    group = relationship(u'Rbservice', remote_side=[id])
    medicalAidProfile = relationship(u'Rbmedicalaidprofile')
    rbMedicalKind = relationship(u'Rbmedicalkind')


class Rbserviceclas(Base):
    __tablename__ = u'rbServiceClass'
    __table_args__ = (
        Index(u'section', u'section', u'code'),
    )

    id = Column(Integer, primary_key=True)
    section = Column(String(1), nullable=False)
    code = Column(String(3), nullable=False)
    name = Column(String(200), nullable=False)


class Rbservicefinance(Base):
    __tablename__ = u'rbServiceFinance'

    id = Column(Integer, primary_key=True)
    code = Column(String(2, u'utf8_unicode_ci'), nullable=False)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)


class Rbservicegroup(Base):
    __tablename__ = u'rbServiceGroup'
    __table_args__ = (
        Index(u'group_id', u'group_id', u'service_id'),
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, nullable=False)
    service_id = Column(Integer, nullable=False)
    required = Column(Integer, nullable=False, server_default=u"'0'")


class Rbservicesection(Base):
    __tablename__ = u'rbServiceSection'

    id = Column(Integer, primary_key=True)
    code = Column(String(1), nullable=False)
    name = Column(String(100), nullable=False)


class Rbservicetype(Base):
    __tablename__ = u'rbServiceType'
    __table_args__ = (
        Index(u'section', u'section', u'code'),
    )

    id = Column(Integer, primary_key=True)
    section = Column(String(1), nullable=False)
    code = Column(String(3), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)


class Rbserviceuet(Base):
    __tablename__ = u'rbServiceUET'

    id = Column(Integer, primary_key=True)
    rbService_id = Column(ForeignKey('rbService.id'), nullable=False, index=True)
    age = Column(String(10, u'utf8_unicode_ci'), nullable=False)
    UET = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")

    rbService = relationship(u'Rbservice')


class RbserviceProfile(Base):
    __tablename__ = u'rbService_Profile'
    __table_args__ = (
        Index(u'id', u'id', u'idx'),
    )

    id = Column(Integer, primary_key=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(ForeignKey('rbService.id'), nullable=False, index=True)
    speciality_id = Column(ForeignKey('rbSpeciality.id'), index=True)
    sex = Column(Integer, nullable=False, server_default=u"'0'")
    age = Column(String(9), nullable=False, server_default=u"''")
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    mkbRegExp = Column(String(64), nullable=False, server_default=u"''")
    medicalAidProfile_id = Column(ForeignKey('rbMedicalAidProfile.id'), index=True)

    master = relationship(u'Rbservice')
    medicalAidProfile = relationship(u'Rbmedicalaidprofile')
    speciality = relationship(u'Rbspeciality')


class Rbsocstatusclass(Base, Info):
    __tablename__ = u'rbSocStatusClass'

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('rbSocStatusClass.id'), index=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)

    group = relationship(u'Rbsocstatusclass', remote_side=[id])

    def __unicode__(self):
        return self.name

# class Rbsocstatusclasstypeassoc(Base):
#     __tablename__ = u'rbSocStatusClassTypeAssoc'
#     __table_args__ = (
#         Index(u'type_id', u'type_id', u'class_id'),
#     )
#
#     id = Column(Integer, primary_key=True)
#     class_id = Column(Integer, ForeignKey('rbSocStatusClass.id'), nullable=False, index=True)
#     type_id = Column(Integer, ForeignKey('rbSocStatusType.id'), nullable=False)
Rbsocstatusclasstypeassoc = Table('rbSocStatusClassTypeAssoc', Base.metadata,
    Column('class_id', Integer, ForeignKey('rbSocStatusClass.id')),
    Column('type_id', Integer, ForeignKey('rbSocStatusType.id'))
    )


class Rbsocstatustype(Base, Info):
    __tablename__ = u'rbSocStatusType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(250), nullable=False, index=True)
    socCode = Column(String(8), nullable=False, index=True)
    TFOMSCode = Column(Integer)
    regionalCode = Column(String(8), nullable=False)

    classes = relationship(u'Rbsocstatusclass', secondary=Rbsocstatusclasstypeassoc)


class Rbspecialvariablespreference(Base):
    __tablename__ = u'rbSpecialVariablesPreferences'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    query = Column(Text, nullable=False)


class Rbspeciality(Base, RBInfo):
    __tablename__ = u'rbSpeciality'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    OKSOName = Column(Unicode(60), nullable=False)
    OKSOCode = Column(String(8), nullable=False)
    service_id = Column(Integer, index=True)
    sex = Column(Integer, nullable=False)
    age = Column(String(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)
    mkbFilter = Column(String(32), nullable=False)
    regionalCode = Column(String(16), nullable=False)
    quotingEnabled = Column(Integer, server_default=u"'0'")


class Rbstorage(Base):
    __tablename__ = u'rbStorage'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(50), nullable=False, unique=True)
    name = Column(String(256))
    orgStructure_id = Column(ForeignKey('OrgStructure.id'), index=True)

    orgStructure = relationship(u'Orgstructure')


class Rbtariffcategory(Base, RBInfo):
    __tablename__ = u'rbTariffCategory'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class Rbtarifftype(Base):
    __tablename__ = u'rbTariffType'

    id = Column(Integer, primary_key=True)
    code = Column(String(2, u'utf8_unicode_ci'), nullable=False)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)


class Rbtempinvalidbreak(Base):
    __tablename__ = u'rbTempInvalidBreak'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False, server_default=u"'0'")
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(80), nullable=False, index=True)


class Rbtempinvaliddocument(Base):
    __tablename__ = u'rbTempInvalidDocument'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(80), nullable=False, index=True)
    checkingSerial = Column(Enum(u'???', u'?????', u'??????'), nullable=False)
    checkingNumber = Column(Enum(u'???', u'?????', u'??????'), nullable=False)
    checkingAmount = Column(Enum(u'???', u'????????'), nullable=False)


class Rbtempinvalidduplicatereason(Base):
    __tablename__ = u'rbTempInvalidDuplicateReason'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False)


class Rbtempinvalidreason(Base):
    __tablename__ = u'rbTempInvalidReason'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False, server_default=u"'0'")
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    requiredDiagnosis = Column(Integer, nullable=False)
    grouping = Column(Integer, nullable=False)
    primary = Column(Integer, nullable=False)
    prolongate = Column(Integer, nullable=False)
    restriction = Column(Integer, nullable=False)
    regionalCode = Column(String(3), nullable=False)


class Rbtempinvalidregime(Base):
    __tablename__ = u'rbTempInvalidRegime'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False, server_default=u"'0'")
    doctype_id = Column(Integer, index=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class Rbtempinvalidresult(Base):
    __tablename__ = u'rbTempInvalidResult'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False, server_default=u"'0'")
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(80), nullable=False, index=True)
    able = Column(Integer, nullable=False)
    closed = Column(Integer, nullable=False, server_default=u"'0'")
    status = Column(Integer, nullable=False)


class Rbtest(Base):
    __tablename__ = u'rbTest'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")


class Rbtesttubetype(Base):
    __tablename__ = u'rbTestTubeType'

    id = Column(Integer, primary_key=True)
    code = Column(String(64))
    name = Column(String(128), nullable=False)
    volume = Column(Float(asdecimal=True), nullable=False)
    unit_id = Column(ForeignKey('rbUnit.id'), nullable=False, index=True)
    covCol = Column(String(64))
    image = Column(MEDIUMBLOB)
    color = Column(String(8))

    unit = relationship(u'Rbunit')


class Rbthesauru(Base):
    __tablename__ = u'rbThesaurus'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, index=True)
    code = Column(String(30), nullable=False, index=True)
    name = Column(String(255), nullable=False, server_default=u"''")
    template = Column(String(255), nullable=False, server_default=u"''")


class Rbtimequotingtype(Base):
    __tablename__ = u'rbTimeQuotingType'

    id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=False, unique=True)
    name = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)


class Rbtissuetype(Base, RBInfo):
    __tablename__ = u'rbTissueType'

    id = Column(Integer, primary_key=True)
    code = Column(String(64), nullable=False)
    name = Column(String(128), nullable=False)
    group_id = Column(ForeignKey('rbTissueType.id'), index=True)
    sexCode = Column("sex", Integer, nullable=False, server_default=u"'0'")

    group = relationship(u'Rbtissuetype', remote_side=[id])

    @property
    def sex(self):
        return {0: u'Любой',
                1: u'М',
                2: u'Ж'}[self.sexCode]


class Rbtransferdatetype(Base):
    __tablename__ = u'rbTransferDateType'

    id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=False, unique=True)
    name = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)


class Rbtraumatype(Base):
    __tablename__ = u'rbTraumaType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class Rbtreatment(Base, RBInfo):
    __tablename__ = u'rbTreatment'

    id = Column(Integer, primary_key=True)
    code = Column(String(32), nullable=False)
    name = Column(Text, nullable=False)
    pacientModel_id = Column(ForeignKey('rbPacientModel.id'), nullable=False, index=True)

    pacientModel = relationship(u'Rbpacientmodel')


class Rbtrfubloodcomponenttype(Base):
    __tablename__ = u'rbTrfuBloodComponentType'

    id = Column(Integer, primary_key=True)
    trfu_id = Column(Integer)
    code = Column(String(32))
    name = Column(String(256))
    unused = Column(Integer, nullable=False, server_default=u"'0'")


class Rbtrfulaboratorymeasuretype(Base):
    __tablename__ = u'rbTrfuLaboratoryMeasureTypes'

    id = Column(Integer, primary_key=True)
    trfu_id = Column(Integer)
    name = Column(String(255))


class Rbtrfuproceduretype(Base):
    __tablename__ = u'rbTrfuProcedureTypes'

    id = Column(Integer, primary_key=True)
    trfu_id = Column(Integer)
    name = Column(String(255))
    unused = Column(Integer, nullable=False, server_default=u"'0'")


class Rbufm(Base):
    __tablename__ = u'rbUFMS'

    id = Column(Integer, primary_key=True)
    code = Column(String(50, u'utf8_bin'), nullable=False)
    name = Column(String(256, u'utf8_bin'), nullable=False)


class Rbunit(Base, RBInfo):
    __tablename__ = u'rbUnit'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(256), index=True)
    name = Column(Unicode(256), index=True)


class Rbuserprofile(Base):
    __tablename__ = u'rbUserProfile'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    withDep = Column(Integer, nullable=False, server_default=u"'0'")


class RbuserprofileRight(Base):
    __tablename__ = u'rbUserProfile_Right'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    userRight_id = Column(Integer, nullable=False, index=True)


class Rbuserright(Base):
    __tablename__ = u'rbUserRight'

    id = Column(Integer, primary_key=True)
    code = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)


class Rbvisittype(Base):
    __tablename__ = u'rbVisitType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    serviceModifier = Column(String(128), nullable=False)


class RbF001Tfom(Base):
    __tablename__ = u'rb_F001_Tfoms'

    tf_kod = Column(String(255), primary_key=True)
    address = Column(String(255))
    d_edit = Column(Date)
    d_end = Column(Date)
    e_mail = Column(String(255))
    fam_dir = Column(String(255))
    fax = Column(String(255))
    idx = Column(String(255))
    im_dir = Column(String(255))
    kf_tf = Column(BigInteger)
    name_tfk = Column(String(255))
    name_tfp = Column(String(255))
    ot_dir = Column(String(255))
    phone = Column(String(255))
    tf_ogrn = Column(String(255))
    tf_okato = Column(String(255))
    www = Column(String(255))


class RbF002Smo(Base):
    __tablename__ = u'rb_F002_SMO'

    smocod = Column(String(255), primary_key=True)
    addr_f = Column(String(255))
    addr_j = Column(String(255))
    d_begin = Column(Date)
    d_edit = Column(Date)
    d_end = Column(Date)
    d_start = Column(Date)
    data_e = Column(Date)
    duved = Column(Date)
    e_mail = Column(String(255))
    fam_ruk = Column(String(255))
    fax = Column(String(255))
    im_ruk = Column(String(255))
    index_f = Column(String(255))
    index_j = Column(String(255))
    inn = Column(String(255))
    kol_zl = Column(BigInteger)
    kpp = Column(String(255))
    n_doc = Column(String(255))
    nal_p = Column(String(255))
    nam_smok = Column(String(255))
    nam_smop = Column(String(255))
    name_e = Column(String(255))
    ogrn = Column(String(255))
    okopf = Column(String(255))
    org = Column(BigInteger)
    ot_ruk = Column(String(255))
    phone = Column(String(255))
    tf_okato = Column(String(255))
    www = Column(String(255))


class RbF003Mo(Base):
    __tablename__ = u'rb_F003_MO'

    mcod = Column(String(255), primary_key=True)
    addr_j = Column(String(255))
    d_begin = Column(Date)
    d_edit = Column(Date)
    d_end = Column(Date)
    d_start = Column(Date)
    data_e = Column(Date)
    duved = Column(Date)
    e_mail = Column(String(255))
    fam_ruk = Column(String(255))
    fax = Column(String(255))
    im_ruk = Column(String(255))
    index_j = Column(String(255))
    inn = Column(String(255))
    kpp = Column(String(255))
    lpu = Column(Integer)
    mp = Column(String(255))
    n_doc = Column(String(255))
    nam_mok = Column(String(255))
    nam_mop = Column(String(255))
    name_e = Column(String(255))
    ogrn = Column(String(255))
    okopf = Column(String(255))
    org = Column(BigInteger)
    ot_ruk = Column(String(255))
    phone = Column(String(255))
    tf_okato = Column(String(255))
    vedpri = Column(BigInteger)
    www = Column(String(255))


class RbF007Vedom(Base):
    __tablename__ = u'rb_F007_Vedom'

    idved = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    vedname = Column(String(255))


class RbF008Tipom(Base):
    __tablename__ = u'rb_F008_TipOMS'

    iddoc = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    docname = Column(String(255))


class RbF009Statzl(Base):
    __tablename__ = u'rb_F009_StatZL'

    idstatus = Column(String(255), primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    statusname = Column(String(255))


class RbF010Subekti(Base):
    __tablename__ = u'rb_F010_Subekti'

    kod_tf = Column(String(255), primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    kod_okato = Column(String(255))
    okrug = Column(BigInteger)
    subname = Column(String(255))


class RbF011Tipdoc(Base):
    __tablename__ = u'rb_F011_Tipdoc'

    iddoc = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    docname = Column(String(255))
    docnum = Column(String(255))
    docser = Column(String(255))


class RbF015Fedokr(Base):
    __tablename__ = u'rb_F015_FedOkr'

    kod_ok = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    okrname = Column(String(255))


class RbKladr(Base):
    __tablename__ = u'rb_Kladr'

    code = Column(String(255), primary_key=True)
    gninmb = Column(String(255))
    idx = Column(String(255))
    name = Column(String(255))
    ocatd = Column(String(255))
    socr = Column(String(255))
    status = Column(String(255))
    uno = Column(String(255))


class RbKladrstreet(Base):
    __tablename__ = u'rb_KladrStreet'

    code = Column(String(255), primary_key=True)
    gninmb = Column(String(255))
    idx = Column(String(255))
    name = Column(String(255))
    ocatd = Column(String(255))
    socr = Column(String(255))
    uno = Column(String(255))


class RbM001Mkb10(Base):
    __tablename__ = u'rb_M001_MKB10'

    idds = Column(String(255), primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    dsname = Column(String(255))


class RbO001Oksm(Base):
    __tablename__ = u'rb_O001_Oksm'

    kod = Column(String(255), primary_key=True)
    alfa2 = Column(String(255))
    alfa3 = Column(String(255))
    data_upd = Column(Date)
    name11 = Column(String(255))
    name12 = Column(String(255))
    nomakt = Column(String(255))
    nomdescr = Column(String(255))
    status = Column(BigInteger)


class RbO002Okato(Base):
    __tablename__ = u'rb_O002_Okato'

    ter = Column(String(255), primary_key=True)
    centrum = Column(String(255))
    data_upd = Column(Date)
    kod1 = Column(String(255))
    kod2 = Column(String(255))
    kod3 = Column(String(255))
    name1 = Column(String(255))
    nomakt = Column(String(255))
    nomdescr = Column(String(255))
    razdel = Column(String(255))
    status = Column(BigInteger)


class RbO003Okved(Base):
    __tablename__ = u'rb_O003_Okved'

    kod = Column(String(255), primary_key=True)
    data_upd = Column(Date)
    name11 = Column(String(255))
    name12 = Column(String(255))
    nomakt = Column(String(255))
    nomdescr = Column(String(255))
    prazdel = Column(String(255))
    razdel = Column(String(255))
    status = Column(BigInteger)


class RbO004Okf(Base):
    __tablename__ = u'rb_O004_Okfs'

    kod = Column(String(255), primary_key=True)
    alg = Column(String(255))
    data_upd = Column(Date)
    name1 = Column(String(255))
    nomakt = Column(String(255))
    status = Column(BigInteger)


class RbO005Okopf(Base):
    __tablename__ = u'rb_O005_Okopf'

    kod = Column(String(255), primary_key=True)
    alg = Column(String(255))
    data_upd = Column(Date)
    name1 = Column(String(255))
    nomakt = Column(String(255))
    status = Column(BigInteger)


class RbV001Nomerclr(Base):
    __tablename__ = u'rb_V001_Nomerclr'

    idrb = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    rbname = Column(String(255))


class RbV002Profot(Base):
    __tablename__ = u'rb_V002_ProfOt'

    idpr = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    prname = Column(String(255))


class RbV003Licusl(Base):
    __tablename__ = u'rb_V003_LicUsl'

    idrl = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    ierarh = Column(BigInteger)
    licname = Column(String(255))
    prim = Column(BigInteger)


class RbV004Medspec(Base):
    __tablename__ = u'rb_V004_Medspec'

    idmsp = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    mspname = Column(String(255))


class RbV005Pol(Base):
    __tablename__ = u'rb_V005_Pol'

    idpol = Column(BigInteger, primary_key=True)
    polname = Column(String(255))


class RbV006Uslmp(Base):
    __tablename__ = u'rb_V006_UslMp'

    idump = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    umpname = Column(String(255))


class RbV007Nommo(Base):
    __tablename__ = u'rb_V007_NomMO'

    idnmo = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    nmoname = Column(String(255))


class RbV008Vidmp(Base):
    __tablename__ = u'rb_V008_VidMp'

    idvmp = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    vmpname = Column(String(255))


class RbV009Rezult(Base):
    __tablename__ = u'rb_V009_Rezult'

    idrmp = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    iduslov = Column(BigInteger)
    rmpname = Column(String(255))


class RbV010Sposob(Base):
    __tablename__ = u'rb_V010_Sposob'

    idsp = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    spname = Column(String(255))


class RbV012Ishod(Base):
    __tablename__ = u'rb_V012_Ishod'

    idiz = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    iduslov = Column(BigInteger)
    izname = Column(String(255))


class Rdfirstname(Base):
    __tablename__ = u'rdFirstName'
    __table_args__ = (
        Index(u'sex', u'sex', u'name'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, index=True)
    sex = Column(Integer, nullable=False)


class Rdpolis(Base):
    __tablename__ = u'rdPOLIS_S'

    id = Column(Integer, primary_key=True)
    CODE = Column(String(10), nullable=False, index=True)
    PAYER = Column(String(5), nullable=False)
    TYPEINS = Column(String(1), nullable=False)


class Rdpatrname(Base):
    __tablename__ = u'rdPatrName'
    __table_args__ = (
        Index(u'sex', u'sex', u'name'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, index=True)
    sex = Column(Integer, nullable=False)


class Rlsactmatter(Base):
    __tablename__ = u'rlsActMatters'
    __table_args__ = (
        Index(u'name_localName', u'name', u'localName'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    localName = Column(String(255))


class Rlsbalanceofgood(Base):
    __tablename__ = u'rlsBalanceOfGoods'

    id = Column(Integer, primary_key=True)
    rlsNomen_id = Column(ForeignKey('rlsNomen.id'), nullable=False, index=True)
    value = Column(Float(asdecimal=True), nullable=False)
    bestBefore = Column(Date, nullable=False)
    disabled = Column(Integer, nullable=False, server_default=u"'0'")
    updateDateTime = Column(DateTime)
    storage_id = Column(ForeignKey('rbStorage.id'), index=True)

    rlsNomen = relationship(u'Rlsnoman')
    storage = relationship(u'Rbstorage')


class Rlsfilling(Base):
    __tablename__ = u'rlsFilling'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)


class Rlsform(Base):
    __tablename__ = u'rlsForm'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)


class Rlsnoman(Base):
    __tablename__ = u'rlsNomen'

    id = Column(Integer, primary_key=True)
    actMatters_id = Column(ForeignKey('rlsActMatters.id'), index=True)
    tradeName_id = Column(ForeignKey('rlsTradeName.id'), nullable=False, index=True)
    form_id = Column(ForeignKey('rlsForm.id'), index=True)
    packing_id = Column(ForeignKey('rlsPacking.id'), index=True)
    filling_id = Column(ForeignKey('rlsFilling.id'), index=True)
    unit_id = Column(ForeignKey('rbUnit.id'), index=True)
    dosageValue = Column(String(128))
    dosageUnit_id = Column(ForeignKey('rbUnit.id'), index=True)
    drugLifetime = Column(Integer)
    regDate = Column(Date)
    annDate = Column(Date)

    actMatters = relationship(u'Rlsactmatter')
    dosageUnit = relationship(u'Rbunit', primaryjoin='Rlsnoman.dosageUnit_id == Rbunit.id')
    filling = relationship(u'Rlsfilling')
    form = relationship(u'Rlsform')
    packing = relationship(u'Rlspacking')
    tradeName = relationship(u'Rlstradename')
    unit = relationship(u'Rbunit', primaryjoin='Rlsnoman.unit_id == Rbunit.id')


class Rlspacking(Base):
    __tablename__ = u'rlsPacking'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)


class Rlspharmgroup(Base):
    __tablename__ = u'rlsPharmGroup'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    code = Column(String(8))
    name = Column(String(128))
    path = Column(String(128))
    pathx = Column(String(128))
    nameRaw = Column(String(128), index=True)


class Rlspharmgrouptocode(Base):
    __tablename__ = u'rlsPharmGroupToCode'

    rlsPharmGroup_id = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    code = Column(Integer, primary_key=True, nullable=False, index=True, server_default=u"'0'")


class Rlstradename(Base):
    __tablename__ = u'rlsTradeName'
    __table_args__ = (
        Index(u'name_localName', u'name', u'localName'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    localName = Column(String(255))


class Trfuorderissueresult(Base):
    __tablename__ = u'trfuOrderIssueResult'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    trfu_blood_comp = Column(Integer)
    comp_number = Column(String(40))
    comp_type_id = Column(ForeignKey('rbTrfuBloodComponentType.id'), index=True)
    blood_type_id = Column(ForeignKey('rbBloodType.id'), index=True)
    volume = Column(Integer)
    dose_count = Column(Float(asdecimal=True))
    trfu_donor_id = Column(Integer)

    action = relationship(u'Action')
    blood_type = relationship(u'Rbbloodtype')
    comp_type = relationship(u'Rbtrfubloodcomponenttype')


class v_Client_Quoting(Base):
    __tablename__ = u'vClient_Quoting'

    quotaId = Column(u'id', Integer, primary_key=True)
    createDatetime = Column(u'createDatetime', DateTime)
    createPerson_id = Column(u'createPerson_id', Integer)
    modifyDatetime = Column(u'modifyDatetime', DateTime)
    modifyPerson_id = Column(u'modifyPerson_id', Integer)
    deleted = Column(u'deleted', Integer, server_default=u"'0'")
    clientId = Column(u'master_id', Integer, ForeignKey("Client.id"))
    identifier = Column(u'identifier', String(16))
    quotaTicket = Column(u'quotaTicket', String(20))
    quotaType_id = Column(u'quotaType_id', Integer, ForeignKey("QuotaType.id"))
    stage = Column(u'stage', Integer)
    directionDate = Column(u'directionDate', DateTime)
    freeInput = Column(u'freeInput', String(128))
    org_id = Column(u'org_id', Integer, ForeignKey("Organisation.id"))
    amount = Column(u'amount', Integer, server_default=u"'0'")
    MKB = Column(u'MKB', String(8))
    status = Column(u'status', Integer, server_default=u"'0'")
    request = Column(u'request', Integer, server_default=u"'0'")
    statment = Column(u'statment', String(255))
    dateRegistration = Column(u'dateRegistration', DateTime)
    dateEnd = Column(u'dateEnd', DateTime)
    orgStructure_id = Column(u'orgStructure_id', Integer, ForeignKey("OrgStructure.id"))
    regionCode = Column(u'regionCode', String(13))
    pacientModel_id = Column(u'pacientModel_id', Integer, ForeignKey("rbPacientModel.id"))
    treatment_id = Column(u'treatment_id', Integer, ForeignKey("rbTreatment.id"))
    event_id = Column(u'event_id', Integer, ForeignKey("Event.id"))
    prevTalon_event_id = Column(u'prevTalon_event_id', Integer)

    quotaType = relationship(u"Quotatype")
    organisation = relationship(u"Organisation")
    orgstructure = relationship(u"Orgstructure")
    pacientModel = relationship(u"Rbpacientmodel")
    treatment = relationship(u"Rbtreatment")


def trim(s):
    return u' '.join(unicode(s).split())


def formatShortNameInt(lastName, firstName, patrName):
    return trim(lastName + ' ' + ((firstName[:1]+'.') if firstName else '') + ((patrName[:1]+'.') if patrName else ''))


def formatNameInt(lastName, firstName, patrName):
    return trim(lastName+' '+firstName+' '+patrName)


def code128C(barcode):
    """Make Code 128C of integer barcode (100000 - 999999)"""
    b_struct = struct.Struct(">BBBBBB")
    if not (100000 <= barcode <= 999999):
        # Этого не должно случиться.
        return None
    # Стартовый и стоповый символы в нашей таблице символов имеют иные коды (+64)
    start = 0xcd
    stop = 0xce
    c, c3 = divmod(barcode, 100)
    c, c2 = divmod(c, 100)
    c, c1 = divmod(c, 100)
    cs = reduce(lambda x, (y, c): (x + y*c) % 103, [(c1, 1), (c2, 2), (c3, 3)], 2)
    # Транслируем коды символов
    c1, c2, c3, cs = tuple(map(lambda w: w + 100 if w > 94 else w + 32, (c1, c2, c3, cs)))
    barcode_char = b_struct.pack(start, c1, c2, c3, cs, stop)
    return barcode_char