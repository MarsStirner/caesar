# -*- coding: utf-8 -*-
from dateutil import parser
from nemesis.systemwide import db
from nemesis.models.exists import QuotaCatalog


def worker(model):
    if model == QuotaCatalog:
        return QuotaCatalogWorker(model)


class QuotaCatalogWorker(object):

    def __init__(self, model):
        self.model = model

    def get_list(self, order=None):
        return self.model.query.order_by(order).all()

    def get_by_id(self, _id):
        return self.model.query.get(_id)

    def __fill_obj(self, obj, data):
        if 'finance_id' in data:
            obj.finance_id = data['finance_id']
        if 'create_datetime' in data:
            obj.createDatetime = data['create_datetime']
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

    def add(self, data):
        obj = self.__fill_obj(self.model(), data)
        db.session.add(obj)
        db.session.commit()
        return obj

    def update(self, _id, data):
        obj = self.get_by_id(_id)
        if not obj:
            return None
        obj = self.__fill_obj(obj, data)
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
