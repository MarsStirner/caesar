# -*- coding: utf-8 -*-
import datetime
import jinja2
from application.database import db
from ..config import MODULE_NAME
from ..lib.html import escape, convenience_HtmlRip, replace_first_paragraph
from ..lib.num_to_text_converter import NumToTextConverter
from models_utils import *
from kladr_models import *
from sqlalchemy.dialects.mysql.base import LONGBLOB, MEDIUMBLOB


TABLE_PREFIX = MODULE_NAME


class ConfigVariables(db.Model):
    __tablename__ = '%s_config' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(25), unique=True, nullable=False)
    name = db.Column(db.Unicode(50), unique=True, nullable=False)
    value = db.Column(db.Unicode(100))
    value_type = db.Column(db.String(30))

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


class Account(db.Model, Info):
    __tablename__ = u'Account'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    contract_id = db.Column(db.Integer, db.ForeignKey('Contract.id'), nullable=False, index=True)
    orgStructure_id = db.Column(db.Integer, db.ForeignKey('OrgStructure.id'))
    payer_id = db.Column(db.Integer, db.ForeignKey('Organisation.id'), nullable=False, index=True)
    settleDate = db.Column(db.Date, nullable=False)
    number = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    uet = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    sum = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    exposeDate = db.Column(db.Date)
    payedAmount = db.Column(db.Float(asdecimal=True), nullable=False)
    payedSum = db.Column(db.Float(asdecimal=True), nullable=False)
    refusedAmount = db.Column(db.Float(asdecimal=True), nullable=False)
    refusedSum = db.Column(db.Float(asdecimal=True), nullable=False)
    format_id = db.Column(db.Integer, db.ForeignKey('rbAccountExportFormat.id'), index=True)

    payer = db.relationship(u'Organisation')
    orgStructure = db.relationship(u'Orgstructure')
    contract = db.relationship(u'Contract')
    format = db.relationship(u'Rbaccountexportformat')
    items = db.relationship(u'AccountItem')

    @property
    def sumInWords(self):
        sum_conv = NumToTextConverter(self.sum)
        return sum_conv.convert().getRubText() + sum_conv.convert().getKopText()

    def __unicode__(self):
        return u'%s от %s' % (self.number, self.date)


class AccountItem(db.Model, Info):
    __tablename__ = u'Account_Item'

    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    master_id = db.Column(db.Integer, db.ForeignKey('Account.id'), nullable=False, index=True)
    serviceDate = db.Column(db.Date, server_default=u"'0000-00-00'")
    event_id = db.Column(db.Integer, db.ForeignKey('Event.id'), index=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('Visit.id'), index=True)
    action_id = db.Column(db.Integer, db.ForeignKey('Action.id'), index=True)
    price = db.Column(db.Float(asdecimal=True), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('rbMedicalAidUnit.id'), index=True)
    amount = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    uet = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    sum = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    date = db.Column(db.Date)
    number = db.Column(db.String(20), nullable=False)
    refuseType_id = db.Column(db.Integer, db.ForeignKey('rbPayRefuseType.id'), index=True)
    reexposeItem_id = db.Column(db.Integer, db.ForeignKey('Account_Item.id'), index=True)
    note = db.Column(db.String(256), nullable=False)
    tariff_id = db.Column(db.Integer, db.ForeignKey('Contract_Tariff.id'), index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('rbService.id'))
    paymentConfirmationDate = db.Column(db.Date)

    event = db.relationship(u'Event')
    visit = db.relationship(u'Visit')
    action = db.relationship(u'Action')
    refuseType = db.relationship(u'Rbpayrefusetype')
    reexposeItem = db.relationship(u'AccountItem', remote_side=[id])
    service = db.relationship(u'Rbservice')
    unit = db.relationship(u'Rbmedicalaidunit')

    @property
    def sumInWords(self):
        sum_conv = NumToTextConverter(self.sum)
        return sum_conv.convert().getRubText() + sum_conv.convert().getKopText()

    def __unicode__(self):
        return u'%s %s %s' % (self.serviceDate, self.event.client, self.sum)


class Action(db.Model):
    __tablename__ = u'Action'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    actionType_id = db.Column(db.Integer, db.ForeignKey('ActionType.id'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('Event.id'), index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    directionDate = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=False)
    setPerson_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    isUrgent = db.Column(db.Boolean, nullable=False, server_default=u"'0'")
    begDate = db.Column(db.DateTime)
    plannedEndDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime)
    note = db.Column(db.Text, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    office = db.Column(db.String(16), nullable=False)
    amount = db.Column(db.Float(asdecimal=True), nullable=False)
    uet = db.Column(db.Float(asdecimal=True), server_default=u"'0'")
    expose = db.Column(db.Boolean, nullable=False, server_default=u"'1'")
    payStatus = db.Column(db.Integer, nullable=False)
    account = db.Column(db.Boolean, nullable=False)
    finance_id = db.Column(db.Integer, db.ForeignKey('rbFinance.id'), index=True)
    prescription_id = db.Column(db.Integer, index=True)
    takenTissueJournal_id = db.Column(db.ForeignKey('TakenTissueJournal.id'), index=True)
    contract_id = db.Column(db.Integer, index=True)
    coordDate = db.Column(db.DateTime)
    coordAgent = db.Column(db.String(128), nullable=False, server_default=u"''")
    coordInspector = db.Column(db.String(128), nullable=False, server_default=u"''")
    coordText = db.Column(db.String, nullable=False)
    hospitalUidFrom = db.Column(db.String(128), nullable=False, server_default=u"'0'")
    pacientInQueueType = db.Column(db.Integer, server_default=u"'0'")
    AppointmentType = db.Column(db.Enum(u'0', u'amb', u'hospital', u'polyclinic', u'diagnostics', u'portal', u'otherLPU'),
                             nullable=False)
    version = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    parentAction_id = db.Column(db.Integer, index=True)
    uuid_id = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")
    dcm_study_uid = db.Column(db.String(50))

    actionType = db.relationship(u'Actiontype')
    event = db.relationship(u'Event')
    person = db.relationship(u'Person', foreign_keys='Action.person_id')
    setPerson = db.relationship(u'Person', foreign_keys='Action.setPerson_id')
    takenTissueJournal = db.relationship(u'Takentissuejournal')
    tissues = db.relationship(u'Tissue', secondary=u'ActionTissue')
    properties = db.relationship(u'Actionproperty')
    self_finance = db.relationship(u'Rbfinance')

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
            return self.self_finance
        else:
            return self.event.eventType.finance

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
    def showTime(self):
        return self.actionType.showTime if self.actionType else None

    @property
    def isMes(self):
        return self.actionType.isMes if self.actionType else None

    @property
    def nomenclatureService(self):
        return self.actionType.nomenclatureService if self.actionType else None

    # @property
    # def isHtml(self):
    #     return self.actionType.isHtml if self.actionType else None

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


class Bbtresponse(Action):
    __tablename__ = u'bbtResponse'

    id = db.Column(db.ForeignKey('Action.id'), primary_key=True)
    final = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    defects = db.Column(db.Text)
    doctor_id = db.Column(db.ForeignKey('Person.id'), nullable=False, index=True)
    codeLIS = db.Column(db.String(20), nullable=False)

    doctor = db.relationship(u'Person')


class Actionproperty(db.Model, Info):
    __tablename__ = u'ActionProperty'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    action_id = db.Column(db.Integer, db.ForeignKey('Action.id'), nullable=False, index=True)
    type_id = db.Column(db.Integer, db.ForeignKey('ActionPropertyType.id'), nullable=False, index=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('rbUnit.id'), index=True)
    norm = db.Column(db.String(64), nullable=False)
    isAssigned = db.Column(db.Boolean, nullable=False, server_default=u"'0'")
    evaluation = db.Column(db.Integer)
    version = db.Column(db.Integer, nullable=False, server_default=u"'0'")

    type = db.relationship(u'Actionpropertytype')
    unit_all = db.relationship(u'Rbunit')

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
        if self.type.typeName == "Constructor":
            class_name = u'ActionpropertyText'
        elif self.type.typeName == "AnalysisStatus":
            class_name = u'ActionpropertyInteger'
        elif self.type.typeName == u"Запись в др. ЛПУ":
            class_name = u'ActionpropertyOtherlpurecord'
        elif self.type.typeName == u"FlatDirectory":
            class_name = u'ActionpropertyFdrecord'
        else:
            class_name = u'Actionproperty{0}'.format(self.type.typeName.capitalize())

        cl = globals()[class_name]
        values = db_session.query(cl).filter(cl.id == self.id).all()
        db_session.close()
        if self.type.typeName == "Table":
            return values[0].get_value(self.type.valueDomain) if values else ""
        else:
            if values and self.type.isVector:
                return [value.get_value() for value in values]
            elif values:
                return values[0].get_value()
            else:
                return ""

    def __unicode__(self):
        return unicode(self.value)
    # image = property(lambda self: self._property.getImage())
    # imageUrl = property(_getImageUrl)


class Actionpropertytemplate(db.Model):
    __tablename__ = u'ActionPropertyTemplate'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.Integer, index=True)
    parentCode = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(64), nullable=False, index=True)
    federalCode = db.Column(db.String(64), nullable=False, index=True)
    regionalCode = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(120), nullable=False, index=True)
    abbrev = db.Column(db.String(64), nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.String(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    service_id = db.Column(db.Integer, index=True)


class Actionpropertytype(db.Model, Info):
    __tablename__ = u'ActionPropertyType'

    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    actionType_id = db.Column(db.Integer, db.ForeignKey('ActionType.id'), nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    template_id = db.Column(db.Integer, index=True)
    name = db.Column(db.String(128), nullable=False)
    descr = db.Column(db.String(128), nullable=False)
    unit_id = db.Column(db.Integer, index=True)
    typeName = db.Column(db.String(64), nullable=False)
    valueDomain = db.Column(db.Text, nullable=False)
    defaultValue = db.Column(db.String(5000), nullable=False)
    isVector = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    norm = db.Column(db.String(64), nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.String(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    penalty = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    visibleInJobTicket = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isAssignable = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    test_id = db.Column(db.Integer, index=True)
    defaultEvaluation = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    toEpicrisis = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    code = db.Column(db.String(25), index=True)
    mandatory = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    readOnly = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    createDatetime = db.Column(db.DateTime, nullable=False, index=True)
    createPerson_id = db.Column(db.Integer)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer)

    @property
    def value(self):
        if self.typeName == "Constructor":
            class_name = u'ActionpropertyText'
        elif self.typeName == "AnalysisStatus":
            class_name = u'ActionpropertyInteger'
        else:
            class_name = u'Actionproperty{0}'.format(self.typeName.capitalize())

        cl = globals()[class_name]
        return cl().get_value()


class ActionpropertyAction(db.Model):
    __tablename__ = u'ActionProperty_Action'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Integer, index=True)

    def get_value(self):
        return self.value if self.value else ''

    def __unicode__(self):
        return self.value


class ActionpropertyDate(db.Model):
    __tablename__ = u'ActionProperty_Date'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Date)

    def get_value(self):
        self.value if self.value else ''

    def __unicode__(self):
        return self.value


class ActionpropertyDouble(db.Model):
    __tablename__ = u'ActionProperty_Double'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Float(asdecimal=True, decimal_return_scale=2), nullable=False)

    def get_value(self):
        return round(self.value, 2) if self.value else 0.0

    def __unicode__(self):
        return self.value


class ActionpropertyFdrecord(db.Model):
    __tablename__ = u'ActionProperty_FDRecord'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True)
    index = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    value = db.Column(db.ForeignKey('FDRecord.id'), nullable=False, index=True)

    FDRecord = db.relationship(u'Fdrecord')

    def get_value(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        return db_session.query(Fdrecord).filter(Fdrecord.id == self.value).first().get_value()


class ActionpropertyHospitalbed(db.Model):
    __tablename__ = u'ActionProperty_HospitalBed'

    id = db.Column(db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.ForeignKey('OrgStructure_HospitalBed.id'), index=True)

    ActionProperty = db.relationship(u'Actionproperty')
    OrgStructure_HospitalBed = db.relationship(u'OrgstructureHospitalbed')

    def get_value(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        value = db_session.query(OrgstructureHospitalbed).filter(OrgstructureHospitalbed.id == self.value).first()
        db_session.close()
        return value


class ActionpropertyHospitalbedprofile(db.Model):
    __tablename__ = u'ActionProperty_HospitalBedProfile'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Integer, index=True)

    def get_value(self):
        #    TODO: переделать
        return self.value if self.value else ''


class ActionpropertyImage(db.Model):
    __tablename__ = u'ActionProperty_Image'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(MEDIUMBLOB)

    def get_value(self):
        return self.value if self.value else ''


class ActionpropertyImagemap(db.Model):
    __tablename__ = u'ActionProperty_ImageMap'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.String)

    def get_value(self):
        return self.value if self.value else ''


class ActionpropertyInteger(db.Model):
    __tablename__ = u'ActionProperty_Integer'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Integer, nullable=False)

    def get_value(self):
        return self.value if self.value else 0

    def __unicode__(self):
        return self.value


class ActionpropertyRLS(ActionpropertyInteger):

    def get_value(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        value = db_session.query(v_Nomen).filter(v_Nomen.code == self.value).first()
        db_session.close()
        return value


class ActionpropertyOperationType(ActionpropertyInteger):

    def get_value(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        value = db_session.query(Rboperationtype).filter(Rboperationtype.code == self.value).first()
        db_session.close()
        if self.value and value.name:
            text = '(%s) %s' % (value.code, value.name)
        elif self.value:
            text = '{%s}' % self.value
        else:
            text = ''
        return text


class ActionpropertyJobticket(db.Model):
    __tablename__ = u'ActionProperty_Job_Ticket'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Integer, index=True)

    def get_value(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        value = db_session.query(JobTicket).get(self.value)
        db_session.close()
        return value if value else ''


class ActionpropertyMkb(db.Model):
    __tablename__ = u'ActionProperty_MKB'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Integer, index=True)

    def get_value(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        value = db_session.query(Mkb).get(self.value)
        db_session.close()
        return value if value else ''


class ActionpropertyOrgstructure(db.Model):
    __tablename__ = u'ActionProperty_OrgStructure'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Integer, index=True)

    def get_value(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        value = db_session.query(Orgstructure).filter(Orgstructure.id == self.value).first()
        db_session.close()
        return value

    def __unicode__(self):
        return self.value


class ActionpropertyOrganisation(db.Model):
    __tablename__ = u'ActionProperty_Organisation'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Integer, index=True)

    def get_value(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        value = db_session.query(Organisation).filter(Organisation.id == self.value).first()
        db_session.close()
        return value

    def __unicode__(self):
        return self.value


class ActionpropertyOtherlpurecord(db.Model):
    __tablename__ = u'ActionProperty_OtherLPURecord'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Text(collation=u'utf8_unicode_ci'), nullable=False)

    def get_value(self):
        return self.value if self.value else ''


class ActionpropertyPerson(db.Model):
    __tablename__ = u'ActionProperty_Person'

    id = db.Column(db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    value = db.Column(db.ForeignKey('Person.id'), index=True)

    ActionProperty = db.relationship(u'Actionproperty')
    Person = db.relationship(u'Person')

    def get_value(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        value = db_session.query(Person).filter(Person.id == self.value).first()
        db_session.close()
        return value

    def __unicode__(self):
        return self.value


class ActionpropertyString(db.Model):
    __tablename__ = u'ActionProperty_String'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Text, nullable=False)

    def get_value(self):
        return escape(self.value) if self.value else ''

    def __unicode__(self):
        return self.value


class ActionpropertyText(ActionpropertyString):

    def get_value(self):
        return replace_first_paragraph(convenience_HtmlRip(self.value)) if self.value else ''


class ActionpropertyHtml(ActionpropertyString):

    def get_value(self):
        return convenience_HtmlRip(self.value) if self.value else ''


class ActionpropertyTable(ActionpropertyInteger):

    def get_value(self, table_code):
        from blueprints.print_subsystem.utils import get_lpu_session

        trfu_tables = {"trfuOrderIssueResult": Trfuorderissueresult, "trfuLaboratoryMeasure": Trfulaboratorymeasure,
                       "trfuFinalVolume": Trfufinalvolume}

        db_session = get_lpu_session()
        table = db_session.query(Rbaptable).filter(Rbaptable.code == table_code).first()
        field_names = [field.name for field in table.fields]
        table_filed_names = [field.fieldName for field in table.fields]
        value_table_name = table.tableName
        master_field = table.masterField
        values = db_session.query(trfu_tables[value_table_name]).filter("{0}.{1} = {2}".format(value_table_name,
                                                                                               master_field, self.value)).all()
        db_session.close()
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


class ActionpropertyTime(db.Model):
    __tablename__ = u'ActionProperty_Time'

    id = db.Column(db.Integer, db.ForeignKey('ActionProperty.id'), primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Time, nullable=False)

    def get_value(self):
        return self.value if self.value else ''

    def __unicode__(self):
        return self.get_value()


class ActionpropertyReferenceRb(ActionpropertyInteger):

    def get_value(self, domain):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        table_name = domain.split(';')[0]
        value = db_session.query(table_name).get(self.value)
        db_session.close()
        return value if value else ''

    def __unicode__(self):
        return self.get_value()


class ActionpropertyRbbloodcomponenttype(db.Model):
    __tablename__ = u'ActionProperty_rbBloodComponentType'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.Integer, nullable=False)

    def get_value(self):
        return self.value if self.value else ''


class ActionpropertyRbfinance(db.Model):
    __tablename__ = u'ActionProperty_rbFinance'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Integer, index=True)

    def get_value(self):
        return self.value if self.value else ''


class ActionpropertyRbreasonofabsence(db.Model):
    __tablename__ = u'ActionProperty_rbReasonOfAbsence'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    index = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    value = db.Column(db.Integer, index=True)

    def get_value(self):
        return self.value if self.value else ''


