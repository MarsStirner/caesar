# -*- coding: utf-8 -*-

import calendar
import jinja2
import requests
import datetime

from collections import defaultdict

from flask.ext.login import current_user
from werkzeug.utils import cached_property
from flask import g
from sqlalchemy import Column, Integer, String, Unicode, DateTime, ForeignKey, Date, Float, or_, Boolean, Text, \
    SmallInteger, Time, Index, BigInteger, Enum, Table, BLOB, UnicodeText
from sqlalchemy.orm import relationship, backref, reconstructor

from nemesis.lib.vesta_props import VestaProperty
from nemesis.models.enums import AllergyPower
from ..config import MODULE_NAME
from ..lib.html import convenience_HtmlRip, replace_first_paragraph
from ..lib.num_to_text_converter import NumToTextConverter
from models_utils import DateTimeInfo, formatNameInt, formatShortNameInt, code128C, formatSex, \
    DummyProperty, DateInfo, Query, formatMonthsWeeks, formatDays, formatYears, formatYearsMonths, TimeInfo, \
    get_model_by_name, calcAgeTuple
from caesar.blueprints.print_subsystem.models.rbinfo import Info, RBInfo
from kladr_models import Kladr, Street
from ..database import Base, metadata
from sqlalchemy.dialects.mysql.base import MEDIUMBLOB
from nemesis.lib.const import (STATIONARY_EVENT_CODES, DIAGNOSTIC_EVENT_CODES, POLICLINIC_EVENT_CODES,
    PAID_EVENT_CODE, OMS_EVENT_CODE, DMS_EVENT_CODE, BUDGET_EVENT_CODE, DAY_HOSPITAL_CODE)


TABLE_PREFIX = MODULE_NAME


class ConfigVariables(Base):
    __bind_key__ = 'caesar'
    __tablename__ = '%s_config' % TABLE_PREFIX

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(25), unique=True, nullable=False)
    name = Column(Unicode(50), unique=True, nullable=False)
    value = Column(Unicode(100))
    value_type = Column(String(30))

    def __unicode__(self):
        return self.code


class Account(Info):
    __tablename__ = u'Account'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    contract_id = Column(Integer, ForeignKey('Contract.id'), nullable=False, index=True)
    orgStructure_id = Column(Integer, ForeignKey('OrgStructure.id'))
    payer_id = Column(Integer, ForeignKey('Organisation.id'), nullable=False, index=True)
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
    format_id = Column(Integer, ForeignKey('rbAccountExportFormat.id'), index=True)

    payer = relationship(u'Organisation')
    orgStructure = relationship(u'Orgstructure')
    contract = relationship(u'Contract')
    format = relationship(u'rbAccountExportFormat')
    items = relationship(u'AccountItem')

    @property
    def sumInWords(self):
        sum_conv = NumToTextConverter(self.sum)
        return sum_conv.convert().getRubText() + sum_conv.convert().getKopText()

    def __unicode__(self):
        return u'%s от %s' % (self.number, self.date)


class AccountItem(Info):
    __tablename__ = u'Account_Item'

    id = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    master_id = Column(Integer, ForeignKey('Account.id'), nullable=False, index=True)
    serviceDate = Column(Date, server_default=u"'0000-00-00'")
    event_id = Column(Integer, ForeignKey('Event.id'), index=True)
    visit_id = Column(Integer, ForeignKey('Visit.id'), index=True)
    action_id = Column(Integer, ForeignKey('Action.id'), index=True)
    price = Column(Float(asdecimal=True), nullable=False)
    unit_id = Column(Integer, ForeignKey('rbMedicalAidUnit.id'), index=True)
    amount = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    uet = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    sum = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    date = Column(Date)
    number = Column(String(20), nullable=False)
    refuseType_id = Column(Integer, ForeignKey('rbPayRefuseType.id'), index=True)
    reexposeItem_id = Column(Integer, ForeignKey('Account_Item.id'), index=True)
    note = Column(String(256), nullable=False)
    tariff_id = Column(Integer, ForeignKey('Contract_Tariff.id'), index=True)
    service_id = Column(Integer, ForeignKey('rbService.id'))
    paymentConfirmationDate = Column(Date)

    event = relationship(u'Event')
    visit = relationship(u'Visit')
    action = relationship(u'Action')
    refuseType = relationship(u'rbPayRefuseType')
    reexposeItem = relationship(u'AccountItem', remote_side=[id])
    service = relationship(u'rbService')
    unit = relationship(u'rbMedicalAidUnit')

    @property
    def sumInWords(self):
        sum_conv = NumToTextConverter(self.sum)
        return sum_conv.convert().getRubText() + sum_conv.convert().getKopText()

    def __unicode__(self):
        return u'%s %s %s' % (self.serviceDate, self.event.client, self.sum)


class Action(Info):
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
    directionDate_raw = Column("directionDate", DateTime)
    status = Column(Integer, nullable=False)
    setPerson_id = Column(Integer, ForeignKey('Person.id'), index=True)
    isUrgent = Column(Boolean, nullable=False, server_default=u"'0'")
    begDate_raw = Column("begDate", DateTime)
    plannedEndDate_raw = Column("plannedEndDate", DateTime, nullable=False)
    endDate_raw = Column("endDate", DateTime)
    note = Column(Text, nullable=False)
    person_id = Column(Integer, ForeignKey('Person.id'), index=True)
    office = Column(String(16), nullable=False)
    amount = Column(Float, nullable=False)
    uet = Column(Float, server_default=u"'0'")
    expose = Column(Boolean, nullable=False, server_default=u"'1'")
    payStatus = Column(Integer, nullable=False)
    account = Column(Boolean, nullable=False)
    finance_id = Column(Integer, ForeignKey('rbFinance.id'), index=True)
    prescription_id = Column(Integer, index=True)
    takenTissueJournal_id = Column(ForeignKey('TakenTissueJournal.id'), index=True)
    contract_id = Column(ForeignKey('Contract.id'), index=True)
    coordDate_raw = Column("coordDate", DateTime)
    coordAgent = Column(String(128), nullable=False, server_default=u"''")
    coordInspector = Column(String(128), nullable=False, server_default=u"''")
    coordText = Column(String, nullable=False)
    hospitalUidFrom = Column(String(128), nullable=False, server_default=u"'0'")
    pacientInQueueType = Column(Integer, server_default=u"'0'")
    AppointmentType = Column(Enum(u'0', u'amb', u'hospital', u'polyclinic', u'diagnostics', u'portal', u'otherLPU'),
                                nullable=False)
    version = Column(Integer, nullable=False, server_default=u"'0'")
    parentAction_id = Column(Integer, index=True)
    uuid_id = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    dcm_study_uid = Column(String(50))

    actionType = relationship(u'Actiontype')
    event = relationship(u'Event')
    person = relationship(u'Person', foreign_keys='Action.person_id')
    setPerson = relationship(u'Person', foreign_keys='Action.setPerson_id')
    takenTissue = relationship(u'TakenTissueJournal')
    tissues = relationship(u'Tissue', secondary=u'ActionTissue')
    properties = relationship(
        u'ActionProperty',
        primaryjoin="and_("
                    "ActionProperty.action_id==Action.id, "
                    "ActionProperty.type_id==Actionpropertytype.id, "
                    "ActionProperty.deleted==0)",
        order_by="Actionpropertytype.idx"
    )
    self_contract = relationship('Contract')
    bbt_response = relationship(u'BbtResponse', uselist=False)

    # def getPrice(self, tariffCategoryId=None):
    #     if self.price is None:
    #         event = self.getEventInfo()
    #         tariffDescr = event.getTariffDescr()
    #         tariffList = tariffDescr.actionTariffList
    #         serviceId = self.service.id
    #         tariffCategoryId = self.person.tariffCategory.id
    #         self._price = CContractTariffCache.getPrice(tariffList, serviceId, tariffCategoryId)
    #     return self._price

    @cached_property
    def diag_info(self):
        from .diagnosis import ActionDiagnosesInfo
        return ActionDiagnosesInfo(self)

    @property
    def begDate(self):
        return DateTimeInfo(self.begDate_raw)

    @property
    def endDate(self):
        return DateTimeInfo(self.endDate_raw)

    @property
    def directionDate(self):
        return DateTimeInfo(self.directionDate_raw)

    @property
    def plannedEndDate(self):
        return DateTimeInfo(self.plannedEndDate_raw)

    @property
    def coordDate(self):
        return DateTimeInfo(self.coordDate_raw)

    @property
    def finance(self):
        if self.contract_id:
            return self.self_contract.finance
        elif self.event:
            return self.event.contract.finance

    @property
    def contract(self):
        if self.contract_id:
            return self.self_contract
        elif self.event:
            return self.event.contract

    @property
    def propsByCode(self):
        return dict(
            (prop.type.code, prop)
            for prop in self.properties
            if prop.type.code
        )

    def get_prop_value(self, prop_name, default=None):
        prop = self.propsByCode.get(prop_name)
        return prop.value if prop else default

    def get_property_by_code(self, code):
        for property in self.properties:
            if property.type.code == code:
                return property
        property_type = self.actionType.get_property_type_by_code(code)
        if property_type:
            return property_type.default_value()
        return None

    def get_property_by_name(self, name):
        for property in self.properties:
            if property.type.name == unicode(name):
                return property
        property_type = self.actionType.get_property_type_by_name(name)
        if property_type:
            return property_type
        return None

    def get_property_by_index(self, index):
        self.properties = sorted(self.properties, key=lambda prop: prop.type.idx)
        return self.properties[index]

    @property
    def group(self):
        return self.actionType.group if self.actionType else None

    @property
    def class_(self):
        return self.actionType.class_ if self.actionType else None

    @property
    def code(self):
        return self.actionType.code if self.actionType else None

    @property
    def flatCode(self):
        return self.actionType.flatCode if self.actionType else None

    @property
    def name(self):
        return self.actionType.name if self.actionType else None

    @property
    def title(self):
        return self.actionType.title if self.actionType else None

    @property
    def service(self):
        return self.actionType.service if self.actionType else None

    @property
    def services(self):
        return self.actionType.services if self.actionType else None

    @property
    def showTime(self):
        return self.actionType.showTime if self.actionType else None

    @property
    def isMes(self):
        return self.actionType.isMes if self.actionType else None

    @property
    def nomenclatureService(self):
        return self.actionType.nomenclatureService if self.actionType else None

    # @property
    # def tariff(self):
    #     services = self.services
    #     if not services:
    #         return
    #     if not hasattr(self, '_tariff'):
    #         event_date = self.event.setDate_raw.date()
    #         cur_date = datetime.date.today()
    #         service_id_list = [ats.service_id for ats in services
    #                            if ats.begDate <= event_date <= (ats.endDate or cur_date)]
    #         contract = self.contract
    #         query = Query(ContractTariff).filter(
    #             ContractTariff.master_id == contract.id,
    #             ContractTariff.service_id.in_(service_id_list),
    #             ContractTariff.deleted == 0,
    #             ContractTariff.eventType_id == self.event.eventType_id,
    #             # or_(
    #             #     ContractTariff.eventType_id == self.event.eventType_id,
    #             #     ContractTariff.eventType_id.is_(None)
    #             # ),
    #             ContractTariff.begDate <= event_date,
    #             ContractTariff.endDate >= event_date
    #         )
    #         tariff = query.first()
    #         self._tariff = tariff
    #     return self._tariff

    # @property
    # def price(self):
    #     tariff = self.tariff
    #     if tariff:
    #         return tariff.price
    #     return 0.0

    # @property
    # def sum_total(self):
    #     return self.price * self.amount

    # @property
    # def isHtml(self):
    #     return self.actionType.isHtml if self.actionType else None

    def _load_ap_price_info(self):
        """Инициализировать свойства данными из соответствующего прайс-листа"""
        from nemesis.lib.data_ctrl.accounting.pricelist import PriceListItemController
        from nemesis.lib.data import get_assignable_apts

        assignable = get_assignable_apts(self.actionType_id)
        assignable_apt_ids = [apt_data[0] for apt_data in assignable]
        contract_id = self.event.contract_id
        pli_ctrl = PriceListItemController()

        filtered_apt_prices = pli_ctrl.get_apts_prices_by_pricelist(assignable_apt_ids, contract_id)
        flt_apt_ids = filtered_apt_prices.keys()
        for prop in self.properties:
            if prop.type_id in flt_apt_ids:
                prop.has_pricelist_service = True
                prop.pl_price = filtered_apt_prices[prop.type_id]
            else:
                prop.has_pricelist_service = False

    def __iter__(self):
        for property in self.properties:
            yield property

    def __getitem__(self, key):
        if isinstance(key, basestring):
            return self.get_property_by_name(unicode(key))
        elif isinstance(key, tuple):
            return self.get_property_by_code(unicode(key[0]))
        elif isinstance(key, (int, long)):
            return self.get_property_by_index(key)


class ActionProperty(Info):
    __tablename__ = u'ActionProperty'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False, default=datetime.datetime.now)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    action_id = Column(Integer, ForeignKey('Action.id'), nullable=False, index=True)
    type_id = Column(Integer, ForeignKey('ActionPropertyType.id'), nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey('rbUnit.id'), index=True)
    norm = Column(String(64), nullable=False, default='')
    isAssigned = Column(Boolean, nullable=False, server_default=u"'0'")
    evaluation = Column(Integer, default=None)
    version = Column(Integer, nullable=False, server_default=u"'0'")

    action = relationship(u'Action')
    type = relationship(u'Actionpropertytype')
    unit_all = relationship(u'rbUnit')

    def __init__(self):
        self._has_pricelist_service = None
        self._pl_price = None

    def get_value_class(self):
        # Следующая магия вытаскивает класс, ассоциированный с backref-пропертей, созданной этим же классом у нашего
        # ActionProperty. Объекты этого класса мы будем создавать для значений
        return getattr(self.__class__, self.__get_property_name()).property.mapper.class_

    def __get_property_name(self):
        return '_value_%s' % self.type.get_appendix()

    def get_value_instance(self):
        class_name = 'ActionProperty_%s' % self.type.get_appendix()
        cls = globals().get(class_name)
        if cls is not None:
            instance = cls()
            instance.property_object = self
            instance.idx = 0
            return instance

    @property
    def value_object(self):
        return getattr(self, self.__get_property_name())

    @value_object.setter
    def value_object(self, value):
        setattr(self, self.__get_property_name(), value)

    @property
    def value(self):
        value_object = self.value_object

        if not value_object:
            value_object = [self.get_value_instance()]

        if self.type.isVector:
            return [item.value for item in value_object if item.id]
        else:
            return value_object[0].value if value_object[0].id else None

    @property
    def name(self):
        return self.type.name

    @property
    def descr(self):
        return self.type.descr

    @property
    def unit(self):
        return self.type.unit

    @property
    def isAssignable(self):
        return self.type.isAssignable

    @reconstructor
    def init_on_load(self):
        self._has_pricelist_service = None
        self._pl_price = None

    @property
    def has_pricelist_service(self):
        if self._has_pricelist_service is None:
            self.action._load_ap_price_info()
        return self._has_pricelist_service

    @has_pricelist_service.setter
    def has_pricelist_service(self, value):
        self._has_pricelist_service = value

    @property
    def pl_price(self):
        if self._pl_price is None:
            self.action._load_ap_price_info()
        return self._pl_price

    @pl_price.setter
    def pl_price(self, value):
        self._pl_price = value

    #     if self.type.typeName == "Table":
    #         return values[0].get_value(self.type.valueDomain) if values else ""

    def __nonzero__(self):
        return bool(self.value_object is not None and (self.value or self.value == 0))

    def __unicode__(self):
        if self.type.isVector:
            return ', '.join([unicode(item) for item in self.value])
        else:
            return unicode(self.value)
    # image = property(lambda self: self._property.getImage())
    # imageUrl = property(_getImageUrl)


class Actionpropertytemplate(Info):
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


