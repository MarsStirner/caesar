# -*- coding: utf-8 -*-

from .base import BaseModelManager, FieldConverter, FCType
from nemesis.models.accounting import PriceList, PriceListItem
from nemesis.lib.utils import (safe_int, safe_unicode, safe_double, safe_date, safe_bool)


class PriceListModelManager(BaseModelManager):
    def __init__(self):
        self._finance_mng = self.get_manager('rbFinance')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            FieldConverter(FCType.basic, 'begDate', safe_date, 'beg_date'),
            FieldConverter(FCType.basic, 'endDate', safe_date, 'end_date'),
            FieldConverter(
                FCType.relation,
                'finance', (self.handle_onetomany_nonedit, ),
                'finance',
                model_manager=self._finance_mng),
        ]
        super(PriceListModelManager, self).__init__(PriceList, fields)


class PriceListItemModelManager(BaseModelManager):
    def __init__(self):
        self._service_mng = self.get_manager('rbService')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'priceList_id', safe_int, 'pricelist_id'),
            FieldConverter(FCType.basic, 'begDate', safe_date, 'beg_date'),
            FieldConverter(FCType.basic, 'endDate', safe_date, 'end_date'),
            FieldConverter(FCType.basic, 'serviceCodeOW', safe_unicode, 'service_code'),
            FieldConverter(FCType.basic, 'serviceNameOW', safe_unicode, 'service_name'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            FieldConverter(FCType.basic, 'price', safe_double, 'price'),
            FieldConverter(FCType.basic, 'isAccumulativePrice', safe_int, 'is_accumulative_price', safe_bool),
            FieldConverter(
                FCType.relation,
                'service', (self.handle_onetomany_nonedit, ),
                'service',
                model_manager=self._service_mng
            ),
        ]
        super(PriceListItemModelManager, self).__init__(PriceListItem, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(PriceListItemModelManager, self).create(data, parent_id, parent_obj)
        item.priceList_id = data.get('pricelist_id') if data is not None else parent_id
        pl_mng = PriceListModelManager()
        if item.priceList_id:
            pricelist = pl_mng.get_by_id(item.priceList_id)
            item.begDate = pricelist.begDate
            item.endDate = pricelist.endDate
        return item

    def filter_(self, **kwargs):
        query = self._model.query
        if 'name' in kwargs:
            query = query.filter(PriceListItem.serviceNameOW.like(u'%{0}%'.format(kwargs['name'])))
        if 'code' in kwargs:
            query = query.filter(PriceListItem.serviceCodeOW.like(u'%{0}%'.format(kwargs['code'])))
        if 'beg_date_from' in kwargs:
            query = query.filter(PriceListItem.begDate >= safe_date(kwargs['beg_date_from']))
        if 'beg_date_to' in kwargs:
            query = query.filter(PriceListItem.begDate <= safe_date(kwargs['beg_date_to']))
        if 'end_date_from' in kwargs:
            query = query.filter(PriceListItem.endDate >= safe_date(kwargs['end_date_from']))
        if 'end_date_to' in kwargs:
            query = query.filter(PriceListItem.endDate <= safe_date(kwargs['end_date_to']))
        if 'pricelist_id' in kwargs:
            query = query.filter(PriceListItem.priceList_id == kwargs['pricelist_id'])

        return query