class Actiontemplate(db.Model):
    __tablename__ = u'ActionTemplate'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.Integer, index=True)
    code = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.String(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    owner_id = db.Column(db.Integer, index=True)
    speciality_id = db.Column(db.Integer, index=True)
    action_id = db.Column(db.Integer, index=True)


t_ActionTissue = db.Table(
    u'ActionTissue', db.metadata,
    db.Column(u'action_id', db.ForeignKey('Action.id'), primary_key=True, nullable=False, index=True),
    db.Column(u'tissue_id', db.ForeignKey('Tissue.id'), primary_key=True, nullable=False, index=True)
)


class Actiontype(db.Model, Info):
    __tablename__ = u'ActionType'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    hidden = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    class_ = db.Column(u'class', db.Integer, nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('ActionType.id'), index=True)
    code = db.Column(db.String(25), nullable=False)
    name = db.Column(db.Unicode(255), nullable=False)
    title = db.Column(db.Unicode(255), nullable=False)
    flatCode = db.Column(db.String(64), nullable=False, index=True)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.String(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    office = db.Column(db.String(32), nullable=False)
    showInForm = db.Column(db.Integer, nullable=False)
    genTimetable = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('rbService.id'), index=True)
    quotaType_id = db.Column(db.Integer, index=True)
    context = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'1'")
    amountEvaluation = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    defaultStatus = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    defaultDirectionDate = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    defaultPlannedEndDate = db.Column(db.Integer, nullable=False)
    defaultEndDate = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    defaultExecPerson_id = db.Column(db.Integer, index=True)
    defaultPersonInEvent = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    defaultPersonInEditor = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    maxOccursInEvent = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    showTime = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isMES = db.Column(db.Integer)
    nomenclativeService_id = db.Column(db.Integer, db.ForeignKey('rbService.id'), index=True)
    isPreferable = db.Column(db.Integer, nullable=False, server_default=u"'1'")
    prescribedType_id = db.Column(db.Integer, index=True)
    shedule_id = db.Column(db.Integer, index=True)
    isRequiredCoordination = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isRequiredTissue = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    testTubeType_id = db.Column(db.Integer, index=True)
    jobType_id = db.Column(db.Integer, index=True)
    mnem = db.Column(db.String(32), server_default=u"''")

    service = db.relationship(u'Rbservice', foreign_keys='Actiontype.service_id')
    nomenclatureService = db.relationship(u'Rbservice', foreign_keys='Actiontype.nomenclativeService_id')
    property_types = db.relationship(u'Actionpropertytype')
    group = db.relationship(u'Actiontype', remote_side=[id])

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


class ActiontypeEventtypeCheck(db.Model):
    __tablename__ = u'ActionType_EventType_check'

    id = db.Column(db.Integer, primary_key=True)
    actionType_id = db.Column(db.ForeignKey('ActionType.id'), nullable=False, index=True)
    eventType_id = db.Column(db.ForeignKey('EventType.id'), nullable=False, index=True)
    related_actionType_id = db.Column(db.ForeignKey('ActionType.id'), index=True)
    relationType = db.Column(db.Integer)

    actionType = db.relationship(u'Actiontype', primaryjoin='ActiontypeEventtypeCheck.actionType_id == Actiontype.id')
    eventType = db.relationship(u'Eventtype')
    related_actionType = db.relationship(u'Actiontype', primaryjoin='ActiontypeEventtypeCheck.related_actionType_id == Actiontype.id')


class ActiontypeQuotatype(db.Model):
    __tablename__ = u'ActionType_QuotaType'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    quotaClass = db.Column(db.Integer)
    finance_id = db.Column(db.Integer, index=True)
    quotaType_id = db.Column(db.Integer, index=True)


class ActiontypeService(db.Model):
    __tablename__ = u'ActionType_Service'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    finance_id = db.Column(db.Integer, index=True)
    service_id = db.Column(db.Integer, index=True)


class ActiontypeTissuetype(db.Model):
    __tablename__ = u'ActionType_TissueType'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.ForeignKey('ActionType.id'), nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    tissueType_id = db.Column(db.ForeignKey('rbTissueType.id'), index=True)
    amount = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    unit_id = db.Column(db.ForeignKey('rbUnit.id'), index=True)

    master = db.relationship(u'Actiontype')
    tissueType = db.relationship(u'Rbtissuetype')
    unit = db.relationship(u'Rbunit')


class ActiontypeUser(db.Model):
    __tablename__ = u'ActionType_User'
    __table_args__ = (
        db.Index(u'person_id_profile_id', u'person_id', u'profile_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    actionType_id = db.Column(db.ForeignKey('ActionType.id'), nullable=False, index=True)
    person_id = db.Column(db.ForeignKey('Person.id'))
    profile_id = db.Column(db.ForeignKey('rbUserProfile.id'), index=True)

    actionType = db.relationship(u'Actiontype')
    person = db.relationship(u'Person')
    profile = db.relationship(u'Rbuserprofile')


class Address(db.Model, Info):
    __tablename__ = u'Address'
    __table_args__ = (
        db.Index(u'house_id', u'house_id', u'flat'),
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    house_id = db.Column(db.Integer, db.ForeignKey('AddressHouse.id'), nullable=False)
    flat = db.Column(db.String(6), nullable=False)

    house = db.relationship(u'Addresshouse')

    @property
    def KLADRCode(self):
        return self.house.KLADRCode

    @property
    def KLADRStreetCode(self):
        return self.house.KLADRStreetCode

    @property
    def city(self):
        from blueprints.print_subsystem.utils import get_kladr_session
        if self.KLADRCode:
            kladr_session = get_kladr_session()
            record = kladr_session.query(Kladr).filter(Kladr.CODE == self.KLADRCode).first()
            name = [" ".join([record.NAME, record.SOCR])]
            parent = record.parent
            while parent:
                record = kladr_session.query(Kladr).filter(Kladr.CODE == parent.ljust(13, "0")).first()
                name.insert(0, " ".join([record.NAME, record.SOCR]))
                parent = record.parent
            return ", ".join(name)
        else:
            return ''

    @property
    def town(self):
        return self.city

    @property
    def text(self):
        parts = [self.city]
        if self.street:
            parts.append(self.street)
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

    @property
    def street(self):
        from blueprints.print_subsystem.utils import get_kladr_session
        if self.KLADRStreetCode:
            kladr_session = get_kladr_session()
            record = kladr_session.query(Street).filter(Street.CODE == self.KLADRStreetCode).first()
            return record.NAME + " " + record.SOCR
        else:
            return ''

    def __unicode__(self):
        return self.text


class Addressareaitem(db.Model):
    __tablename__ = u'AddressAreaItem'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    LPU_id = db.Column(db.Integer, nullable=False, index=True)
    struct_id = db.Column(db.Integer, nullable=False, index=True)
    house_id = db.Column(db.Integer, nullable=False, index=True)
    flatRange = db.Column(db.Integer, nullable=False)
    begFlat = db.Column(db.Integer, nullable=False)
    endFlat = db.Column(db.Integer, nullable=False)
    begDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date)


class Addresshouse(db.Model):
    __tablename__ = u'AddressHouse'
    __table_args__ = (
        db.Index(u'KLADRCode', u'KLADRCode', u'KLADRStreetCode', u'number', u'corpus'),
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    KLADRCode = db.Column(db.String(13), nullable=False)
    KLADRStreetCode = db.Column(db.String(17), nullable=False)
    number = db.Column(db.String(8), nullable=False)
    corpus = db.Column(db.String(8), nullable=False)


class Applock(db.Model):
    __tablename__ = u'AppLock'

    id = db.Column(db.BigInteger, primary_key=True)
    lockTime = db.Column(db.DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    retTime = db.Column(db.DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    connectionId = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")
    person_id = db.Column(db.Integer)
    addr = db.Column(db.String(255), nullable=False)


t_AppLock_Detail = db.Table(
    u'AppLock_Detail', db.metadata,
    db.Column(u'master_id', db.BigInteger, nullable=False, index=True),
    db.Column(u'tableName', db.String(64), nullable=False),
    db.Column(u'recordId', db.Integer, nullable=False),
    db.Column(u'recordIndex', db.Integer, nullable=False, server_default=u"'0'"),
    db.Index(u'rec', u'recordId', u'tableName')
)


t_AssignmentHour = db.Table(
    u'AssignmentHour', db.metadata,
    db.Column(u'action_id', db.Integer, nullable=False),
    db.Column(u'createDatetime', db.DateTime, nullable=False),
    db.Column(u'hour', db.Integer),
    db.Column(u'complete', db.Integer, server_default=u"'0'"),
    db.Column(u'comments', db.String(120))
)


class Bank(db.Model, Info):
    __tablename__ = u'Bank'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    bik = db.Column("BIK", db.String(10), nullable=False, index=True)
    name = db.Column(db.Unicode(100), nullable=False, index=True)
    branchName = db.Column(db.Unicode(100), nullable=False)
    corrAccount = db.Column(db.String(20), nullable=False)
    subAccount = db.Column(db.String(20), nullable=False)


class Blankaction(db.Model):
    __tablename__ = u'BlankActions'

    id = db.Column(db.Integer, primary_key=True)
    doctype_id = db.Column(db.ForeignKey('ActionType.id'), index=True)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    checkingSerial = db.Column(db.Integer, nullable=False)
    checkingNumber = db.Column(db.Integer, nullable=False)
    checkingAmount = db.Column(db.Integer, nullable=False)

    doctype = db.relationship(u'Actiontype')


class BlankactionsMoving(db.Model):
    __tablename__ = u'BlankActions_Moving'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    date = db.Column(db.Date, nullable=False)
    blankParty_id = db.Column(db.ForeignKey('BlankActions_Party.id'), nullable=False, index=True)
    serial = db.Column(db.String(8), nullable=False)
    orgStructure_id = db.Column(db.ForeignKey('OrgStructure.id'), index=True)
    person_id = db.Column(db.ForeignKey('Person.id'), index=True)
    received = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    used = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    returnDate = db.Column(db.Date)
    returnAmount = db.Column(db.Integer, nullable=False, server_default=u"'0'")

    blankParty = db.relationship(u'BlankactionsParty')
    createPerson = db.relationship(u'Person', primaryjoin='BlankactionsMoving.createPerson_id == Person.id')
    modifyPerson = db.relationship(u'Person', primaryjoin='BlankactionsMoving.modifyPerson_id == Person.id')
    orgStructure = db.relationship(u'Orgstructure')
    person = db.relationship(u'Person', primaryjoin='BlankactionsMoving.person_id == Person.id')


class BlankactionsParty(db.Model):
    __tablename__ = u'BlankActions_Party'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    date = db.Column(db.Date, nullable=False)
    doctype_id = db.Column(db.ForeignKey('rbBlankActions.id'), nullable=False, index=True)
    person_id = db.Column(db.ForeignKey('Person.id'), index=True)
    serial = db.Column(db.String(8), nullable=False)
    numberFrom = db.Column(db.String(16), nullable=False)
    numberTo = db.Column(db.String(16), nullable=False)
    amount = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    extradited = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    balance = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    used = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    writing = db.Column(db.Integer, nullable=False, server_default=u"'0'")

    createPerson = db.relationship(u'Person', primaryjoin='BlankactionsParty.createPerson_id == Person.id')
    doctype = db.relationship(u'Rbblankaction')
    modifyPerson = db.relationship(u'Person', primaryjoin='BlankactionsParty.modifyPerson_id == Person.id')
    person = db.relationship(u'Person', primaryjoin='BlankactionsParty.person_id == Person.id')


class BlanktempinvalidMoving(db.Model):
    __tablename__ = u'BlankTempInvalid_Moving'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    date = db.Column(db.Date, nullable=False)
    blankParty_id = db.Column(db.ForeignKey('BlankTempInvalid_Party.id'), nullable=False, index=True)
    serial = db.Column(db.String(8), nullable=False)
    orgStructure_id = db.Column(db.ForeignKey('OrgStructure.id'), index=True)
    person_id = db.Column(db.ForeignKey('Person.id'), index=True)
    received = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    used = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    returnDate = db.Column(db.Date)
    returnAmount = db.Column(db.Integer, nullable=False, server_default=u"'0'")

    blankParty = db.relationship(u'BlanktempinvalidParty')
    createPerson = db.relationship(u'Person', primaryjoin='BlanktempinvalidMoving.createPerson_id == Person.id')
    modifyPerson = db.relationship(u'Person', primaryjoin='BlanktempinvalidMoving.modifyPerson_id == Person.id')
    orgStructure = db.relationship(u'Orgstructure')
    person = db.relationship(u'Person', primaryjoin='BlanktempinvalidMoving.person_id == Person.id')


class BlanktempinvalidParty(db.Model):
    __tablename__ = u'BlankTempInvalid_Party'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    date = db.Column(db.Date, nullable=False)
    doctype_id = db.Column(db.ForeignKey('rbBlankTempInvalids.id'), nullable=False, index=True)
    person_id = db.Column(db.ForeignKey('Person.id'), index=True)
    serial = db.Column(db.String(8), nullable=False)
    numberFrom = db.Column(db.String(16), nullable=False)
    numberTo = db.Column(db.String(16), nullable=False)
    amount = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    extradited = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    balance = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    used = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    writing = db.Column(db.Integer, nullable=False, server_default=u"'0'")

    createPerson = db.relationship(u'Person', primaryjoin='BlanktempinvalidParty.createPerson_id == Person.id')
    doctype = db.relationship(u'Rbblanktempinvalid')
    modifyPerson = db.relationship(u'Person', primaryjoin='BlanktempinvalidParty.modifyPerson_id == Person.id')
    person = db.relationship(u'Person', primaryjoin='BlanktempinvalidParty.person_id == Person.id')


class Blanktempinvalid(db.Model):
    __tablename__ = u'BlankTempInvalids'

    id = db.Column(db.Integer, primary_key=True)
    doctype_id = db.Column(db.ForeignKey('rbTempInvalidDocument.id'), index=True)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    checkingSerial = db.Column(db.Integer, nullable=False)
    checkingNumber = db.Column(db.Integer, nullable=False)
    checkingAmount = db.Column(db.Integer, nullable=False)

    doctype = db.relationship(u'Rbtempinvaliddocument')


class Bloodhistory(db.Model):
    __tablename__ = u'BloodHistory'

    id = db.Column(db.Integer, primary_key=True)
    bloodDate = db.Column(db.Date, nullable=False)
    client_id = db.Column(db.Integer, nullable=False)
    bloodType_id = db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, nullable=False)


class Calendarexception(db.Model):
    __tablename__ = u'CalendarExceptions'
    __table_args__ = (
        db.Index(u'CHANGEDAY', u'date', u'fromDate'),
        db.Index(u'HOLIDAY', u'date', u'startYear')
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    date = db.Column(db.Date, nullable=False)
    isHoliday = db.Column(db.Integer, nullable=False)
    startYear = db.Column(db.SmallInteger)
    finishYear = db.Column(db.SmallInteger)
    fromDate = db.Column(db.Date)
    text = db.Column(db.String(250), nullable=False)


class Client(db.Model, Info):
    __tablename__ = u'Client'
    __table_args__ = (
        db.Index(u'lastName', u'lastName', u'firstName', u'patrName', u'birthDate', u'id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    lastName = db.Column(db.Unicode(30), nullable=False)
    firstName = db.Column(db.Unicode(30), nullable=False)
    patrName = db.Column(db.Unicode(30), nullable=False)
    birthDate = db.Column(db.Date, nullable=False, index=True)
    sexCode = db.Column("sex", db.Integer, nullable=False)
    SNILS_short = db.Column("SNILS", db.String(11), nullable=False, index=True)
    bloodType_id = db.Column(db.ForeignKey('rbBloodType.id'), index=True)
    bloodDate = db.Column(db.Date)
    bloodNotes = db.Column(db.String, nullable=False)
    growth = db.Column(db.String(16), nullable=False)
    weight = db.Column(db.String(16), nullable=False)
    notes = db.Column(db.String, nullable=False)
    version = db.Column(db.Integer, nullable=False)
    birthPlace = db.Column(db.Unicode(128), nullable=False, server_default=u"''")
    embryonalPeriodWeek = db.Column(db.String(16), nullable=False, server_default=u"''")
    uuid_id = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")

    bloodType = db.relationship(u'Rbbloodtype')
    client_attachments = db.relationship(u'Clientattach', primaryjoin='and_(Clientattach.client_id==Client.id, Clientattach.deleted==0)',
                                      order_by="desc(Clientattach.id)")
    socStatuses = db.relationship(u'Clientsocstatus',
                               primaryjoin="and_(Clientsocstatus.deleted == 0,Clientsocstatus.client_id==Client.id,"
                               "or_(Clientsocstatus.endDate == None, Clientsocstatus.endDate>='{0}'))".format(datetime.date.today()))
    documentsAll = db.relationship(u'Clientdocument', primaryjoin='and_(Clientdocument.clientId==Client.id,'
                                                               'Clientdocument.deleted == 0)',
                                order_by="desc(Clientdocument.documentId)")
    intolerances = db.relationship(u'Clientintolerancemedicament',
                                primaryjoin='and_(Clientintolerancemedicament.client_id==Client.id,'
                                            'Clientintolerancemedicament.deleted == 0)')
    allergies = db.relationship(u'Clientallergy', primaryjoin='and_(Clientallergy.client_id==Client.id,'
                                                           'Clientallergy.deleted == 0)')
    contacts = db.relationship(u'Clientcontact', primaryjoin='and_(Clientcontact.client_id==Client.id,'
                                                          'Clientcontact.deleted == 0)')
    direct_relations = db.relationship(u'DirectClientRelation', foreign_keys='Clientrelation.client_id')
    reversed_relations = db.relationship(u'ReversedClientRelation', foreign_keys='Clientrelation.relative_id')
    policies = db.relationship(u'Clientpolicy', primaryjoin='and_(Clientpolicy.clientId==Client.id,'
                                                         'Clientpolicy.deleted == 0)', order_by="desc(Clientpolicy.id)")
    works = db.relationship(u'Clientwork', primaryjoin='and_(Clientwork.client_id==Client.id, Clientwork.deleted == 0)',
                         order_by="desc(Clientwork.id)")
    reg_addresses = db.relationship(u'Clientaddress',
                                 primaryjoin="and_(Client.id==Clientaddress.client_id, Clientaddress.type==0)",
                                 order_by="desc(Clientaddress.id)")
    loc_addresses = db.relationship(u'Clientaddress',
                                 primaryjoin="and_(Client.id==Clientaddress.client_id, Clientaddress.type==1)",
                                 order_by="desc(Clientaddress.id)")

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
        contacts = [(contact.name, contact.contact, contact.notes) for contact in self.contacts]
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
        return self.works[0]

    @property
    def ageTuple(self):
        date = self.date
        if not date:
            date = datetime.date.today()
        d = calcAgeInDays(self.birthDate, date)
        if d >= 0:
            return (d,
                    d/7,
                    calcAgeInMonths(self.birthDate, date),
                    calcAgeInYears(self.birthDate, date))
        else:
            return None
        return ""

    @property
    def age(self):
        if not self.ageTuple:
            return u'ещё не родился'
        (days, weeks, months, years) = self.ageTuple
        if years > 7:
            return formatYears(years)
        elif years > 1:
            return formatYearsMonths(years, months-12*years)
        elif months > 1:
            return formatMonthsWeeks(months, weeks)
        else:
            return formatDays(days)

    @property
    def regAddress(self):
        return self.reg_addresses[0]

    @property
    def locAddress(self):
        return self.loc_addresses[0]

    def __unicode__(self):
        return self.formatShortNameInt(self.lastName, self.firstName, self.patrName)


class Patientstohs(db.Model):
    __tablename__ = u'PatientsToHS'

    client_id = db.Column(db.ForeignKey('Client.id'), primary_key=True)
    sendTime = db.Column(db.DateTime, nullable=False, server_default=u'CURRENT_TIMESTAMP')
    errCount = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    info = db.Column(db.String(1024))


class Clientaddress(db.Model, Info):
    __tablename__ = u'ClientAddress'
    __table_args__ = (
        db.Index(u'address_id', u'address_id', u'type'),
        db.Index(u'client_id', u'client_id', u'type', u'address_id')
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('Address.id'))
    freeInput = db.Column(db.String(200), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    localityType = db.Column(db.Integer, nullable=False)

    address = db.relationship(u'Address')

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

    def __unicode__(self):
        if self.text:
            return self.text
        else:
            return self.freeInput


class Clientallergy(db.Model, Info):
    __tablename__ = u'ClientAllergy'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False, index=True)
    name = db.Column("nameSubstance", db.Unicode(128), nullable=False)
    power = db.Column(db.Integer, nullable=False)
    createDate = db.Column(db.Date)
    notes = db.Column(db.String, nullable=False)
    version = db.Column(db.Integer, nullable=False)

    client = db.relationship(u'Client')

    def __unicode__(self):
        return self.name


class Clientattach(db.Model, Info):
    __tablename__ = u'ClientAttach'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False, index=True)
    attachType_id = db.Column(db.ForeignKey('rbAttachType.id'), nullable=False, index=True)
    LPU_id = db.Column(db.ForeignKey('Organisation.id'), nullable=False, index=True)
    orgStructure_id = db.Column(db.ForeignKey('OrgStructure.id'), index=True)
    begDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date)
    document_id = db.Column(db.ForeignKey('ClientDocument.id'), index=True)

    client = db.relationship(u'Client')
    self_document = db.relationship(u'Clientdocument')
    org = db.relationship(u'Organisation')
    orgStructure = db.relationship(u'Orgstructure')
    attachType = db.relationship(u'Rbattachtype')

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
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        documents = db_session.query(Clientdocument).filter(Clientdocument.clientId == self.client_id).\
            filter(Clientdocument.deleted == 0).all()
        documents = [document for document in documents if document.documentType and document.documentType.group.code == "1"]
        return documents[-1]

    def __unicode__(self):
        if self._ok:
            result = self.name
            if self._outcome:
                result += ' ' + unicode(self.endDate)
            elif self.attachType.temporary:
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


class Clientcontact(db.Model, Info):
    __tablename__ = u'ClientContact'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False, index=True)
    contactType_id = db.Column(db.Integer, db.ForeignKey('rbContactType.id'), nullable=False, index=True)
    contact = db.Column(db.String(32), nullable=False)
    notes = db.Column(db.Unicode(64), nullable=False)
    version = db.Column(db.Integer, nullable=False)

    client = db.relationship(u'Client')
    contactType = db.relationship(u'Rbcontacttype')

    @property
    def name(self):
        return self.contactType.names


class Clientdocument(db.Model, Info):
    __tablename__ = u'ClientDocument'
    __table_args__ = (
        db.Index(u'Ser_Numb', u'serial', u'number'),
    )

    documentId = db.Column("id", db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    clientId = db.Column("client_id", db.ForeignKey('Client.id'), nullable=False, index=True)
    documentType_id = db.Column(db.Integer, db.ForeignKey('rbDocumentType.id'), nullable=False, index=True)
    serial = db.Column(db.String(8), nullable=False)
    number = db.Column(db.String(16), nullable=False)
    date = db.Column(db.Date, nullable=False)
    origin = db.Column(db.String(256), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    endDate = db.Column(db.Date)

    client = db.relationship(u'Client')
    documentType = db.relationship(u'Rbdocumenttype')

    @property
    def documentTypeCode(self):
        return self.documentType.regionalCode

    def __unicode__(self):
        return (' '.join([self.documentType.name, self.serial, self.number])).strip()


class Clientfdproperty(db.Model):
    __tablename__ = u'ClientFDProperty'

    id = db.Column(db.Integer, primary_key=True)
    flatDirectory_id = db.Column(db.ForeignKey('FlatDirectory.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    version = db.Column(db.Integer, nullable=False)

    flatDirectory = db.relationship(u'Flatdirectory')


class Clientflatdirectory(db.Model):
    __tablename__ = u'ClientFlatDirectory'

    id = db.Column(db.Integer, primary_key=True)
    clientFDProperty_id = db.Column(db.ForeignKey('ClientFDProperty.id'), nullable=False, index=True)
    fdRecord_id = db.Column(db.ForeignKey('FDRecord.id'), nullable=False, index=True)
    dateStart = db.Column(db.DateTime)
    dateEnd = db.Column(db.DateTime)
    createDateTime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, nullable=False)
    modifyDateTime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer)
    deleted = db.Column(db.Integer, nullable=False)
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False, index=True)
    comment = db.Column(db.String)
    version = db.Column(db.Integer, nullable=False)

    clientFDProperty = db.relationship(u'Clientfdproperty')
    client = db.relationship(u'Client')
    fdRecord = db.relationship(u'Fdrecord')


class Clientidentification(db.Model, Info):
    __tablename__ = u'ClientIdentification'
    __table_args__ = (
        db.Index(u'accountingSystem_id', u'accountingSystem_id', u'identifier'),
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False, index=True)
    accountingSystem_id = db.Column(db.Integer, db.ForeignKey('rbAccountingSystem.id'), nullable=False)
    identifier = db.Column(db.String(16), nullable=False)
    checkDate = db.Column(db.Date)
    version = db.Column(db.Integer, nullable=False)

    client = db.relationship(u'Client')
    accountingSystems = db.relationship(u'Rbaccountingsystem')

    @property
    def code(self):
        return self.attachType.code

    @property
    def name(self):
        return self.attachType.name

    # byCode = {code: identifier}
    # nameDict = {code: name}


class Clientintolerancemedicament(db.Model, Info):
    __tablename__ = u'ClientIntoleranceMedicament'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False, index=True)
    name = db.Column("nameMedicament", db.String(128), nullable=False)
    power = db.Column(db.Integer, nullable=False)
    createDate = db.Column(db.Date)
    notes = db.Column(db.String, nullable=False)
    version = db.Column(db.Integer, nullable=False)

    client = db.relationship(u'Client')

    def __unicode__(self):
        return self.name


class Clientpolicy(db.Model, Info):
    __tablename__ = u'ClientPolicy'
    __table_args__ = (
        db.Index(u'Serial_Num', u'serial', u'number'),
        db.Index(u'client_insurer', u'client_id', u'insurer_id')
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    clientId = db.Column("client_id", db.ForeignKey('Client.id'), nullable=False)
    insurer_id = db.Column(db.Integer, db.ForeignKey('Organisation.id'), index=True)
    policyType_id = db.Column(db.Integer, db.ForeignKey('rbPolicyType.id'), index=True)
    serial = db.Column(db.String(16), nullable=False)
    number = db.Column(db.String(16), nullable=False)
    begDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date)
    name = db.Column(db.Unicode(64), nullable=False, server_default=u"''")
    note = db.Column(db.String(200), nullable=False, server_default=u"''")
    version = db.Column(db.Integer, nullable=False)

    client = db.relationship(u'Client')
    insurer = db.relationship(u'Organisation')
    policyType = db.relationship(u'Rbpolicytype')

    def __unicode__(self):
        return (' '.join([self.policyType.name, unicode(self.insurer), self.serial, self.number])).strip()


class Clientrelation(db.Model, Info):
    __tablename__ = u'ClientRelation'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False, index=True)
    relativeType_id = db.Column(db.Integer, db.ForeignKey('rbRelationType.id'), index=True)
    relative_id = db.Column(db.Integer, db.ForeignKey('Client.id'), nullable=False, index=True)
    version = db.Column(db.Integer, nullable=False)

    relativeType = db.relationship(u'Rbrelationtype')

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

    other = db.relationship(u'Client', foreign_keys='Clientrelation.relative_id')

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

    other = db.relationship(u'Client', foreign_keys='Clientrelation.client_id')

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


class Clientsocstatus(db.Model, Info):
    __tablename__ = u'ClientSocStatus'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False, index=True)
    socStatusClass_id = db.Column(db.ForeignKey('rbSocStatusClass.id'), index=True)
    socStatusType_id = db.Column(db.ForeignKey('rbSocStatusType.id'), nullable=False, index=True)
    begDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date)
    document_id = db.Column(db.ForeignKey('ClientDocument.id'), index=True)
    version = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(256), nullable=False, server_default=u"''")
    benefitCategory_id = db.Column(db.Integer)

    client = db.relationship(u'Client')
    socStatusType = db.relationship(u'Rbsocstatustype')
    self_document = db.relationship(u'Clientdocument')

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
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        documents = db_session.query(Clientdocument).filter(Clientdocument.clientId == self.client_id).\
            filter(Clientdocument.deleted == 0).all()
        documents = [document for document in documents if document.documentType and
                     document.documentType.group.code == "1"]
        return documents[-1]

    def __unicode__(self):
        return self.name


class Clientwork(db.Model):
    __tablename__ = u'ClientWork'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False, index=True)
    org_id = db.Column(db.ForeignKey('Organisation.id'), index=True)
    shortName = db.Column('freeInput', db.String(200), nullable=False)
    post = db.Column(db.String(200), nullable=False)
    stage = db.Column(db.Integer, nullable=False)
    OKVED = db.Column(db.String(10), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    rank_id = db.Column(db.Integer, nullable=False)
    arm_id = db.Column(db.Integer, nullable=False)

    client = db.relationship(u'Client')
    organisation = db.relationship(u'Organisation')
    hurts = db.relationship(u'ClientworkHurt')

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


class ClientworkHurt(db.Model, Info):
    __tablename__ = u'ClientWork_Hurt'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.ForeignKey('ClientWork.id'), nullable=False, index=True)
    hurtType_id = db.Column(db.ForeignKey('rbHurtType.id'), nullable=False, index=True)
    stage = db.Column(db.Integer, nullable=False)

    clientWork = db.relationship(u'Clientwork')
    hurtType = db.relationship(u'Rbhurttype')
    factors = db.relationship(u'ClientworkHurtFactor')

    def hurtTypeCode(self):
        return self.hurtType.code

    def hurtTypeName(self):
        return self.hurtType.name

    code = property(hurtTypeCode)
    name = property(hurtTypeName)