class Actionpropertytype(Info):
    __tablename__ = u'ActionPropertyType'

    id = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    actionType_id = Column(Integer, ForeignKey('ActionType.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    template_id = Column(ForeignKey('ActionPropertyTemplate.id'), index=True)
    name = Column(String(128), nullable=False)
    descr = Column(String(128), nullable=False)
    unit_id = Column(ForeignKey('rbUnit.id'), index=True)
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
    test_id = Column(ForeignKey('rbTest.id'), index=True)
    defaultEvaluation = Column(Integer, nullable=False, server_default=u"'0'")
    toEpicrisis = Column(Integer, nullable=False, server_default=u"'0'")
    code = Column(String(25), index=True)
    mandatory = Column(Integer, nullable=False, server_default=u"'0'")
    readOnly = Column(Integer, nullable=False, server_default=u"'0'")
    createDatetime = Column(DateTime, nullable=False, index=True)
    createPerson_id = Column(Integer)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer)

    unit = relationship('rbUnit', lazy=False)
    test = relationship('rbTest')
    template = relationship('Actionpropertytemplate')

    def get_appendix(self):
        type_name = self.typeName
        if type_name in ["Constructor", u"Жалобы"]:
            return 'Text'
        elif type_name == u"Запись в др. ЛПУ":
            return 'OtherLPURecord'
        elif type_name == "FlatDirectory":
            return 'FDRecord'
        return type_name


class ActionProperty__ValueType(Info):
    __abstract__ = True

    @classmethod
    def format_value(cls, prop, json_data):
        return json_data


class ActionProperty_Action(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_Action'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('Action.id'), index=True)

    value = relationship('Action')
    property_object = relationship('ActionProperty', backref='_value_Action')


class ActionProperty_Date(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_Date'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', Date)

    @property
    def value(self):
        return DateInfo(self.value_) if self.value_ else ''
    property_object = relationship('ActionProperty', backref='_value_Date')


class ActionProperty_Double(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_Double'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Float, nullable=False)
    property_object = relationship('ActionProperty', backref='_value_Double')


class ActionProperty_FDRecord(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_FDRecord'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True)
    index = Column(Integer, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('FDRecord.id'), nullable=False, index=True)

    property_object = relationship('ActionProperty', backref='_value_FDRecord')

    @property
    def value(self):
        return Query(Fdrecord).filter(Fdrecord.id == self.value_).first().get_value()


class ActionProperty_HospitalBed(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_HospitalBed'

    id = Column(ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('OrgStructure_HospitalBed.id'), index=True)

    value = relationship(u'OrgstructureHospitalbed')
    property_object = relationship('ActionProperty', backref='_value_HospitalBed')


class ActionProperty_HospitalBedProfile(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_HospitalBedProfile'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('rbHospitalBedProfile.id'), index=True)

    value = relationship('rbHospitalBedProfile')
    property_object = relationship('ActionProperty', backref='_value_HospitalBedProfile')


class ActionProperty_Image(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_Image'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(BLOB)
    property_object = relationship('ActionProperty', backref='_value_Image')


class ActionProperty_ImageMap(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_ImageMap'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(String)
    property_object = relationship('ActionProperty', backref='_value_ImageMap')


class ActionProperty_Diagnosis(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_Diagnosis'
    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('Diagnostic.id'), nullable=False)

    value_model = relationship('Diagnostic')
    property_object = relationship('ActionProperty', backref='_value_Diagnosis')

    @property
    def value(self):
        return self.value_model

    @value.setter
    def value(self, val):
        if self.value_model is not None and self.value_model in g.printing_session and self.value_model.id == val.id:
            self.value_model = g.printing_session.merge(val)
        else:
            self.value_model = val


class ActionProperty_Integer_Base(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_Integer'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', Integer, nullable=False)


class ActionProperty_Integer(ActionProperty_Integer_Base):
    property_object = relationship('ActionProperty', backref='_value_Integer')

    @property
    def value(self):
        return self.value_

    @value.setter
    def value(self, val):
        self.value_ = val


class ActionProperty_AnalysisStatus(ActionProperty_Integer_Base):
    property_object = relationship('ActionProperty', backref='_value_AnalysisStatus')

    @property
    def value(self):
        return Query(rbAnalysisStatus).get(self.value_) if self.value_ else None

    @value.setter
    def value(self, val):
        self.value_ = val.id if val is not None else None


class ActionProperty_OperationType(ActionProperty_Integer_Base):
    property_object = relationship('ActionProperty', backref='_value_OperationType')

    @property
    def value(self):
        return Query(rbOperationType).get(self.value_) if self.value_ else None

    @value.setter
    def value(self, val):
        self.value_ = val.id if val is not None else None


class ActionProperty_Boolean(ActionProperty_Integer_Base):
    property_object = relationship('ActionProperty', backref='_value_Boolean')

    @property
    def value(self):
        return bool(self.value_)

    @value.setter
    def value(self, val):
        self.value_ = 1 if val else 0


class ActionProperty_JobTicket(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_Job_Ticket'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('Job_Ticket.id'), index=True)

    value = relationship('JobTicket')
    property_object = relationship('ActionProperty', backref='_value_JobTicket')


class ActionProperty_MKB(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_MKB'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('MKB.id'), index=True)

    value = relationship('Mkb')
    property_object = relationship('ActionProperty', backref='_value_MKB')


class ActionProperty_OrgStructure(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_OrgStructure'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('OrgStructure.id'), index=True)

    value = relationship('Orgstructure')
    property_object = relationship('ActionProperty', backref='_value_OrgStructure')


class ActionProperty_Organisation(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_Organisation'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('Organisation.id'), index=True)

    value = relationship('Organisation')
    property_object = relationship('ActionProperty', backref='_value_Organisation')


class ActionProperty_OtherLPURecord(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_OtherLPURecord'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)

    property_object = relationship('ActionProperty', backref='_value_OtherLPURecord')


class ActionProperty_Person(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_Person'

    id = Column(ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('Person.id'), index=True)

    value = relationship(u'Person')
    property_object = relationship('ActionProperty', backref='_value_Person')


class ActionProperty_String_Base(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_String'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', Text, nullable=False)


class ActionProperty_String(ActionProperty_String_Base):
    property_object = relationship('ActionProperty', backref='_value_String')

    @property
    def value(self):
        return self.value_ if self.value_ else ''


class ActionProperty_Text(ActionProperty_String_Base):
    property_object = relationship('ActionProperty', backref='_value_Text')

    @property
    def value(self):
        return replace_first_paragraph(convenience_HtmlRip(self.value_)) if self.value_ else ''


class ActionProperty_Html(ActionProperty_String_Base):
    property_object = relationship('ActionProperty', backref='_value_Html')

    @property
    def value(self):
        return convenience_HtmlRip(self.value_) if self.value_ else ''


class ActionProperty_Table(ActionProperty_Integer_Base):
    property_object = relationship('ActionProperty', backref='_value_Table')

    @property
    def value(self):
        table_code = self.property_object.type.valueDomain
        trfu_tables = {"trfuOrderIssueResult": trfuOrderIssueResult, "trfuLaboratoryMeasure": trfuLaboratoryMeasure,
                       "trfuFinalVolume": trfuFinalVolume}
        table = Query(rbAPTable).filter(rbAPTable.code == table_code).first()
        field_names = [field.name for field in table.fields if field.fieldName != 'stickerUrl']
        table_filed_names = [field.fieldName for field in table.fields if field.fieldName != 'stickerUrl']
        value_table_name = table.tableName
        master_field = table.masterField
        values = Query(trfu_tables[value_table_name]).filter("{0}.{1} = {2}".format(
            value_table_name,
            master_field,
            self.value_)
        ).all()
        template = u'''
                    <table width="100%" border="1" align="center" style="border-style:solid;" cellspacing="0">
                        <thead><tr>{% for col in field_names %}<th>{{ col }}</th>{% endfor %}</tr></thead>
                        {% for row in range(values|length) %}<tr>
                            {% for col in table_filed_names %}<td align="center" valign="middle">
                            {{values[row][col]}}
                            </td>{% endfor %}
                        </tr>{% endfor %}
                    </table>
                    '''
        return jinja2.Template(template).render(field_names=field_names, table_filed_names=table_filed_names, values=values)


class ActionProperty_Time(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_Time'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', Time, nullable=False)
    property_object = relationship('ActionProperty', backref='_value_Time')

    @property
    def value(self):
        return TimeInfo(self.value_) if self.value_ else ''

    def __str__(self):
        return self.value


class ActionProperty_RLS(ActionProperty_Integer_Base):

    @property
    def value(self):
        return Query(v_Nomen).get(self.value_).first() if self.value_ else None
    property_object = relationship('ActionProperty', backref='_value_RLS')


class ActionProperty_ReferenceRb(ActionProperty_Integer_Base):

    @property
    def value(self):
        if not hasattr(self, 'table_name'):
            domain = Query(ActionProperty).get(self.id).type.valueDomain
            self.table_name = domain.split(';')[0]
        model = get_model_by_name(self.table_name)
        return Query(model).get(self.value_)

    property_object = relationship('ActionProperty', backref='_value_ReferenceRb')


class ActionProperty_ExtReferenceRb(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_ExtRef'

    id = Column(Integer, ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', Text, nullable=False)

    @property
    def value(self):
        from nemesis.app import app
        if not hasattr(self, 'table_name'):
            domain = Query(ActionProperty).get(self.id).type.valueDomain
            self.table_name = domain.split(';')[0]
        try:
            response = requests.get(u'{0}v1/{1}/code/{2}'.format(app.config['VESTA_URL'], self.table_name, self.value_))
            result = response.json()['data']
        except Exception, e:
            import traceback
            traceback.print_exc()
            return
        else:
            return {'id': result['_id'], 'name': result['name'], 'code': result['code']}

    property_object = relationship('ActionProperty', backref='_value_ExtReferenceRb')


class ActionProperty_rbFinance(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_rbFinance'

    id = Column(ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('rbFinance.id'), index=True)

    value = relationship('rbFinance')
    property_object = relationship('ActionProperty', backref='_value_rbFinance')


class ActionProperty_rbReasonOfAbsence(ActionProperty__ValueType):
    __tablename__ = u'ActionProperty_rbReasonOfAbsence'

    id = Column(ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value_ = Column('value', ForeignKey('rbReasonOfAbsence.id'), index=True)

    value = relationship('rbReasonOfAbsence')
    property_object = relationship('ActionProperty', backref='_value_rbReasonOfAbsence')


class Actiontemplate(Info):
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


class Actiontype(Info):
    __tablename__ = u'ActionType'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    hidden = Column(Integer, nullable=False, server_default=u"'0'")
    class_ = Column(u'class', Integer, nullable=False, index=True)
    group_id = Column(Integer, ForeignKey('ActionType.id'), index=True)
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

    service = relationship(u'rbService', foreign_keys='Actiontype.service_id')
    services = relationship(u'ActiontypeService')
    nomenclatureService = relationship(u'rbService', foreign_keys='Actiontype.nomenclativeService_id')
    property_types = relationship(u'Actionpropertytype')
    group = relationship(u'Actiontype', remote_side=[id])
    diagnosis_types = relationship(u'rbDiagnosisTypeN', secondary='ActionType_DiagnosisType')

    def get_property_type_by_name(self, name):
        for property_type in self.property_types:
            if property_type.name == unicode(name):
                return property_type
        return None

    def get_property_type_by_code(self, code):
        for property_type in self.property_types:
            if property_type.name == code:
                return property_type
        return None


class ActiontypeEventtypeCheck(Info):
    __tablename__ = u'ActionType_EventType_check'

    id = Column(Integer, primary_key=True)
    actionType_id = Column(ForeignKey('ActionType.id'), nullable=False, index=True)
    eventType_id = Column(ForeignKey('EventType.id'), nullable=False, index=True)
    related_actionType_id = Column(ForeignKey('ActionType.id'), index=True)
    relationType = Column(Integer)

    actionType = relationship(u'Actiontype', primaryjoin='ActiontypeEventtypeCheck.actionType_id == Actiontype.id')
    eventType = relationship(u'Eventtype')
    related_actionType = relationship(u'Actiontype', primaryjoin='ActiontypeEventtypeCheck.related_actionType_id == Actiontype.id')


class ActiontypeQuotatype(Info):
    __tablename__ = u'ActionType_QuotaType'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    quotaClass = Column(Integer)
    finance_id = Column(Integer, index=True)
    quotaType_id = Column(Integer, index=True)


class ActiontypeService(Info):
    __tablename__ = u'ActionType_Service'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, ForeignKey('ActionType.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    service_id = Column(Integer, ForeignKey('rbService.id'), index=True, nullable=False)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date)

    service = relationship('rbService')


class ActiontypeTissuetype(Info):
    __tablename__ = u'ActionType_TissueType'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('ActionType.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    tissueType_id = Column(ForeignKey('rbTissueType.id'), index=True)
    amount = Column(Integer, nullable=False, server_default=u"'0'")
    unit_id = Column(ForeignKey('rbUnit.id'), index=True)

    master = relationship(u'Actiontype')
    tissueType = relationship(u'rbTissueType')
    unit = relationship(u'rbUnit')


class ActiontypeUser(Info):
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
    profile = relationship(u'rbUserProfile')


class Address(Info):
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
    house_id = Column(Integer, ForeignKey('AddressHouse.id'), nullable=False)
    flat = Column(String(6), nullable=False)

    house = relationship(u'Addresshouse')

    @property
    def KLADRCode(self):
        # без учета последних двух цифр, которые относятся к версии кода
        return self.house.KLADRCode[:-2] if len(self.house.KLADRCode) == 13 else self.house.KLADRCode

    @property
    def KLADRStreetCode(self):
        # без учета последних двух цифр, которые относятся к версии кода
        return (
            self.house.KLADRStreetCode[:-2]
            if self.house.KLADRStreetCode and len(self.house.KLADRStreetCode) == 17
            else self.house.KLADRStreetCode
        )

    @property
    def kladr_locality(self):
        if self.KLADRCode:
            if not hasattr(self, '_kladr_locality'):
                from nemesis.lib.vesta import Vesta
                self._kladr_locality = Vesta.get_kladr_locality(self.KLADRCode)
            return self._kladr_locality
        else:
            return None

    @property
    def city(self):
        return self.kladr_locality.fullname if self.kladr_locality else ''

    @property
    def city_old(self):
        if self.house.KLADRCode:
            record = Kladr.query.filter(Kladr.CODE == self.house.KLADRCode).first()
            name = [" ".join([record.NAME, record.SOCR])]
            parent = record.parent
            while parent:
                record = Kladr.query.filter(Kladr.CODE == parent.ljust(13, "0")).first()
                name.insert(0, " ".join([record.NAME, record.SOCR]))
                parent = record.parent
            return ", ".join(name)
        else:
            return ''

    @property
    def town(self):
        return self.city

    @property
    def kladr_street(self):
        if self.KLADRStreetCode:
            if not hasattr(self, '_kladr_street'):
                from nemesis.lib.vesta import Vesta
                self._kladr_street = Vesta.get_kladr_street(self.KLADRStreetCode)
            return self._kladr_street
        else:
            return None

    @property
    def street(self):
        return self.kladr_street.name if self.kladr_street else ''

    @property
    def street_free(self):
        return self.house.streetFreeInput if self.house else None

    @property
    def street_old(self):
        if self.house.KLADRStreetCode:
            record = Street.query.filter(Street.CODE == self.house.KLADRStreetCode).first()
            return record.NAME + " " + record.SOCR
        else:
            return ''

    @property
    def text(self):
        parts = [self.city]
        if self.street or self.street_free:
            parts.append(self.street or self.street_free)
        if self.number:
            parts.append(u'д.'+self.number)
        if self.corpus:
            parts.append(u'к.'+self.corpus)
        if self.flat:
            parts.append(u'кв.'+self.flat)
        return (', '.join(parts)).strip()

    @property
    def number(self):
        return self.house.number

    @property
    def corpus(self):
        return self.house.corpus

    def __unicode__(self):
        return self.text


class Addressareaitem(Info):
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


class Addresshouse(Info):
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
    KLADRStreetCode = Column(String(17))
    streetFreeInput = Column(Unicode(128))
    number = Column(String(8), nullable=False)
    corpus = Column(String(8), nullable=False)


class Applock(Info):
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


class Bank(Info):
    __tablename__ = u'Bank'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    bik = Column("BIK", String(10), nullable=False, index=True)
    name = Column(Unicode(100), nullable=False, index=True)
    branchName = Column(Unicode(100), nullable=False)
    corrAccount = Column(String(20), nullable=False)
    subAccount = Column(String(20), nullable=False)


class Blankaction(Info):
    __tablename__ = u'BlankActions'

    id = Column(Integer, primary_key=True)
    doctype_id = Column(ForeignKey('ActionType.id'), index=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    checkingSerial = Column(Integer, nullable=False)
    checkingNumber = Column(Integer, nullable=False)
    checkingAmount = Column(Integer, nullable=False)

    doctype = relationship(u'Actiontype')


class BlankactionsMoving(Info):
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


class BlankactionsParty(Info):
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
    doctype = relationship(u'rbBlankActions')
    modifyPerson = relationship(u'Person', primaryjoin='BlankactionsParty.modifyPerson_id == Person.id')
    person = relationship(u'Person', primaryjoin='BlankactionsParty.person_id == Person.id')


class BlanktempinvalidMoving(Info):
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


class BlanktempinvalidParty(Info):
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
    doctype = relationship(u'rbBlankTempInvalids')
    modifyPerson = relationship(u'Person', primaryjoin='BlanktempinvalidParty.modifyPerson_id == Person.id')
    person = relationship(u'Person', primaryjoin='BlanktempinvalidParty.person_id == Person.id')


class Blanktempinvalid(Info):
    __tablename__ = u'BlankTempInvalids'

    id = Column(Integer, primary_key=True)
    doctype_id = Column(ForeignKey('rbTempInvalidDocument.id'), index=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    checkingSerial = Column(Integer, nullable=False)
    checkingNumber = Column(Integer, nullable=False)
    checkingAmount = Column(Integer, nullable=False)

    doctype = relationship(u'rbTempInvalidDocument')


class Bloodhistory(Info):
    __tablename__ = u'BloodHistory'

    id = Column(Integer, primary_key=True)
    bloodDate = Column(Date, nullable=False)
    client_id = Column(Integer, ForeignKey('Client.id'), nullable=False)
    bloodType_id = Column(Integer, ForeignKey('rbBloodType.id'), nullable=False)
    person_id = Column(Integer, ForeignKey('Person.id'), nullable=False)

    bloodType = relationship("rbBloodType")
    person = relationship('Person')

    def __init__(self, blood_type, date, person, client):
        self.bloodType_id = int(blood_type) if blood_type else None
        self.bloodDate = date
        self.person_id = int(person) if person else None
        self.client = client

    def __int__(self):
        return self.id


class Calendarexception(Info):
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


class Client(Info):
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
    birthDate_raw = Column("birthDate", Date, nullable=False, index=True)
    sexCode = Column("sex", Integer, nullable=False)
    SNILS_short = Column("SNILS", String(11), nullable=False, index=True)
    bloodType_id = Column(ForeignKey('rbBloodType.id'), index=True)
    bloodDate = Column(Date)
    bloodNotes = Column(String, nullable=False)
    growth = Column(String(16), nullable=False)
    weight = Column(String(16), nullable=False)
    notes = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    birthPlace = Column(Unicode(128), nullable=False, server_default=u"''")
    embryonalPeriodWeek = Column(String(16), nullable=False, server_default=u"''")
    uuid_id = Column(Integer, nullable=False, index=True, server_default=u"'0'")

    client_attachments = relationship(u'Clientattach', primaryjoin='and_(Clientattach.client_id==Client.id, Clientattach.deleted==0)',
                                      order_by="desc(Clientattach.id)")
    blood_history = relationship(
        u'Bloodhistory',
        backref=backref('client'),
        order_by='desc(Bloodhistory.bloodDate)'
    )
    socStatuses = relationship(u'Clientsocstatus',
                               primaryjoin="and_(Clientsocstatus.deleted == 0,Clientsocstatus.client_id==Client.id,"
                               "or_(Clientsocstatus.endDate == None, Clientsocstatus.endDate>='{0}'))".format(datetime.date.today()))
    documentsAll = relationship(u'Clientdocument', primaryjoin='and_(Clientdocument.clientId==Client.id,'
                                                               'Clientdocument.deleted == 0)',
                                order_by="desc(Clientdocument.documentId)")
    intolerances = relationship(u'Clientintolerancemedicament',
                                primaryjoin='and_(Clientintolerancemedicament.client_id==Client.id,'
                                            'Clientintolerancemedicament.deleted == 0)')
    allergies = relationship(u'Clientallergy', primaryjoin='and_(Clientallergy.client_id==Client.id,'
                                                           'Clientallergy.deleted == 0)')
    contacts = relationship(u'Clientcontact', primaryjoin='and_(Clientcontact.client_id==Client.id,'
                                                          'Clientcontact.deleted == 0)')
    direct_relations = relationship(u'DirectClientRelation', foreign_keys='Clientrelation.client_id')
    reversed_relations = relationship(u'ReversedClientRelation', foreign_keys='Clientrelation.relative_id')
    policies = relationship(u'Clientpolicy', primaryjoin='and_(Clientpolicy.clientId==Client.id,'
                                                         'Clientpolicy.deleted == 0)', order_by="desc(Clientpolicy.id)")
    works = relationship(u'Clientwork', primaryjoin='and_(Clientwork.client_id==Client.id, Clientwork.deleted == 0)',
                         order_by="desc(Clientwork.id)")
    reg_addresses = relationship(u'Clientaddress',
                                 primaryjoin="and_(Client.id==Clientaddress.client_id, Clientaddress.type==0)",
                                 order_by="desc(Clientaddress.id)")
    loc_addresses = relationship(u'Clientaddress',
                                 primaryjoin="and_(Client.id==Clientaddress.client_id, Clientaddress.type==1)",
                                 order_by="desc(Clientaddress.id)")
    appointments = relationship(
        u'ScheduleClientTicket',
        lazy='dynamic',  #order_by='desc(ScheduleTicket.begDateTime)',
        primaryjoin='and_('
                    'ScheduleClientTicket.deleted == 0, '
                    'ScheduleClientTicket.client_id == Client.id)',
        innerjoin=True
    )

    @property
    def birthDate(self):
        return DateInfo(self.birthDate_raw)

    @property
    def bloodType(self):
        return self.blood_history[0].bloodType if self.blood_history else None

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
        if self.SNILS_short:
            s = self.SNILS_short+' '*14
            return s[0:3]+'-'+s[3:6]+'-'+s[6:9]+' '+s[9:11]
        else:
            return u''

    @property
    def permanentAttach(self):
        for attach in self.client_attachments:
            if attach.attachType.temporary == 0:
                return attach

    @property
    def temporaryAttach(self):
        for attach in self.client_attachments:
            if attach.attachType.temporary != 0:
                return attach

    @property
    def document(self):
        for document in self.documentsAll:
            if document.documentType and document.documentType.group.code == '1':
                return document

    @property
    def relations(self):
        return self.reversed_relations + self.direct_relations

    @property
    def phones(self):
        contacts = [(contact.name, contact.contact, contact.notes) for contact in self.contacts
                    if contact.contactType.code not in ('04', '05')]
        return ', '.join([(phone[0]+': '+phone[1]+' ('+phone[2]+')') if phone[2] else (phone[0]+': '+phone[1])
                          for phone in contacts])

    @property
    def compulsoryPolicy(self):
        for policy in self.policies:
            if not policy.policyType or u"ОМС" in policy.policyType.name:
                return policy

    @property
    def voluntaryPolicy(self):
        for policy in self.policies:
            if policy.policyType and policy.policyType.name.startswith(u"ДМС"):
                return policy

    @property
    def policy(self):
        return self.compulsoryPolicy if self.compulsoryPolicy else Clientpolicy()

    @property
    def policyDMS(self):
        return self.voluntaryPolicy if self.voluntaryPolicy else Clientpolicy()

    @property
    def fullName(self):
        return formatNameInt(self.lastName, self.firstName, self.patrName)

    @property
    def shortName(self):
        return formatShortNameInt(self.lastName, self.firstName, self.patrName)

    @property
    def work(self):
        return self.works[0] if self.works else Clientwork()

    def age_tuple(self, moment=None):
        """
        @type moment: datetime.datetime
        """
        if not self.birthDate:
            return None
        if not moment:
            moment = datetime.date.today()
        return calcAgeTuple(self.birthDate, moment)

    @property
    def ageTuple(self):
        return self.age_tuple()

    @property
    def age(self):
        bd = self.birthDate_raw
        date = datetime.date.today()
        if not self.age_tuple():
            return u'ещё не родился'
        (days, weeks, months, years) = self.age_tuple()
        if years > 7:
            return formatYears(years)
        elif years > 1:
            return formatYearsMonths(years, months-12*years)
        elif months > 1:
            # TODO: отрефакторить магию, здесь неясен смысл divmod(bd.month + months, 12)
            #  в декабре это вызывало проблемы с определением возраста пациента младше года
            add_year, new_month = divmod(bd.month + months, 12)
            if new_month:
                new_day = min(bd.day, calendar.monthrange(bd.year+add_year, new_month)[1])
                fmonth_date = datetime.date(bd.year+add_year, new_month, new_day)
            else:
                fmonth_date = bd
            return formatMonthsWeeks(months, (date-fmonth_date).days/7)
        else:
            return formatDays(days)

    @property
    def regAddress(self):
        return self.reg_addresses[0] if self.reg_addresses else None

    @property
    def locAddress(self):
        return self.loc_addresses[0] if self.loc_addresses else None

    @property
    def prescriptions(self):
        from .prescriptions import MedicalPrescription

        return Query(MedicalPrescription).join(Action, Event).filter(Event.client_id == self.id).all()

    def __unicode__(self):
        return self.formatShortNameInt(self.lastName, self.firstName, self.patrName)


class Patientstohs(Info):
    __tablename__ = u'PatientsToHS'

    client_id = Column(ForeignKey('Client.id'), primary_key=True)
    sendTime = Column(DateTime, nullable=False, server_default=u'CURRENT_TIMESTAMP')
    errCount = Column(Integer, nullable=False, server_default=u"'0'")
    info = Column(String(1024))


class Clientaddress(Info):
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
    address_id = Column(Integer, ForeignKey('Address.id'))
    freeInput = Column(String(255), nullable=False, server_default="''")
    version = Column(Integer, nullable=False, server_default="'0'")
    localityType = Column(Integer, nullable=False)

    address = relationship(u'Address')

    @property
    def KLADRCode(self):
        return self.address.house.KLADRCode if self.address else ''

    @property
    def KLADRStreetCode(self):
        return self.address.house.KLADRStreetCode if self.address else ''

    @property
    def city(self):
        return self.address.city if self.address else ''

    @property
    def town(self):
        return self.address.town if self.address else ''

    @property
    def text(self):
        return self.address.text if self.address else ''

    @property
    def number(self):
        return self.address.number if self.address else ''

    @property
    def corpus(self):
        return self.address.corpus if self.address else ''

    @property
    def is_russian(self):
        return bool(self.KLADRCode)

    def is_from_kladr(self, full=True):
        if full:
            return bool(self.KLADRCode and self.KLADRStreetCode)
        else:
            return bool(self.KLADRCode)

    def __unicode__(self):
        if self.text:
            return self.text
        else:
            return self.freeInput


class Clientallergy(Info):
    __tablename__ = u'ClientAllergy'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    name = Column("nameSubstance", Unicode(128), nullable=False)
    power = Column(Integer, nullable=False)
    createDate = Column(Date)
    notes = Column(String, nullable=False)
    version = Column(Integer, nullable=False)

    client = relationship(u'Client')

    @property
    def power_name(self):
        return AllergyPower.names[self.power]

    def __unicode__(self):
        return self.name


class Clientattach(Info):
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
    self_document = relationship(u'Clientdocument')
    org = relationship(u'Organisation')
    orgStructure = relationship(u'Orgstructure')
    attachType = relationship(u'rbAttachType')

    @property
    def code(self):
        return self.attachType.code

    @property
    def name(self):
        return self.attachType.name

    @property
    def outcome(self):
        return self.attachType.outcome

    @property
    def document(self):
        if self.document_id:
            return self.self_document
        else:
            return self.getClientDocument()

    def getClientDocument(self):
        documents = Query(Clientdocument).filter(Clientdocument.clientId == self.client_id).\
            filter(Clientdocument.deleted == 0).all()
        documents = [document for document in documents if document.documentType and document.documentType.group.code == "1"]
        return documents[-1]

    def __unicode__(self):
        try:
            result = self.name
            if self.outcome:
                result += ' ' + unicode(self.endDate)
            elif self.attachType.temporary:
                result += ' ' + self.org.shortName
                if self.begDate:
                    result += u' c ' + unicode(self.begDate)
                if self.endDate:
                    result += u' по ' + unicode(self.endDate)
            else:
                result += ' ' + self.org.shortName
        except AttributeError:
            result = ''
        return result


class Clientcontact(Info):
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
    contactType = relationship(u'rbContactType')

    @property
    def name(self):
        return self.contactType.name

    def __unicode__(self):
        return (self.name+': '+self.contact+' ('+self.notes+')') if self.notes else (self.name+': '+self.contact)


class Clientdocument(Info):
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
    documentType = relationship(u'rbDocumentType')

    @property
    def documentTypeCode(self):
        return self.documentType.regionalCode

    def __unicode__(self):
        return (' '.join([self.documentType.name if self.documentType else '', self.serial if self.serial else '',
                          self.number if self.number else ''])).strip()


class Clientfdproperty(Info):
    __tablename__ = u'ClientFDProperty'

    id = Column(Integer, primary_key=True)
    flatDirectory_id = Column(ForeignKey('FlatDirectory.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    version = Column(Integer, nullable=False)

    flatDirectory = relationship(u'Flatdirectory')


class Clientflatdirectory(Info):
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


class Clientidentification(Info):
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
    accountingSystems = relationship(u'rbAccountingSystem')

    @property
    def code(self):
        return self.attachType.code

    @property
    def name(self):
        return self.attachType.name

    # byCode = {code: identifier}
    # nameDict = {code: name}


class Clientintolerancemedicament(Info):
    __tablename__ = u'ClientIntoleranceMedicament'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    client_id = Column(ForeignKey('Client.id'), nullable=False, index=True)
    name = Column("nameMedicament", String(128), nullable=False)
    power = Column(Integer, nullable=False)
    createDate = Column(Date)
    notes = Column(String, nullable=False)
    version = Column(Integer, nullable=False)

    client = relationship(u'Client')

    @property
    def power_name(self):
        return AllergyPower.names[self.power]

    def __unicode__(self):
        return self.name


class Clientpolicy(Info):
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
    policyType = relationship(u'rbPolicyType')

    def __init__(self):
        self.serial = ""
        self.number = ""
        self.name = ""
        self.note = ""
        self.insurer = Organisation()
        self.policyType = rbPolicyType()

    def __unicode__(self):
        return (' '.join([self.policyType.name, unicode(self.insurer), self.serial, self.number])).strip()


class Clientrelation(Info):
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

    relativeType = relationship(u'rbRelationType')

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
        return self.leftName

    @property
    def otherRole(self):
        return self.rightName

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
        return self.rightName

    @property
    def otherRole(self):
        return self.leftName

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


class Clientsocstatus(Info):
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
    begDate = Column(Date)
    endDate = Column(Date)
    document_id = Column(ForeignKey('ClientDocument.id'), index=True)
    version = Column(Integer, nullable=False)
    note = Column(String(256), nullable=False, server_default=u"''")
    benefitCategory_id = Column(Integer)

    client = relationship(u'Client')
    socStatusType = relationship(u'rbSocStatusType')
    self_document = relationship(u'Clientdocument')

    @property
    def classes(self):
        return self.socStatusType.classes

    @property
    def code(self):
        return self.socStatusType.code

    @property
    def name(self):
        return self.socStatusType.name

    @property
    def document(self):
        if self.document_id:
            return self.self_document
        else:
            return self.getClientDocument()

    def getClientDocument(self):
        documents = Query(Clientdocument).filter(Clientdocument.clientId == self.client_id).\
            filter(Clientdocument.deleted == 0).all()
        documents = [document for document in documents if document.documentType and
                     document.documentType.group.code == "1"]
        return documents[-1]

    def __unicode__(self):
        return self.name


class Clientwork(Info):
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


class ClientworkHurt(Info):
    __tablename__ = u'ClientWork_Hurt'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('ClientWork.id'), nullable=False, index=True)
    hurtType_id = Column(ForeignKey('rbHurtType.id'), nullable=False, index=True)
    stage = Column(Integer, nullable=False)

    clientWork = relationship(u'Clientwork')
    hurtType = relationship(u'rbHurtType')
    factors = relationship(u'ClientworkHurtFactor')

    def hurtTypeCode(self):
        return self.hurtType.code

    def hurtTypeName(self):
        return self.hurtType.name

    code = property(hurtTypeCode)
    name = property(hurtTypeName)


class ClientworkHurtFactor(Info):
    __tablename__ = u'ClientWork_Hurt_Factor'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('ClientWork_Hurt.id'), nullable=False, index=True)
    factorType_id = Column(ForeignKey('rbHurtFactorType.id'), nullable=False, index=True)

    master = relationship(u'ClientworkHurt')
    factorType = relationship(u'rbHurtFactorType')

    @property
    def code(self):
        return self.factorType.code

    @property
    def name(self):
        return self.factorType.name


class ClientQuoting(Info):
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
    quotaDetails_id = Column(ForeignKey(u'VMPQuotaDetails.id'), nullable=False, index=True)
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
    event_id = Column(Integer, index=True)
    prevTalon_event_id = Column(Integer)
    version = Column(Integer, nullable=False)

    master = relationship(u'Client')
    details = relationship('VMPQuotaDetails', lazy=False)

    @property
    def patientModel(self):
        return self.details.patientModel

    @property
    def treatment(self):
        return self.details.treatment

    @property
    def quotaType(self):
        return self.details.quotaType

    @property
    def mkb(self):
        return self.details.mkb


class ClientQuotingdiscussion(Info):
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


class Couponstransferquote(Info):
    __tablename__ = u'CouponsTransferQuotes'

    id = Column(Integer, primary_key=True)
    srcQuotingType_id = Column(ForeignKey('rbTimeQuotingType.code'), nullable=False, index=True)
    dstQuotingType_id = Column(ForeignKey('rbTimeQuotingType.code'), nullable=False, index=True)
    transferDayType = Column(ForeignKey('rbTransferDateType.code'), nullable=False, index=True)
    transferTime = Column(Time, nullable=False)
    couponsEnabled = Column(Integer, server_default=u"'0'")

    dstQuotingType = relationship(u'rbTimeQuotingType', primaryjoin='Couponstransferquote.dstQuotingType_id == rbTimeQuotingType.code')
    srcQuotingType = relationship(u'rbTimeQuotingType', primaryjoin='Couponstransferquote.srcQuotingType_id == rbTimeQuotingType.code')
    rbTransferDateType = relationship(u'rbTransferDateType')


class Drugchart(Info):
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


class Drugcomponent(Info):
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


class Emergencybrigade(Info):
    __tablename__ = u'EmergencyBrigade'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class EmergencybrigadePersonnel(Info):
    __tablename__ = u'EmergencyBrigade_Personnel'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    person_id = Column(Integer, nullable=False, index=True)


class Emergencycall(Info):
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


class Event(Info):
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
    prevEventDate_row = Column("prevEventDate", DateTime)
    setDate_raw = Column("setDate", DateTime, nullable=False, index=True)
    setPerson_id = Column(Integer, ForeignKey('Person.id'), index=True)
    execDate_raw = Column("execDate", DateTime, index=True)
    execPerson_id = Column(Integer, ForeignKey('Person.id'), index=True)
    isPrimaryCode = Column("isPrimary", Integer, nullable=False)
    order = Column(Integer, nullable=False)
    result_id = Column(Integer, ForeignKey('rbResult.id'), index=True)
    nextEventDate_row = Column("nextEventDate", DateTime)
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

    actions = relationship(u'Action', primaryjoin='and_(Action.event_id==Event.id,'
                                                     'Action.deleted == 0)')
    eventType = relationship(u'Eventtype')
    execPerson = relationship(u'Person', foreign_keys='Event.execPerson_id')
    setPerson = relationship(u'Person', foreign_keys='Event.setPerson_id')
    curator = relationship(u'Person', foreign_keys='Event.curator_id')
    assistant = relationship(u'Person', foreign_keys='Event.assistant_id')
    contract = relationship(u'Contract')
    organisation = relationship(u'Organisation')
    mesSpecification = relationship(u'rbMesSpecification')
    rbAcheResult = relationship(u'rbAcheResult')
    result = relationship(u'rbResult')
    typeAsset = relationship(u'rbEmergencyTypeAsset')
    client = relationship(u'Client')
    visits = relationship(u'Visit')
    diagnostics = DummyProperty(list, u'Поле diagnostics у обращения не реализовано')
    diagnosises = DummyProperty(list, u'Поле diagnosises у обращения не реализовано')

    @property
    def setDate(self):
        return DateTimeInfo(self.setDate_raw)

    @property
    def execDate(self):
        return DateTimeInfo(self.execDate_raw)

    @property
    def prevEventDate(self):
        return DateInfo(self.prevEventDate_raw)

    @property
    def nextEventDate(self):
        return DateInfo(self.nextEventDate_raw)

    @property
    def isPrimary(self):
        return self.isPrimaryCode == 1

    @property
    def finance(self):
        return self.eventType.finance

    @property
    def orgStructure(self):
        if self.eventType.requestType.code == 'policlinic' and self.orgStructure_id:
            return Query(Orgstructure).get(self.orgStructure_id)
        elif self.eventType.requestType.code in ('hospital', 'clinic', 'stationary'):
            movings = [action for action in self.actions if (action.endDate.datetime is None and
                                                             action.actionType.flatCode == 'moving')]
            return movings[-1][('orgStructStay',)].value if movings else None
        return None

    def getPatientLocation(self, dt=None):
        from ..lib.data import get_patient_location
        return get_patient_location(self, dt)

    @property
    def hospLength(self):
        if not hasattr(self, '_hosp_length'):
            from ..lib.data import get_hosp_length
            self._hosp_length = get_hosp_length(self)
        return self._hosp_length

    @property
    def hospitalBed(self):
        if not hasattr(self, '_hospital_bed'):
            from ..lib.data import get_patient_hospital_bed
            self._hospital_bed = get_patient_hospital_bed(self)
        return self._hospital_bed

    @property
    def is_closed(self):
        from nemesis.lib.data import addPeriod
        if self.is_stationary:
            # Текущая дата больше, чем дата завершения + 2 рабочих дня
            # согласно какому-то мегаприказу МЗ и главврача ФНКЦ
            # Установлен результат обращения
            return self.is_pre_closed and datetime.date.today() > addPeriod(
                self.execDate.date(),
                2,
                False
            )
        else:
            return self.is_pre_closed

    @property
    def is_pre_closed(self):
        return self.execDate and (self.result_id is not None)

    @property
    def is_policlinic(self):
        return self.eventType.requestType.code in POLICLINIC_EVENT_CODES

    @property
    def is_stationary(self):
        return self.eventType.requestType.code in STATIONARY_EVENT_CODES

    @property
    def is_day_hospital(self):
        return self.eventType.requestType.code == DAY_HOSPITAL_CODE

    @property
    def is_diagnostic(self):
        return self.eventType.requestType.code in DIAGNOSTIC_EVENT_CODES

    @property
    def is_paid(self):
        return self.eventType.finance.code == PAID_EVENT_CODE

    @property
    def is_oms(self):
        return self.eventType.finance.code == OMS_EVENT_CODE

    @property
    def is_dms(self):
        return self.eventType.finance.code == DMS_EVENT_CODE

    @property
    def is_budget(self):
        return self.eventType.finance.code == BUDGET_EVENT_CODE

    @property
    def departmentManager(self):
        persons = Query(Person).filter(Person.orgStructure_id == self.orgStructure.id).all() if self.orgStructure else []
        if persons:
            for person in persons:
                if person.post and person.post.flatCode == u'departmentManager':
                    return person
        return None

    @property
    def date(self):
        date = self.execDate if self.execDate is not None else datetime.date.today()
        return date

    @property
    def prescriptions(self):
        from .prescriptions import MedicalPrescription

        return Query(MedicalPrescription).join(Action).filter(Action.event_id == self.id).all()

    def __unicode__(self):
        return unicode(self.eventType)


class Hsintegration(Event):
    __tablename__ = u'HSIntegration'

    event_id = Column(ForeignKey('Event.id'), primary_key=True)
    status = Column(Enum(u'NEW', u'SENDED', u'ERROR'), nullable=False, server_default=u"'NEW'")
    info = Column(String(1024))


class Eventtype(RBInfo):
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

    counter = relationship(u'rbCounter')
    rbMedicalKind = relationship(u'rbMedicalKind')
    purpose = relationship(u'rbEventTypePurpose')
    finance = relationship(u'rbFinance')
    service = relationship(u'rbService')
    requestType = relationship(u'rbRequestType')

    def __unicode__(self):
        return self.name


class Eventtypeform(Info):
    __tablename__ = u'EventTypeForm'

    id = Column(Integer, primary_key=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    eventType_id = Column(Integer, nullable=False, index=True)
    code = Column(String(8), nullable=False)
    name = Column(String(64), nullable=False)
    descr = Column(String(64), nullable=False)
    pass_ = Column(u'pass', Integer, nullable=False)


class EventtypeAction(Info):
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

    tissueType = relationship(u'rbTissueType')


class EventtypeDiagnostic(Info):
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


class EventFeed(Info):
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


class EventPerson(Info):
    __tablename__ = u'Event_Persons'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False, index=True)
    person_id = Column(Integer, nullable=False, index=True)
    begDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime)


class Fdfield(Info):
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
    flatDirectory = relationship(u'Flatdirectory', primaryjoin='Fdfield.flatDirectory_id == Flatdirectory.id')

    values = relationship(u'Fdfieldvalue', backref=backref('fdField'), lazy='dynamic')

    def get_value(self, record_id):
        return self.values.filter(Fdfieldvalue.fdRecord_id == record_id).first().value


class Fdfieldtype(Info):
    __tablename__ = u'FDFieldType'

    id = Column(Integer, primary_key=True)
    name = Column(String(4096), nullable=False)
    description = Column(String(4096))


class Fdfieldvalue(Info):
    __tablename__ = u'FDFieldValue'

    id = Column(Integer, primary_key=True)
    fdRecord_id = Column(ForeignKey('FDRecord.id'), nullable=False, index=True)
    fdField_id = Column(ForeignKey('FDField.id'), nullable=False, index=True)
    value = Column(String)

    # fdRecord = relationship(u'Fdrecord')


class Fdrecord(Info):
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
    values = relationship(u'Fdfieldvalue', backref=backref('Fdrecord'), lazy='dynamic')

    def get_value(self):
        return [value.value for value in self.values]
        #return [field.get_value(self.id) for field in self.FlatDirectory.fields] # в нтк столбцы не упорядочены


class Flatdirectory(Info):
    __tablename__ = u'FlatDirectory'

    id = Column(Integer, primary_key=True)
    name = Column(String(4096), nullable=False)
    code = Column(String(128), index=True)
    description = Column(String(4096))

    fields = relationship(u'Fdfield', foreign_keys='Fdfield.flatDirectory_code', backref=backref('FlatDirectory'),
                             lazy='dynamic')


class Informermessage(Info):
    __tablename__ = u'InformerMessage'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False)
    subject = Column(String(128), nullable=False)
    text = Column(String, nullable=False)


class InformermessageReadmark(Info):
    __tablename__ = u'InformerMessage_readMark'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    person_id = Column(Integer, index=True)


class Job(Info):
    __tablename__ = u'Job'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    jobType_id = Column(Integer, ForeignKey('rbJobType.id'), nullable=False, index=True)
    orgStructure_id = Column(Integer, ForeignKey('OrgStructure.id'), nullable=False, index=True)
    date = Column(Date, nullable=False)
    begTime = Column(Time, nullable=False)
    endTime = Column(Time, nullable=False)
    quantity = Column(Integer, nullable=False)

    job_type = relationship(u'rbJobType', lazy='joined')
    org_structure = relationship(u'Orgstructure', lazy='joined')


class JobTicket(Info):
    __tablename__ = u'Job_Ticket'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, ForeignKey('Job.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    datetime = Column(DateTime, nullable=False)
    resTimestamp = Column(DateTime)
    resConnectionId = Column(Integer)
    status = Column(Integer, nullable=False, server_default=u"'0'")
    begDateTime = Column(DateTime)
    endDateTime = Column(DateTime)
    label = Column(String(64), nullable=False, server_default=u"''")
    note = Column(String(128), nullable=False, server_default=u"''")

    job = relationship(u'Job', lazy='joined')

    @property
    def jobType(self):
        self.job.job_type

    @property
    def orgStructure(self):
        self.job.org_structure

    def __unicode__(self):
        return u'%s, %s, %s' % (unicode(self.jobType),
                                unicode(self.datetime),
                                unicode(self.orgStructure))


class Lastchange(Info):
    __tablename__ = u'LastChanges'

    id = Column(Integer, primary_key=True)
    table = Column(String(32), nullable=False)
    table_key_id = Column(Integer, nullable=False)
    flags = Column(Text, nullable=False)


class Layoutattribute(Info):
    __tablename__ = u'LayoutAttribute'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1023), nullable=False)
    code = Column(String(255), nullable=False)
    typeName = Column(String(255))
    measure = Column(String(255))
    defaultValue = Column(String(1023))


class Layoutattributevalue(Info):
    __tablename__ = u'LayoutAttributeValue'

    id = Column(Integer, primary_key=True)
    actionPropertyType_id = Column(Integer, nullable=False)
    layoutAttribute_id = Column(ForeignKey('LayoutAttribute.id'), nullable=False, index=True)
    value = Column(String(1023), nullable=False)

    layoutAttribute = relationship(u'Layoutattribute')


class Licence(Info):
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


class LicenceService(Info):
    __tablename__ = u'Licence_Service'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    service_id = Column(Integer, nullable=False, index=True)


class Mkb(Info):
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

    def __unicode__(self):
        return self.DiagID  # + ' ' + self.DiagName

    @property
    def descr(self):
        mainCode = self.DiagID[:5]
        subclass = self.DiagID[5:]
        record = Query(Mkb).filter(Mkb.DiagID == mainCode).first()
        result = self.DiagID
        if record:
            result = record.DiagName
            if subclass:
                subclassId = record.MKBSubclass_id
                recordSubclass = (RbmkbsubclassItem.
                                  query.
                                  filter(RbmkbsubclassItem.master_id == subclassId,
                                         RbmkbsubclassItem.code == subclass).
                                  first())
                if recordSubclass:
                    result = u'{0} {1}'.format(result, recordSubclass.name)
                else:
                    result = u'{0} {1}'.format(result, subclass)
        return result



class MkbQuotatypePacientmodel(Info):
    __tablename__ = u'MKB_QuotaType_PacientModel'

    id = Column(Integer, primary_key=True)
    MKB_id = Column(Integer, nullable=False)
    pacientModel_id = Column(Integer, nullable=False)
    quotaType_id = Column(Integer, nullable=False)


class Media(Info):
    __tablename__ = u'Media'

    id = Column(Integer, primary_key=True)
    filename = Column(String(256, u'utf8_bin'), nullable=False)
    file = Column(MEDIUMBLOB)


class Medicalkindunit(Info):
    __tablename__ = u'MedicalKindUnit'

    id = Column(Integer, primary_key=True)
    rbMedicalKind_id = Column(ForeignKey('rbMedicalKind.id'), nullable=False, index=True)
    eventType_id = Column(ForeignKey('EventType.id'), index=True)
    rbMedicalAidUnit_id = Column(ForeignKey('rbMedicalAidUnit.id'), nullable=False, index=True)
    rbPayType_id = Column(ForeignKey('rbPayType.id'), nullable=False, index=True)
    rbTariffType_id = Column(ForeignKey('rbTariffType.id'), nullable=False, index=True)

    eventType = relationship(u'Eventtype')
    rbMedicalAidUnit = relationship(u'rbMedicalAidUnit')
    rbMedicalKind = relationship(u'rbMedicalKind')
    rbPayType = relationship(u'rbPayType')
    rbTariffType = relationship(u'rbTariffType')


class Meta(Info):
    __tablename__ = u'Meta'

    name = Column(String(100), primary_key=True)
    value = Column(Text)


class Modeldescription(Info):
    __tablename__ = u'ModelDescription'

    id = Column(Integer, primary_key=True)
    idx = Column(Integer, nullable=False, index=True, server_default=u"'0'")
    name = Column(String(64), nullable=False)
    fieldIdx = Column(Integer, nullable=False, server_default=u"'-1'")
    tableName = Column(String(64), nullable=False)


class Notificationoccurred(Info):
    __tablename__ = u'NotificationOccurred'

    id = Column(Integer, primary_key=True)
    eventDatetime = Column(DateTime, nullable=False)
    clientId = Column(Integer, nullable=False)
    userId = Column(ForeignKey('Person.id'), nullable=False, index=True)

    Person = relationship(u'Person')


class Orgstructure(Info):
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

    parent = relationship(u'Orgstructure', lazy="immediate", remote_side=[id])
    organisation = relationship(u'Organisation')
    Net = relationship(u'rbNet')

    def getNet(self):
        if self.Net is None:
            if self.parent:
                self.Net = self.parent.getNet()
            elif self.organisation:
                self.Net = self.organisation.net
        return self.Net

    def get_org_structure_full_name(self):
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
        return self.get_org_structure_full_name()

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


class OrgstructureActiontype(Info):
    __tablename__ = u'OrgStructure_ActionType'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    actionType_id = Column(Integer, index=True)


class OrgstructureAddres(Info):
    __tablename__ = u'OrgStructure_Address'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    house_id = Column(Integer, nullable=False, index=True)
    firstFlat = Column(Integer, nullable=False, server_default=u"'0'")
    lastFlat = Column(Integer, nullable=False, server_default=u"'0'")


class OrgstructureDisabledattendance(Info):
    __tablename__ = u'OrgStructure_DisabledAttendance'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('OrgStructure.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    attachType_id = Column(ForeignKey('rbAttachType.id'), index=True)
    disabledType = Column(Integer, nullable=False, server_default=u"'0'")

    attachType = relationship(u'rbAttachType')
    master = relationship(u'Orgstructure')


class OrgstructureEventtype(Info):
    __tablename__ = u'OrgStructure_EventType'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    eventType_id = Column(Integer, index=True)


class OrgstructureGap(Info):
    __tablename__ = u'OrgStructure_Gap'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    begTime = Column(Time, nullable=False)
    endTime = Column(Time, nullable=False)
    speciality_id = Column(Integer, index=True)
    person_id = Column(Integer, index=True)


class OrgstructureHospitalbed(Info):
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
    type = relationship(u'rbHospitalBedType')
    profile = relationship(u'rbHospitalBedProfile')
    schedule = relationship(u'rbHospitalBedShedule')

    @property
    def isPermanent(self):
        return self.isPermanentCode == 1


class OrgstructureJob(Info):
    __tablename__ = u'OrgStructure_Job'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    jobType_id = Column(Integer, index=True)
    begTime = Column(Time, nullable=False)
    endTime = Column(Time, nullable=False)
    quantity = Column(Integer, nullable=False)


class OrgstructureStock(Info):
    __tablename__ = u'OrgStructure_Stock'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('OrgStructure.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    finance_id = Column(ForeignKey('rbFinance.id'), index=True)
    constrainedQnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    orderQnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")

    finance = relationship(u'rbFinance')
    master = relationship(u'Orgstructure')
    nomenclature = relationship(u'rbNomenclature')


class Organisation(Info):
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
    fullName = Column(Unicode(255), nullable=False)
    shortName = Column(Unicode(255), nullable=False)
    title = Column(Unicode(255), nullable=False, index=True)
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
    region = Column(Unicode(40), nullable=False)
    Address = Column(Unicode(255), nullable=False)
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
    isLPU = Column(Integer, nullable=False, server_default=u"'0'")
    isStationary = Column(Integer, nullable=False, server_default=u"'0'")


    net = relationship(u'rbNet')
    OKPF = relationship(u'rbOKPF')
    OKFS = relationship(u'rbOKFS')
    org_accounts = relationship(u'OrganisationAccount')

    def __init__(self):
        self.title = ""
        self.fullName = ""
        self.shortName = ""

    @property
    def bank(self):
        return [account.bank for account in self.org_accounts]

    def __unicode__(self):
        return self.shortName


class OrganisationAccount(Info):
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


class OrganisationPolicyserial(Info):
    __tablename__ = u'Organisation_PolicySerial'

    id = Column(Integer, primary_key=True)
    organisation_id = Column(Integer, nullable=False, index=True)
    serial = Column(String(16), nullable=False)
    policyType_id = Column(Integer, index=True)


class Person(Info):
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

    post = relationship(u'rbPost')
    speciality = relationship(u'rbSpeciality')
    organisation = relationship(u'Organisation')
    orgStructure = relationship(u'Orgstructure')
    academicDegree = relationship(u'rbAcademicDegree')
    academicTitle = relationship(u'rbAcademicTitle')
    tariffCategory = relationship(u'rbTariffCategory')

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

    @property
    def nameText(self):
        return u' '.join((u'%s %s %s' % (self.lastName, self.firstName, self.patrName)).split())

    def __unicode__(self):
        result = formatShortNameInt(self.lastName, self.firstName, self.patrName)
        if self.speciality:
            result += ', '+self.speciality.name
        return unicode(result)


class Personaddres(Info):
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


class Persondocument(Info):
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


class Personeducation(Info):
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


class Personorder(Info):
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


class Persontimetemplate(Info):
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


class PersonActivity(Info):
    __tablename__ = u'Person_Activity'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    activity_id = Column(Integer, index=True)


class PersonProfile(Info):
    __tablename__ = u'Person_Profiles'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, nullable=False, index=True)
    userProfile_id = Column(Integer, nullable=False, index=True)


class PersonTimetemplate(Info):
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


class Pharmacy(Info):
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


class Prescriptionsendingre(Info):
    __tablename__ = u'PrescriptionSendingRes'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(100))
    version = Column(Integer)
    interval_id = Column(ForeignKey('DrugChart.id'), index=True)
    drugComponent_id = Column(ForeignKey('DrugComponent.id'), index=True)

    drugComponent = relationship(u'Drugcomponent')
    interval = relationship(u'Drugchart')


class Prescriptionsto1c(Info):
    __tablename__ = u'PrescriptionsTo1C'

    interval_id = Column(Integer, primary_key=True)
    errCount = Column(Integer, nullable=False, server_default=u"'0'")
    info = Column(String(1024))
    is_prescription = Column(Integer)
    new_status = Column(Integer)
    old_status = Column(Integer)
    sendTime = Column(DateTime, nullable=False, server_default=u'CURRENT_TIMESTAMP')


class QuotaCatalog(Info):
    __tablename__ = u'QuotaCatalog'

    id = Column(Integer, primary_key=True)
    finance_id = Column(ForeignKey('rbFinance.id'), nullable=False, index=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    catalogNumber = Column(Unicode(45), nullable=False, server_default=u"''")
    documentDate = Column(Date, nullable=True)
    documentNumber = Column(Unicode(45), nullable=True)
    documentCorresp = Column(Unicode(256), nullable=True)
    comment = Column(UnicodeText, nullable=True)

    finance = relationship('rbFinance', lazy=False)

    def __unicode__(self):
        return u'Приказ %s № %s от %s' % (
            self.documentCorresp,
            self.documentNumber,
            self.documentNumber
        )


class QuotaType(Info):
    __tablename__ = u'QuotaType'

    id = Column(Integer, primary_key=True)
    catalog_id = Column(ForeignKey('QuotaCatalog.id'), nullable=False, index=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    class_ = Column(u'class', Integer, nullable=False)
    profile_code = Column(String(16))
    group_code = Column(String(16))
    type_code = Column(String(16))
    code = Column(String(16), nullable=False)
    name = Column(Unicode(255), nullable=False)
    teenOlder = Column(Integer, nullable=False)
    price = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")

    catalog = relationship('QuotaCatalog', backref='quotaTypes')

    def __unicode__(self):
        return self.name


class MKB_VMPQuotaFilter(Info):
    __tablename__ = u'MKB_VMPQuotaFilter'

    id = Column(Integer, primary_key=True)
    MKB_id = Column(ForeignKey('MKB.id'), nullable=False, index=True)
    quotaDetails_id = Column(ForeignKey('VMPQuotaDetails.id'), nullable=False, index=True)


class VMPQuotaDetails(Info):
    __tablename__ = u'VMPQuotaDetails'

    id = Column(Integer, primary_key=True)
    pacientModel_id = Column(ForeignKey('rbPacientModel.id'), nullable=False, index=True)
    treatment_id = Column(ForeignKey('rbTreatment.id'), nullable=False, index=True)
    quotaType_id = Column(ForeignKey('QuotaType.id'), nullable=False, index=True)

    patientModel = relationship('rbPacientModel', lazy=False)
    treatment = relationship('rbTreatment', lazy=False)
    quotaType = relationship('QuotaType', lazy=False, backref='quotaDetails')
    mkb = relationship('Mkb', secondary=MKB_VMPQuotaFilter.__table__)

    def __unicode__(self):
        return u'%s [%s]' % (self.treatment.name, self.patientModel.name)


class Quoting(Info):
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


class Quotingbyspeciality(Info):
    __tablename__ = u'QuotingBySpeciality'

    id = Column(Integer, primary_key=True)
    speciality_id = Column(ForeignKey('rbSpeciality.id'), nullable=False, index=True)
    organisation_id = Column(ForeignKey('Organisation.id'), nullable=False, index=True)
    coupons_quote = Column(Integer)
    coupons_remaining = Column(Integer)

    organisation = relationship(u'Organisation')
    speciality = relationship(u'rbSpeciality')


class Quotingbytime(Info):
    __tablename__ = u'QuotingByTime'

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer)
    quoting_date = Column(Date, nullable=False)
    QuotingTimeStart = Column(Time, nullable=False)
    QuotingTimeEnd = Column(Time, nullable=False)
    QuotingType = Column(Integer)


class QuotingRegion(Info):
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


class Setting(Info):
    __tablename__ = u'Setting'

    id = Column(Integer, primary_key=True)
    path = Column(String(255), nullable=False, unique=True)
    value = Column(Text, nullable=False)


class Socstatu(Info):
    __tablename__ = u'SocStatus'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    socStatusClass_id = Column(Integer, nullable=False, index=True)
    socStatusType_id = Column(Integer, nullable=False, index=True)


class Stockmotion(Info):
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


class StockmotionItem(Info):
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

    finance = relationship(u'rbFinance', primaryjoin='StockmotionItem.finance_id == rbFinance.id')
    master = relationship(u'Stockmotion')
    nomenclature = relationship(u'rbNomenclature')
    oldFinance = relationship(u'rbFinance', primaryjoin='StockmotionItem.oldFinance_id == rbFinance.id')


class Stockrecipe(Info):
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


class StockrecipeItem(Info):
    __tablename__ = u'StockRecipe_Item'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('StockRecipe.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    qnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    isOut = Column(Integer, nullable=False, server_default=u"'0'")

    master = relationship(u'Stockrecipe')
    nomenclature = relationship(u'rbNomenclature')


class Stockrequisition(Info):
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


class StockrequisitionItem(Info):
    __tablename__ = u'StockRequisition_Item'

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('StockRequisition.id'), nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    finance_id = Column(ForeignKey('rbFinance.id'), index=True)
    qnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    satisfiedQnt = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")

    finance = relationship(u'rbFinance')
    master = relationship(u'Stockrequisition')
    nomenclature = relationship(u'rbNomenclature')


class Stocktran(Info):
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

    creFinance = relationship(u'rbFinance', primaryjoin='Stocktran.creFinance_id == rbFinance.id')
    creNomenclature = relationship(u'rbNomenclature', primaryjoin='Stocktran.creNomenclature_id == rbNomenclature.id')
    creOrgStructure = relationship(u'Orgstructure', primaryjoin='Stocktran.creOrgStructure_id == Orgstructure.id')
    debFinance = relationship(u'rbFinance', primaryjoin='Stocktran.debFinance_id == rbFinance.id')
    debNomenclature = relationship(u'rbNomenclature', primaryjoin='Stocktran.debNomenclature_id == rbNomenclature.id')
    debOrgStructure = relationship(u'Orgstructure', primaryjoin='Stocktran.debOrgStructure_id == Orgstructure.id')
    stockMotionItem = relationship(u'StockmotionItem')


Action_TakenTissueJournal = Table('Action_TakenTissueJournal', metadata,
                                  Column('action_id', Integer, ForeignKey('Action.id')),
                                  Column('takenTissueJournal_id', Integer, ForeignKey('TakenTissueJournal.id'))
                                  )


class TakenTissueJournal(Info):
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
    note = Column(String(128), nullable=False, default='')
    barcode = Column(Integer, nullable=False)  # set with trigger
    period = Column(Integer, nullable=False)  # set with trigger
    testTubeType_id = Column(ForeignKey('rbTestTubeType.id'), index=True)
    statusCode = Column("status", Integer, nullable=False, server_default=u"'0'")

    client = relationship(u'Client')
    execPerson = relationship(u'Person')
    tissueType = relationship(u'rbTissueType')
    testTubeType = relationship(u'rbTestTubeType')
    unit = relationship(u'rbUnit')
    actions = relationship(u'Action', secondary=Action_TakenTissueJournal, lazy='joined')

    @property
    def barcode_s(self):
        return code128C(self.barcode).decode('windows-1252')

    # @property
    # def status(self):
    #     return TTJStatus(self.statusCode) if self.statusCode is not None else None


class Tempinvalid(Info):
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


class Tempinvalidduplicate(Info):
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


class TempinvalidPeriod(Info):
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


class Tissue(Info):
    __tablename__ = u'Tissue'

    id = Column(Integer, primary_key=True)
    type_id = Column(ForeignKey('rbTissueType.id'), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    barcode = Column(String(255), nullable=False, index=True)
    event_id = Column(ForeignKey('Event.id'), nullable=False, index=True)

    event = relationship(u'Event')
    type = relationship(u'rbTissueType')


class Uuid(Info):
    __tablename__ = u'UUID'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(100), nullable=False, unique=True)


class Variablesforsql(Info):
    __tablename__ = u'VariablesforSQL'

    id = Column(Integer, primary_key=True)
    specialVarName_id = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False)
    var_type = Column(String(64), nullable=False)
    label = Column(String(64), nullable=False)


class Version(Info):
    __tablename__ = u'Versions'

    id = Column(Integer, primary_key=True)
    table = Column(String(64), nullable=False, unique=True)
    version = Column(Integer, nullable=False, server_default=u"'0'")


class Visit(Info):
    __tablename__ = u'Visit'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    event_id = Column(Integer, ForeignKey('Event.id'), nullable=False, index=True)
    scene_id = Column(Integer, ForeignKey('rbScene.id'), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    visitType_id = Column(Integer, ForeignKey('rbVisitType.id'), nullable=False, index=True)
    person_id = Column(Integer, ForeignKey('Person.id'), nullable=False, index=True)
    isPrimary = Column(Integer, nullable=False)
    finance_id = Column(Integer, ForeignKey('rbFinance.id'), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey('rbService.id'), index=True)
    payStatus = Column(Integer, nullable=False)

    service = relationship(u'rbService')
    person = relationship(u'Person')
    finance = relationship(u'rbFinance')
    scene = relationship(u'rbScene')
    type = relationship(u'rbVisitType')
    event = relationship(u'Event')


class ActionDocument(Info):
    __tablename__ = u'action_document'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    modify_date = Column(DateTime, nullable=False)
    template_id = Column(ForeignKey('rbPrintTemplate.id'), nullable=False, index=True)
    document = Column(MEDIUMBLOB, nullable=False)

    action = relationship(u'Action')
    template = relationship(u'rbPrintTemplate')


class BbtResponse(Info):
    __tablename__ = u'bbtResponse'

    id = Column(ForeignKey('Action.id'), primary_key=True)
    final = Column(Integer, nullable=False, server_default=u"'0'")
    defects = Column(Text)
    doctor_id = Column(ForeignKey('Person.id'), nullable=False, index=True)
    codeLIS = Column(String(20), nullable=False)

    doctor = relationship(u'Person')
    values_organism = relationship(
        u'BbtResultOrganism',
        primaryjoin='BbtResponse.id == BbtResultOrganism.action_id',
        foreign_keys=[id],
        uselist=True
    )
    values_text = relationship(
        u'BbtResultText',
        primaryjoin='BbtResponse.id == BbtResultText.action_id',
        foreign_keys=[id],
        uselist=True
    )
    # values_table = relationship(u'BbtResultTable')
    # values_image = relationship(u'BbtResultImage')


class BbtResultOrganism(Info):
    __tablename__ = u'bbtResult_Organism'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    organism_id = Column(ForeignKey('rbMicroorganism.id'), nullable=False, index=True)
    concentration = Column(String(256), nullable=False)

    microorganism = relationship(u'rbMicroorganism', lazy='joined')
    sens_values = relationship(u'BbtOrganism_SensValues', lazy='joined')


class BbtOrganism_SensValues(Info):
    __tablename__ = u'bbtOrganism_SensValues'
    __table_args__ = (
        Index(u'bbtResult_Organism_id_index', u'bbtResult_Organism_id'),
    )

    id = Column(Integer, primary_key=True)
    bbtResult_Organism_id = Column(ForeignKey('bbtResult_Organism.id'), nullable=False)
    antibiotic_id = Column(ForeignKey('rbAntibiotic.id'), index=True)
    MIC = Column(String(20), nullable=False)
    activity = Column(String(5), nullable=False)

    antibiotic = relationship(u'rbAntibiotic', lazy='joined')


class BbtResultText(Info):
    __tablename__ = u'bbtResult_Text'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    valueText = Column(Text)


class BbtResultTable(Info):
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

    indicator = relationship(u'rbBacIndicator')


class BbtResultImage(Info):
    __tablename__ = u'bbtResult_Image'
    __table_args__ = (
        Index(u'action_id_index', u'action_id', u'idx'),
    )

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False)
    idx = Column(Integer, nullable=False)
    description = Column(String(256))
    image = Column(BLOB, nullable=False)


class Mrbmodelagegroup(Info):
    __tablename__ = u'mrbModelAgeGroup'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelaidcase(Info):
    __tablename__ = u'mrbModelAidCase'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelaidpurpose(Info):
    __tablename__ = u'mrbModelAidPurpose'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelcategory(Info):
    __tablename__ = u'mrbModelCategory'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelcontinuation(Info):
    __tablename__ = u'mrbModelContinuation'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodeldiseaseclas(Info):
    __tablename__ = u'mrbModelDiseaseClass'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelexpectedresult(Info):
    __tablename__ = u'mrbModelExpectedResult'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelinstitutiontype(Info):
    __tablename__ = u'mrbModelInstitutionType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelsertificationrequirement(Info):
    __tablename__ = u'mrbModelSertificationRequirement'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class Mrbmodelstatebadnes(Info):
    __tablename__ = u'mrbModelStateBadness'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(128), nullable=False)


class NewTable(Info):
    __tablename__ = u'new_table'

    idnew_table = Column(Integer, primary_key=True)


class Rb64district(Info):
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


class Rb64placetype(Info):
    __tablename__ = u'rb64PlaceType'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class Rb64reason(Info):
    __tablename__ = u'rb64Reason'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class Rb64streettype(Info):
    __tablename__ = u'rb64StreetType'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class rbAPTable(Info):
    __tablename__ = u'rbAPTable'

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(256), nullable=False)
    tableName = Column(String(256), nullable=False)
    masterField = Column(String(256), nullable=False)


class rbAPTablefield(Info):
    __tablename__ = u'rbAPTableField'

    id = Column(Integer, primary_key=True)
    idx = Column(Integer, nullable=False)
    master_id = Column(ForeignKey('rbAPTable.id'), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    fieldName = Column(String(256), nullable=False)
    referenceTable = Column(String(256))

    master = relationship(u'rbAPTable', backref="fields")


class rbAcademicDegree(RBInfo):
    __tablename__ = u'rbAcademicDegree'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False)
    name = Column(Unicode(64), nullable=False)

    def __unicode__(self):
        return self.name


class rbAcademicTitle(RBInfo):
    __tablename__ = u'rbAcademicTitle'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)

    def __unicode__(self):
        return self.name


class rbAccountExportFormat(RBInfo):
    __tablename__ = u'rbAccountExportFormat'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    prog = Column(String(128), nullable=False)
    preferentArchiver = Column(String(128), nullable=False)
    emailRequired = Column(Integer, nullable=False)
    emailTo = Column(String(64), nullable=False)
    subject = Column(Unicode(128), nullable=False)
    message = Column(Text, nullable=False)


class rbAccountingSystem(RBInfo):
    __tablename__ = u'rbAccountingSystem'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    isEditable = Column(Integer, nullable=False, server_default=u"'0'")
    showInClientInfo = Column(Integer, nullable=False, server_default=u"'0'")


class rbAcheResult(RBInfo):
    __tablename__ = u'rbAcheResult'

    id = Column(Integer, primary_key=True)
    eventPurpose_id = Column(ForeignKey('rbEventTypePurpose.id'), nullable=False, index=True)
    code = Column(String(3, u'utf8_unicode_ci'), nullable=False)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)

    eventPurpose = relationship(u'rbEventTypePurpose')


class rbActionShedule(Info):
    __tablename__ = u'rbActionShedule'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, server_default=u"''")
    name = Column(String(64), nullable=False, server_default=u"''")
    period = Column(Integer, nullable=False, server_default=u"'1'")


class rbActionSheduleItem(Info):
    __tablename__ = u'rbActionShedule_Item'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    idx = Column(Integer, nullable=False, server_default=u"'0'")
    offset = Column(Integer, nullable=False, server_default=u"'0'")
    time = Column(Time, nullable=False, server_default=u"'00:00:00'")


class rbActivity(Info):
    __tablename__ = u'rbActivity'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    regionalCode = Column(String(8), nullable=False, index=True)


class rbAgreementType(Info):
    __tablename__ = u'rbAgreementType'

    id = Column(Integer, primary_key=True)
    code = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)
    quotaStatusModifier = Column(Integer, server_default=u"'0'")


class rbAnalysisStatus(Info):
    __tablename__ = u'rbAnalysisStatus'

    id = Column(Integer, primary_key=True)
    statusName = Column(String(80), nullable=False, unique=True)


class rbAnalyticalReports(Info):
    __tablename__ = u'rbAnalyticalReports'

    id = Column(Integer, primary_key=True)
    name = Column(String(45))
    PrintTemplate_id = Column(Integer)


class rbAntibiotic(RBInfo):
    __tablename__ = u'rbAntibiotic'

    id = Column(Integer, primary_key=True)
    code = Column(String(128), nullable=False)
    name = Column(String(256), nullable=False)


class rbAttachType(Info):
    __tablename__ = u'rbAttachType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    temporary = Column(Integer, nullable=False)
    outcome = Column(Integer, nullable=False)
    finance_id = Column(Integer, nullable=False, index=True)


class rbBacIndicator(RBInfo):
    __tablename__ = u'rbBacIndicator'

    id = Column(Integer, primary_key=True)
    code = Column(String(128), nullable=False)
    name = Column(String(256), nullable=False)


class rbBlankActions(Info):
    __tablename__ = u'rbBlankActions'

    id = Column(Integer, primary_key=True)
    doctype_id = Column(ForeignKey('ActionType.id'), nullable=False, index=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    checkingSerial = Column(Integer, nullable=False)
    checkingNumber = Column(Integer, nullable=False)
    checkingAmount = Column(Integer, nullable=False)

    doctype = relationship(u'Actiontype')


class rbBlankTempInvalids(Info):
    __tablename__ = u'rbBlankTempInvalids'

    id = Column(Integer, primary_key=True)
    doctype_id = Column(ForeignKey('rbTempInvalidDocument.id'), nullable=False, index=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    checkingSerial = Column(Integer, nullable=False)
    checkingNumber = Column(Integer, nullable=False)
    checkingAmount = Column(Integer, nullable=False)

    doctype = relationship(u'rbTempInvalidDocument')


class rbBloodType(RBInfo):
    __tablename__ = u'rbBloodType'

    id = Column(Integer, primary_key=True)
    code = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)


class rbCashOperation(RBInfo):
    __tablename__ = u'rbCashOperation'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False)


class rbComplain(Info):
    __tablename__ = u'rbComplain'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, index=True)
    code = Column(String(64), nullable=False, index=True)
    name = Column(String(120), nullable=False, index=True)


class rbContactType(RBInfo):
    __tablename__ = u'rbContactType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class rbCoreActionProperty(Info):
    __tablename__ = u'rbCoreActionProperty'

    id = Column(Integer, primary_key=True)
    actionType_id = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False)
    actionPropertyType_id = Column(Integer, nullable=False)


class rbCounter(Info):
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


class rbDiagnosisType(RBInfo):
    __tablename__ = u'rbDiagnosisType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    replaceInDiagnosis = Column(String(8), nullable=False)
    flatCode = Column(String(64), nullable=False)


class rbDiet(Info):
    __tablename__ = u'rbDiet'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class rbDiseaseCharacter(RBInfo):
    __tablename__ = u'rbDiseaseCharacter'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    replaceInDiagnosis = Column(String(8), nullable=False)


class rbDiseasePhases(Info):
    __tablename__ = u'rbDiseasePhases'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    characterRelation = Column(Integer, nullable=False, server_default=u"'0'")


class rbDiseaseStage(Info):
    __tablename__ = u'rbDiseaseStage'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    characterRelation = Column(Integer, nullable=False, server_default=u"'0'")


class rbDispanser(RBInfo):
    __tablename__ = u'rbDispanser'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    observed = Column(Integer, nullable=False)


class rbDocumentType(RBInfo):
    __tablename__ = u'rbDocumentType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    regionalCode = Column(String(16), nullable=False)
    name = Column(Unicode(64), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey('rbDocumentTypeGroup.id'), nullable=False, index=True)
    serial_format = Column(Integer, nullable=False)
    number_format = Column(Integer, nullable=False)
    federalCode = Column(String(16), nullable=False)
    socCode = Column(String(8), nullable=False, index=True)
    TFOMSCode = Column(Integer)

    group = relationship(u'rbDocumentTypeGroup')

    def __init__(self):
        RBInfo.__init__(self)


class rbDocumentTypeGroup(RBInfo):
    __tablename__ = u'rbDocumentTypeGroup'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)

    def __init__(self):
        RBInfo.__init__(self)


class rbEmergencyAccident(Info):
    __tablename__ = u'rbEmergencyAccident'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyCauseCall(Info):
    __tablename__ = u'rbEmergencyCauseCall'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)
    typeCause = Column(Integer, nullable=False, server_default=u"'0'")


class rbEmergencyDeath(Info):
    __tablename__ = u'rbEmergencyDeath'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyDiseased(Info):
    __tablename__ = u'rbEmergencyDiseased'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyEbriety(Info):
    __tablename__ = u'rbEmergencyEbriety'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyMethodTransportation(Info):
    __tablename__ = u'rbEmergencyMethodTransportation'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyPlaceCall(Info):
    __tablename__ = u'rbEmergencyPlaceCall'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyPlaceReceptionCall(Info):
    __tablename__ = u'rbEmergencyPlaceReceptionCall'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyReasondDelays(Info):
    __tablename__ = u'rbEmergencyReasondDelays'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyReceivedCall(Info):
    __tablename__ = u'rbEmergencyReceivedCall'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyResult(Info):
    __tablename__ = u'rbEmergencyResult'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyTransferredTransportation(Info):
    __tablename__ = u'rbEmergencyTransferredTransportation'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEmergencyTypeAsset(RBInfo):
    __tablename__ = u'rbEmergencyTypeAsset'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    codeRegional = Column(String(8), nullable=False, index=True)


class rbEventProfile(Info):
    __tablename__ = u'rbEventProfile'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    regionalCode = Column(String(16), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class rbEventTypePurpose(RBInfo):
    __tablename__ = u'rbEventTypePurpose'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    codePlace = Column(String(2))

    def __init__(self):
        RBInfo.__init__(self)


class rbFinance(RBInfo):
    __tablename__ = u'rbFinance'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)

    def __init__(self):
        RBInfo.__init__(self)


class rbFinance1C(Info):
    __tablename__ = u'rbFinance1C'

    id = Column(Integer, primary_key=True)
    code1C = Column(String(127), nullable=False)
    finance_id = Column(ForeignKey('rbFinance.id'), nullable=False, index=True)

    finance = relationship(u'rbFinance')


class rbHealthGroup(Info):
    __tablename__ = u'rbHealthGroup'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class rbHospitalBedProfile(RBInfo):
    __tablename__ = u'rbHospitalBedProfile'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    service_id = Column(Integer, index=True)

    def __init__(self):
        RBInfo.__init__(self)


class rbHospitalBedProfile_Service(Info):
    __tablename__ = u'rbHospitalBedProfile_Service'

    id = Column(Integer, primary_key=True)
    rbHospitalBedProfile_id = Column(ForeignKey('rbHospitalBedProfile.id'), nullable=False, index=True)
    rbService_id = Column(ForeignKey('rbService.id'), nullable=False, index=True)

    rbHospitalBedProfile = relationship(u'rbHospitalBedProfile')
    rbService = relationship(u'rbService')


class rbHospitalBedShedule(RBInfo):
    __tablename__ = u'rbHospitalBedShedule'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class rbHospitalBedType(RBInfo):
    __tablename__ = u'rbHospitalBedType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class rbHurtFactorType(Info):
    __tablename__ = u'rbHurtFactorType'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(250), nullable=False, index=True)


class rbHurtType(RBInfo):
    __tablename__ = u'rbHurtType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(256), nullable=False, index=True)


class rbImageMap(Info):
    __tablename__ = u'rbImageMap'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False)
    name = Column(String(64), nullable=False)
    image = Column(MEDIUMBLOB, nullable=False)
    markSize = Column(Integer)


class rbJobType(RBInfo):
    __tablename__ = u'rbJobType'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, index=True)
    code = Column(String(64), nullable=False)
    regionalCode = Column(String(64), nullable=False)
    name = Column(Unicode(128), nullable=False)
    laboratory_id = Column(Integer, index=True)
    isInstant = Column(Integer, nullable=False, server_default=u"'0'")

    def __init__(self):
        RBInfo.__init__(self)


class rbLaboratory(Info):
    __tablename__ = u'rbLaboratory'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    protocol = Column(Integer, nullable=False)
    address = Column(String(128), nullable=False)
    ownName = Column(String(128), nullable=False)
    labName = Column(String(128), nullable=False)


class rbLaboratory_Test(Info):
    __tablename__ = u'rbLaboratory_Test'
    __table_args__ = (
        Index(u'code', u'book', u'code'),
    )

    id = Column(Integer, primary_key=True)
    master_id = Column(ForeignKey('rbLaboratory.id'), nullable=False, index=True)
    test_id = Column(ForeignKey('rbTest.id'), nullable=False, index=True)
    book = Column(String(64), nullable=False)
    code = Column(String(64), nullable=False)

    test = relationship(u'rbTest', backref="lab_test")
    laboratory = relationship(u'rbLaboratory')


class Rbmkbsubclas(Info):
    __tablename__ = u'rbMKBSubclass'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False)
    name = Column(String(128), nullable=False)


class RbmkbsubclassItem(Info):
    __tablename__ = u'rbMKBSubclass_Item'
    __table_args__ = (
        Index(u'master_id', u'master_id', u'code'),
    )

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False)
    code = Column(String(8), nullable=False)
    name = Column(String(128), nullable=False)


class rbMealTime(Info):
    __tablename__ = u'rbMealTime'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    begTime = Column(Time, nullable=False)
    endTime = Column(Time, nullable=False)


class rbMedicalAidProfile(Info):
    __tablename__ = u'rbMedicalAidProfile'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    regionalCode = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)


class rbMedicalAidType(Info):
    __tablename__ = u'rbMedicalAidType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False)


class rbMedicalAidUnit(Info):
    __tablename__ = u'rbMedicalAidUnit'

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    descr = Column(String(64), nullable=False)
    regionalCode = Column(String(1), nullable=False)


class rbMedicalKind(Info):
    __tablename__ = u'rbMedicalKind'

    id = Column(Integer, primary_key=True)
    code = Column(String(1, u'utf8_unicode_ci'), nullable=False)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)


class rbMenu(Info):
    __tablename__ = u'rbMenu'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class rbMenu_Content(Info):
    __tablename__ = u'rbMenu_Content'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    mealTime_id = Column(Integer, nullable=False, index=True)
    diet_id = Column(Integer, nullable=False, index=True)


class rbMesSpecification(RBInfo):
    __tablename__ = u'rbMesSpecification'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    regionalCode = Column(String(16), nullable=False)
    name = Column(Unicode(64), nullable=False)
    done = Column(Integer, nullable=False)


class rbMethodOfAdministration(RBInfo):
    __tablename__ = u'rbMethodOfAdministration'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class rbMicroorganism(RBInfo):
    __tablename__ = u'rbMicroorganism'

    id = Column(Integer, primary_key=True)
    code = Column(String(128), nullable=False)
    name = Column(String(256), nullable=False)


class rbNet(RBInfo):
    __tablename__ = u'rbNet'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    sexCode = Column("sex", Integer, nullable=False, server_default=u"'0'")
    age = Column(Unicode(9), nullable=False)
    age_bu = Column(Integer)
    age_bc = Column(SmallInteger)
    age_eu = Column(Integer)
    age_ec = Column(SmallInteger)

    @property
    def sex(self):
        return formatSex(self.sexCode)


class rbNomenclature(Info):
    __tablename__ = u'rbNomenclature'

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('rbNomenclature.id'), index=True)
    code = Column(String(64), nullable=False)
    regionalCode = Column(String(64), nullable=False)
    name = Column(String(128), nullable=False)

    group = relationship(u'rbNomenclature', remote_side=[id])


class rbOKFS(RBInfo):
    __tablename__ = u'rbOKFS'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    ownership = Column(Integer, nullable=False, server_default=u"'0'")


class rbOKPF(RBInfo):
    __tablename__ = u'rbOKPF'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class rbOKVED(Info):
    __tablename__ = u'rbOKVED'

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, index=True)
    div = Column(String(10), nullable=False)
    class_ = Column(u'class', String(2), nullable=False)
    group_ = Column(String(2), nullable=False)
    vid = Column(String(2), nullable=False)
    OKVED = Column(String(8), nullable=False, index=True)
    name = Column(String(250), nullable=False, index=True)


class rbOperationType(RBInfo):
    __tablename__ = u'rbOperationType'

    id = Column(Integer, primary_key=True)
    cd_r = Column(Integer, nullable=False)
    cd_subr = Column(Integer, nullable=False)
    code = Column(String(8), nullable=False, index=True)
    ktso = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False, index=True)

    def __unicode__(self):
        return self.code + ' ' + self.name


