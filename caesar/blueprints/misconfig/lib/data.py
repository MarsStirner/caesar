# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import exc
from nemesis.systemwide import db
from nemesis.models.exists import QuotaCatalog, QuotaType, VMPQuotaDetails, MKB
from nemesis.models.utils import safe_current_user_id
from nemesis.lib.utils import safe_traverse, safe_date


def worker(model):
    if model == QuotaCatalog:
        return QuotaCatalogWorker(model)
    if model == QuotaType:
        return QuotaTypeWorker(model)
    if model == VMPQuotaDetails:
        return QuotaDetailsWorker(model)


def transfer_fields(src, dst, names):
    for name in names:
        setattr(dst, name, getattr(src, name))


class WorkerException(Exception):
    """Исключение в работе с БД
    :ivar code: код ответа и соответствующий код в метаданных
    :ivar message: текстовое пояснение ошибки
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return u'%s' % self.message


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
        try:
            db.session.execute(self.model.__table__.delete().where(self.model.id == _id))
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            print(e)
            raise WorkerException(
                u'Ошибка удаления. Существуют непустые зависимости в БД, сначала необходимо удалить их.')
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
            obj.begDate = safe_date(data['beg_date'])

        if 'end_date' in data and data['end_date']:
            obj.endDate = safe_date(data['end_date'])

        if 'catalog_number' in data:
            obj.catalogNumber = data['catalog_number']

        if 'document_number' in data:
            obj.documentNumber = data['document_number']

        if 'document_date' in data:
            obj.documentDate = safe_date(data['document_date'])

        if 'document_corresp' in data:
            obj.documentCorresp = data['document_corresp']

        if 'comment' in data:
            obj.comment = data['comment']

        return obj

    def clone(self, _id):
        obj = self.get_by_id(_id)
        now = datetime.now()

        if not obj:
            return

        def clone_QC(qc):
            new = QuotaCatalog()
            new.createDatetime = new.modifyDatetime = now
            new.createPerson_id = new.modifyPerson_id = safe_current_user_id()
            transfer_fields(qc, new, ('begDate', 'endDate', 'documentNumber', 'documentDate', 'documentCorresp', 'finance', 'catalogNumber', 'comment'))
            new.quotaTypes = [
                clone_QT(qt, new)
                for qt in qc.quotaTypes
                if qt
            ]
            db.session.add(new)
            return new

        def clone_QT(qt, qc):
            new = QuotaType()
            new.createDatetime = new.modifyDatetime = now
            new.createPerson_id = new.modifyPerson_id = safe_current_user_id()
            new.catalog = qc
            transfer_fields(qt, new, ('class_', 'profile_code', 'group_code', 'type_code', 'code', 'name', 'teenOlder', 'price'))
            new.quotaDetails = [
                clone_QD(qd, new)
                for qd in qt.quotaDetails
                if qd
            ]
            db.session.add(new)
            return new

        def clone_QD(qd, qt):
            new = VMPQuotaDetails()
            new.createDatetime = new.modifyDatetime = now
            new.createPerson_id = new.modifyPerson_id = safe_current_user_id()
            new.quota_type = qt
            transfer_fields(qd, new, ('pacient_model', 'treatment', 'mkb', 'price'))
            db.session.add(new)
            return new

        result = clone_QC(obj)
        db.session.commit()
        return result


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

    def delete(self, _id):
        try:
            super(QuotaTypeWorker, self).delete(_id)
        except WorkerException as e:
            obj = self.get_by_id(_id)
            obj.deleted = 1
            db.session.commit()
        return True


class QuotaDetailsWorker(BaseWorker):

    def _fill_obj(self, obj, data):

        if 'patient_model' in data:
            obj.pacientModel_id = safe_traverse(data['patient_model'], 'id')
        elif 'patient_model_id' in data:
            obj.pacientModel_id = data['patient_model_id']

        if 'treatment' in data:
            obj.treatment_id = safe_traverse(data['treatment'], 'id')
        elif 'treatment_id' in data:
            obj.treatment_id = data['treatment_id']

        if 'quota_type' in data:
            obj.quotaType_id = safe_traverse(data['quota_type'], 'id')
        elif 'quota_type_id' in data:
            obj.quotaType_id = data['quota_type_id']

        if 'mkb' in data and data['mkb']:
            obj.mkb = MKB.query.filter(MKB.id.in_(
                [mkb['id'] for mkb in data['mkb']]
            )).order_by(MKB.DiagID).all()

        if 'price' in data:
            obj.price = data['price']

        return obj