class ClientworkHurtFactor(db.Model, Info):
    __tablename__ = u'ClientWork_Hurt_Factor'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.ForeignKey('ClientWork_Hurt.id'), nullable=False, index=True)
    factorType_id = db.Column(db.ForeignKey('rbHurtFactorType.id'), nullable=False, index=True)

    master = db.relationship(u'ClientworkHurt')
    factorType = db.relationship(u'Rbhurtfactortype')

    @property
    def code(self):
        return self.factorType.code

    @property
    def name(self):
        return self.factorType.name


class ClientQuoting(db.Model):
    __tablename__ = u'Client_Quoting'
    __table_args__ = (
        db.Index(u'deleted_prevTalon_event_id', u'deleted', u'prevTalon_event_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    master_id = db.Column(db.ForeignKey('Client.id'), index=True)
    identifier = db.Column(db.String(16))
    quotaTicket = db.Column(db.String(20))
    quotaType_id = db.Column(db.Integer)
    stage = db.Column(db.Integer)
    directionDate = db.Column(db.DateTime, nullable=False)
    freeInput = db.Column(db.String(128))
    org_id = db.Column(db.Integer)
    amount = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    MKB = db.Column(db.String(8), nullable=False)
    status = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    request = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    statment = db.Column(db.String(255))
    dateRegistration = db.Column(db.DateTime, nullable=False)
    dateEnd = db.Column(db.DateTime, nullable=False)
    orgStructure_id = db.Column(db.Integer)
    regionCode = db.Column(db.String(13), index=True)
    pacientModel_id = db.Column(db.Integer, nullable=False)
    treatment_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, index=True)
    prevTalon_event_id = db.Column(db.Integer)
    version = db.Column(db.Integer, nullable=False)

    master = db.relationship(u'Client')


class ClientQuotingdiscussion(db.Model):
    __tablename__ = u'Client_QuotingDiscussion'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.ForeignKey('Client.id'), index=True)
    dateMessage = db.Column(db.DateTime, nullable=False)
    agreementType_id = db.Column(db.Integer)
    responsiblePerson_id = db.Column(db.Integer)
    cosignatory = db.Column(db.String(25))
    cosignatoryPost = db.Column(db.String(20))
    cosignatoryName = db.Column(db.String(50))
    remark = db.Column(db.String(128))

    master = db.relationship(u'Client')


class Contract(db.Model, Info):
    __tablename__ = u'Contract'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    number = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date, nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('Organisation.id'), nullable=False, index=True)
    recipientAccount_id = db.Column(db.Integer, db.ForeignKey('Organisation_Account.id'), index=True)
    recipientKBK = db.Column(db.String(30), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('Organisation.id'), index=True)
    payerAccount_id = db.Column(db.Integer, db.ForeignKey('Organisation_Account.id'), index=True)
    payerKBK = db.Column(db.String(30), nullable=False)
    begDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    finance_id = db.Column(db.Integer, db.ForeignKey('rbFinance.id'), nullable=False, index=True)
    grouping = db.Column(db.String(64), nullable=False)
    resolution = db.Column(db.String(64), nullable=False)
    format_id = db.Column(db.Integer, index=True)
    exposeUnfinishedEventVisits = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    exposeUnfinishedEventActions = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    visitExposition = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    actionExposition = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    exposeDiscipline = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    priceList_id = db.Column(db.Integer)
    coefficient = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    coefficientEx = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")

    recipient = db.relationship(u'Organisation', foreign_keys='Contract.recipient_id')
    payer = db.relationship(u'Organisation', foreign_keys='Contract.payer_id')
    finance = db.relationship(u'Rbfinance')
    recipientAccount = db.relationship(u'OrganisationAccount', foreign_keys='Contract.recipientAccount_id')
    payerAccount = db.relationship(u'OrganisationAccount', foreign_keys='Contract.payerAccount_id')

    def convertToText(self, num):
        converter = NumToTextConverter(num)
        return converter.convert()

    def __unicode__(self):
        return self.number + ' ' + self.date


class ContractContingent(db.Model):
    __tablename__ = u'Contract_Contingent'

    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    master_id = db.Column(db.Integer, nullable=False, index=True)
    client_id = db.Column(db.Integer, index=True)
    attachType_id = db.Column(db.Integer, index=True)
    org_id = db.Column(db.Integer, index=True)
    socStatusType_id = db.Column(db.Integer, index=True)
    insurer_id = db.Column(db.Integer, index=True)
    policyType_id = db.Column(db.Integer, index=True)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.String(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)


class ContractContragent(db.Model):
    __tablename__ = u'Contract_Contragent'

    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    master_id = db.Column(db.Integer, nullable=False, index=True)
    insurer_id = db.Column(db.Integer, nullable=False, index=True)
    payer_id = db.Column(db.Integer, nullable=False, index=True)
    payerAccount_id = db.Column(db.Integer, nullable=False, index=True)
    payerKBK = db.Column(db.String(30), nullable=False)
    begDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)


class ContractSpecification(db.Model):
    __tablename__ = u'Contract_Specification'

    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    master_id = db.Column(db.Integer, nullable=False, index=True)
    eventType_id = db.Column(db.Integer, nullable=False, index=True)


class ContractTariff(db.Model):
    __tablename__ = u'Contract_Tariff'

    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    master_id = db.Column(db.Integer, nullable=False, index=True)
    eventType_id = db.Column(db.Integer, index=True)
    tariffType = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, index=True)
    tariffCategory_id = db.Column(db.Integer, index=True)
    begDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.String(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    unit_id = db.Column(db.Integer, index=True)
    amount = db.Column(db.Float(asdecimal=True), nullable=False)
    uet = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    price = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    limitationExceedMode = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    limitation = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    priceEx = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    MKB = db.Column(db.String(8), nullable=False)
    rbServiceFinance_id = db.Column(db.ForeignKey('rbServiceFinance.id'), index=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer)

    rbServiceFinance = db.relationship(u'Rbservicefinance')


class Couponstransferquote(db.Model):
    __tablename__ = u'CouponsTransferQuotes'

    id = db.Column(db.Integer, primary_key=True)
    srcQuotingType_id = db.Column(db.ForeignKey('rbTimeQuotingType.code'), nullable=False, index=True)
    dstQuotingType_id = db.Column(db.ForeignKey('rbTimeQuotingType.code'), nullable=False, index=True)
    transferDayType = db.Column(db.ForeignKey('rbTransferDateType.code'), nullable=False, index=True)
    transferTime = db.Column(db.Time, nullable=False)
    couponsEnabled = db.Column(db.Integer, server_default=u"'0'")

    dstQuotingType = db.relationship(u'Rbtimequotingtype', primaryjoin='Couponstransferquote.dstQuotingType_id == Rbtimequotingtype.code')
    srcQuotingType = db.relationship(u'Rbtimequotingtype', primaryjoin='Couponstransferquote.srcQuotingType_id == Rbtimequotingtype.code')
    rbTransferDateType = db.relationship(u'Rbtransferdatetype')


class Diagnosi(db.Model):
    __tablename__ = u'Diagnosis'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    client_id = db.Column(db.Integer, nullable=False, index=True)
    diagnosisType_id = db.Column(db.Integer, nullable=False, index=True)
    character_id = db.Column(db.Integer, index=True)
    MKB = db.Column(db.String(8), nullable=False)
    MKBEx = db.Column(db.String(8), nullable=False)
    dispanser_id = db.Column(db.Integer, index=True)
    traumaType_id = db.Column(db.Integer, index=True)
    setDate = db.Column(db.Date)
    endDate = db.Column(db.Date, nullable=False)
    mod_id = db.Column(db.Integer, index=True)
    person_id = db.Column(db.Integer, index=True)
    diagnosisName = db.Column(db.String(64), nullable=False)


class Diagnostic(db.Model):
    __tablename__ = u'Diagnostic'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    event_id = db.Column(db.Integer, nullable=False, index=True)
    diagnosis_id = db.Column(db.Integer, index=True)
    diagnosisType_id = db.Column(db.Integer, nullable=False, index=True)
    character_id = db.Column(db.Integer, index=True)
    stage_id = db.Column(db.Integer, index=True)
    phase_id = db.Column(db.Integer, index=True)
    dispanser_id = db.Column(db.Integer, index=True)
    sanatorium = db.Column(db.Integer, nullable=False)
    hospital = db.Column(db.Integer, nullable=False)
    traumaType_id = db.Column(db.Integer, index=True)
    speciality_id = db.Column(db.Integer, nullable=False, index=True)
    person_id = db.Column(db.Integer, index=True)
    healthGroup_id = db.Column(db.Integer, index=True)
    result_id = db.Column(db.Integer, index=True)
    setDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime)
    notes = db.Column(db.Text, nullable=False)
    rbAcheResult_id = db.Column(db.ForeignKey('rbAcheResult.id'), index=True)
    version = db.Column(db.Integer, nullable=False)
    action_id = db.Column(db.Integer, index=True)

    rbAcheResult = db.relationship(u'Rbacheresult')


class Drugchart(db.Model):
    __tablename__ = u'DrugChart'

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.ForeignKey('Action.id'), nullable=False, index=True)
    master_id = db.Column(db.ForeignKey('DrugChart.id'), index=True)
    begDateTime = db.Column(db.DateTime, nullable=False)
    endDateTime = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=False)
    statusDateTime = db.Column(db.Integer)
    note = db.Column(db.String(256), server_default=u"''")
    uuid = db.Column(db.String(100))
    version = db.Column(db.Integer)

    action = db.relationship(u'Action')
    master = db.relationship(u'Drugchart', remote_side=[id])


class Drugcomponent(db.Model):
    __tablename__ = u'DrugComponent'

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.ForeignKey('Action.id'), nullable=False, index=True)
    nomen = db.Column(db.Integer, index=True)
    name = db.Column(db.String(255))
    dose = db.Column(db.Float)
    unit = db.Column(db.Integer)
    createDateTime = db.Column(db.DateTime, nullable=False)
    cancelDateTime = db.Column(db.DateTime)

    action = db.relationship(u'Action')


class Emergencybrigade(db.Model):
    __tablename__ = u'EmergencyBrigade'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class EmergencybrigadePersonnel(db.Model):
    __tablename__ = u'EmergencyBrigade_Personnel'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    person_id = db.Column(db.Integer, nullable=False, index=True)


class Emergencycall(db.Model):
    __tablename__ = u'EmergencyCall'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    event_id = db.Column(db.Integer, nullable=False, index=True)
    numberCardCall = db.Column(db.String(64), nullable=False)
    brigade_id = db.Column(db.Integer, index=True)
    causeCall_id = db.Column(db.Integer, index=True)
    whoCallOnPhone = db.Column(db.String(64), nullable=False)
    numberPhone = db.Column(db.String(32), nullable=False)
    begDate = db.Column(db.DateTime, nullable=False, index=True)
    passDate = db.Column(db.DateTime, nullable=False, index=True)
    departureDate = db.Column(db.DateTime, nullable=False, index=True)
    arrivalDate = db.Column(db.DateTime, nullable=False, index=True)
    finishServiceDate = db.Column(db.DateTime, nullable=False, index=True)
    endDate = db.Column(db.DateTime, index=True)
    placeReceptionCall_id = db.Column(db.Integer, index=True)
    receivedCall_id = db.Column(db.Integer, index=True)
    reasondDelays_id = db.Column(db.Integer, index=True)
    resultCall_id = db.Column(db.Integer, index=True)
    accident_id = db.Column(db.Integer, index=True)
    death_id = db.Column(db.Integer, index=True)
    ebriety_id = db.Column(db.Integer, index=True)
    diseased_id = db.Column(db.Integer, index=True)
    placeCall_id = db.Column(db.Integer, index=True)
    methodTransport_id = db.Column(db.Integer, index=True)
    transfTransport_id = db.Column(db.Integer, index=True)
    renunOfHospital = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")
    faceRenunOfHospital = db.Column(db.String(64), nullable=False, index=True)
    disease = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")
    birth = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")
    pregnancyFailure = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")
    noteCall = db.Column(db.Text, nullable=False)