class rbPacientModel(RBInfo):
    __tablename__ = u'rbPacientModel'

    id = Column(Integer, primary_key=True)
    code = Column(String(32), nullable=False)
    name = Column(Text, nullable=False)


class rbPayRefuseType(RBInfo):
    __tablename__ = u'rbPayRefuseType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(128), nullable=False, index=True)
    finance_id = Column(Integer, nullable=False, index=True)
    rerun = Column(Integer, nullable=False)


class rbPolicyType(RBInfo):
    __tablename__ = u'rbPolicyType'

    id = Column(Integer, primary_key=True)
    code = Column(String(64), nullable=False, unique=True)
    name = Column(Unicode(256), nullable=False, index=True)
    TFOMSCode = Column(String(8))


class rbPost(RBInfo):
    __tablename__ = u'rbPost'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    regionalCode = Column(String(8), nullable=False)
    key = Column(String(6), nullable=False, index=True)
    high = Column(String(6), nullable=False)
    flatCode = Column(String(65), nullable=False)


class rbPrintTemplate(Info):
    __tablename__ = u'rbPrintTemplate'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    context = Column(String(64), nullable=False)
    fileName = Column(String(128), nullable=False)
    default = Column(String, nullable=False)
    dpdAgreement = Column(Integer, nullable=False, server_default=u"'0'")
    render = Column(Integer, nullable=False, server_default=u"'0'")
    templateText = Column(String, nullable=False)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")

    meta_data = relationship('rbPrintTemplateMeta', lazy=False, order_by='rbPrintTemplateMeta.id')


