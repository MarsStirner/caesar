# -*- coding: utf-8 -*-

import datetime

from nemesis.lib.types import CalculatedProperty, CalculatedPropertyRO
from .models_utils import Query
from sqlalchemy import Column, Unicode, ForeignKey, Date, Float, DateTime, SmallInteger, Numeric, String
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy import orm

from ..database import Base
from nemesis.models.enums import ServiceKind


class Contract(Base):
    __tablename__ = u'Contract'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")
    number = Column(String(64), nullable=False)
    date = Column(Date, nullable=False)
    recipient_id = Column(Integer, ForeignKey('Contract_Contragent.id'), nullable=False)
    payer_id = Column(Integer, ForeignKey('Contract_Contragent.id'), nullable=False)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date)
    finance_id = Column(Integer, ForeignKey('rbFinance.id'), nullable=False)
    contractType_id = Column(Integer, ForeignKey('rbContractType.id'), nullable=False)
    resolution = Column(String(512), nullable=False)
    draft = Column(Integer, nullable=False, server_default=u"'0'")

    recipient = relationship('Contract_Contragent', foreign_keys=[recipient_id])
    payer = relationship('Contract_Contragent', foreign_keys=[payer_id])
    finance = relationship('rbFinance')
    contract_type = relationship('rbContractType')
    contingent_list = relationship(
        'Contract_Contingent',
        primaryjoin='and_(Contract_Contingent.contract_id == Contract.id, Contract_Contingent.deleted == 0)',
        backref='contract'
    )
    pricelist_list = relationship(
        'PriceList',
        secondary='Contract_PriceList',
        secondaryjoin='and_(Contract_PriceListAssoc.priceList_id == PriceList.id, PriceList.deleted == 0)',
    )

    def __unicode__(self):
        return u'%s %s' % (self.number, self.date)

    def __json__(self):
        return {
            'id': self.id,
            'number': self.number,
            'date': self.date,
            'begDate': self.begDate,
            'endDate': self.endDate,
        }

    def __int__(self):
        return self.id


class Contract_Contragent(Base):
    __tablename__ = u'Contract_Contragent'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('Client.id'))
    organisation_id = Column(Integer, ForeignKey('Organisation.id'))
    deleted = Column(Integer, nullable=False, server_default=u"'0'")

    client = relationship('Client')
    org = relationship('Organisation')
    payer_contract_list = relationship(
        'Contract',
        primaryjoin='and_(Contract_Contragent.id == Contract.payer_id, Contract.deleted == 0)'
    )
    payer_finance_trx_list = relationship('FinanceTransaction')


class Contract_Contingent(Base):
    __tablename__ = u'Contract_Contingent'

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('Contract.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('Client.id'), nullable=False)
    deleted = Column(Integer, nullable=False, server_default=u"'0'")

    client = relationship('Client')

    def __json__(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'client_id': self.client_id,
        }


class PriceList(Base):
    __tablename__ = u'PriceList'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    code = Column(Unicode(16), nullable=False)
    name = Column(Unicode(255), nullable=False)
    deleted = Column(SmallInteger, nullable=False, server_default=u"'0'")
    finance_id = Column(Integer, ForeignKey('rbFinance.id'), nullable=False)
    begDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    draft = Column(Integer, nullable=False, server_default=u"'0'")

    finance = relationship(u'rbFinance')


class PriceListItem(Base):
    __tablename__ = u'PriceListItem'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    priceList_id = Column(Integer, ForeignKey('PriceList.id'), nullable=False)
    deleted = Column(SmallInteger, nullable=False, server_default=u"'0'")
    service_id = Column(Integer, ForeignKey('rbService.id'), nullable=False)
    serviceCodeOW = Column(Unicode(64))
    serviceNameOW = Column(Unicode(256))
    begDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    isAccumulativePrice = Column(SmallInteger, nullable=False, server_default=u"'0'")

    service = relationship(u'rbService')


class Contract_PriceListAssoc(Base):
    __tablename__ = u'Contract_PriceList'
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('Contract.id'), nullable=False)
    priceList_id = Column(Integer, ForeignKey('PriceList.id'), nullable=False)


class rbContractType(Base):
    __tablename__ = 'rbContractType'
    _table_description = u'Тип контракта'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Unicode(8), nullable=False)
    name = Column(Unicode(64), nullable=False)
    counterPartyOne = Column(SmallInteger, nullable=False)
    counterPartyTwo = Column(SmallInteger, nullable=False)
    requireContingent = Column(SmallInteger, nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'require_ontingent': self.requireContingent
        }

    def __int__(self):
        return self.id


class rbServiceKind(Base):
    __tablename__ = 'rbServiceKind'
    _table_description = u'Вид экземпляра услуги'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Unicode(16), nullable=False)
    name = Column(Unicode(128), nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }

    def __int__(self):
        return self.id