class Event(db.Model, Info):
    __tablename__ = u'Event'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    externalId = db.Column(db.String(30), nullable=False)
    eventType_id = db.Column(db.Integer, db.ForeignKey('EventType.id'), nullable=False, index=True)
    org_id = db.Column(db.Integer, db.ForeignKey('Organisation.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('Client.id'), index=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('Contract.id'), index=True)
    prevEventDate = db.Column(db.DateTime)
    setDate = db.Column(db.DateTime, nullable=False, index=True)
    setPerson_id = db.Column(db.Integer, index=True)
    execDate = db.Column(db.DateTime, index=True)
    execPerson_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    isPrimaryCode = db.Column("isPrimary", db.Integer, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    result_id = db.Column(db.Integer, db.ForeignKey('rbResult.id'), index=True)
    nextEventDate = db.Column(db.DateTime)
    payStatus = db.Column(db.Integer, nullable=False)
    typeAsset_id = db.Column(db.Integer, db.ForeignKey('rbEmergencyTypeAsset.id'), index=True)
    note = db.Column(db.Text, nullable=False)
    curator_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    assistant_id = db.Column(db.Integer, db.ForeignKey('Person.id'), index=True)
    pregnancyWeek = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    MES_id = db.Column(db.Integer, index=True)
    mesSpecification_id = db.Column(db.ForeignKey('rbMesSpecification.id'), index=True)
    rbAcheResult_id = db.Column(db.ForeignKey('rbAcheResult.id'), index=True)
    version = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    privilege = db.Column(db.Integer, server_default=u"'0'")
    urgent = db.Column(db.Integer, server_default=u"'0'")
    orgStructure_id = db.Column(db.Integer, db.ForeignKey('Person.orgStructure_id'))
    uuid_id = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")
    lpu_transfer = db.Column(db.String(100))

    actions = db.relationship(u'Action')
    eventType = db.relationship(u'Eventtype')
    execPerson = db.relationship(u'Person', foreign_keys='Event.execPerson_id')
    curator = db.relationship(u'Person', foreign_keys='Event.curator_id')
    assistant = db.relationship(u'Person', foreign_keys='Event.assistant_id')
    contract = db.relationship(u'Contract')
    organisation = db.relationship(u'Organisation')
    mesSpecification = db.relationship(u'Rbmesspecification')
    rbAcheResult = db.relationship(u'Rbacheresult')
    result = db.relationship(u'Rbresult')
    typeAsset = db.relationship(u'Rbemergencytypeasset')
    localContract = db.relationship(u'EventLocalcontract')
    client = db.relationship(u'Client')
    visits = db.relationship(u'Visit')

    @property
    def isPrimary(self):
        return self.isPrimaryCode == 1

    @property
    def finance(self):
        return self.eventType.finance

    @property
    def departmentManager(self):
        from blueprints.print_subsystem.utils import get_lpu_session
        db_session = get_lpu_session()
        persons = db_session.query(Person).filter(Person.orgStructure_id == self.orgStructure_id).all() if self.orgStructure_id else []
        db_session.close()
        if persons:
            for person in persons:
                if person.post.flatCode == u'departmentManager':
                    return person
        return None

    @property
    def date(self):
        date = self.execDate if self.execDate is not None else datetime.date.today()
        return date

    def __unicode__(self):
        return unicode(self.eventType)


class Hsintegration(Event):
    __tablename__ = u'HSIntegration'

    event_id = db.Column(db.ForeignKey('Event.id'), primary_key=True)
    status = db.Column(db.Enum(u'NEW', u'SENDED', u'ERROR'), nullable=False, server_default=u"'NEW'")
    info = db.Column(db.String(1024))


class Eventtype(db.Model, RBInfo):
    __tablename__ = u'EventType'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    purpose_id = db.Column(db.Integer, db.ForeignKey('rbEventTypePurpose.id'), index=True)
    finance_id = db.Column(db.Integer, db.ForeignKey('rbFinance.id'), index=True)
    scene_id = db.Column(db.Integer, index=True)
    visitServiceModifier = db.Column(db.String(128), nullable=False)
    visitServiceFilter = db.Column(db.String(32), nullable=False)
    visitFinance = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    actionFinance = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    period = db.Column(db.Integer, nullable=False)
    singleInPeriod = db.Column(db.Integer, nullable=False)
    isLong = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    dateInput = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    service_id = db.Column(db.Integer, db.ForeignKey('rbService.id'), index=True)
    printContext = db.Column("context", db.String(64), nullable=False)
    form = db.Column(db.String(64), nullable=False)
    minDuration = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    maxDuration = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    showStatusActionsInPlanner = db.Column(db.Integer, nullable=False, server_default=u"'1'")
    showDiagnosticActionsInPlanner = db.Column(db.Integer, nullable=False, server_default=u"'1'")
    showCureActionsInPlanner = db.Column(db.Integer, nullable=False, server_default=u"'1'")
    showMiscActionsInPlanner = db.Column(db.Integer, nullable=False, server_default=u"'1'")
    limitStatusActionsInput = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    limitDiagnosticActionsInput = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    limitCureActionsInput = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    limitMiscActionsInput = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    showTime = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    medicalAidType_id = db.Column(db.Integer, index=True)
    eventProfile_id = db.Column(db.Integer, index=True)
    mesRequired = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    mesCodeMask = db.Column(db.String(64), server_default=u"''")
    mesNameMask = db.Column(db.String(64), server_default=u"''")
    counter_id = db.Column(db.ForeignKey('rbCounter.id'), index=True)
    isExternal = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isAssistant = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isCurator = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    canHavePayableActions = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isRequiredCoordination = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isOrgStructurePriority = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isTakenTissue = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    sex = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    age = db.Column(db.String(9), nullable=False)
    rbMedicalKind_id = db.Column(db.ForeignKey('rbMedicalKind.id'), index=True)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    requestType_id = db.Column(db.Integer, db.ForeignKey('rbRequestType.id'))

    counter = db.relationship(u'Rbcounter')
    rbMedicalKind = db.relationship(u'Rbmedicalkind')
    purpose = db.relationship(u'Rbeventtypepurpose')
    finance = db.relationship(u'Rbfinance')
    service = db.relationship(u'Rbservice')
    requestType = db.relationship(u'Rbrequesttype')


class Eventtypeform(db.Model):
    __tablename__ = u'EventTypeForm'

    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    eventType_id = db.Column(db.Integer, nullable=False, index=True)
    code = db.Column(db.String(8), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    descr = db.Column(db.String(64), nullable=False)
    pass_ = db.Column(u'pass', db.Integer, nullable=False)


class EventtypeAction(db.Model):
    __tablename__ = u'EventType_Action'

    id = db.Column(db.Integer, primary_key=True)
    eventType_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    actionType_id = db.Column(db.Integer, nullable=False, index=True)
    speciality_id = db.Column(db.Integer, index=True)
    tissueType_id = db.Column(db.ForeignKey('rbTissueType.id'), index=True)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.String(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    selectionGroup = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    actuality = db.Column(db.Integer, nullable=False)
    expose = db.Column(db.Integer, nullable=False, server_default=u"'1'")
    payable = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    academicDegree_id = db.Column(db.Integer, index=True)

    tissueType = db.relationship(u'Rbtissuetype')


class EventtypeDiagnostic(db.Model):
    __tablename__ = u'EventType_Diagnostic'

    id = db.Column(db.Integer, primary_key=True)
    eventType_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    speciality_id = db.Column(db.Integer, index=True)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.String(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    defaultHealthGroup_id = db.Column(db.Integer, index=True)
    defaultMKB = db.Column(db.String(5), nullable=False)
    defaultDispanser_id = db.Column(db.Integer, index=True)
    selectionGroup = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    actuality = db.Column(db.Integer, nullable=False)
    visitType_id = db.Column(db.Integer)


class EventFeed(db.Model):
    __tablename__ = u'Event_Feed'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    event_id = db.Column(db.Integer, nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False)
    mealTime_id = db.Column(db.Integer, index=True)
    diet_id = db.Column(db.Integer, index=True)


class EventLocalcontract(db.Model, Info):
    __tablename__ = u'Event_LocalContract'
    __table_args__ = (
        db.Index(u'lastName', u'lastName', u'firstName', u'patrName', u'birthDate', u'id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey('Event.id'), nullable=False, index=True)
    coordDate = db.Column(db.DateTime)
    coordAgent = db.Column(db.String(128), nullable=False, server_default=u"''")
    coordInspector = db.Column(db.String(128), nullable=False, server_default=u"''")
    coordText = db.Column(db.String, nullable=False)
    dateContract = db.Column(db.Date, nullable=False)
    numberContract = db.Column(db.Unicode(64), nullable=False)
    sumLimit = db.Column(db.Float(asdecimal=True), nullable=False)
    lastName = db.Column(db.Unicode(30), nullable=False)
    firstName = db.Column(db.Unicode(30), nullable=False)
    patrName = db.Column(db.Unicode(30), nullable=False)
    birthDate = db.Column(db.Date, nullable=False, index=True)
    documentType_id = db.Column(db.Integer, db.ForeignKey('rbDocumentType.id'), index=True)
    serialLeft = db.Column(db.Unicode(8), nullable=False)
    serialRight = db.Column(db.Unicode(8), nullable=False)
    number = db.Column(db.String(16), nullable=False)
    regAddress = db.Column(db.Unicode(64), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey('Organisation.id'), index=True)

    org = db.relationship(u'Organisation')
    documentType = db.relationship(u'Rbdocumenttype')

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


class EventPayment(db.Model):
    __tablename__ = u'Event_Payment'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    cashOperation_id = db.Column(db.ForeignKey('rbCashOperation.id'), index=True)
    sum = db.Column(db.Float(asdecimal=True), nullable=False)
    typePayment = db.Column(db.Integer, nullable=False)
    settlementAccount = db.Column(db.String(64))
    bank_id = db.Column(db.Integer, index=True)
    numberCreditCard = db.Column(db.String(64))
    cashBox = db.Column(db.String(32), nullable=False)

    cashOperation = db.relationship(u'Rbcashoperation')


class EventPerson(db.Model):
    __tablename__ = u'Event_Persons'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, nullable=False, index=True)
    person_id = db.Column(db.Integer, nullable=False, index=True)
    begDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime)


class Fdfield(db.Model):
    __tablename__ = u'FDField'

    id = db.Column(db.Integer, primary_key=True)
    fdFieldType_id = db.Column(db.ForeignKey('FDFieldType.id'), nullable=False, index=True)
    flatDirectory_id = db.Column(db.ForeignKey('FlatDirectory.id'), nullable=False, index=True)
    flatDirectory_code = db.Column(db.ForeignKey('FlatDirectory.code'), index=True)
    name = db.Column(db.String(4096), nullable=False)
    description = db.Column(db.String(4096))
    mask = db.Column(db.String(4096))
    mandatory = db.Column(db.Integer)
    order = db.Column(db.Integer)

    fdFieldType = db.relationship(u'Fdfieldtype')
    flatDirectory = db.relationship(u'Flatdirectory', primaryjoin='Fdfield.flatDirectory_id == Flatdirectory.id')

    values = db.relationship(u'Fdfieldvalue', backref=db.backref('fdField'), lazy='dynamic')

    def get_value(self, record_id):
        return self.values.filter(Fdfieldvalue.fdRecord_id == record_id).first().value


class Fdfieldtype(db.Model):
    __tablename__ = u'FDFieldType'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(4096), nullable=False)
    description = db.Column(db.String(4096))


class Fdfieldvalue(db.Model):
    __tablename__ = u'FDFieldValue'

    id = db.Column(db.Integer, primary_key=True)
    fdRecord_id = db.Column(db.ForeignKey('FDRecord.id'), nullable=False, index=True)
    fdField_id = db.Column(db.ForeignKey('FDField.id'), nullable=False, index=True)
    value = db.Column(db.String)

    # fdRecord = db.relationship(u'Fdrecord')


class Fdrecord(db.Model):
    __tablename__ = u'FDRecord'

    id = db.Column(db.Integer, primary_key=True)
    flatDirectory_id = db.Column(db.ForeignKey('FlatDirectory.id'), nullable=False, index=True)
    flatDirectory_code = db.Column(db.ForeignKey('FlatDirectory.code'), index=True)
    order = db.Column(db.Integer)
    name = db.Column(db.String(4096))
    description = db.Column(db.String(4096))
    dateStart = db.Column(db.DateTime)
    dateEnd = db.Column(db.DateTime)

    FlatDirectory = db.relationship(u'Flatdirectory', primaryjoin='Fdrecord.flatDirectory_code == Flatdirectory.code')
    flatDirectory = db.relationship(u'Flatdirectory', primaryjoin='Fdrecord.flatDirectory_id == Flatdirectory.id')
    values = db.relationship(u'Fdfieldvalue', backref=db.backref('Fdrecord'), lazy='dynamic')

    def get_value(self):
        return [value.value for value in self.values]
        #return [field.get_value(self.id) for field in self.FlatDirectory.fields] # в нтк столбцы не упорядочены


class Flatdirectory(db.Model):
    __tablename__ = u'FlatDirectory'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(4096), nullable=False)
    code = db.Column(db.String(128), index=True)
    description = db.Column(db.String(4096))

    fields = db.relationship(u'Fdfield', foreign_keys='Fdfield.flatDirectory_code', backref=db.backref('FlatDirectory'),
                             lazy='dynamic')


class Informermessage(db.Model):
    __tablename__ = u'InformerMessage'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(128), nullable=False)
    text = db.Column(db.String, nullable=False)


class InformermessageReadmark(db.Model):
    __tablename__ = u'InformerMessage_readMark'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    person_id = db.Column(db.Integer, index=True)


class Job(db.Model):
    __tablename__ = u'Job'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    jobType_id = db.Column(db.Integer, db.ForeignKey('rbJobType.id'), nullable=False, index=True)
    orgStructure_id = db.Column(db.Integer, db.ForeignKey('OrgStructure.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    begTime = db.Column(db.Time, nullable=False)
    endTime = db.Column(db.Time, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    job_type = db.relationship(u'Rbjobtype')
    org_structure = db.relationship(u'Orgstructure')


class JobTicket(db.Model, Info):
    __tablename__ = u'Job_Ticket'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, db.ForeignKey('Job.id'), nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    datetime = db.Column(db.DateTime, nullable=False)
    resTimestamp = db.Column(db.DateTime)
    resConnectionId = db.Column(db.Integer)
    status = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    begDateTime = db.Column(db.DateTime)
    endDateTime = db.Column(db.DateTime)
    label = db.Column(db.String(64), nullable=False, server_default=u"''")
    note = db.Column(db.String(128), nullable=False, server_default=u"''")

    job = db.relationship(u'Job')

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


class Lastchange(db.Model):
    __tablename__ = u'LastChanges'

    id = db.Column(db.Integer, primary_key=True)
    table = db.Column(db.String(32), nullable=False)
    table_key_id = db.Column(db.Integer, nullable=False)
    flags = db.Column(db.Text, nullable=False)


class Layoutattribute(db.Model):
    __tablename__ = u'LayoutAttribute'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1023), nullable=False)
    code = db.Column(db.String(255), nullable=False)
    typeName = db.Column(db.String(255))
    measure = db.Column(db.String(255))
    defaultValue = db.Column(db.String(1023))


class Layoutattributevalue(db.Model):
    __tablename__ = u'LayoutAttributeValue'

    id = db.Column(db.Integer, primary_key=True)
    actionPropertyType_id = db.Column(db.Integer, nullable=False)
    layoutAttribute_id = db.Column(db.ForeignKey('LayoutAttribute.id'), nullable=False, index=True)
    value = db.Column(db.String(1023), nullable=False)

    layoutAttribute = db.relationship(u'Layoutattribute')


class Licence(db.Model):
    __tablename__ = u'Licence'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    serial = db.Column(db.String(8), nullable=False)
    number = db.Column(db.String(16), nullable=False)
    date = db.Column(db.Date, nullable=False)
    person_id = db.Column(db.Integer, index=True)
    begDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)


class LicenceService(db.Model):
    __tablename__ = u'Licence_Service'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    service_id = db.Column(db.Integer, nullable=False, index=True)


class Mkb(db.Model, Info):
    __tablename__ = u'MKB'
    __table_args__ = (
        db.Index(u'BlockID', u'BlockID', u'DiagID'),
        db.Index(u'ClassID_2', u'ClassID', u'BlockID', u'BlockName'),
        db.Index(u'ClassID', u'ClassID', u'ClassName')
    )

    id = db.Column(db.Integer, primary_key=True)
    ClassID = db.Column(db.String(8), nullable=False)
    ClassName = db.Column(db.String(150), nullable=False)
    BlockID = db.Column(db.String(9), nullable=False)
    BlockName = db.Column(db.String(160), nullable=False)
    DiagID = db.Column(db.String(8), nullable=False, index=True)
    DiagName = db.Column(db.String(160), nullable=False, index=True)
    Prim = db.Column(db.String(1), nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.String(12), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    characters = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, index=True)
    MKBSubclass_id = db.Column(db.Integer)

    def __unicode__(self):
        return self.DiagID


class MkbQuotatypePacientmodel(db.Model):
    __tablename__ = u'MKB_QuotaType_PacientModel'

    id = db.Column(db.Integer, primary_key=True)
    MKB_id = db.Column(db.Integer, nullable=False)
    pacientModel_id = db.Column(db.Integer, nullable=False)
    quotaType_id = db.Column(db.Integer, nullable=False)


class Media(db.Model):
    __tablename__ = u'Media'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256, u'utf8_bin'), nullable=False)
    file = db.Column(MEDIUMBLOB)


class Medicalkindunit(db.Model):
    __tablename__ = u'MedicalKindUnit'

    id = db.Column(db.Integer, primary_key=True)
    rbMedicalKind_id = db.Column(db.ForeignKey('rbMedicalKind.id'), nullable=False, index=True)
    eventType_id = db.Column(db.ForeignKey('EventType.id'), index=True)
    rbMedicalAidUnit_id = db.Column(db.ForeignKey('rbMedicalAidUnit.id'), nullable=False, index=True)
    rbPayType_id = db.Column(db.ForeignKey('rbPayType.id'), nullable=False, index=True)
    rbTariffType_id = db.Column(db.ForeignKey('rbTariffType.id'), nullable=False, index=True)

    eventType = db.relationship(u'Eventtype')
    rbMedicalAidUnit = db.relationship(u'Rbmedicalaidunit')
    rbMedicalKind = db.relationship(u'Rbmedicalkind')
    rbPayType = db.relationship(u'Rbpaytype')
    rbTariffType = db.relationship(u'Rbtarifftype')


class Meta(db.Model):
    __tablename__ = u'Meta'

    name = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text)


class Modeldescription(db.Model):
    __tablename__ = u'ModelDescription'

    id = db.Column(db.Integer, primary_key=True)
    idx = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")
    name = db.Column(db.String(64), nullable=False)
    fieldIdx = db.Column(db.Integer, nullable=False, server_default=u"'-1'")
    tableName = db.Column(db.String(64), nullable=False)


class Notificationoccurred(db.Model):
    __tablename__ = u'NotificationOccurred'

    id = db.Column(db.Integer, primary_key=True)
    eventDatetime = db.Column(db.DateTime, nullable=False)
    clientId = db.Column(db.Integer, nullable=False)
    userId = db.Column(db.ForeignKey('Person.id'), nullable=False, index=True)

    Person = db.relationship(u'Person')


class Orgstructure(db.Model, Info):
    __tablename__ = u'OrgStructure'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    organisation_id = db.Column(db.Integer, db.ForeignKey('Organisation.id'), nullable=False, index=True)
    code = db.Column(db.Unicode(255), nullable=False)
    name = db.Column(db.Unicode(255), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('OrgStructure.id'), index=True)
    type = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    net_id = db.Column(db.Integer, db.ForeignKey('rbNet.id'), index=True)
    isArea = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    hasHospitalBeds = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    hasStocks = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    infisCode = db.Column(db.String(16), nullable=False)
    infisInternalCode = db.Column(db.String(16), nullable=False)
    infisDepTypeCode = db.Column(db.String(16), nullable=False)
    infisTariffCode = db.Column(db.String(16), nullable=False)
    availableForExternal = db.Column(db.Integer, nullable=False, server_default=u"'1'")
    Address = db.Column(db.String(255), nullable=False)
    inheritEventTypes = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    inheritActionTypes = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    inheritGaps = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    uuid_id = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")
    show = db.Column(db.Integer, nullable=False, server_default=u"'1'")

    parent = db.relationship(u'Orgstructure', lazy="immediate", remote_side=[id])
    organisation = db.relationship(u'Organisation')
    Net = db.relationship(u'Rbnet')

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


class OrgstructureActiontype(db.Model):
    __tablename__ = u'OrgStructure_ActionType'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    actionType_id = db.Column(db.Integer, index=True)


class OrgstructureAddres(db.Model):
    __tablename__ = u'OrgStructure_Address'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    house_id = db.Column(db.Integer, nullable=False, index=True)
    firstFlat = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    lastFlat = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class OrgstructureDisabledattendance(db.Model):
    __tablename__ = u'OrgStructure_DisabledAttendance'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.ForeignKey('OrgStructure.id'), nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    attachType_id = db.Column(db.ForeignKey('rbAttachType.id'), index=True)
    disabledType = db.Column(db.Integer, nullable=False, server_default=u"'0'")

    attachType = db.relationship(u'Rbattachtype')
    master = db.relationship(u'Orgstructure')


class OrgstructureEventtype(db.Model):
    __tablename__ = u'OrgStructure_EventType'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    eventType_id = db.Column(db.Integer, index=True)


class OrgstructureGap(db.Model):
    __tablename__ = u'OrgStructure_Gap'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    begTime = db.Column(db.Time, nullable=False)
    endTime = db.Column(db.Time, nullable=False)
    speciality_id = db.Column(db.Integer, index=True)
    person_id = db.Column(db.Integer, index=True)