class rbQuotaStatus(Info):
    __tablename__ = u'rbQuotaStatus'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(50), nullable=False, index=True)


class rbReasonOfAbsence(RBInfo):
    __tablename__ = u'rbReasonOfAbsence'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)


class rbRelationType(RBInfo):
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


class rbRequestType(RBInfo):
    __tablename__ = u'rbRequestType'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    relevant = Column(Integer, nullable=False, server_default=u"'1'")


class rbResult(RBInfo):
    __tablename__ = u'rbResult'

    id = Column(Integer, primary_key=True)
    eventPurpose_id = Column(Integer, nullable=False, index=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    continued = Column(Integer, nullable=False)
    regionalCode = Column(String(8), nullable=False)


class rbScene(RBInfo):
    __tablename__ = u'rbScene'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    serviceModifier = Column(Unicode(128), nullable=False)


class rbService(RBInfo):
    __tablename__ = u'rbService'
    __table_args__ = (
        Index(u'infis', u'infis', u'eisLegacy'),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(31), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    eisLegacy = Column(Boolean, nullable=False)
    nomenclatureLegacy = Column(Integer, nullable=False, server_default=u"'0'")
    license = Column(Integer, nullable=False)
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
    isComplex = Column(SmallInteger, nullable=False, server_default=u"'0'")

    medicalAidProfile = relationship(u'rbMedicalAidProfile')
    rbMedicalKind = relationship(u'rbMedicalKind')
    subservice_assoc = relationship(
        'rbServiceGroupAssoc',
        primaryjoin='rbService.id==rbServiceGroupAssoc.group_id'
    )


class rbServiceGroupAssoc(Base):
    __tablename__ = u'rbServiceGroup'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('rbService.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('rbService.id'), nullable=False)
    required = Column(SmallInteger, nullable=False, server_default="'0'")
    serviceKind_id = Column(Integer, ForeignKey('rbServiceKind.id'), nullable=False)

    subservice = relationship('rbService', foreign_keys=[service_id])
    service_kind = relationship('rbServiceKind')

    def __json__(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'service_id': self.service_id,
            'serviceKind_id': self.serviceKind_id
        }

    def __int__(self):
        return self.id


class rbServiceClass(Info):
    __tablename__ = u'rbServiceClass'
    __table_args__ = (
        Index(u'section', u'section', u'code'),
    )

    id = Column(Integer, primary_key=True)
    section = Column(String(1), nullable=False)
    code = Column(String(3), nullable=False)
    name = Column(String(200), nullable=False)


class rbServiceFinance(Info):
    __tablename__ = u'rbServiceFinance'

    id = Column(Integer, primary_key=True)
    code = Column(String(2, u'utf8_unicode_ci'), nullable=False)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)


class rbServiceSection(Info):
    __tablename__ = u'rbServiceSection'

    id = Column(Integer, primary_key=True)
    code = Column(String(1), nullable=False)
    name = Column(String(100), nullable=False)


class rbServiceType(Info):
    __tablename__ = u'rbServiceType'
    __table_args__ = (
        Index(u'section', u'section', u'code'),
    )

    id = Column(Integer, primary_key=True)
    section = Column(String(1), nullable=False)
    code = Column(String(3), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)


class rbServiceUET(Info):
    __tablename__ = u'rbServiceUET'

    id = Column(Integer, primary_key=True)
    rbService_id = Column(ForeignKey('rbService.id'), nullable=False, index=True)
    age = Column(String(10, u'utf8_unicode_ci'), nullable=False)
    UET = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")

    rbService = relationship(u'rbService')


class rbService_Profile(Info):
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

    master = relationship(u'rbService')
    medicalAidProfile = relationship(u'rbMedicalAidProfile')
    speciality = relationship(u'rbSpeciality')


class rbSocStatusClass(Info):
    __tablename__ = u'rbSocStatusClass'

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('rbSocStatusClass.id'), index=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)

    group = relationship(u'rbSocStatusClass', remote_side=[id])

    def __unicode__(self):
        return self.name

# class Rbsocstatusclasstypeassoc(Info):
#     __tablename__ = u'rbSocStatusClassTypeAssoc'
#     __table_args__ = (
#         Index(u'type_id', u'type_id', u'class_id'),
#     )
#
#     id = Column(Integer, primary_key=True)
#     class_id = Column(Integer, ForeignKey('rbSocStatusClass.id'), nullable=False, index=True)
#     type_id = Column(Integer, ForeignKey('rbSocStatusType.id'), nullable=False)
Rbsocstatusclasstypeassoc = Table('rbSocStatusClassTypeAssoc', metadata,
    Column('class_id', Integer, ForeignKey('rbSocStatusClass.id')),
    Column('type_id', Integer, ForeignKey('rbSocStatusType.id'))
    )


class rbSocStatusType(Info):
    __tablename__ = u'rbSocStatusType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(250), nullable=False, index=True)
    socCode = Column(String(8), nullable=False, index=True)
    TFOMSCode = Column(Integer)
    regionalCode = Column(String(8), nullable=False)

    classes = relationship(u'rbSocStatusClass', secondary=Rbsocstatusclasstypeassoc)


class rbSpecialVariablesPreferences(Info):
    __tablename__ = u'rbSpecialVariablesPreferences'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    arguments_raw = Column('arguments', Text)
    query_text = Column('query', Text, nullable=False)

    @property
    def arguments(self):
        import json
        try:
            return json.loads(self.arguments_raw) or []
        except:
            return []


class rbSpeciality(RBInfo):
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


class rbStorage(Info):
    __tablename__ = u'rbStorage'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(50), nullable=False, unique=True)
    name = Column(String(256))
    orgStructure_id = Column(ForeignKey('OrgStructure.id'), index=True)

    orgStructure = relationship(u'Orgstructure')