class Service(Base):
    __tablename__ = u'Service'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    priceListItem_id = Column(Integer, ForeignKey('PriceListItem.id'), nullable=False)
    serviceKind_id = Column(Integer, ForeignKey('rbServiceKind.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('Service.id'))
    event_id = Column(Integer, ForeignKey('Event.id'), nullable=False)
    action_id = Column(Integer, ForeignKey('Action.id'))
    actionProperty_id = Column(Integer, ForeignKey('ActionProperty.id'))
    amount = Column(Float, nullable=False)
    deleted = Column(SmallInteger, nullable=False, server_default=u"'0'")
    discount_id = Column(Integer, ForeignKey('ServiceDiscount.id'))

    price_list_item = relationship('PriceListItem')
    service_kind = relationship('rbServiceKind')
    parent_service = relationship('Service', remote_side=[id])
    event = relationship('Event')
    action = relationship('Action')
    action_property = relationship('ActionProperty')
    discount = relationship('ServiceDiscount')

    def __init__(self):
        self._in_invoice = None
        self._invoice = None
        self._invoice_loaded = False
        self._subservice_list = None
        self._sum = None
        self._sum_loaded = False

    @orm.reconstructor
    def init_on_load(self):
        self._in_invoice = None
        self._invoice = None
        self._invoice_loaded = False
        self._subservice_list = None
        self._sum = None
        self._sum_loaded = False

    @property
    def sum_(self):
        if not self._sum_loaded:
            self._sum = self._get_recalc_sum()
            self._sum_loaded = True
        return self._sum

    def set_sum_(self, val):
        self._sum = val
        self._sum_loaded = True

    @property
    def in_invoice(self):
        if self._in_invoice is None:
            self._in_invoice = self._get_in_invoice()
        return self._in_invoice

    @property
    def invoice(self):
        if not self._invoice_loaded:
            invoice = self._get_invoice()
            self._invoice = invoice
            self._invoice_loaded = True
        return self._invoice

    @property
    def subservice_list(self):
        if self._subservice_list is None:
            self.init_subservice_list()
        return self._subservice_list

    @subservice_list.setter
    def subservice_list(self, value):
        self._subservice_list = value

    def recalc_sum(self):
        self._sum = self._get_recalc_sum()

    def init_subservice_list(self):
        self._subservice_list = self._get_subservices()
        for ss in self._subservice_list:
            ss.init_subservice_list()

    @property
    def serviced_entity(self):
        return self.get_serviced_entity()

    def get_serviced_entity(self):
        if self.serviceKind_id == ServiceKind.simple_action[0]:
            return self.action
        elif self.serviceKind_id == ServiceKind.group[0]:
            return None
        elif self.serviceKind_id == ServiceKind.lab_action[0]:
            return self.action
        elif self.serviceKind_id == ServiceKind.lab_test[0]:
            return self.action_property

    def get_flatten_subservices(self):
        flatten = []

        def traverse(s):
            for ss in s.subservice_list:
                if ss.subservice_list:
                    traverse(ss)
                else:
                    flatten.append(ss)

        traverse(self)
        return flatten

    def _get_in_invoice(self):
        from nemesis.lib.data_ctrl.accounting.service import ServiceController
        service_ctrl = ServiceController()
        return service_ctrl.check_service_in_invoice(self)

    def _get_invoice(self):
        from nemesis.lib.data_ctrl.accounting.invoice import InvoiceController
        invoice_ctrl = InvoiceController()
        invoice = invoice_ctrl.get_service_invoice(self)
        return invoice

    def _get_recalc_sum(self):
        from nemesis.lib.data_ctrl.accounting.utils import calc_service_total_sum
        return calc_service_total_sum(self) if self.priceListItem_id is not None else 0

    def _get_subservices(self):
        from nemesis.lib.data_ctrl.accounting.service import ServiceController
        service_ctrl = ServiceController()
        ss_list = service_ctrl.get_subservices(self)
        return ss_list


class ServiceDiscount(Base):
    __tablename__ = u'ServiceDiscount'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    code = Column(Unicode(32))
    name = Column(Unicode(1024), nullable=False)
    valuePct = Column(Float)
    valueFixed = Column(Numeric(15, 2))
    begDate = Column(Date, nullable=False)
    endDate = Column(Date)
    deleted = Column(SmallInteger, nullable=False, server_default=u"'0'")


class Invoice(Base):
    __tablename__ = u'Invoice'

    id = Column(Integer, primary_key=True)
    createDatetime = Column(DateTime, nullable=False)
    createPerson_id = Column(ForeignKey('Person.id'), index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(ForeignKey('Person.id'), index=True)
    contract_id = Column(ForeignKey('Contract.id'), nullable=False)
    parent_id = Column(ForeignKey('Invoice.id'))
    setDate = Column(Date, nullable=False)
    settleDate = Column(Date)
    number = Column(Unicode(20), nullable=False)
    deedNumber = Column(Unicode(20))
    deleted = Column(SmallInteger, nullable=False, server_default=u"'0'")
    note = Column(Unicode(255))
    draft = Column(Integer, nullable=False, server_default=u"'0'")

    createPerson = relationship('Person', foreign_keys=[createPerson_id])
    modifyPerson = relationship('Person', foreign_keys=[modifyPerson_id])
    contract = relationship('Contract')
    parent = relationship('Invoice', remote_side=[id])
    item_list = relationship(
        'InvoiceItem',
        primaryjoin='and_(InvoiceItem.invoice_id==Invoice.id, InvoiceItem.parent_id == None, InvoiceItem.deleted == 0)'
    )
    refund_items = relationship(
        'InvoiceItem',
        primaryjoin='and_(InvoiceItem.refund_id == Invoice.id, InvoiceItem.deleted == 0)'
    )

    total_sum = CalculatedProperty('_total_sum')
    refund_sum = CalculatedProperty('_refund_sum')
    coordinated_refund = CalculatedPropertyRO('_coordinated_refund')

    @orm.reconstructor
    def kill_calculated_fields(self):
        del self.total_sum
        del self.refund_sum
        del self.coordinated_refund

    @total_sum
    def total_sum(self):
        from nemesis.lib.data_ctrl.accounting.utils import calc_invoice_total_sum
        return calc_invoice_total_sum(self)

    @refund_sum
    def refund_sum(self):
        from nemesis.lib.data_ctrl.accounting.utils import calc_invoice_refund_sum
        return calc_invoice_refund_sum(self)

    @coordinated_refund
    def coordinated_refund(self):
        return Query(Invoice).filter(
            Invoice.parent == self,
            Invoice.deleted == 0,
            Invoice.settleDate == None,
        ).first()

    def get_all_entities(self):
        result = [self]
        for item in self.item_list:
            result.append(item)
            result.extend(item.get_flatten_subitems())

        return result


class InvoiceItem(Base):
    __tablename__ = u'InvoiceItem'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('Invoice.id'), nullable=False)
    refund_id = Column(ForeignKey('Invoice.id'))
    concreteService_id = Column(Integer, ForeignKey('Service.id'))
    discount_id = Column(Integer, ForeignKey('ServiceDiscount.id'))
    price = Column(Numeric(15, 2), nullable=False)
    amount = Column(Float, nullable=False)
    sum = Column(Numeric(15, 2), nullable=False)
    deleted = Column(SmallInteger, nullable=False, server_default=u"'0'")
    parent_id = Column(Integer, ForeignKey('InvoiceItem.id'))

    invoice = relationship('Invoice', foreign_keys=[invoice_id])
    refund = relationship('Invoice', foreign_keys=[refund_id])
    service = relationship('Service')
    discount = relationship('ServiceDiscount')
    parent_item = relationship('InvoiceItem', remote_side=[id])

    @orm.reconstructor
    def kill_calculated_fields(self):
        del self.subitem_list

    @property
    def subitem_list(self):
        if not hasattr(self, '_subitem_list'):
            self.init_subitem_list()
        return self._subitem_list

    @subitem_list.setter
    def subitem_list(self, value):
        self._subitem_list = value

    @subitem_list.deleter
    def subitem_list(self):
        if hasattr(self, '_subitem_list'):
            del self._subitem_list

    @property
    def is_refunded(self):
        return self.refund_id is not None

    def init_subitem_list(self):
        self._subitem_list = self._get_subitems()
        for ss in self._subitem_list:
            ss.init_subitem_list()

    def get_flatten_subitems(self):
        flatten = []

        def traverse(item):
            for si in item.subitem_list:
                if si.subitem_list:
                    traverse(si)
                else:
                    flatten.append(si)

        traverse(self)
        return flatten

    def _get_subitems(self):
        from nemesis.lib.data_ctrl.accounting.invoice import InvoiceItemController
        ii_ctrl = InvoiceItemController()
        si_list = ii_ctrl.get_subitems(self)
        return si_list


class FinanceTransaction(Base):
    __tablename__ = u'FinanceTransaction'

    id = Column(Integer, primary_key=True)
    trxDatetime = Column(DateTime, nullable=False, default=datetime.datetime.now)
    trxType_id = Column(Integer, ForeignKey('rbFinanceTransactionType.id'), nullable=False)
    financeOperationType_id = Column(Integer, ForeignKey('rbFinanceOperationType.id'), nullable=False)
    contragent_id = Column(Integer, ForeignKey('Contract_Contragent.id'), nullable=False)
    invoice_id = Column(Integer, ForeignKey('Invoice.id'))
    payType_id = Column(Integer, ForeignKey('rbPayType.id'))
    sum = Column(Numeric(15, 2), nullable=False)

    contragent = relationship('Contract_Contragent')
    invoice = relationship('Invoice', backref='transactions')
    trx_type = relationship('rbFinanceTransactionType')
    operation_type = relationship('rbFinanceOperationType')
    pay_type = relationship('rbPayType')


class rbFinanceTransactionType(Base):
    __tablename__ = 'rbFinanceTransactionType'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Unicode(16), nullable=False)
    name = Column(Unicode(64), nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
        }

    def __int__(self):
        return self.id


class rbFinanceOperationType(Base):
    __tablename__ = 'rbFinanceOperationType'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Unicode(16), nullable=False)
    name = Column(Unicode(64), nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
        }

    def __int__(self):
        return self.id


class rbPayType(Base):
    __tablename__ = 'rbPayType'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Unicode(16), nullable=False)
    name = Column(Unicode(64), nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
        }

    def __int__(self):
        return self.id