class OrgstructureHospitalbed(db.Model, Info):
    __tablename__ = u'OrgStructure_HospitalBed'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, db.ForeignKey('OrgStructure.id'), nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    code = db.Column(db.String(16), nullable=False, server_default=u"''")
    name = db.Column(db.String(64), nullable=False, server_default=u"''")
    isPermanentCode = db.Column("isPermanent", db.Integer, nullable=False, server_default=u"'0'")
    type_id = db.Column(db.Integer, db.ForeignKey('rbHospitalBedType.id'), index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('rbHospitalBedProfile.id'), index=True)
    relief = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    schedule_id = db.Column(db.Integer, db.ForeignKey('rbHospitalBedShedule.id'), index=True)
    begDate = db.Column(db.Date)
    endDate = db.Column(db.Date)
    sex = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    age = db.Column(db.String(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    involution = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    begDateInvolute = db.Column(db.Date)
    endDateInvolute = db.Column(db.Date)

    orgStructure = db.relationship(u'Orgstructure')
    type = db.relationship(u'Rbhospitalbedtype')
    profile = db.relationship(u'Rbhospitalbedprofile')
    schedule = db.relationship(u'Rbhospitalbedshedule')

    @property
    def isPermanent(self):
        return self.isPermanentCode == 1


class OrgstructureJob(db.Model):
    __tablename__ = u'OrgStructure_Job'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    jobType_id = db.Column(db.Integer, index=True)
    begTime = db.Column(db.Time, nullable=False)
    endTime = db.Column(db.Time, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class OrgstructureStock(db.Model):
    __tablename__ = u'OrgStructure_Stock'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.ForeignKey('OrgStructure.id'), nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = db.Column(db.ForeignKey('rbNomenclature.id'), index=True)
    finance_id = db.Column(db.ForeignKey('rbFinance.id'), index=True)
    constrainedQnt = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    orderQnt = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")

    finance = db.relationship(u'Rbfinance')
    master = db.relationship(u'Orgstructure')
    nomenclature = db.relationship(u'Rbnomenclature')


class Organisation(db.Model, Info):
    __tablename__ = u'Organisation'
    __table_args__ = (
        db.Index(u'shortName', u'shortName', u'INN', u'OGRN'),
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    fullName = db.Column(db.Unicode(255), nullable=False)
    shortName = db.Column(db.Unicode(255), nullable=False)
    title = db.Column(db.Unicode(255), nullable=False, index=True)
    net_id = db.Column(db.Integer, db.ForeignKey('rbNet.id'), index=True)
    infisCode = db.Column(db.String(12), nullable=False, index=True)
    obsoleteInfisCode = db.Column(db.String(60), nullable=False)
    OKVED = db.Column(db.String(64), nullable=False, index=True)
    INN = db.Column(db.String(15), nullable=False, index=True)
    KPP = db.Column(db.String(15), nullable=False)
    OGRN = db.Column(db.String(15), nullable=False, index=True)
    OKATO = db.Column(db.String(15), nullable=False)
    OKPF_code = db.Column(db.String(4), nullable=False)
    OKPF_id = db.Column(db.Integer, db.ForeignKey('rbOKPF.id'), index=True)
    OKFS_code = db.Column(db.Integer, nullable=False)
    OKFS_id = db.Column(db.Integer, db.ForeignKey('rbOKFS.id'), index=True)
    OKPO = db.Column(db.String(15), nullable=False)
    FSS = db.Column(db.String(10), nullable=False)
    region = db.Column(db.Unicode(40), nullable=False)
    Address = db.Column(db.Unicode(255), nullable=False)
    chief = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    accountant = db.Column(db.String(64), nullable=False)
    isInsurer = db.Column(db.Integer, nullable=False, index=True)
    compulsoryServiceStop = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    voluntaryServiceStop = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    area = db.Column(db.String(13), nullable=False)
    isHospital = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    notes = db.Column(db.String, nullable=False)
    head_id = db.Column(db.Integer, index=True)
    miacCode = db.Column(db.String(10), nullable=False)
    isOrganisation = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    uuid_id = db.Column(db.Integer, nullable=False, index=True, server_default=u"'0'")


    net = db.relationship(u'Rbnet')
    OKPF = db.relationship(u'Rbokpf')
    OKFS = db.relationship(u'Rbokfs')
    org_accounts = db.relationship(u'OrganisationAccount')

    @property
    def bank(self):
        return [account.bank for account in self.org_accounts]

    def __unicode__(self):
        return self.shortName


class OrganisationAccount(db.Model, Info):
    __tablename__ = u'Organisation_Account'

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey('Organisation.id'), nullable=False, index=True)
    bankName = db.Column(db.Unicode(128), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.String, nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('Bank.id'), nullable=False, index=True)
    cash = db.Column(db.Integer, nullable=False)

    org = db.relationship(u'Organisation')
    bank = db.relationship(u'Bank')


class OrganisationPolicyserial(db.Model):
    __tablename__ = u'Organisation_PolicySerial'

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, nullable=False, index=True)
    serial = db.Column(db.String(16), nullable=False)
    policyType_id = db.Column(db.Integer, index=True)


class Person(db.Model):
    __tablename__ = u'Person'
    __table_args__ = (
        db.Index(u'lastName', u'lastName', u'firstName', u'patrName'),
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    code = db.Column(db.String(12), nullable=False)
    federalCode = db.Column(db.Unicode(255), nullable=False)
    regionalCode = db.Column(db.String(16), nullable=False)
    lastName = db.Column(db.Unicode(30), nullable=False)
    firstName = db.Column(db.Unicode(30), nullable=False)
    patrName = db.Column(db.Unicode(30), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('rbPost.id'), index=True)
    speciality_id = db.Column(db.Integer, db.ForeignKey('rbSpeciality.id'), index=True)
    org_id = db.Column(db.Integer, db.ForeignKey('Organisation.id'), index=True)
    orgStructure_id = db.Column(db.Integer, db.ForeignKey('OrgStructure.id'), index=True)
    office = db.Column(db.Unicode(8), nullable=False)
    office2 = db.Column(db.Unicode(8), nullable=False)
    tariffCategory_id = db.Column(db.Integer, db.ForeignKey('rbTariffCategory.id'), index=True)
    finance_id = db.Column(db.Integer, db.ForeignKey('rbFinance.id'), index=True)
    retireDate = db.Column(db.Date, index=True)
    ambPlan = db.Column(db.SmallInteger, nullable=False)
    ambPlan2 = db.Column(db.SmallInteger, nullable=False)
    ambNorm = db.Column(db.SmallInteger, nullable=False)
    homPlan = db.Column(db.SmallInteger, nullable=False)
    homPlan2 = db.Column(db.SmallInteger, nullable=False)
    homNorm = db.Column(db.SmallInteger, nullable=False)
    expPlan = db.Column(db.SmallInteger, nullable=False)
    expNorm = db.Column(db.SmallInteger, nullable=False)
    login = db.Column(db.Unicode(32), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    userProfile_id = db.Column(db.Integer, index=True)
    retired = db.Column(db.Integer, nullable=False)
    birthDate = db.Column(db.Date, nullable=False)
    birthPlace = db.Column(db.String(64), nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    SNILS = db.Column(db.String(11), nullable=False)
    INN = db.Column(db.String(15), nullable=False)
    availableForExternal = db.Column(db.Integer, nullable=False, server_default=u"'1'")
    primaryQuota = db.Column(db.SmallInteger, nullable=False, server_default=u"'50'")
    ownQuota = db.Column(db.SmallInteger, nullable=False, server_default=u"'25'")
    consultancyQuota = db.Column(db.SmallInteger, nullable=False, server_default=u"'25'")
    externalQuota = db.Column(db.SmallInteger, nullable=False, server_default=u"'10'")
    lastAccessibleTimelineDate = db.Column(db.Date)
    timelineAccessibleDays = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    typeTimeLinePerson = db.Column(db.Integer, nullable=False)
    maxOverQueue = db.Column(db.Integer, server_default=u"'0'")
    maxCito = db.Column(db.Integer, server_default=u"'0'")
    quotUnit = db.Column(db.Integer, server_default=u"'0'")
    academicdegree_id = db.Column(db.Integer, db.ForeignKey('rbAcademicDegree.id'))
    academicTitle_id = db.Column(db.Integer, db.ForeignKey('rbAcademicTitle.id'))

    post = db.relationship(u'Rbpost')
    speciality = db.relationship(u'Rbspeciality')
    organisation = db.relationship(u'Organisation')
    orgStructure = db.relationship(u'Orgstructure')
    academicDegree = db.relationship(u'Rbacademicdegree')
    academicTitle = db.relationship(u'Rbacademictitle')
    tariffCategory = db.relationship(u'Rbtariffcategory')

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
        result = formatShortNameInt(self.lastName, self.firstName, self.patrName)
        if self.speciality:
            result += ', '+self.speciality.name
        return unicode(result)


class Personaddres(db.Model):
    __tablename__ = u'PersonAddress'
    __table_args__ = (
        db.Index(u'person_id', u'person_id', u'type', u'address_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    address_id = db.Column(db.Integer)


class Persondocument(db.Model):
    __tablename__ = u'PersonDocument'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, nullable=False, index=True)
    documentType_id = db.Column(db.Integer, index=True)
    serial = db.Column(db.String(8), nullable=False)
    number = db.Column(db.String(16), nullable=False)
    date = db.Column(db.Date, nullable=False)
    origin = db.Column(db.String(64), nullable=False)


class Personeducation(db.Model):
    __tablename__ = u'PersonEducation'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, nullable=False, index=True)
    documentType_id = db.Column(db.Integer, index=True)
    serial = db.Column(db.String(8), nullable=False)
    number = db.Column(db.String(16), nullable=False)
    date = db.Column(db.Date, nullable=False)
    origin = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    validFromDate = db.Column(db.Date)
    validToDate = db.Column(db.Date)
    speciality_id = db.Column(db.Integer)
    educationCost = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    cost = db.Column(db.Float(asdecimal=True))


class Personorder(db.Model):
    __tablename__ = u'PersonOrder'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(64), nullable=False)
    documentDate = db.Column(db.Date, nullable=False)
    documentNumber = db.Column(db.String(16), nullable=False)
    documentType_id = db.Column(db.Integer, index=True)
    salary = db.Column(db.String(64), nullable=False)
    validFromDate = db.Column(db.Date)
    validToDate = db.Column(db.Date)
    orgStructure_id = db.Column(db.Integer, index=True)
    post_id = db.Column(db.Integer, index=True)


class Persontimetemplate(db.Model):
    __tablename__ = u'PersonTimeTemplate'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    master_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    ambBegTime = db.Column(db.Time)
    ambEndTime = db.Column(db.Time)
    ambPlan = db.Column(db.SmallInteger, nullable=False)
    office = db.Column(db.String(8), nullable=False)
    ambBegTime2 = db.Column(db.Time)
    ambEndTime2 = db.Column(db.Time)
    ambPlan2 = db.Column(db.SmallInteger, nullable=False)
    office2 = db.Column(db.String(8), nullable=False)
    homBegTime = db.Column(db.Time)
    homEndTime = db.Column(db.Time)
    homPlan = db.Column(db.SmallInteger, nullable=False)
    homBegTime2 = db.Column(db.Time)
    homEndTime2 = db.Column(db.Time)
    homPlan2 = db.Column(db.SmallInteger, nullable=False)


class PersonActivity(db.Model):
    __tablename__ = u'Person_Activity'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    activity_id = db.Column(db.Integer, index=True)


class PersonProfile(db.Model):
    __tablename__ = u'Person_Profiles'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, nullable=False, index=True)
    userProfile_id = db.Column(db.Integer, nullable=False, index=True)


class PersonTimetemplate(db.Model):
    __tablename__ = u'Person_TimeTemplate'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    master_id = db.Column(db.ForeignKey('Person.id'), nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    ambBegTime = db.Column(db.Time)
    ambEndTime = db.Column(db.Time)
    ambPlan = db.Column(db.SmallInteger, nullable=False)
    office = db.Column(db.String(8), nullable=False)
    ambBegTime2 = db.Column(db.Time)
    ambEndTime2 = db.Column(db.Time)
    ambPlan2 = db.Column(db.SmallInteger, nullable=False)
    office2 = db.Column(db.String(8), nullable=False)
    homBegTime = db.Column(db.Time)
    homEndTime = db.Column(db.Time)
    homPlan = db.Column(db.SmallInteger, nullable=False)
    homBegTime2 = db.Column(db.Time)
    homEndTime2 = db.Column(db.Time)
    homPlan2 = db.Column(db.SmallInteger, nullable=False)

    createPerson = db.relationship(u'Person', primaryjoin='PersonTimetemplate.createPerson_id == Person.id')
    master = db.relationship(u'Person', primaryjoin='PersonTimetemplate.master_id == Person.id')
    modifyPerson = db.relationship(u'Person', primaryjoin='PersonTimetemplate.modifyPerson_id == Person.id')


class Pharmacy(db.Model):
    __tablename__ = u'Pharmacy'

    actionId = db.Column(db.Integer, primary_key=True)
    flatCode = db.Column(db.String(255))
    attempts = db.Column(db.Integer, server_default=u"'0'")
    status = db.Column(db.Enum(u'ADDED', u'COMPLETE', u'ERROR'), server_default=u"'ADDED'")
    uuid = db.Column(db.String(255), server_default=u"'0'")
    result = db.Column(db.String(255), server_default=u"''")
    error_string = db.Column(db.String(255))
    rev = db.Column(db.String(255), server_default=u"''")
    value = db.Column(db.Integer, server_default=u"'0'")


class Prescriptionsendingre(db.Model):
    __tablename__ = u'PrescriptionSendingRes'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100))
    version = db.Column(db.Integer)
    interval_id = db.Column(db.ForeignKey('DrugChart.id'), index=True)
    drugComponent_id = db.Column(db.ForeignKey('DrugComponent.id'), index=True)

    drugComponent = db.relationship(u'Drugcomponent')
    interval = db.relationship(u'Drugchart')


class Prescriptionsto1c(db.Model):
    __tablename__ = u'PrescriptionsTo1C'

    interval_id = db.Column(db.Integer, primary_key=True)
    errCount = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    info = db.Column(db.String(1024))
    is_prescription = db.Column(db.Integer)
    new_status = db.Column(db.Integer)
    old_status = db.Column(db.Integer)
    sendTime = db.Column(db.DateTime, nullable=False, server_default=u'CURRENT_TIMESTAMP')


class Quotatype(db.Model):
    __tablename__ = u'QuotaType'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    class_ = db.Column(u'class', db.Integer, nullable=False)
    group_code = db.Column(db.String(16))
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.Unicode(255), nullable=False)
    teenOlder = db.Column(db.Integer, nullable=False)

    def __unicode__(self):
        return self.name


class Quoting(db.Model):
    __tablename__ = u'Quoting'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    quotaType_id = db.Column(db.Integer)
    beginDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    limitation = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    used = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    confirmed = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    inQueue = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Quotingbyspeciality(db.Model):
    __tablename__ = u'QuotingBySpeciality'

    id = db.Column(db.Integer, primary_key=True)
    speciality_id = db.Column(db.ForeignKey('rbSpeciality.id'), nullable=False, index=True)
    organisation_id = db.Column(db.ForeignKey('Organisation.id'), nullable=False, index=True)
    coupons_quote = db.Column(db.Integer)
    coupons_remaining = db.Column(db.Integer)

    organisation = db.relationship(u'Organisation')
    speciality = db.relationship(u'Rbspeciality')


class Quotingbytime(db.Model):
    __tablename__ = u'QuotingByTime'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer)
    quoting_date = db.Column(db.Date, nullable=False)
    QuotingTimeStart = db.Column(db.Time, nullable=False)
    QuotingTimeEnd = db.Column(db.Time, nullable=False)
    QuotingType = db.Column(db.Integer)


class QuotingRegion(db.Model):
    __tablename__ = u'Quoting_Region'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    master_id = db.Column(db.Integer, index=True)
    region_code = db.Column(db.String(13), index=True)
    limitation = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    used = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    confirmed = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    inQueue = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Setting(db.Model):
    __tablename__ = u'Setting'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255), nullable=False, unique=True)
    value = db.Column(db.Text, nullable=False)


class Socstatu(db.Model):
    __tablename__ = u'SocStatus'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    socStatusClass_id = db.Column(db.Integer, nullable=False, index=True)
    socStatusType_id = db.Column(db.Integer, nullable=False, index=True)


class Stockmotion(db.Model):
    __tablename__ = u'StockMotion'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, server_default=u"'0'")
    date = db.Column(db.DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    supplier_id = db.Column(db.ForeignKey('OrgStructure.id'), index=True)
    receiver_id = db.Column(db.ForeignKey('OrgStructure.id'), index=True)
    note = db.Column(db.String, nullable=False)
    supplierPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    receiverPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)

    createPerson = db.relationship(u'Person', primaryjoin='Stockmotion.createPerson_id == Person.id')
    modifyPerson = db.relationship(u'Person', primaryjoin='Stockmotion.modifyPerson_id == Person.id')
    receiverPerson = db.relationship(u'Person', primaryjoin='Stockmotion.receiverPerson_id == Person.id')
    receiver = db.relationship(u'Orgstructure', primaryjoin='Stockmotion.receiver_id == Orgstructure.id')
    supplierPerson = db.relationship(u'Person', primaryjoin='Stockmotion.supplierPerson_id == Person.id')
    supplier = db.relationship(u'Orgstructure', primaryjoin='Stockmotion.supplier_id == Orgstructure.id')


class StockmotionItem(db.Model):
    __tablename__ = u'StockMotion_Item'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.ForeignKey('StockMotion.id'), nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = db.Column(db.ForeignKey('rbNomenclature.id'), index=True)
    finance_id = db.Column(db.ForeignKey('rbFinance.id'), index=True)
    qnt = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    sum = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    oldQnt = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    oldSum = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    oldFinance_id = db.Column(db.ForeignKey('rbFinance.id'), index=True)
    isOut = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    note = db.Column(db.String, nullable=False)

    finance = db.relationship(u'Rbfinance', primaryjoin='StockmotionItem.finance_id == Rbfinance.id')
    master = db.relationship(u'Stockmotion')
    nomenclature = db.relationship(u'Rbnomenclature')
    oldFinance = db.relationship(u'Rbfinance', primaryjoin='StockmotionItem.oldFinance_id == Rbfinance.id')


class Stockrecipe(db.Model):
    __tablename__ = u'StockRecipe'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.ForeignKey('StockRecipe.id'), index=True)
    code = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(64), nullable=False)

    createPerson = db.relationship(u'Person', primaryjoin='Stockrecipe.createPerson_id == Person.id')
    group = db.relationship(u'Stockrecipe', remote_side=[id])
    modifyPerson = db.relationship(u'Person', primaryjoin='Stockrecipe.modifyPerson_id == Person.id')


class StockrecipeItem(db.Model):
    __tablename__ = u'StockRecipe_Item'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.ForeignKey('StockRecipe.id'), nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = db.Column(db.ForeignKey('rbNomenclature.id'), index=True)
    qnt = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    isOut = db.Column(db.Integer, nullable=False, server_default=u"'0'")

    master = db.relationship(u'Stockrecipe')
    nomenclature = db.relationship(u'Rbnomenclature')


class Stockrequisition(db.Model):
    __tablename__ = u'StockRequisition'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    createPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    modifyPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    date = db.Column(db.Date, nullable=False, server_default=u"'0000-00-00'")
    deadline = db.Column(db.DateTime)
    supplier_id = db.Column(db.ForeignKey('OrgStructure.id'), index=True)
    recipient_id = db.Column(db.ForeignKey('OrgStructure.id'), index=True)
    revoked = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    note = db.Column(db.String, nullable=False)

    createPerson = db.relationship(u'Person', primaryjoin='Stockrequisition.createPerson_id == Person.id')
    modifyPerson = db.relationship(u'Person', primaryjoin='Stockrequisition.modifyPerson_id == Person.id')
    recipient = db.relationship(u'Orgstructure', primaryjoin='Stockrequisition.recipient_id == Orgstructure.id')
    supplier = db.relationship(u'Orgstructure', primaryjoin='Stockrequisition.supplier_id == Orgstructure.id')


class StockrequisitionItem(db.Model):
    __tablename__ = u'StockRequisition_Item'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.ForeignKey('StockRequisition.id'), nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    nomenclature_id = db.Column(db.ForeignKey('rbNomenclature.id'), index=True)
    finance_id = db.Column(db.ForeignKey('rbFinance.id'), index=True)
    qnt = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    satisfiedQnt = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")

    finance = db.relationship(u'Rbfinance')
    master = db.relationship(u'Stockrequisition')
    nomenclature = db.relationship(u'Rbnomenclature')


class Stocktran(db.Model):
    __tablename__ = u'StockTrans'
    __table_args__ = (
        db.Index(u'cre', u'creOrgStructure_id', u'creNomenclature_id', u'creFinance_id'),
        db.Index(u'deb', u'debOrgStructure_id', u'debNomenclature_id', u'debFinance_id')
    )

    id = db.Column(db.BigInteger, primary_key=True)
    stockMotionItem_id = db.Column(db.ForeignKey('StockMotion_Item.id'), nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False, server_default=u"'0000-00-00 00:00:00'")
    qnt = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    sum = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    debOrgStructure_id = db.Column(db.ForeignKey('OrgStructure.id'), index=True)
    debNomenclature_id = db.Column(db.ForeignKey('rbNomenclature.id'), index=True)
    debFinance_id = db.Column(db.ForeignKey('rbFinance.id'), index=True)
    creOrgStructure_id = db.Column(db.ForeignKey('OrgStructure.id'), index=True)
    creNomenclature_id = db.Column(db.ForeignKey('rbNomenclature.id'), index=True)
    creFinance_id = db.Column(db.ForeignKey('rbFinance.id'), index=True)

    creFinance = db.relationship(u'Rbfinance', primaryjoin='Stocktran.creFinance_id == Rbfinance.id')
    creNomenclature = db.relationship(u'Rbnomenclature', primaryjoin='Stocktran.creNomenclature_id == Rbnomenclature.id')
    creOrgStructure = db.relationship(u'Orgstructure', primaryjoin='Stocktran.creOrgStructure_id == Orgstructure.id')
    debFinance = db.relationship(u'Rbfinance', primaryjoin='Stocktran.debFinance_id == Rbfinance.id')
    debNomenclature = db.relationship(u'Rbnomenclature', primaryjoin='Stocktran.debNomenclature_id == Rbnomenclature.id')
    debOrgStructure = db.relationship(u'Orgstructure', primaryjoin='Stocktran.debOrgStructure_id == Orgstructure.id')
    stockMotionItem = db.relationship(u'StockmotionItem')