class rbTariffCategory(RBInfo):
    __tablename__ = u'rbTariffCategory'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class rbTariffType(Info):
    __tablename__ = u'rbTariffType'

    id = Column(Integer, primary_key=True)
    code = Column(String(2, u'utf8_unicode_ci'), nullable=False)
    name = Column(String(64, u'utf8_unicode_ci'), nullable=False)


class rbTempInvalidBreak(Info):
    __tablename__ = u'rbTempInvalidBreak'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False, server_default=u"'0'")
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(80), nullable=False, index=True)


class rbTempInvalidDocument(Info):
    __tablename__ = u'rbTempInvalidDocument'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(80), nullable=False, index=True)
    checkingSerial = Column(Enum(u'???', u'?????', u'??????'), nullable=False)
    checkingNumber = Column(Enum(u'???', u'?????', u'??????'), nullable=False)
    checkingAmount = Column(Enum(u'???', u'????????'), nullable=False)


class rbTempInvalidDuplicateReason(Info):
    __tablename__ = u'rbTempInvalidDuplicateReason'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False)


class rbTempInvalidReason(Info):
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


class rbTempInvalidRegime(Info):
    __tablename__ = u'rbTempInvalidRegime'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False, server_default=u"'0'")
    doctype_id = Column(Integer, index=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)


