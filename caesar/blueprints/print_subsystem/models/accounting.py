# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import Column, Unicode, ForeignKey, Date, Float, DateTime, SmallInteger, Numeric, String
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy import orm

from ..database import Base


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
    contingent_list = relationship('Contract_Contingent', backref='contract')
    pricelist_list = relationship('PriceList', secondary='Contract_PriceList')

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
    usingInsurancePolicy = Column(SmallInteger, nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'using_insurance_policy': self.usingInsurancePolicy
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
    action_id = Column(Integer, ForeignKey('Action.id'))
    amount = Column(Float, nullable=False)
    deleted = Column(SmallInteger, nullable=False, server_default=u"'0'")
    discount_id = Column(Integer, ForeignKey('ServiceDiscount.id'))

    price_list_item = relationship('PriceListItem')
    action = relationship('Action')
    discount = relationship('ServiceDiscount')

    def __init__(self):
        self.sum_ = self._get_recalc_sum()
        self._in_invoice = None
        self._invoice = None
        self._invoice_loaded = False

    @orm.reconstructor
    def init_on_load(self):
        self.sum_ = self._get_recalc_sum()
        self._in_invoice = None
        self._invoice = None
        self._invoice_loaded = False

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
        from nemesis.lib.data_ctrl.accounting.utils import calc_service_sum
        return calc_service_sum(self) if self.priceListItem_id is not None else 0


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
    createPerson_id = Column(Integer, index=True)
    modifyDatetime = Column(DateTime, nullable=False)
    modifyPerson_id = Column(Integer, index=True)
    contract_id = Column(Integer, ForeignKey('Contract.id'), nullable=False)
    setDate = Column(Date, nullable=False)
    settleDate = Column(Date)
    number = Column(Unicode(20), nullable=False)
    deedNumber = Column(Unicode(20))
    deleted = Column(SmallInteger, nullable=False, server_default=u"'0'")
    note = Column(Unicode(255))
    draft = Column(Integer, nullable=False, server_default=u"'0'")

    contract = relationship('Contract')
    item_list = relationship('InvoiceItem', backref='invoice')

    def __init__(self):
        self.total_sum = self._get_recalc_total_sum()

    @orm.reconstructor
    def init_on_load(self):
        self.total_sum = self._get_recalc_total_sum()

    def _get_recalc_total_sum(self):
        from nemesis.lib.data_ctrl.accounting.utils import calc_invoice_total_sum
        return calc_invoice_total_sum(self)


class InvoiceItem(Base):
    __tablename__ = u'InvoiceItem'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('Invoice.id'), nullable=False)
    concreteService_id = Column(Integer, ForeignKey('Service.id'))
    discount_id = Column(Integer, ForeignKey('ServiceDiscount.id'))
    price = Column(Numeric(15, 2), nullable=False)
    amount = Column(Float, nullable=False)
    sum = Column(Numeric(15, 2), nullable=False)
    deleted = Column(SmallInteger, nullable=False, server_default=u"'0'")

    service = relationship(u'Service')
    discount = relationship('ServiceDiscount')


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
    invoice = relationship('Invoice')
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