class Takentissuejournal(db.Model):
    __tablename__ = u'TakenTissueJournal'
    __table_args__ = (
        db.Index(u'period_barcode', u'period', u'barcode'),
    )

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.ForeignKey('Client.id'), nullable=False, index=True)
    tissueType_id = db.Column(db.ForeignKey('rbTissueType.id'), nullable=False, index=True)
    externalId = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    unit_id = db.Column(db.ForeignKey('rbUnit.id'), index=True)
    datetimeTaken = db.Column(db.DateTime, nullable=False)
    execPerson_id = db.Column(db.ForeignKey('Person.id'), index=True)
    note = db.Column(db.String(128), nullable=False)
    barcode = db.Column(db.Integer, nullable=False)
    period = db.Column(db.Integer, nullable=False)

    client = db.relationship(u'Client')
    execPerson = db.relationship(u'Person')
    tissueType = db.relationship(u'Rbtissuetype')
    unit = db.relationship(u'Rbunit')

    @property
    def barcode_s(self):
        return code128C(self.barcode).decode('windows-1252')


class Tempinvalid(db.Model):
    __tablename__ = u'TempInvalid'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    type = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    doctype = db.Column(db.Integer, nullable=False)
    doctype_id = db.Column(db.Integer, index=True)
    serial = db.Column(db.String(8), nullable=False)
    number = db.Column(db.String(16), nullable=False)
    client_id = db.Column(db.Integer, nullable=False, index=True)
    tempInvalidReason_id = db.Column(db.Integer, index=True)
    begDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False, index=True)
    person_id = db.Column(db.Integer, index=True)
    diagnosis_id = db.Column(db.Integer, index=True)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    notes = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    closed = db.Column(db.Integer, nullable=False)
    prev_id = db.Column(db.Integer, index=True)
    insuranceOfficeMark = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    caseBegDate = db.Column(db.Date, nullable=False)
    event_id = db.Column(db.Integer)


class Tempinvalidduplicate(db.Model):
    __tablename__ = u'TempInvalidDuplicate'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False)
    tempInvalid_id = db.Column(db.Integer, nullable=False, index=True)
    person_id = db.Column(db.Integer, index=True)
    date = db.Column(db.Date, nullable=False)
    serial = db.Column(db.String(8), nullable=False)
    number = db.Column(db.String(16), nullable=False)
    destination = db.Column(db.String(128), nullable=False)
    reason_id = db.Column(db.Integer, index=True)
    note = db.Column(db.String, nullable=False)
    insuranceOfficeMark = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class TempinvalidPeriod(db.Model):
    __tablename__ = u'TempInvalid_Period'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    diagnosis_id = db.Column(db.Integer, index=True)
    begPerson_id = db.Column(db.Integer, index=True)
    begDate = db.Column(db.Date, nullable=False)
    endPerson_id = db.Column(db.Integer, index=True)
    endDate = db.Column(db.Date, nullable=False)
    isExternal = db.Column(db.Integer, nullable=False)
    regime_id = db.Column(db.Integer, index=True)
    break_id = db.Column(db.Integer, index=True)
    result_id = db.Column(db.Integer, index=True)
    note = db.Column(db.String(256), nullable=False)


class Tissue(db.Model):
    __tablename__ = u'Tissue'

    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.ForeignKey('rbTissueType.id'), nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False)
    barcode = db.Column(db.String(255), nullable=False, index=True)
    event_id = db.Column(db.ForeignKey('Event.id'), nullable=False, index=True)

    event = db.relationship(u'Event')
    type = db.relationship(u'Rbtissuetype')


class Uuid(db.Model):
    __tablename__ = u'UUID'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100), nullable=False, unique=True)


class Variablesforsql(db.Model):
    __tablename__ = u'VariablesforSQL'

    id = db.Column(db.Integer, primary_key=True)
    specialVarName_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    var_type = db.Column(db.String(64), nullable=False)
    label = db.Column(db.String(64), nullable=False)


class Version(db.Model):
    __tablename__ = u'Versions'

    id = db.Column(db.Integer, primary_key=True)
    table = db.Column(db.String(64), nullable=False, unique=True)
    version = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Visit(db.Model, Info):
    __tablename__ = u'Visit'

    id = db.Column(db.Integer, primary_key=True)
    createDatetime = db.Column(db.DateTime, nullable=False)
    createPerson_id = db.Column(db.Integer, index=True)
    modifyDatetime = db.Column(db.DateTime, nullable=False)
    modifyPerson_id = db.Column(db.Integer, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    event_id = db.Column(db.Integer, db.ForeignKey('Event.id'), nullable=False, index=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('rbScene.id'), nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False)
    visitType_id = db.Column(db.Integer, db.ForeignKey('rbVisitType.id'), nullable=False, index=True)
    person_id = db.Column(db.Integer, db.ForeignKey('Person.id'), nullable=False, index=True)
    isPrimary = db.Column(db.Integer, nullable=False)
    finance_id = db.Column(db.Integer, db.ForeignKey('rbFinance.id'), nullable=False, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('rbService.id'), index=True)
    payStatus = db.Column(db.Integer, nullable=False)

    service = db.relationship(u'Rbservice')
    person = db.relationship(u'Person')
    finance = db.relationship(u'Rbfinance')
    scene = db.relationship(u'Rbscene')
    type = db.relationship(u'Rbvisittype')


class ActionDocument(db.Model):
    __tablename__ = u'action_document'

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.ForeignKey('Action.id'), nullable=False, index=True)
    modify_date = db.Column(db.DateTime, nullable=False)
    template_id = db.Column(db.ForeignKey('rbPrintTemplate.id'), nullable=False, index=True)
    document = db.Column(MEDIUMBLOB, nullable=False)

    action = db.relationship(u'Action')
    template = db.relationship(u'Rbprinttemplate')


class BbtorganismSensvalue(db.Model):
    __tablename__ = u'bbtOrganism_SensValues'
    __table_args__ = (
        db.Index(u'bbtResult_Organism_id_index', u'bbtResult_Organism_id', u'idx'),
    )

    id = db.Column(db.Integer, primary_key=True)
    bbtResult_Organism_id = db.Column(db.ForeignKey('bbtResult_Organism.id'), nullable=False)
    idx = db.Column(db.Integer)
    antibiotic_id = db.Column(db.ForeignKey('rbAntibiotic.id'), index=True)
    MIC = db.Column(db.String(20), nullable=False)
    activity = db.Column(db.String(5), nullable=False)

    antibiotic = db.relationship(u'Rbantibiotic')
    bbtResult_Organism = db.relationship(u'BbtresultOrganism')


class BbtresultImage(db.Model):
    __tablename__ = u'bbtResult_Image'
    __table_args__ = (
        db.Index(u'action_id_index', u'action_id', u'idx'),
    )

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.ForeignKey('Action.id'), nullable=False)
    idx = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(256))
    image = db.Column(LONGBLOB, nullable=False)

    action = db.relationship(u'Action')


class BbtresultOrganism(db.Model):
    __tablename__ = u'bbtResult_Organism'

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.ForeignKey('Action.id'), nullable=False, index=True)
    organism_id = db.Column(db.ForeignKey('rbMicroorganism.id'), nullable=False, index=True)
    concentration = db.Column(db.String(256), nullable=False)

    action = db.relationship(u'Action')
    organism = db.relationship(u'Rbmicroorganism')


class BbtresultTable(db.Model):
    __tablename__ = u'bbtResult_Table'

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.ForeignKey('Action.id'), nullable=False, index=True)
    indicator_id = db.Column(db.ForeignKey('rbBacIndicator.id'), nullable=False, index=True)
    normString = db.Column(db.String(256))
    normalityIndex = db.Column(db.Float)
    unit = db.Column(db.String(20))
    signDateTime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Text)
    comment = db.Column(db.Text)

    action = db.relationship(u'Action')
    indicator = db.relationship(u'Rbbacindicator')


class BbtresultText(db.Model):
    __tablename__ = u'bbtResult_Text'

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.ForeignKey('Action.id'), nullable=False, index=True)
    valueText = db.Column(db.Text)

    action = db.relationship(u'Action')


class Mrbmodelagegroup(db.Model):
    __tablename__ = u'mrbModelAgeGroup'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)


class Mrbmodelaidcase(db.Model):
    __tablename__ = u'mrbModelAidCase'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)


class Mrbmodelaidpurpose(db.Model):
    __tablename__ = u'mrbModelAidPurpose'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)


class Mrbmodelcategory(db.Model):
    __tablename__ = u'mrbModelCategory'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)


class Mrbmodelcontinuation(db.Model):
    __tablename__ = u'mrbModelContinuation'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)


class Mrbmodeldiseaseclas(db.Model):
    __tablename__ = u'mrbModelDiseaseClass'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)


class Mrbmodelexpectedresult(db.Model):
    __tablename__ = u'mrbModelExpectedResult'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)


class Mrbmodelinstitutiontype(db.Model):
    __tablename__ = u'mrbModelInstitutionType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)


class Mrbmodelsertificationrequirement(db.Model):
    __tablename__ = u'mrbModelSertificationRequirement'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)


class Mrbmodelstatebadnes(db.Model):
    __tablename__ = u'mrbModelStateBadness'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)


class NewTable(db.Model):
    __tablename__ = u'new_table'

    idnew_table = db.Column(db.Integer, primary_key=True)


class Rb64district(db.Model):
    __tablename__ = u'rb64District'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code_tfoms = db.Column(db.Integer, nullable=False)
    socr = db.Column(db.String(10), nullable=False)
    code = db.Column(db.String(15), nullable=False)
    index = db.Column(db.Integer)
    gninmb = db.Column(db.Integer, nullable=False)
    uno = db.Column(db.Integer)
    ocatd = db.Column(db.String(15), nullable=False)
    status = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    parent = db.Column(db.Integer, nullable=False)
    infis = db.Column(db.String(15))
    prefix = db.Column(db.Integer, nullable=False)


class Rb64placetype(db.Model):
    __tablename__ = u'rb64PlaceType'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class Rb64reason(db.Model):
    __tablename__ = u'rb64Reason'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Rb64streettype(db.Model):
    __tablename__ = u'rb64StreetType'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class Rbaptable(db.Model):
    __tablename__ = u'rbAPTable'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(256), nullable=False)
    tableName = db.Column(db.String(256), nullable=False)
    masterField = db.Column(db.String(256), nullable=False)


class Rbaptablefield(db.Model):
    __tablename__ = u'rbAPTableField'

    id = db.Column(db.Integer, primary_key=True)
    idx = db.Column(db.Integer, nullable=False)
    master_id = db.Column(db.ForeignKey('rbAPTable.id'), nullable=False, index=True)
    name = db.Column(db.String(256), nullable=False)
    fieldName = db.Column(db.String(256), nullable=False)
    referenceTable = db.Column(db.String(256))

    master = db.relationship(u'Rbaptable', backref="fields")


class Rbacademicdegree(db.Model, RBInfo):
    __tablename__ = u'rbAcademicDegree'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False)
    name = db.Column(db.Unicode(64), nullable=False)


class Rbacademictitle(db.Model, RBInfo):
    __tablename__ = u'rbAcademicTitle'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)


class Rbaccountexportformat(db.Model, RBInfo):
    __tablename__ = u'rbAccountExportFormat'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    prog = db.Column(db.String(128), nullable=False)
    preferentArchiver = db.Column(db.String(128), nullable=False)
    emailRequired = db.Column(db.Integer, nullable=False)
    emailTo = db.Column(db.String(64), nullable=False)
    subject = db.Column(db.Unicode(128), nullable=False)
    message = db.Column(db.Text, nullable=False)


class Rbaccountingsystem(db.Model, RBInfo):
    __tablename__ = u'rbAccountingSystem'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    isEditable = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    showInClientInfo = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbacheresult(db.Model, RBInfo):
    __tablename__ = u'rbAcheResult'

    id = db.Column(db.Integer, primary_key=True)
    eventPurpose_id = db.Column(db.ForeignKey('rbEventTypePurpose.id'), nullable=False, index=True)
    code = db.Column(db.String(3, u'utf8_unicode_ci'), nullable=False)
    name = db.Column(db.String(64, u'utf8_unicode_ci'), nullable=False)

    eventPurpose = db.relationship(u'Rbeventtypepurpose')


class Rbactionshedule(db.Model):
    __tablename__ = u'rbActionShedule'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, server_default=u"''")
    name = db.Column(db.String(64), nullable=False, server_default=u"''")
    period = db.Column(db.Integer, nullable=False, server_default=u"'1'")


class RbactionsheduleItem(db.Model):
    __tablename__ = u'rbActionShedule_Item'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    offset = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    time = db.Column(db.Time, nullable=False, server_default=u"'00:00:00'")


class Rbactivity(db.Model):
    __tablename__ = u'rbActivity'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    regionalCode = db.Column(db.String(8), nullable=False, index=True)


class Rbagreementtype(db.Model):
    __tablename__ = u'rbAgreementType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    quotaStatusModifier = db.Column(db.Integer, server_default=u"'0'")


class Rbanalysisstatu(db.Model):
    __tablename__ = u'rbAnalysisStatus'

    id = db.Column(db.Integer, primary_key=True)
    statusName = db.Column(db.String(80), nullable=False, unique=True)


class Rbanalyticalreport(db.Model):
    __tablename__ = u'rbAnalyticalReports'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    PrintTemplate_id = db.Column(db.Integer)


class Rbantibiotic(db.Model):
    __tablename__ = u'rbAntibiotic'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(256), nullable=False)


class Rbattachtype(db.Model):
    __tablename__ = u'rbAttachType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    temporary = db.Column(db.Integer, nullable=False)
    outcome = db.Column(db.Integer, nullable=False)
    finance_id = db.Column(db.Integer, nullable=False, index=True)


class Rbbacindicator(db.Model):
    __tablename__ = u'rbBacIndicator'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(256), nullable=False)


class Rbblankaction(db.Model):
    __tablename__ = u'rbBlankActions'

    id = db.Column(db.Integer, primary_key=True)
    doctype_id = db.Column(db.ForeignKey('ActionType.id'), nullable=False, index=True)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    checkingSerial = db.Column(db.Integer, nullable=False)
    checkingNumber = db.Column(db.Integer, nullable=False)
    checkingAmount = db.Column(db.Integer, nullable=False)

    doctype = db.relationship(u'Actiontype')


class Rbblanktempinvalid(db.Model):
    __tablename__ = u'rbBlankTempInvalids'

    id = db.Column(db.Integer, primary_key=True)
    doctype_id = db.Column(db.ForeignKey('rbTempInvalidDocument.id'), nullable=False, index=True)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    checkingSerial = db.Column(db.Integer, nullable=False)
    checkingNumber = db.Column(db.Integer, nullable=False)
    checkingAmount = db.Column(db.Integer, nullable=False)

    doctype = db.relationship(u'Rbtempinvaliddocument')


class Rbbloodtype(db.Model, RBInfo):
    __tablename__ = u'rbBloodType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(64), nullable=False)


class Rbcashoperation(db.Model, RBInfo):
    __tablename__ = u'rbCashOperation'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False)


class Rbcomplain(db.Model):
    __tablename__ = u'rbComplain'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, index=True)
    code = db.Column(db.String(64), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False, index=True)


class Rbcontacttype(db.Model, RBInfo):
    __tablename__ = u'rbContactType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)


class Rbcoreactionproperty(db.Model):
    __tablename__ = u'rbCoreActionProperty'

    id = db.Column(db.Integer, primary_key=True)
    actionType_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    actionPropertyType_id = db.Column(db.Integer, nullable=False)


class Rbcounter(db.Model):
    __tablename__ = u'rbCounter'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    prefix = db.Column(db.String(32))
    separator = db.Column(db.String(8), server_default=u"' '")
    reset = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    startDate = db.Column(db.DateTime, nullable=False)
    resetDate = db.Column(db.DateTime)
    sequenceFlag = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbdiagnosistype(db.Model):
    __tablename__ = u'rbDiagnosisType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    replaceInDiagnosis = db.Column(db.String(8), nullable=False)
    flatCode = db.Column(db.String(64), nullable=False)


class Rbdiet(db.Model):
    __tablename__ = u'rbDiet'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)


class Rbdiseasecharacter(db.Model):
    __tablename__ = u'rbDiseaseCharacter'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    replaceInDiagnosis = db.Column(db.String(8), nullable=False)


class Rbdiseasephase(db.Model):
    __tablename__ = u'rbDiseasePhases'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    characterRelation = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbdiseasestage(db.Model):
    __tablename__ = u'rbDiseaseStage'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    characterRelation = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbdispanser(db.Model, RBInfo):
    __tablename__ = u'rbDispanser'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    observed = db.Column(db.Integer, nullable=False)


class Rbdocumenttype(db.Model, RBInfo):
    __tablename__ = u'rbDocumentType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    regionalCode = db.Column(db.String(16), nullable=False)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('rbDocumentTypeGroup.id'), nullable=False, index=True)
    serial_format = db.Column(db.Integer, nullable=False)
    number_format = db.Column(db.Integer, nullable=False)
    federalCode = db.Column(db.String(16), nullable=False)
    socCode = db.Column(db.String(8), nullable=False, index=True)
    TFOMSCode = db.Column(db.Integer)

    group = db.relationship(u'Rbdocumenttypegroup')


class Rbdocumenttypegroup(db.Model, RBInfo):
    __tablename__ = u'rbDocumentTypeGroup'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)


class Rbemergencyaccident(db.Model):
    __tablename__ = u'rbEmergencyAccident'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencycausecall(db.Model):
    __tablename__ = u'rbEmergencyCauseCall'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)
    typeCause = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbemergencydeath(db.Model):
    __tablename__ = u'rbEmergencyDeath'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencydiseased(db.Model):
    __tablename__ = u'rbEmergencyDiseased'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencyebriety(db.Model):
    __tablename__ = u'rbEmergencyEbriety'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencymethodtransportation(db.Model):
    __tablename__ = u'rbEmergencyMethodTransportation'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencyplacecall(db.Model):
    __tablename__ = u'rbEmergencyPlaceCall'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencyplacereceptioncall(db.Model):
    __tablename__ = u'rbEmergencyPlaceReceptionCall'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencyreasonddelay(db.Model):
    __tablename__ = u'rbEmergencyReasondDelays'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencyreceivedcall(db.Model):
    __tablename__ = u'rbEmergencyReceivedCall'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencyresult(db.Model):
    __tablename__ = u'rbEmergencyResult'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencytransferredtransportation(db.Model):
    __tablename__ = u'rbEmergencyTransferredTransportation'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbemergencytypeasset(db.Model, RBInfo):
    __tablename__ = u'rbEmergencyTypeAsset'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    codeRegional = db.Column(db.String(8), nullable=False, index=True)


class Rbeventprofile(db.Model):
    __tablename__ = u'rbEventProfile'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    regionalCode = db.Column(db.String(16), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)


class Rbeventtypepurpose(db.Model, RBInfo):
    __tablename__ = u'rbEventTypePurpose'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    codePlace = db.Column(db.String(2))


class Rbfinance(db.Model, RBInfo):
    __tablename__ = u'rbFinance'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)


class Rbfinance1c(db.Model):
    __tablename__ = u'rbFinance1C'

    id = db.Column(db.Integer, primary_key=True)
    code1C = db.Column(db.String(127), nullable=False)
    finance_id = db.Column(db.ForeignKey('rbFinance.id'), nullable=False, index=True)

    finance = db.relationship(u'Rbfinance')


class Rbhealthgroup(db.Model):
    __tablename__ = u'rbHealthGroup'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)


class Rbhospitalbedprofile(db.Model, RBInfo):
    __tablename__ = u'rbHospitalBedProfile'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    service_id = db.Column(db.Integer, index=True)


class RbhospitalbedprofileService(db.Model):
    __tablename__ = u'rbHospitalBedProfile_Service'

    id = db.Column(db.Integer, primary_key=True)
    rbHospitalBedProfile_id = db.Column(db.ForeignKey('rbHospitalBedProfile.id'), nullable=False, index=True)
    rbService_id = db.Column(db.ForeignKey('rbService.id'), nullable=False, index=True)

    rbHospitalBedProfile = db.relationship(u'Rbhospitalbedprofile')
    rbService = db.relationship(u'Rbservice')


class Rbhospitalbedshedule(db.Model, RBInfo):
    __tablename__ = u'rbHospitalBedShedule'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)


class Rbhospitalbedtype(db.Model, RBInfo):
    __tablename__ = u'rbHospitalBedType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)