class rbTempInvalidResult(RBInfo):
    __tablename__ = u'rbTempInvalidResult'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False, server_default=u"'0'")
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(80), nullable=False, index=True)
    able = Column(Integer, nullable=False)
    closed = Column(Integer, nullable=False, server_default=u"'0'")
    status = Column(Integer, nullable=False)


class rbTest(RBInfo):
    __tablename__ = u'rbTest'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")


class rbTest_Service(Info):
    __tablename__ = u'rbTest_Service'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('rbTest.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('rbService.id'), nullable=False)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date)


class rbTestTubeType(RBInfo):
    __tablename__ = u'rbTestTubeType'

    id = Column(Integer, primary_key=True)
    code = Column(String(64))
    name = Column(String(128), nullable=False)
    volume = Column(Float(asdecimal=True), nullable=False)
    unit_id = Column(ForeignKey('rbUnit.id'), nullable=False, index=True)
    covCol = Column(String(64))
    image = Column(MEDIUMBLOB)
    color = Column(String(8))

    unit = relationship(u'rbUnit')


class rbThesaurus(Info):
    __tablename__ = u'rbThesaurus'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, index=True)
    code = Column(String(30), nullable=False, index=True)
    name = Column(String(255), nullable=False, server_default=u"''")
    template = Column(String(255), nullable=False, server_default=u"''")


