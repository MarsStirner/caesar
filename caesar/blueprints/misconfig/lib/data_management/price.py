# -*- coding: utf-8 -*-
from .base import BaseModelManager, FieldConverter, FCType, represent_model
from nemesis.models.exists import PriceList, ContractTariff
from nemesis.lib.utils import (get_new_uuid, safe_int, safe_unicode, safe_traverse, safe_bool, safe_date)
from nemesis.systemwide import db


class PriceModelManager(BaseModelManager):
    def __init__(self):
        self._finance_mng = self.get_manager('rbFinance')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            FieldConverter(
                FCType.relation,
                'finance', (self.handle_onetomany_nonedit, ),
                'finance',
                model_manager=self._finance_mng),
        ]
        super(PriceModelManager, self).__init__(PriceList, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(PriceModelManager, self).create(data, parent_id, parent_obj)
        return item


class TariffModelManager(BaseModelManager):
    def __init__(self):
        self._service_mng = self.get_manager('rbService')
        self._servicefin_mng = self.get_manager('rbServiceFinance')
        self._et_mng = self.get_manager('EventType')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'begDate', safe_date, 'birth_date'),
            FieldConverter(FCType.basic, 'endDate', safe_date, 'birth_date'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            FieldConverter(FCType.basic, 'priceList_id', safe_int, 'price_list_id'),
            FieldConverter(FCType.basic, 'price', safe_unicode, 'price'),
            FieldConverter(FCType.basic, 'amount', safe_int, 'amount'),
            FieldConverter(FCType.basic, 'uet', safe_int, 'uet'),
            FieldConverter(
                FCType.relation,
                'rbServiceFinance', (self.handle_onetomany_nonedit, ),
                'rbServiceFinance',
                model_manager=self._servicefin_mng),
            FieldConverter(
                FCType.relation,
                'service', (self.handle_onetomany_nonedit, ),
                'service',
                model_manager=self._service_mng),
            FieldConverter(
                FCType.relation,
                'event_type', (self.handle_onetomany_nonedit, ),
                'event_type',
                model_manager=self._et_mng),
        ]
        super(TariffModelManager, self).__init__(ContractTariff, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(TariffModelManager, self).create(data, parent_id, parent_obj)
        return item