class Rbhurtfactortype(db.Model):
    __tablename__ = u'rbHurtFactorType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    name = db.Column(db.String(250), nullable=False, index=True)


class Rbhurttype(db.Model, RBInfo):
    __tablename__ = u'rbHurtType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(256), nullable=False, index=True)


class Rbimagemap(db.Model):
    __tablename__ = u'rbImageMap'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    image = db.Column(MEDIUMBLOB, nullable=False)
    markSize = db.Column(db.Integer)


class Rbjobtype(db.Model, RBInfo):
    __tablename__ = u'rbJobType'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, index=True)
    code = db.Column(db.String(64), nullable=False)
    regionalCode = db.Column(db.String(64), nullable=False)
    name = db.Column(db.Unicode(128), nullable=False)
    laboratory_id = db.Column(db.Integer, index=True)
    isInstant = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rblaboratory(db.Model):
    __tablename__ = u'rbLaboratory'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    protocol = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(128), nullable=False)
    ownName = db.Column(db.String(128), nullable=False)
    labName = db.Column(db.String(128), nullable=False)


class RblaboratoryTest(db.Model):
    __tablename__ = u'rbLaboratory_Test'
    __table_args__ = (
        db.Index(u'code', u'book', u'code'),
    )

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    test_id = db.Column(db.Integer, nullable=False, index=True)
    book = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(64), nullable=False)


class Rbmkbsubclas(db.Model):
    __tablename__ = u'rbMKBSubclass'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False)
    name = db.Column(db.String(128), nullable=False)


class RbmkbsubclassItem(db.Model):
    __tablename__ = u'rbMKBSubclass_Item'
    __table_args__ = (
        db.Index(u'master_id', u'master_id', u'code'),
    )

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(8), nullable=False)
    name = db.Column(db.String(128), nullable=False)


class Rbmealtime(db.Model):
    __tablename__ = u'rbMealTime'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    begTime = db.Column(db.Time, nullable=False)
    endTime = db.Column(db.Time, nullable=False)


class Rbmedicalaidprofile(db.Model):
    __tablename__ = u'rbMedicalAidProfile'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    regionalCode = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(64), nullable=False)


class Rbmedicalaidtype(db.Model):
    __tablename__ = u'rbMedicalAidType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)


class Rbmedicalaidunit(db.Model):
    __tablename__ = u'rbMedicalAidUnit'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    descr = db.Column(db.String(64), nullable=False)
    regionalCode = db.Column(db.String(1), nullable=False)


class Rbmedicalkind(db.Model):
    __tablename__ = u'rbMedicalKind'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(1, u'utf8_unicode_ci'), nullable=False)
    name = db.Column(db.String(64, u'utf8_unicode_ci'), nullable=False)


class Rbmenu(db.Model):
    __tablename__ = u'rbMenu'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)


class RbmenuContent(db.Model):
    __tablename__ = u'rbMenu_Content'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    mealTime_id = db.Column(db.Integer, nullable=False, index=True)
    diet_id = db.Column(db.Integer, nullable=False, index=True)


class Rbmesspecification(db.Model, RBInfo):
    __tablename__ = u'rbMesSpecification'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    regionalCode = db.Column(db.String(16), nullable=False)
    name = db.Column(db.Unicode(64), nullable=False)
    done = db.Column(db.Integer, nullable=False)


class Rbmethodofadministration(db.Model):
    __tablename__ = u'rbMethodOfAdministration'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)


class Rbmicroorganism(db.Model):
    __tablename__ = u'rbMicroorganism'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(256), nullable=False)


class Rbnet(db.Model, RBInfo):
    __tablename__ = u'rbNet'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    sexCode = db.Column("sex", db.Integer, nullable=False, server_default=u"'0'")
    age = db.Column(db.Unicode(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)

    @property
    def sex(self):
        return formatSex(self.sexCode)


class Rbnomenclature(db.Model):
    __tablename__ = u'rbNomenclature'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.ForeignKey('rbNomenclature.id'), index=True)
    code = db.Column(db.String(64), nullable=False)
    regionalCode = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(128), nullable=False)

    group = db.relationship(u'Rbnomenclature', remote_side=[id])


class Rbokfs(db.Model, RBInfo):
    __tablename__ = u'rbOKFS'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    ownership = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbokpf(db.Model, RBInfo):
    __tablename__ = u'rbOKPF'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)


class Rbokved(db.Model):
    __tablename__ = u'rbOKVED'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False, index=True)
    div = db.Column(db.String(10), nullable=False)
    class_ = db.Column(u'class', db.String(2), nullable=False)
    group_ = db.Column(db.String(2), nullable=False)
    vid = db.Column(db.String(2), nullable=False)
    OKVED = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(250), nullable=False, index=True)


class Rboperationtype(db.Model):
    __tablename__ = u'rbOperationType'

    id = db.Column(db.Integer, primary_key=True)
    cd_r = db.Column(db.Integer, nullable=False)
    cd_subr = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(8), nullable=False, index=True)
    ktso = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(64), nullable=False, index=True)


class Rbpacientmodel(db.Model, RBInfo):
    __tablename__ = u'rbPacientModel'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), nullable=False)
    name = db.Column(db.Text, nullable=False)
    quotaType_id = db.Column(db.ForeignKey('QuotaType.id'), nullable=False, index=True)

    quotaType = db.relationship(u'Quotatype')


class Rbpayrefusetype(db.Model, RBInfo):
    __tablename__ = u'rbPayRefuseType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(128), nullable=False, index=True)
    finance_id = db.Column(db.Integer, nullable=False, index=True)
    rerun = db.Column(db.Integer, nullable=False)


class Rbpaytype(db.Model):
    __tablename__ = u'rbPayType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(2, u'utf8_unicode_ci'), nullable=False)
    name = db.Column(db.String(64, u'utf8_unicode_ci'), nullable=False)


class Rbpolicytype(db.Model, RBInfo):
    __tablename__ = u'rbPolicyType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), nullable=False, unique=True)
    name = db.Column(db.Unicode(256), nullable=False, index=True)
    TFOMSCode = db.Column(db.String(8))


class Rbpost(db.Model, RBInfo):
    __tablename__ = u'rbPost'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    regionalCode = db.Column(db.String(8), nullable=False)
    key = db.Column(db.String(6), nullable=False, index=True)
    high = db.Column(db.String(6), nullable=False)
    flatCode = db.Column(db.String(65), nullable=False)


class Rbprinttemplate(db.Model):
    __tablename__ = u'rbPrintTemplate'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    context = db.Column(db.String(64), nullable=False)
    fileName = db.Column(db.String(128), nullable=False)
    default = db.Column(db.String, nullable=False)
    dpdAgreement = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    render = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbquotastatu(db.Model):
    __tablename__ = u'rbQuotaStatus'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False, index=True)


class Rbreasonofabsence(db.Model, RBInfo):
    __tablename__ = u'rbReasonOfAbsence'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)


class Rbrelationtype(db.Model, RBInfo):
    __tablename__ = u'rbRelationType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    leftName = db.Column(db.String(64), nullable=False)
    rightName = db.Column(db.String(64), nullable=False)
    isDirectGenetic = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isBackwardGenetic = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isDirectRepresentative = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isBackwardRepresentative = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isDirectEpidemic = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isBackwardEpidemic = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isDirectDonation = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    isBackwardDonation = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    leftSex = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    rightSex = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    regionalCode = db.Column(db.String(64), nullable=False)
    regionalReverseCode = db.Column(db.String(64), nullable=False)


class Rbrequesttype(db.Model, RBInfo):
    __tablename__ = u'rbRequestType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    relevant = db.Column(db.Integer, nullable=False, server_default=u"'1'")


class Rbresult(db.Model, RBInfo):
    __tablename__ = u'rbResult'

    id = db.Column(db.Integer, primary_key=True)
    eventPurpose_id = db.Column(db.Integer, nullable=False, index=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    continued = db.Column(db.Integer, nullable=False)
    regionalCode = db.Column(db.String(8), nullable=False)


class Rbscene(db.Model, RBInfo):
    __tablename__ = u'rbScene'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    serviceModifier = db.Column(db.Unicode(128), nullable=False)


class Rbservice(db.Model, RBInfo):
    __tablename__ = u'rbService'
    __table_args__ = (
        db.Index(u'infis', u'infis', u'eisLegacy'),
        db.Index(u'group_id_idx', u'group_id', u'idx')
    )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(31), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    eisLegacy = db.Column(db.Boolean, nullable=False)
    nomenclatureLegacy = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    license = db.Column(db.Boolean, nullable=False)
    infis = db.Column(db.String(31), nullable=False)
    begDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    medicalAidProfile_id = db.Column(db.ForeignKey('rbMedicalAidProfile.id'), index=True)
    adultUetDoctor = db.Column(db.Float(asdecimal=True), server_default=u"'0'")
    adultUetAverageMedWorker = db.Column(db.Float(asdecimal=True), server_default=u"'0'")
    childUetDoctor = db.Column(db.Float(asdecimal=True), server_default=u"'0'")
    childUetAverageMedWorker = db.Column(db.Float(asdecimal=True), server_default=u"'0'")
    rbMedicalKind_id = db.Column(db.ForeignKey('rbMedicalKind.id'), index=True)
    UET = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")
    departCode = db.Column(db.String(3))
    group_id = db.Column(db.ForeignKey('rbService.id'))
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")

    group = db.relationship(u'Rbservice', remote_side=[id])
    medicalAidProfile = db.relationship(u'Rbmedicalaidprofile')
    rbMedicalKind = db.relationship(u'Rbmedicalkind')


class Rbserviceclas(db.Model):
    __tablename__ = u'rbServiceClass'
    __table_args__ = (
        db.Index(u'section', u'section', u'code'),
    )

    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(1), nullable=False)
    code = db.Column(db.String(3), nullable=False)
    name = db.Column(db.String(200), nullable=False)


class Rbservicefinance(db.Model):
    __tablename__ = u'rbServiceFinance'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(2, u'utf8_unicode_ci'), nullable=False)
    name = db.Column(db.String(64, u'utf8_unicode_ci'), nullable=False)


class Rbservicegroup(db.Model):
    __tablename__ = u'rbServiceGroup'
    __table_args__ = (
        db.Index(u'group_id', u'group_id', u'service_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, nullable=False)
    required = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbservicesection(db.Model):
    __tablename__ = u'rbServiceSection'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(1), nullable=False)
    name = db.Column(db.String(100), nullable=False)


class Rbservicetype(db.Model):
    __tablename__ = u'rbServiceType'
    __table_args__ = (
        db.Index(u'section', u'section', u'code'),
    )

    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(1), nullable=False)
    code = db.Column(db.String(3), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)


class Rbserviceuet(db.Model):
    __tablename__ = u'rbServiceUET'

    id = db.Column(db.Integer, primary_key=True)
    rbService_id = db.Column(db.ForeignKey('rbService.id'), nullable=False, index=True)
    age = db.Column(db.String(10, u'utf8_unicode_ci'), nullable=False)
    UET = db.Column(db.Float(asdecimal=True), nullable=False, server_default=u"'0'")

    rbService = db.relationship(u'Rbservice')


class RbserviceProfile(db.Model):
    __tablename__ = u'rbService_Profile'
    __table_args__ = (
        db.Index(u'id', u'id', u'idx'),
    )

    id = db.Column(db.Integer, primary_key=True)
    idx = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    master_id = db.Column(db.ForeignKey('rbService.id'), nullable=False, index=True)
    speciality_id = db.Column(db.ForeignKey('rbSpeciality.id'), index=True)
    sex = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    age = db.Column(db.String(9), nullable=False, server_default=u"''")
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    mkbRegExp = db.Column(db.String(64), nullable=False, server_default=u"''")
    medicalAidProfile_id = db.Column(db.ForeignKey('rbMedicalAidProfile.id'), index=True)

    master = db.relationship(u'Rbservice')
    medicalAidProfile = db.relationship(u'Rbmedicalaidprofile')
    speciality = db.relationship(u'Rbspeciality')


class Rbsocstatusclass(db.Model, Info):
    __tablename__ = u'rbSocStatusClass'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.ForeignKey('rbSocStatusClass.id'), index=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)

    group = db.relationship(u'Rbsocstatusclass', remote_side=[id])

    def __unicode__(self):
        return self.name

# class Rbsocstatusclasstypeassoc(db.Model):
#     __tablename__ = u'rbSocStatusClassTypeAssoc'
#     __table_args__ = (
#         db.Index(u'type_id', u'type_id', u'class_id'),
#     )
#
#     id = db.Column(db.Integer, primary_key=True)
#     class_id = db.Column(db.Integer, db.ForeignKey('rbSocStatusClass.id'), nullable=False, index=True)
#     type_id = db.Column(db.Integer, db.ForeignKey('rbSocStatusType.id'), nullable=False)
Rbsocstatusclasstypeassoc = db.Table('rbSocStatusClassTypeAssoc', db.metadata,
    db.Column('class_id', db.Integer, db.ForeignKey('rbSocStatusClass.id')),
    db.Column('type_id', db.Integer, db.ForeignKey('rbSocStatusType.id'))
    )


class Rbsocstatustype(db.Model, Info):
    __tablename__ = u'rbSocStatusType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(250), nullable=False, index=True)
    socCode = db.Column(db.String(8), nullable=False, index=True)
    TFOMSCode = db.Column(db.Integer)
    regionalCode = db.Column(db.String(8), nullable=False)

    classes = db.relationship(u'Rbsocstatusclass', secondary=Rbsocstatusclasstypeassoc)


class Rbspecialvariablespreference(db.Model):
    __tablename__ = u'rbSpecialVariablesPreferences'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    query = db.Column(db.Text, nullable=False)


class Rbspeciality(db.Model, RBInfo):
    __tablename__ = u'rbSpeciality'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    OKSOName = db.Column(db.Unicode(60), nullable=False)
    OKSOCode = db.Column(db.String(8), nullable=False)
    service_id = db.Column(db.Integer, index=True)
    sex = db.Column(db.Integer, nullable=False)
    age = db.Column(db.String(9), nullable=False)
    age_bu = db.Column(db.Integer)
    age_bc = db.Column(db.SmallInteger)
    age_eu = db.Column(db.Integer)
    age_ec = db.Column(db.SmallInteger)
    mkbFilter = db.Column(db.String(32), nullable=False)
    regionalCode = db.Column(db.String(16), nullable=False)
    quotingEnabled = db.Column(db.Integer, server_default=u"'0'")


class Rbstorage(db.Model):
    __tablename__ = u'rbStorage'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(256))
    orgStructure_id = db.Column(db.ForeignKey('OrgStructure.id'), index=True)

    orgStructure = db.relationship(u'Orgstructure')


class Rbtariffcategory(db.Model, RBInfo):
    __tablename__ = u'rbTariffCategory'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)


class Rbtarifftype(db.Model):
    __tablename__ = u'rbTariffType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(2, u'utf8_unicode_ci'), nullable=False)
    name = db.Column(db.String(64, u'utf8_unicode_ci'), nullable=False)


class Rbtempinvalidbreak(db.Model):
    __tablename__ = u'rbTempInvalidBreak'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False, index=True)


class Rbtempinvaliddocument(db.Model):
    __tablename__ = u'rbTempInvalidDocument'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False, index=True)
    checkingSerial = db.Column(db.Enum(u'???', u'?????', u'??????'), nullable=False)
    checkingNumber = db.Column(db.Enum(u'???', u'?????', u'??????'), nullable=False)
    checkingAmount = db.Column(db.Enum(u'???', u'????????'), nullable=False)


class Rbtempinvalidduplicatereason(db.Model):
    __tablename__ = u'rbTempInvalidDuplicateReason'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)


class Rbtempinvalidreason(db.Model):
    __tablename__ = u'rbTempInvalidReason'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    requiredDiagnosis = db.Column(db.Integer, nullable=False)
    grouping = db.Column(db.Integer, nullable=False)
    primary = db.Column(db.Integer, nullable=False)
    prolongate = db.Column(db.Integer, nullable=False)
    restriction = db.Column(db.Integer, nullable=False)
    regionalCode = db.Column(db.String(3), nullable=False)


class Rbtempinvalidregime(db.Model):
    __tablename__ = u'rbTempInvalidRegime'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    doctype_id = db.Column(db.Integer, index=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)


class Rbtempinvalidresult(db.Model):
    __tablename__ = u'rbTempInvalidResult'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False, index=True)
    able = db.Column(db.Integer, nullable=False)
    closed = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    status = db.Column(db.Integer, nullable=False)


class Rbtest(db.Model):
    __tablename__ = u'rbTest'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False, index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbtesttubetype(db.Model):
    __tablename__ = u'rbTestTubeType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64))
    name = db.Column(db.String(128), nullable=False)
    volume = db.Column(db.Float(asdecimal=True), nullable=False)
    unit_id = db.Column(db.ForeignKey('rbUnit.id'), nullable=False, index=True)
    covCol = db.Column(db.String(64))
    image = db.Column(MEDIUMBLOB)
    color = db.Column(db.String(8))

    unit = db.relationship(u'Rbunit')


class Rbthesauru(db.Model):
    __tablename__ = u'rbThesaurus'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, index=True)
    code = db.Column(db.String(30), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, server_default=u"''")
    template = db.Column(db.String(255), nullable=False, server_default=u"''")


class Rbtimequotingtype(db.Model):
    __tablename__ = u'rbTimeQuotingType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.Text(collation=u'utf8_unicode_ci'), nullable=False)


class Rbtissuetype(db.Model, RBInfo):
    __tablename__ = u'rbTissueType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    group_id = db.Column(db.ForeignKey('rbTissueType.id'), index=True)
    sexCode = db.Column("sex", db.Integer, nullable=False, server_default=u"'0'")

    group = db.relationship(u'Rbtissuetype', remote_side=[id])

    @property
    def sex(self):
        return {0: u'Любой',
                1: u'М',
                2: u'Ж'}[self.sexCode]


class Rbtransferdatetype(db.Model):
    __tablename__ = u'rbTransferDateType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.Text(collation=u'utf8_unicode_ci'), nullable=False)


class Rbtraumatype(db.Model):
    __tablename__ = u'rbTraumaType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)


class Rbtreatment(db.Model, RBInfo):
    __tablename__ = u'rbTreatment'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), nullable=False)
    name = db.Column(db.Text, nullable=False)
    pacientModel_id = db.Column(db.ForeignKey('rbPacientModel.id'), nullable=False, index=True)

    pacientModel = db.relationship(u'Rbpacientmodel')


class Rbtrfubloodcomponenttype(db.Model, RBInfo):
    __tablename__ = u'rbTrfuBloodComponentType'

    id = db.Column(db.Integer, primary_key=True)
    trfu_id = db.Column(db.Integer)
    code = db.Column(db.String(32))
    name = db.Column(db.String(256))
    unused = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbtrfulaboratorymeasuretype(db.Model):
    __tablename__ = u'rbTrfuLaboratoryMeasureTypes'

    id = db.Column(db.Integer, primary_key=True)
    trfu_id = db.Column(db.Integer)
    name = db.Column(db.String(255))


class Rbtrfuproceduretype(db.Model):
    __tablename__ = u'rbTrfuProcedureTypes'

    id = db.Column(db.Integer, primary_key=True)
    trfu_id = db.Column(db.Integer)
    name = db.Column(db.String(255))
    unused = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class Rbufms(db.Model):
    __tablename__ = u'rbUFMS'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50, u'utf8_bin'), nullable=False)
    name = db.Column(db.String(256, u'utf8_bin'), nullable=False)


class Rbunit(db.Model, RBInfo):
    __tablename__ = u'rbUnit'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode(256), index=True)
    name = db.Column(db.Unicode(256), index=True)


class Rbuserprofile(db.Model):
    __tablename__ = u'rbUserProfile'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False, index=True)
    withDep = db.Column(db.Integer, nullable=False, server_default=u"'0'")


class RbuserprofileRight(db.Model):
    __tablename__ = u'rbUserProfile_Right'

    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, nullable=False, index=True)
    userRight_id = db.Column(db.Integer, nullable=False, index=True)


class Rbuserright(db.Model):
    __tablename__ = u'rbUserRight'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False, index=True)


class Rbvisittype(db.Model, RBInfo):
    __tablename__ = u'rbVisitType'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode(8), nullable=False, index=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    serviceModifier = db.Column(db.Unicode(128), nullable=False)


class RbF001Tfom(db.Model):
    __tablename__ = u'rb_F001_Tfoms'

    tf_kod = db.Column(db.String(255), primary_key=True)
    address = db.Column(db.String(255))
    d_edit = db.Column(db.Date)
    d_end = db.Column(db.Date)
    e_mail = db.Column(db.String(255))
    fam_dir = db.Column(db.String(255))
    fax = db.Column(db.String(255))
    idx = db.Column(db.String(255))
    im_dir = db.Column(db.String(255))
    kf_tf = db.Column(db.BigInteger)
    name_tfk = db.Column(db.String(255))
    name_tfp = db.Column(db.String(255))
    ot_dir = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    tf_ogrn = db.Column(db.String(255))
    tf_okato = db.Column(db.String(255))
    www = db.Column(db.String(255))


