# -*- coding: utf-8 -*-
from dateutil import parser
from nemesis.systemwide import db
from nemesis.models.exists import QuotaCatalog, QuotaType


def worker(model):
    if model == QuotaCatalog:
        return QuotaCatalogWorker(model)
    if model == QuotaType:
        return QuotaTypeWorker(model)


class BaseWorker(object):

    def __init__(self, model):
        self.model = model

    def get_by_id(self, _id):
        return self.model.query.get(_id)

    def get_list(self, where=None, order=None):
        query = self.model.query
        if where is not None:
            query = query.filter(where)
        if order is not None:
            query = query.order_by(order)
        return query.all()

    def _fill_obj(self, obj, data):
        raise NotImplementedError('Please implement this method')

    def add(self, data):
        obj = self._fill_obj(self.model(), data)
        db.session.add(obj)
        db.session.commit()
        return obj

    def update(self, _id, data):
        obj = self.get_by_id(_id)
        if not obj:
            return None
        obj = self._fill_obj(obj, data)
        db.session.add(obj)
        db.session.commit()
        return obj

    def delete(self, _id):
        obj = self.get_by_id(_id)
        if not obj:
            return None
        db.session.delete(obj)
        db.session.commit()
        return True


class QuotaCatalogWorker(BaseWorker):

    def _fill_obj(self, obj, data):
        if 'finance_id' in data:
            obj.finance_id = data['finance_id']
        if 'create_datetime' in data and data['create_datetime']:
            obj.createDatetime = parser.parse(data['create_datetime'])
        if 'create_person_id' in data:
            obj.createPerson_id = data['create_person_id']
        if 'beg_date' in data and data['beg_date']:
            obj.begDate = parser.parse(data['beg_date']).date()
        if 'end_date' in data and data['end_date']:
            obj.endDate = parser.parse(data['end_date']).date()
        if 'catalog_number' in data:
            obj.catalogNumber = data['catalog_number']
        if 'document_corresp' in data:
            obj.documentCorresp = data['document_corresp']
        if 'comment' in data:
            obj.comment = data['comment']
        return obj


class QuotaTypeWorker(BaseWorker):

    def _fill_obj(self, obj, data):
        if 'catalog_id' in data:
            obj.catalog_id = data['catalog_id']
        if 'create_datetime' in data and data['create_datetime']:
            obj.createDatetime = parser.parse(data['create_datetime'])
        if 'create_person_id' in data:
            obj.createPerson_id = data['create_person_id']
        if 'deleted' in data:
            obj.deleted = data['deleted']
        if 'class' in data:
            obj.class_ = data['class']
        if 'profile_code' in data:
            obj.profile_code = data['profile_code']
        if 'group_code' in data:
            obj.group_code = data['group_code']
        if 'type_code' in data:
            obj.type_code = data['type_code']
        if 'code' in data:
            obj.code = data['code']
        if 'name' in data:
            obj.name = data['name']
        if 'price' in data:
            obj.price = float(data['price'])
        return obj