class rbTimeQuotingType(Info):
    __tablename__ = u'rbTimeQuotingType'

    id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=False, unique=True)
    name = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)


class rbTissueType(RBInfo):
    __tablename__ = u'rbTissueType'

    id = Column(Integer, primary_key=True)
    code = Column(String(64), nullable=False)
    name = Column(String(128), nullable=False)
    group_id = Column(ForeignKey('rbTissueType.id'), index=True)
    sexCode = Column("sex", Integer, nullable=False, server_default=u"'0'")

    group = relationship(u'rbTissueType', remote_side=[id])

    @property
    def sex(self):
        return {0: u'Любой',
                1: u'М',
                2: u'Ж'}[self.sexCode]


class rbTransferDateType(Info):
    __tablename__ = u'rbTransferDateType'

    id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=False, unique=True)
    name = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)


class rbTraumaType(RBInfo):
    __tablename__ = u'rbTraumaType'

    id = Column(Integer, primary_key=True)
    code = Column(String(8), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)

    def __init__(self):
        RBInfo.__init__(self)


class rbTreatment(RBInfo):
    __tablename__ = u'rbTreatment'

    id = Column(Integer, primary_key=True)
    code = Column(String(32), nullable=False)
    name = Column(Text, nullable=False)


class rbTrfuBloodComponentType(RBInfo):
    __tablename__ = u'rbTrfuBloodComponentType'

    id = Column(Integer, primary_key=True)
    trfu_id = Column(Integer)
    code = Column(String(32))
    name = Column(String(256))
    unused = Column(Integer, nullable=False, server_default=u"'0'")


class rbTrfuLaboratoryMeasureTypes(Info):
    __tablename__ = u'rbTrfuLaboratoryMeasureTypes'

    id = Column(Integer, primary_key=True)
    trfu_id = Column(Integer)
    name = Column(String(255))


class rbTrfuProcedureTypes(Info):
    __tablename__ = u'rbTrfuProcedureTypes'

    id = Column(Integer, primary_key=True)
    trfu_id = Column(Integer)
    name = Column(String(255))
    unused = Column(Integer, nullable=False, server_default=u"'0'")


class rbUFMS(Info):
    __tablename__ = u'rbUFMS'

    id = Column(Integer, primary_key=True)
    code = Column(String(50, u'utf8_bin'), nullable=False)
    name = Column(String(256, u'utf8_bin'), nullable=False)


class rbUnit(RBInfo):
    __tablename__ = u'rbUnit'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(256), index=True)
    name = Column(Unicode(256), index=True)


class rbUnitsGroup(Info):
    __tablename__ = "rbUnitsGroup"

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    name = Column(String(255), nullable=False)
    shortname = Column(String(32), nullable=False)

    def __unicode__(self):
        return self.name

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'short_name': self.shortname,
            'children': self.children,
        }


class rbUnits(Info):
    __tablename__ = "rbUnits"

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    name = Column(String(255), nullable=False)
    shortname = Column(String(32), nullable=False)
    group_id = Column(ForeignKey("rbUnitsGroup.id"), index=True, nullable=False)

    group = relationship('rbUnitsGroup', backref='children')

    def __unicode__(self):
        return self.name

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'short_name': self.shortname,
            'group_id': self.group_id
        }


class rbUserProfile(Info):
    __tablename__ = u'rbUserProfile'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    withDep = Column(Integer, nullable=False, server_default=u"'0'")


class rbUserProfile_Right(Info):
    __tablename__ = u'rbUserProfile_Right'

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, nullable=False, index=True)
    userRight_id = Column(Integer, nullable=False, index=True)


class rbUserRight(Info):
    __tablename__ = u'rbUserRight'

    id = Column(Integer, primary_key=True)
    code = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)


class rbVisitType(RBInfo):
    __tablename__ = u'rbVisitType'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(8), nullable=False, index=True)
    name = Column(Unicode(64), nullable=False, index=True)
    serviceModifier = Column(Unicode(128), nullable=False)


class RbF001Tfom(Info):
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


class RbF002Smo(Info):
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


class RbF003Mo(Info):
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


class RbF007Vedom(Info):
    __tablename__ = u'rb_F007_Vedom'

    idved = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    vedname = Column(String(255))


class RbF008Tipom(Info):
    __tablename__ = u'rb_F008_TipOMS'

    iddoc = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    docname = Column(String(255))