class RbF002Smo(db.Model):
    __tablename__ = u'rb_F002_SMO'

    smocod = db.Column(db.String(255), primary_key=True)
    addr_f = db.Column(db.String(255))
    addr_j = db.Column(db.String(255))
    d_begin = db.Column(db.Date)
    d_edit = db.Column(db.Date)
    d_end = db.Column(db.Date)
    d_start = db.Column(db.Date)
    data_e = db.Column(db.Date)
    duved = db.Column(db.Date)
    e_mail = db.Column(db.String(255))
    fam_ruk = db.Column(db.String(255))
    fax = db.Column(db.String(255))
    im_ruk = db.Column(db.String(255))
    index_f = db.Column(db.String(255))
    index_j = db.Column(db.String(255))
    inn = db.Column(db.String(255))
    kol_zl = db.Column(db.BigInteger)
    kpp = db.Column(db.String(255))
    n_doc = db.Column(db.String(255))
    nal_p = db.Column(db.String(255))
    nam_smok = db.Column(db.String(255))
    nam_smop = db.Column(db.String(255))
    name_e = db.Column(db.String(255))
    ogrn = db.Column(db.String(255))
    okopf = db.Column(db.String(255))
    org = db.Column(db.BigInteger)
    ot_ruk = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    tf_okato = db.Column(db.String(255))
    www = db.Column(db.String(255))


class RbF003Mo(db.Model):
    __tablename__ = u'rb_F003_MO'

    mcod = db.Column(db.String(255), primary_key=True)
    addr_j = db.Column(db.String(255))
    d_begin = db.Column(db.Date)
    d_edit = db.Column(db.Date)
    d_end = db.Column(db.Date)
    d_start = db.Column(db.Date)
    data_e = db.Column(db.Date)
    duved = db.Column(db.Date)
    e_mail = db.Column(db.String(255))
    fam_ruk = db.Column(db.String(255))
    fax = db.Column(db.String(255))
    im_ruk = db.Column(db.String(255))
    index_j = db.Column(db.String(255))
    inn = db.Column(db.String(255))
    kpp = db.Column(db.String(255))
    lpu = db.Column(db.Integer)
    mp = db.Column(db.String(255))
    n_doc = db.Column(db.String(255))
    nam_mok = db.Column(db.String(255))
    nam_mop = db.Column(db.String(255))
    name_e = db.Column(db.String(255))
    ogrn = db.Column(db.String(255))
    okopf = db.Column(db.String(255))
    org = db.Column(db.BigInteger)
    ot_ruk = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    tf_okato = db.Column(db.String(255))
    vedpri = db.Column(db.BigInteger)
    www = db.Column(db.String(255))


class RbF007Vedom(db.Model):
    __tablename__ = u'rb_F007_Vedom'

    idved = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    vedname = db.Column(db.String(255))


class RbF008Tipom(db.Model):
    __tablename__ = u'rb_F008_TipOMS'

    iddoc = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    docname = db.Column(db.String(255))


class RbF009Statzl(db.Model):
    __tablename__ = u'rb_F009_StatZL'

    idstatus = db.Column(db.String(255), primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    statusname = db.Column(db.String(255))


class RbF010Subekti(db.Model):
    __tablename__ = u'rb_F010_Subekti'

    kod_tf = db.Column(db.String(255), primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    kod_okato = db.Column(db.String(255))
    okrug = db.Column(db.BigInteger)
    subname = db.Column(db.String(255))


class RbF011Tipdoc(db.Model):
    __tablename__ = u'rb_F011_Tipdoc'

    iddoc = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    docname = db.Column(db.String(255))
    docnum = db.Column(db.String(255))
    docser = db.Column(db.String(255))


class RbF015Fedokr(db.Model):
    __tablename__ = u'rb_F015_FedOkr'

    kod_ok = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    okrname = db.Column(db.String(255))


class RbKladr(db.Model):
    __tablename__ = u'rb_Kladr'

    code = db.Column(db.String(255), primary_key=True)
    gninmb = db.Column(db.String(255))
    idx = db.Column(db.String(255))
    name = db.Column(db.String(255))
    ocatd = db.Column(db.String(255))
    socr = db.Column(db.String(255))
    status = db.Column(db.String(255))
    uno = db.Column(db.String(255))


class RbKladrstreet(db.Model):
    __tablename__ = u'rb_KladrStreet'

    code = db.Column(db.String(255), primary_key=True)
    gninmb = db.Column(db.String(255))
    idx = db.Column(db.String(255))
    name = db.Column(db.String(255))
    ocatd = db.Column(db.String(255))
    socr = db.Column(db.String(255))
    uno = db.Column(db.String(255))


class RbM001Mkb10(db.Model):
    __tablename__ = u'rb_M001_MKB10'

    idds = db.Column(db.String(255), primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    dsname = db.Column(db.String(255))


class RbO001Oksm(db.Model):
    __tablename__ = u'rb_O001_Oksm'

    kod = db.Column(db.String(255), primary_key=True)
    alfa2 = db.Column(db.String(255))
    alfa3 = db.Column(db.String(255))
    data_upd = db.Column(db.Date)
    name11 = db.Column(db.String(255))
    name12 = db.Column(db.String(255))
    nomakt = db.Column(db.String(255))
    nomdescr = db.Column(db.String(255))
    status = db.Column(db.BigInteger)


class RbO002Okato(db.Model):
    __tablename__ = u'rb_O002_Okato'

    ter = db.Column(db.String(255), primary_key=True)
    centrum = db.Column(db.String(255))
    data_upd = db.Column(db.Date)
    kod1 = db.Column(db.String(255))
    kod2 = db.Column(db.String(255))
    kod3 = db.Column(db.String(255))
    name1 = db.Column(db.String(255))
    nomakt = db.Column(db.String(255))
    nomdescr = db.Column(db.String(255))
    razdel = db.Column(db.String(255))
    status = db.Column(db.BigInteger)


class RbO003Okved(db.Model):
    __tablename__ = u'rb_O003_Okved'

    kod = db.Column(db.String(255), primary_key=True)
    data_upd = db.Column(db.Date)
    name11 = db.Column(db.String(255))
    name12 = db.Column(db.String(255))
    nomakt = db.Column(db.String(255))
    nomdescr = db.Column(db.String(255))
    prazdel = db.Column(db.String(255))
    razdel = db.Column(db.String(255))
    status = db.Column(db.BigInteger)


class RbO004Okf(db.Model):
    __tablename__ = u'rb_O004_Okfs'

    kod = db.Column(db.String(255), primary_key=True)
    alg = db.Column(db.String(255))
    data_upd = db.Column(db.Date)
    name1 = db.Column(db.String(255))
    nomakt = db.Column(db.String(255))
    status = db.Column(db.BigInteger)


class RbO005Okopf(db.Model):
    __tablename__ = u'rb_O005_Okopf'

    kod = db.Column(db.String(255), primary_key=True)
    alg = db.Column(db.String(255))
    data_upd = db.Column(db.Date)
    name1 = db.Column(db.String(255))
    nomakt = db.Column(db.String(255))
    status = db.Column(db.BigInteger)


class RbV001Nomerclr(db.Model):
    __tablename__ = u'rb_V001_Nomerclr'

    idrb = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    rbname = db.Column(db.String(255))


class RbV002Profot(db.Model):
    __tablename__ = u'rb_V002_ProfOt'

    idpr = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    prname = db.Column(db.String(255))


class RbV003Licusl(db.Model):
    __tablename__ = u'rb_V003_LicUsl'

    idrl = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    ierarh = db.Column(db.BigInteger)
    licname = db.Column(db.String(255))
    prim = db.Column(db.BigInteger)


class RbV004Medspec(db.Model):
    __tablename__ = u'rb_V004_Medspec'

    idmsp = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    mspname = db.Column(db.String(255))


class RbV005Pol(db.Model):
    __tablename__ = u'rb_V005_Pol'

    idpol = db.Column(db.BigInteger, primary_key=True)
    polname = db.Column(db.String(255))


class RbV006Uslmp(db.Model):
    __tablename__ = u'rb_V006_UslMp'

    idump = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    umpname = db.Column(db.String(255))


class RbV007Nommo(db.Model):
    __tablename__ = u'rb_V007_NomMO'

    idnmo = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    nmoname = db.Column(db.String(255))


class RbV008Vidmp(db.Model):
    __tablename__ = u'rb_V008_VidMp'

    idvmp = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    vmpname = db.Column(db.String(255))


class RbV009Rezult(db.Model):
    __tablename__ = u'rb_V009_Rezult'

    idrmp = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    iduslov = db.Column(db.BigInteger)
    rmpname = db.Column(db.String(255))


class RbV010Sposob(db.Model):
    __tablename__ = u'rb_V010_Sposob'

    idsp = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    spname = db.Column(db.String(255))


class RbV012Ishod(db.Model):
    __tablename__ = u'rb_V012_Ishod'

    idiz = db.Column(db.BigInteger, primary_key=True)
    datebeg = db.Column(db.Date)
    dateend = db.Column(db.Date)
    iduslov = db.Column(db.BigInteger)
    izname = db.Column(db.String(255))


class Rdfirstname(db.Model):
    __tablename__ = u'rdFirstName'
    __table_args__ = (
        db.Index(u'sex', u'sex', u'name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, index=True)
    sex = db.Column(db.Integer, nullable=False)


class Rdpolis(db.Model):
    __tablename__ = u'rdPOLIS_S'

    id = db.Column(db.Integer, primary_key=True)
    CODE = db.Column(db.String(10), nullable=False, index=True)
    PAYER = db.Column(db.String(5), nullable=False)
    TYPEINS = db.Column(db.String(1), nullable=False)


class Rdpatrname(db.Model):
    __tablename__ = u'rdPatrName'
    __table_args__ = (
        db.Index(u'sex', u'sex', u'name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, index=True)
    sex = db.Column(db.Integer, nullable=False)


class Rlsactmatter(db.Model):
    __tablename__ = u'rlsActMatters'
    __table_args__ = (
        db.Index(u'name_localName', u'name', u'localName'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    localName = db.Column(db.String(255))


class Rlsbalanceofgood(db.Model):
    __tablename__ = u'rlsBalanceOfGoods'

    id = db.Column(db.Integer, primary_key=True)
    rlsNomen_id = db.Column(db.ForeignKey('rlsNomen.id'), nullable=False, index=True)
    value = db.Column(db.Float(asdecimal=True), nullable=False)
    bestBefore = db.Column(db.Date, nullable=False)
    disabled = db.Column(db.Integer, nullable=False, server_default=u"'0'")
    updateDateTime = db.Column(db.DateTime)
    storage_id = db.Column(db.ForeignKey('rbStorage.id'), index=True)

    rlsNomen = db.relationship(u'Rlsnoman')
    storage = db.relationship(u'Rbstorage')


class Rlsfilling(db.Model):
    __tablename__ = u'rlsFilling'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)


class Rlsform(db.Model):
    __tablename__ = u'rlsForm'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)


class Rlsnoman(db.Model):
    __tablename__ = u'rlsNomen'

    id = db.Column(db.Integer, primary_key=True)
    actMatters_id = db.Column(db.ForeignKey('rlsActMatters.id'), index=True)
    tradeName_id = db.Column(db.ForeignKey('rlsTradeName.id'), nullable=False, index=True)
    form_id = db.Column(db.ForeignKey('rlsForm.id'), index=True)
    packing_id = db.Column(db.ForeignKey('rlsPacking.id'), index=True)
    filling_id = db.Column(db.ForeignKey('rlsFilling.id'), index=True)
    unit_id = db.Column(db.ForeignKey('rbUnit.id'), index=True)
    dosageValue = db.Column(db.String(128))
    dosageUnit_id = db.Column(db.ForeignKey('rbUnit.id'), index=True)
    drugLifetime = db.Column(db.Integer)
    regDate = db.Column(db.Date)
    annDate = db.Column(db.Date)

    actMatters = db.relationship(u'Rlsactmatter')
    dosageUnit = db.relationship(u'Rbunit', primaryjoin='Rlsnoman.dosageUnit_id == Rbunit.id')
    filling = db.relationship(u'Rlsfilling')
    form = db.relationship(u'Rlsform')
    packing = db.relationship(u'Rlspacking')
    tradeName = db.relationship(u'Rlstradename')
    unit = db.relationship(u'Rbunit', primaryjoin='Rlsnoman.unit_id == Rbunit.id')


class Rlspacking(db.Model):
    __tablename__ = u'rlsPacking'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)


class Rlspharmgroup(db.Model):
    __tablename__ = u'rlsPharmGroup'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer)
    code = db.Column(db.String(8))
    name = db.Column(db.String(128))
    path = db.Column(db.String(128))
    pathx = db.Column(db.String(128))
    nameRaw = db.Column(db.String(128), index=True)


class Rlspharmgrouptocode(db.Model):
    __tablename__ = u'rlsPharmGroupToCode'

    rlsPharmGroup_id = db.Column(db.Integer, primary_key=True, nullable=False, server_default=u"'0'")
    code = db.Column(db.Integer, primary_key=True, nullable=False, index=True, server_default=u"'0'")


class Rlstradename(db.Model):
    __tablename__ = u'rlsTradeName'
    __table_args__ = (
        db.Index(u'name_localName', u'name', u'localName'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    localName = db.Column(db.String(255))


class Trfufinalvolume(db.Model):
    __tablename__ = u'trfuFinalVolume'

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.ForeignKey('Action.id'), nullable=False, index=True)
    time = db.Column(db.Float(asdecimal=True))
    anticoagulantVolume = db.Column(db.Float(asdecimal=True))
    inletVolume = db.Column(db.Float(asdecimal=True))
    plasmaVolume = db.Column(db.Float(asdecimal=True))
    collectVolume = db.Column(db.Float(asdecimal=True))
    anticoagulantInCollect = db.Column(db.Float(asdecimal=True))
    anticoagulantInPlasma = db.Column(db.Float(asdecimal=True))

    action = db.relationship(u'Action')

    def __getitem__(self, name):
        columns = {'time': self.time,
                   'anticoagulantVolume': self.anticoagulantVolume,
                   'inletVolume': self.inletVolume,
                   'plasmaVolume': self.plasmaVolume,
                   'collectVolume': self.collectVolume,
                   'anticoagulantInCollect': self.anticoagulantInCollect,
                   'anticoagulantInPlasma': self.anticoagulantInPlasma}
        return columns[name]


class Trfulaboratorymeasure(db.Model):
    __tablename__ = u'trfuLaboratoryMeasure'

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.ForeignKey('Action.id'), nullable=False, index=True)
    trfu_lab_measure_id = db.Column(db.ForeignKey('rbTrfuLaboratoryMeasureTypes.id'), index=True)
    time = db.Column(db.Float(asdecimal=True))
    beforeOperation = db.Column(db.String(255))
    duringOperation = db.Column(db.String(255))
    inProduct = db.Column(db.String(255))
    afterOperation = db.Column(db.String(255))

    action = db.relationship(u'Action')
    trfu_lab_measure = db.relationship(u'Rbtrfulaboratorymeasuretype')

    def __getitem__(self, name):
        columns = {'trfu_lab_measure_id': self.trfu_lab_measure,
                   'time': self.time,
                   'beforeOperation': self.beforeOperation,
                   'duringOperation': self.duringOperation,
                   'inProduct': self.inProduct,
                   'afterOperation': self.afterOperation}
        return columns[name]


class Trfuorderissueresult(db.Model):
    __tablename__ = u'trfuOrderIssueResult'

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.ForeignKey('Action.id'), nullable=False, index=True)
    trfu_blood_comp = db.Column(db.Integer)
    comp_number = db.Column(db.String(40))
    comp_type_id = db.Column(db.ForeignKey('rbTrfuBloodComponentType.id'), index=True)
    blood_type_id = db.Column(db.ForeignKey('rbBloodType.id'), index=True)
    volume = db.Column(db.Integer)
    dose_count = db.Column(db.Float(asdecimal=True))
    trfu_donor_id = db.Column(db.Integer)

    action = db.relationship(u'Action')
    blood_type = db.relationship(u'Rbbloodtype')
    comp_type = db.relationship(u'Rbtrfubloodcomponenttype')

    def __getitem__(self, name):
        columns = {'trfu_blood_comp': self.trfu_blood_comp,
                   'comp_number': self.comp_number,
                   'comp_type_id': self.comp_type,
                   'blood_type_id': self.blood_type,
                   'volume': self.volume,
                   'dose_count': self.dose_count,
                   'trfu_donor_id': self.trfu_donor_id}
        return columns[name]


class v_Client_Quoting(db.Model):
    __tablename__ = u'vClient_Quoting'

    quotaId = db.Column(u'id', db.Integer, primary_key=True)
    createDatetime = db.Column(u'createDatetime', db.DateTime)
    createPerson_id = db.Column(u'createPerson_id', db.Integer)
    modifyDatetime = db.Column(u'modifyDatetime', db.DateTime)
    modifyPerson_id = db.Column(u'modifyPerson_id', db.Integer)
    deleted = db.Column(u'deleted', db.Integer, server_default=u"'0'")
    clientId = db.Column(u'master_id', db.Integer, db.ForeignKey("Client.id"))
    identifier = db.Column(u'identifier', db.String(16))
    quotaTicket = db.Column(u'quotaTicket', db.String(20))
    quotaType_id = db.Column(u'quotaType_id', db.Integer, db.ForeignKey("QuotaType.id"))
    stage = db.Column(u'stage', db.Integer)
    directionDate = db.Column(u'directionDate', db.DateTime)
    freeInput = db.Column(u'freeInput', db.String(128))
    org_id = db.Column(u'org_id', db.Integer, db.ForeignKey("Organisation.id"))
    amount = db.Column(u'amount', db.Integer, server_default=u"'0'")
    MKB = db.Column(u'MKB', db.String(8))
    status = db.Column(u'status', db.Integer, server_default=u"'0'")
    request = db.Column(u'request', db.Integer, server_default=u"'0'")
    statment = db.Column(u'statment', db.String(255))
    dateRegistration = db.Column(u'dateRegistration', db.DateTime)
    dateEnd = db.Column(u'dateEnd', db.DateTime)
    orgStructure_id = db.Column(u'orgStructure_id', db.Integer, db.ForeignKey("OrgStructure.id"))
    regionCode = db.Column(u'regionCode', db.String(13))
    pacientModel_id = db.Column(u'pacientModel_id', db.Integer, db.ForeignKey("rbPacientModel.id"))
    treatment_id = db.Column(u'treatment_id', db.Integer, db.ForeignKey("rbTreatment.id"))
    event_id = db.Column(u'event_id', db.Integer, db.ForeignKey("Event.id"))
    prevTalon_event_id = db.Column(u'prevTalon_event_id', db.Integer)

    quotaType = db.relationship(u"Quotatype")
    organisation = db.relationship(u"Organisation")
    orgstructure = db.relationship(u"Orgstructure")
    pacientModel = db.relationship(u"Rbpacientmodel")
    treatment = db.relationship(u"Rbtreatment")


class v_Nomen(db.Model):
    __tablename__ = u'vNomen'

    id = db.Column(u'id', db.Integer, primary_key=True)
    tradeName = db.Column(u'tradeName', db.String(255))
    tradeLocalName = db.Column(u'tradeLocalName', db.String(255))
    tradeName_id = db.Column(u'tradeName_id', db.Integer)
    actMattersName = db.Column(u'actMattersName', db.String(255))
    actMattersLocalName = db.Column(u'actMattersLocalName', db.String(255))
    actMatters_id = db.Column(u'actMatters_id', db.Integer)
    form = db.Column(u'form', db.String(128))
    packing = db.Column(u'packing', db.String(128))
    filling = db.Column(u'filling', db.String(128))
    unit_id = db.Column(u'unit_id', db.Integer)
    unitCode = db.Column(u'unitCode', db.String(256))
    unitName = db.Column(u'unitName', db.String(256))
    dosageValue = db.Column(u'dosageValue', db.String(128))
    dosageUnit_id = db.Column(u'dosageUnit_id', db.Integer)
    dosageUnitCode = db.Column(u'dosageUnitCode', db.String(256))
    dosageUnitName = db.Column(u'dosageUnitName', db.String(256))
    regDate = db.Column(u'regDate', db.Date)
    annDate = db.Column(u'annDate', db.Date)
    drugLifetime = db.Column(u'drugLifetime', db.Integer)

    def __unicode__(self):
        return ', '.join([field for field in [self.tradeName, self.form, self.dosageValue, self.filling]])