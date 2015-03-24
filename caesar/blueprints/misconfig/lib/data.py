# -*- coding: utf-8 -*-
from datetime import datetime
from nemesis.systemwide import db
from nemesis.models.exists import QuotaCatalog, QuotaType, VMPQuotaDetails
from nemesis.models.utils import safe_current_user_id
from nemesis.lib.utils import safe_traverse


def worker(model):
    if model == QuotaCatalog:
        return QuotaCatalogWorker(model)
    if model == QuotaType:
        return QuotaTypeWorker(model)
    if model == VMPQuotaDetails:
        return QuotaDetailsWorker(model)


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
        data.update({'create_person_id': safe_current_user_id(),
                     'create_datetime': datetime.now(),
                     'modify_person_id': safe_current_user_id(),
                     'modify_datetime': datetime.now()})
        obj = self._fill_obj(self.model(), data)
        db.session.add(obj)
        db.session.commit()
        return obj

    def update(self, _id, data):
        data.update({'modify_person_id': safe_current_user_id(),
                     'modify_datetime': datetime.now()})
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
        # TODO: catch FK constraints
        db.session.delete(obj)
        db.session.commit()
        return True


class QuotaCatalogWorker(BaseWorker):

    def _fill_obj(self, obj, data):

        if 'finance' in data:
            obj.finance_id = safe_traverse(data['finance'], 'id')
        elif 'finance_id' in data:
            obj.finance_id = data['finance_id']

        if 'create_datetime' in data and data['create_datetime']:
            obj.createDatetime = data['create_datetime']

        if 'create_person_id' in data:
            obj.createPerson_id = data['create_person_id']

        if 'modify_datetime' in data and data['modify_datetime']:
            obj.modifyDatetime = data['modify_datetime']

        if 'modify_person_id' in data:
            obj.modifyPerson_id = data['modify_person_id']

        if 'beg_date' in data and data['beg_date']:
            obj.begDate = data['beg_date'].date()

        if 'end_date' in data and data['end_date']:
            obj.endDate = data['end_date'].date()

        if 'catalog_number' in data:
            obj.catalogNumber = data['catalog_number']

        if 'document_number' in data:
            obj.documentNumber = data['document_number']

        if 'document_date' in data:
            obj.documentDate = data['document_date'].date()

        if 'document_corresp' in data:
            obj.documentCorresp = data['document_corresp']

        if 'comment' in data:
            obj.comment = data['comment']

        return obj


class QuotaTypeWorker(BaseWorker):

    def _fill_obj(self, obj, data):

        if 'catalog_id' in data:
            obj.catalog_id = data['catalog_id']
        elif 'catalog' in data:
            obj.catalog_id = safe_traverse(data['catalog'], 'id')

        if 'create_datetime' in data and data['create_datetime']:
            obj.createDatetime = data['create_datetime']

        if 'create_person_id' in data:
            obj.createPerson_id = data['create_person_id']

        if 'modify_datetime' in data and data['modify_datetime']:
            obj.modifyDatetime = data['modify_datetime']

        if 'modify_person_id' in data:
            obj.modifyPerson_id = data['modify_person_id']

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

        if 'teen_older' in data:
            obj.teenOlder = data['teen_older']

        if 'price' in data:
            obj.price = float(data['price'])

        return obj


class QuotaDetailsWorker(BaseWorker):

    def _fill_obj(self, obj, data):

        if 'patient_model' in data:
            obj.pacientModel_id = safe_traverse(data['patient_model'], 'id')
        elif 'pacient_model_id' in data:
            obj.pacientModel_id = data['pacient_model_id']

        if 'treatment' in data:
            obj.treatment_id = safe_traverse(data['treatment'], 'id')
        elif 'treatment_id' in data:
            obj.treatment_id = data['treatment_id']

        if 'quota_type' in data:
            obj.quotaType_id = safe_traverse(data['quota_type'], 'id')
        elif 'quota_type_id' in data:
            obj.quotaType_id = data['quota_type_id']

        return obj