class RbF009Statzl(Info):
    __tablename__ = u'rb_F009_StatZL'

    idstatus = Column(String(255), primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    statusname = Column(String(255))


class RbF010Subekti(Info):
    __tablename__ = u'rb_F010_Subekti'

    kod_tf = Column(String(255), primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    kod_okato = Column(String(255))
    okrug = Column(BigInteger)
    subname = Column(String(255))


class RbF011Tipdoc(Info):
    __tablename__ = u'rb_F011_Tipdoc'

    iddoc = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    docname = Column(String(255))
    docnum = Column(String(255))
    docser = Column(String(255))


class RbF015Fedokr(Info):
    __tablename__ = u'rb_F015_FedOkr'

    kod_ok = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    okrname = Column(String(255))


class RbKladr(Info):
    __tablename__ = u'rb_Kladr'

    code = Column(String(255), primary_key=True)
    gninmb = Column(String(255))
    idx = Column(String(255))
    name = Column(String(255))
    ocatd = Column(String(255))
    socr = Column(String(255))
    status = Column(String(255))
    uno = Column(String(255))


class RbKladrstreet(Info):
    __tablename__ = u'rb_KladrStreet'

    code = Column(String(255), primary_key=True)
    gninmb = Column(String(255))
    idx = Column(String(255))
    name = Column(String(255))
    ocatd = Column(String(255))
    socr = Column(String(255))
    uno = Column(String(255))


class RbM001Mkb10(Info):
    __tablename__ = u'rb_M001_MKB10'

    idds = Column(String(255), primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    dsname = Column(String(255))


class RbO001Oksm(Info):
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


class RbO002Okato(Info):
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


class RbO003Okved(Info):
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


class RbO004Okf(Info):
    __tablename__ = u'rb_O004_Okfs'

    kod = Column(String(255), primary_key=True)
    alg = Column(String(255))
    data_upd = Column(Date)
    name1 = Column(String(255))
    nomakt = Column(String(255))
    status = Column(BigInteger)


class RbO005Okopf(Info):
    __tablename__ = u'rb_O005_Okopf'

    kod = Column(String(255), primary_key=True)
    alg = Column(String(255))
    data_upd = Column(Date)
    name1 = Column(String(255))
    nomakt = Column(String(255))
    status = Column(BigInteger)


class RbV001Nomerclr(Info):
    __tablename__ = u'rb_V001_Nomerclr'

    idrb = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    rbname = Column(String(255))


class RbV002Profot(Info):
    __tablename__ = u'rb_V002_ProfOt'

    idpr = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    prname = Column(String(255))


class RbV003Licusl(Info):
    __tablename__ = u'rb_V003_LicUsl'

    idrl = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    ierarh = Column(BigInteger)
    licname = Column(String(255))
    prim = Column(BigInteger)


class RbV004Medspec(Info):
    __tablename__ = u'rb_V004_Medspec'

    idmsp = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    mspname = Column(String(255))


class RbV005Pol(Info):
    __tablename__ = u'rb_V005_Pol'

    idpol = Column(BigInteger, primary_key=True)
    polname = Column(String(255))


class RbV006Uslmp(Info):
    __tablename__ = u'rb_V006_UslMp'

    idump = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    umpname = Column(String(255))


class RbV007Nommo(Info):
    __tablename__ = u'rb_V007_NomMO'

    idnmo = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    nmoname = Column(String(255))


class RbV008Vidmp(Info):
    __tablename__ = u'rb_V008_VidMp'

    idvmp = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    vmpname = Column(String(255))


class RbV009Rezult(Info):
    __tablename__ = u'rb_V009_Rezult'

    idrmp = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    iduslov = Column(BigInteger)
    rmpname = Column(String(255))


class RbV010Sposob(Info):
    __tablename__ = u'rb_V010_Sposob'

    idsp = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    spname = Column(String(255))


class RbV012Ishod(Info):
    __tablename__ = u'rb_V012_Ishod'

    idiz = Column(BigInteger, primary_key=True)
    datebeg = Column(Date)
    dateend = Column(Date)
    iduslov = Column(BigInteger)
    izname = Column(String(255))


class rdFirstName(Info):
    __tablename__ = u'rdFirstName'
    __table_args__ = (
        Index(u'sex', u'sex', u'name'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, index=True)
    sex = Column(Integer, nullable=False)


class rdPOLIS_S(Info):
    __tablename__ = u'rdPOLIS_S'

    id = Column(Integer, primary_key=True)
    CODE = Column(String(10), nullable=False, index=True)
    PAYER = Column(String(5), nullable=False)
    TYPEINS = Column(String(1), nullable=False)


class rdPatrName(Info):
    __tablename__ = u'rdPatrName'
    __table_args__ = (
        Index(u'sex', u'sex', u'name'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, index=True)
    sex = Column(Integer, nullable=False)


class rlsActMatters(Info):
    __tablename__ = u'rlsActMatters'
    __table_args__ = (
        Index(u'name_localName', u'name', u'localName'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    localName = Column(String(255))


class rlsBalanceOfGoods(Info):
    __tablename__ = u'rlsBalanceOfGoods'

    id = Column(Integer, primary_key=True)
    rlsNomen_id = Column(ForeignKey('rlsNomen.id'), nullable=False, index=True)
    value = Column(Float(asdecimal=True), nullable=False)
    bestBefore = Column(Date, nullable=False)
    disabled = Column(Integer, nullable=False, server_default=u"'0'")
    updateDateTime = Column(DateTime)
    storage_id = Column(ForeignKey('rbStorage.id'), index=True)

    rlsNomen = relationship(u'rlsNomen')
    storage = relationship(u'rbStorage')


class rlsFilling(Info):
    __tablename__ = u'rlsFilling'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)


class rlsForm(Info):
    __tablename__ = u'rlsForm'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)

    def __unicode__(self):
        return self.name


class rlsNomen(Info):
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

    actMatters = relationship(u'rlsActMatters')
    dosageUnit = relationship(u'rbUnit', primaryjoin='rlsNomen.dosageUnit_id == rbUnit.id')
    filling = relationship(u'rlsFilling')
    form = relationship(u'rlsForm')
    packing = relationship(u'rlsPacking')
    tradeName = relationship(u'rlsTradeName')
    unit = relationship(u'rbUnit', primaryjoin='rlsNomen.unit_id == rbUnit.id')

    def __unicode__(self):
        if self.dosageUnit:
            return u'{0} ({1} {2}; {3}; {4})'.format(self.tradeName, self.dosageValue, self.dosageUnit.code,
                                                    self.form, self.packing)
        return u'{0} ({1}; {2})'.format(self.tradeName.name, self.form.name, self.packing.name)


class rlsPacking(Info):
    __tablename__ = u'rlsPacking'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)

    def __unicode__(self):
        return self.name


class rlsPharmGroup(Info):
    __tablename__ = u'rlsPharmGroup'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    code = Column(String(8))
    name = Column(String(128))
    path = Column(String(128))
    pathx = Column(String(128))
    nameRaw = Column(String(128), index=True)


class rlsPharmGroupToCode(Info):
    __tablename__ = u'rlsPharmGroupToCode'

    rlsPharmGroup_id = Column(Integer, primary_key=True, nullable=False, server_default=u"'0'")
    code = Column(Integer, primary_key=True, nullable=False, index=True, server_default=u"'0'")


class rlsTradeName(Info):
    __tablename__ = u'rlsTradeName'
    __table_args__ = (
        Index(u'name_localName', u'name', u'localName'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    localName = Column(String(255))

    def __unicode__(self):
        return self.name if self.name else ''


class trfuFinalVolume(Info):
    __tablename__ = u'trfuFinalVolume'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    time = Column(Float(asdecimal=True))
    anticoagulantVolume = Column(Float(asdecimal=True))
    inletVolume = Column(Float(asdecimal=True))
    plasmaVolume = Column(Float(asdecimal=True))
    collectVolume = Column(Float(asdecimal=True))
    anticoagulantInCollect = Column(Float(asdecimal=True))
    anticoagulantInPlasma = Column(Float(asdecimal=True))

    action = relationship(u'Action')

    def __getitem__(self, name):
        columns = {'time': self.time,
                   'anticoagulantVolume': self.anticoagulantVolume,
                   'inletVolume': self.inletVolume,
                   'plasmaVolume': self.plasmaVolume,
                   'collectVolume': self.collectVolume,
                   'anticoagulantInCollect': self.anticoagulantInCollect,
                   'anticoagulantInPlasma': self.anticoagulantInPlasma}
        return columns[name]


class trfuLaboratoryMeasure(Info):
    __tablename__ = u'trfuLaboratoryMeasure'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    trfu_lab_measure_id = Column(ForeignKey('rbTrfuLaboratoryMeasureTypes.id'), index=True)
    time = Column(Float(asdecimal=True))
    beforeOperation = Column(String(255))
    duringOperation = Column(String(255))
    inProduct = Column(String(255))
    afterOperation = Column(String(255))

    action = relationship(u'Action')
    trfu_lab_measure = relationship(u'rbTrfuLaboratoryMeasureTypes')

    def __getitem__(self, name):
        columns = {'trfu_lab_measure_id': self.trfu_lab_measure,
                   'time': self.time,
                   'beforeOperation': self.beforeOperation,
                   'duringOperation': self.duringOperation,
                   'inProduct': self.inProduct,
                   'afterOperation': self.afterOperation}
        return columns[name]


class trfuOrderIssueResult(Info):
    __tablename__ = u'trfuOrderIssueResult'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), nullable=False, index=True)
    trfu_blood_comp = Column(Integer)
    comp_number = Column(String(40))
    comp_type_id = Column(ForeignKey('rbTrfuBloodComponentType.id'), index=True)
    blood_type_id = Column(ForeignKey('rbBloodType.id'), index=True)
    volume = Column(Integer)
    dose_count = Column(Float())
    trfu_donor_id = Column(Integer)
    stickerUrl = Column(String(2083))

    action = relationship(u'Action', backref="trfuOrderIssueResult")
    blood_type = relationship(u'rbBloodType')
    comp_type = relationship(u'rbTrfuBloodComponentType')

    def __getitem__(self, name):
        columns = {'trfu_blood_comp': self.trfu_blood_comp,
                   'comp_number': self.comp_number,
                   'comp_type_id': self.comp_type,
                   'blood_type_id': self.blood_type,
                   'volume': self.volume,
                   'dose_count': self.dose_count,
                   'trfu_donor_id': self.trfu_donor_id}
        return columns[name]


class v_Client_Quoting(Info):
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

    quotaType = relationship(u"QuotaType")
    organisation = relationship(u"Organisation")
    orgstructure = relationship(u"Orgstructure")
    pacientModel = relationship(u"rbPacientModel")
    treatment = relationship(u"rbTreatment")


class v_Nomen(Info):
    __tablename__ = u'vNomen'

    id = Column(u'id', Integer, primary_key=True)
    tradeName = Column(u'tradeName', String(255))
    tradeLocalName = Column(u'tradeLocalName', String(255))
    tradeName_id = Column(u'tradeName_id', Integer)
    actMattersName = Column(u'actMattersName', String(255))
    actMattersLocalName = Column(u'actMattersLocalName', String(255))
    actMatters_id = Column(u'actMatters_id', Integer)
    form = Column(u'form', String(128))
    packing = Column(u'packing', String(128))
    filling = Column(u'filling', String(128))
    unit_id = Column(u'unit_id', Integer)
    unitCode = Column(u'unitCode', String(256))
    unitName = Column(u'unitName', String(256))
    dosageValue = Column(u'dosageValue', String(128))
    dosageUnit_id = Column(u'dosageUnit_id', Integer)
    dosageUnitCode = Column(u'dosageUnitCode', String(256))
    dosageUnitName = Column(u'dosageUnitName', String(256))
    regDate = Column(u'regDate', Date)
    annDate = Column(u'annDate', Date)
    drugLifetime = Column(u'drugLifetime', Integer)

    def __unicode__(self):
        return ', '.join(unicode(field) for field in (self.tradeName, self.form, self.dosageValue, self.filling))


class rbPrintTemplateMeta(Info):
    __tablename__ = 'rbPrintTemplateMeta'
    __table_args__ = (
        Index('template_id_name', 'template_id', 'name'),
    )

    id = Column(Integer, primary_key=True)
    template_id = Column(ForeignKey('rbPrintTemplate.id'), nullable=False, index=True)
    type = Column(Enum(
        u'Integer', u'Float', u'String', u'Boolean', u'Date', u'Time', u'List', u'Multilist',
        u'RefBook', u'Organisation', u'OrgStructure', u'Person', u'Service', u'SpecialVariable',
        u'MKB', u'Area', u'MultiRefBook', u'MultiOrganisation', u'MultiOrgStructure', u'MultiPerson',
        u'MultiService', u'MultiMKB', u'MultiArea', u'RefBook.name'
    ), nullable=False)
    name = Column(String(128), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    arguments = Column(String)
    defaultValue = Column(Text)

    template = relationship(u'rbPrintTemplate')

    def __json__(self):
        import json
        if self.arguments:
            try:
                args = json.loads(self.arguments)
            except ValueError:
                args = []
        else:
            args = []
        if self.defaultValue:
            try:
                default = json.loads(self.defaultValue)
            except ValueError:
                default = None
        else:
            default = None
        return {
            'name': self.name,
            'type': self.type,
            'title': self.title,
            'descr': self.description,
            'arguments': args,
            'default': default,
        }


class rbHospitalisationGoal(Info):
    __tablename__ = 'rbHospitalisationGoal'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    name = Column(String(255), nullable=False)

    def __unicode__(self):
        return self.name

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
        }


class rbHospitalisationOrder(Info):
    __tablename__ = 'rbHospitalisationOrder'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    name = Column(String(255), nullable=False)

    def __unicode__(self):
        return self.name

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
        }


class rbFisherKTGRate(Info):
    __tablename__ = 'rbFisherKTGRate'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Unicode(32), nullable=False)
    name = Column(Unicode(128), nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }

    def __int__(self):
        return self.id


class RisarFetusState_heartbeats(Info):
    __tablename__ = u'RisarFetusState_heartbeats'

    id = Column(Integer, primary_key=True)
    fetus_state_id = Column(ForeignKey('RisarFetusState.id'), index=True)
    fetus_state = relationship('RisarFetusState')
    heartbeat_code = Column(String(250))
    heartbeat = VestaProperty('heartbeat_code', 'rbRisarFetus_Heartbeat')


def safe_current_user_id():
    try:
        user_id = int(current_user.get_id()) if current_user else None
    except (ValueError, TypeError):
        user_id = None
    return user_id

class RisarFetusState(Info):
    __tablename__ = u'RisarFetusState'

    id = Column(Integer, primary_key=True)
    action_id = Column(ForeignKey('Action.id'), index=True)
    action = relationship('Action')

    createDatetime = Column(DateTime, nullable=False, default=datetime.datetime.now)
    createPerson_id = Column(Integer, index=True, default=safe_current_user_id)
    modifyDatetime = Column(DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    modifyPerson_id = Column(Integer, index=True, default=safe_current_user_id, onupdate=safe_current_user_id)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")

    position_code = Column(String(250))
    position_2_code = Column(String(250))
    type_code = Column(String(250))
    presenting_part_code = Column(String(250))
    delay_code = Column(String(250))
    basal_code = Column(String(250))
    variability_range_code = Column(String(250))
    frequency_per_minute_code = Column(String(250))
    acceleration_code = Column(String(250))
    deceleration_code = Column(String(250))

    position = VestaProperty('position_code', 'rbRisarFetus_Position')
    position_2 = VestaProperty('position_2_code', 'rbRisarFetus_Position_2')
    type = VestaProperty('type_code', 'rbRisarFetus_Type')
    presenting_part = VestaProperty('presenting_part_code', 'rbRisarPresenting_Part')
    delay = VestaProperty('delay_code', 'rbRisarFetus_Delay')
    basal = VestaProperty('basal_code', 'rbRisarBasal')
    variability_range = VestaProperty('variability_range_code', 'rbRisarVariabilityRange')
    frequency_per_minute = VestaProperty('frequency_per_minute_code', 'rbRisarFrequencyPerMinute')
    acceleration = VestaProperty('acceleration_code', 'rbRisarAcceleration')
    deceleration = VestaProperty('deceleration_code', 'rbRisarDeceleration')

    heart_rate = Column(Integer, nullable=True)
    ktg_input = Column(Boolean, nullable=False, server_default=u"'0'", default=0)
    fisher_ktg_points = Column(Integer)
    fisher_ktg_rate_id = Column(ForeignKey('rbFisherKTGRate.id'))

    fisher_ktg_rate = relationship('rbFisherKTGRate')

    @property
    def heartbeat(self):
        q = g.printing_session.query(RisarFetusState_heartbeats).filter(
            RisarFetusState_heartbeats.fetus_state == self,
        )
        return map(lambda x: x.heartbeat, list(q))
