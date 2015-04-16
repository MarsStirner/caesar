# -*- coding: utf-8 -*-
import sys

from flask import request

from nemesis.systemwide import db
from nemesis.lib.apiutils import api_method, ApiException
from nemesis.models.exists import QuotaCatalog, QuotaType, VMPQuotaDetails, rbPacientModel, rbTreatment, rbTreatmentType

from ..app import module
from ..lib.data import worker, WorkerException


@module.route('/api/v1/quota_catalog', methods=['GET'])
@module.route('/api/v1/quota_catalog/<int:_id>', methods=['GET'])
@api_method
def api_v1_quota_catalog_get(_id=None):
    obj = worker(QuotaCatalog)
    if _id is not None:
        catalog = obj.get_by_id(_id)
        if not catalog:
            raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
        return catalog
    return obj.get_list(order=QuotaCatalog.begDate)


@module.route('/api/v1/quota_catalog', methods=['POST'])
@module.route('/api/v1/quota_catalog/<int:_id>', methods=['POST'])
@api_method
def api_v1_quota_catalog_post(_id=None):
    obj = worker(QuotaCatalog)
    data = request.get_json()
    if _id is not None:
        result = obj.update(_id, data)
        if result is None:
            raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    else:
        result = obj.add(data)
    return result


@module.route('/api/v1/quota_catalog/<int:_id>/clone', methods=['POST', 'GET'])
@api_method
def api_v1_quota_catalog_clone(_id):
    obj = worker(QuotaCatalog)
    result = obj.clone(_id)
    if not result:
        raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    return result

@module.route('/api/v1/quota_catalog/<int:_id>', methods=['DELETE'])
@api_method
def api_v1_quota_catalog_delete(_id):
    obj = worker(QuotaCatalog)
    try:
        result = obj.delete(_id)
    except WorkerException as e:
        raise ApiException(418, e.message)
    if result is None:
        raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    return result


@module.route('/api/v1/quota_profile/<int:catalog_id>', methods=['GET'])
@module.route('/api/v1/quota_profile/<int:catalog_id>/<int:_id>', methods=['GET'])
@api_method
def api_v1_quota_profile_get(catalog_id, _id=None):
    obj = worker(QuotaType)
    if _id is not None:
        data = obj.get_by_id(_id)
        if not data:
            raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
        return data
    return obj.get_list(
        where=db.and_(
            QuotaType.catalog_id == catalog_id,
            QuotaType.profile_code.is_(None),
            QuotaType.deleted == 0),
        order=QuotaType.code
    )


@module.route('/api/v1/quota_profile/<int:catalog_id>', methods=['POST'])
@module.route('/api/v1/quota_profile/<int:catalog_id>/<int:_id>', methods=['POST'])
@api_method
def api_v1_quota_profile_post(catalog_id, _id=None):
    obj = worker(QuotaType)
    data = request.get_json()
    if 'catalog_id' not in data:
        data.update({'catalog_id': catalog_id})
    # type_code - код вида ВМП. Для профиля будет являться его кодом и = коду профиля для его видов ВМП
    if 'code' in data and 'type_code' not in data:
        data.update({'type_code': data['code']})
    if _id is not None:
        result = obj.update(_id, data)
        if result is None:
            raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    else:
        result = obj.add(data)
    return result


@module.route('/api/v1/quota_profile/<int:catalog_id>/<int:_id>', methods=['DELETE'])
@api_method
def api_v1_quota_profile_delete(catalog_id, _id):
    obj = worker(QuotaType)
    result = obj.delete(_id)
    if result is None:
        raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    return result


@module.route('/api/v1/quota_type/<int:profile_id>', methods=['GET'])
@module.route('/api/v1/quota_type/<int:profile_id>/<int:_id>', methods=['GET'])
@api_method
def api_v1_quota_type_get(profile_id, _id=None):
    obj = worker(QuotaType)
    if _id is not None:
        data = obj.get_by_id(_id)
        if not data:
            raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
        return data
    profile = obj.get_by_id(profile_id)
    if profile is None:
        raise ApiException(404, u'Значение с group_id={0} не найдено'.format(_id))
    return obj.get_list(
        where=db.and_(QuotaType.catalog_id == profile.catalog_id,
                      QuotaType.profile_code == profile.code,
                      QuotaType.deleted == 0),
        order=QuotaType.id)


@module.route('/api/v1/quota_type/<int:profile_id>', methods=['POST'])
@module.route('/api/v1/quota_type/<int:profile_id>/<int:_id>', methods=['POST'])
@api_method
def api_v1_quota_type_post(profile_id, _id=None):
    obj = worker(QuotaType)
    data = request.get_json()
    profile = obj.get_by_id(profile_id)
    if profile is None:
        raise ApiException(404, u'Значение с profile_id={0} не найдено'.format(_id))
    if 'profile_code' not in data:
        data.update({'profile_code': profile.code})
    if 'catalog_id' not in data:
        data.update({'catalog_id': profile.catalog_id})
    if _id is not None:
        result = obj.update(_id, data)
        if result is None:
            raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    else:
        result = obj.add(data)
    return result


@module.route('/api/v1/quota_type/<int:group_id>/<int:_id>', methods=['DELETE'])
@api_method
def api_v1_quota_type_delete(group_id, _id):
    obj = worker(QuotaType)
    result = obj.delete(_id)
    if result is None:
        raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    return result


@module.route('/api/v1/quota_detail/<int:quota_type_id>', methods=['GET'])
@module.route('/api/v1/quota_detail/<int:quota_type_id>/<int:_id>', methods=['GET'])
@api_method
def api_v1_quota_detail_get(quota_type_id, _id=None):
    obj = worker(VMPQuotaDetails)
    if _id is not None:
        data = obj.get_by_id(_id)
        if not data:
            raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
        return data
    return obj.get_list(
        where=db.and_(VMPQuotaDetails.quotaType_id == quota_type_id),
        order=VMPQuotaDetails.id)


@module.route('/api/v1/quota_detail/<int:quota_type_id>', methods=['POST'])
@module.route('/api/v1/quota_detail/<int:quota_type_id>/<int:_id>', methods=['POST'])
@api_method
def api_v1_quota_detail_post(quota_type_id, _id=None):
    obj = worker(VMPQuotaDetails)
    data = request.get_json()
    if 'quota_type_id' not in data:
        data.update({'quota_type_id': quota_type_id})
    if _id is not None:
        result = obj.update(_id, data)
        if result is None:
            raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    else:
        result = obj.add(data)
    return result


@module.route('/api/v1/quota_detail/<int:quota_type_id>/<int:_id>', methods=['DELETE'])
@api_method
def api_v1_quota_detail_delete(quota_type_id, _id):
    obj = worker(VMPQuotaDetails)
    try:
        result = obj.delete(_id)
    except WorkerException as e:
        raise ApiException(418, e.message)
    if result is None:
        raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    return result


supported_rbs = {
    'rbPacientModel': rbPacientModel,
    'rbTreatment': rbTreatment,
    'rbTreatmentType': rbTreatmentType
}


@module.route('/api/v1/rb/list/', methods=['GET'])
@api_method
def api_v1_rb_list_get():
    return {
        'supported_rbs': sorted([
            dict(name=t.__tablename__, desc=t._table_description)
            for t_name, t in supported_rbs.iteritems()
        ], key=lambda k: k['desc'])
    }


@module.route('/api/v1/rb/<name>/', methods=['GET'])
@api_method
def api_v1_rb_simple_get(name):
    rbClass = getattr(sys.modules[__name__], name, None)
    if not rbClass:
        raise ApiException(404, u'Не найден справочник по наименованию {0}'.format(name))

    def make_rb(item):
        r = {
            'id': item.id,
            'code': item.code,
            'name': item.name
        }
        if hasattr(item, 'deleted'):
            r['deleted'] = item.deleted
        return r

    return {
        'items': map(make_rb, rbClass.query)
    }


@module.route('/api/v1/rb/<name>/', methods=['POST'])
@module.route('/api/v1/rb/<name>/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_rb_simple_post(name, item_id=None):
    rbClass = getattr(sys.modules[__name__], name, None)
    if not rbClass:
        raise ApiException(404, u'Не найден справочник по наименованию {0}'.format(name))
    data = request.get_json()

    if item_id:
        item = rbClass.query.get(item_id)
    else:
        item = rbClass()
    item.code = data['code']
    item.name = data['name']
    db.session.add(item)
    db.session.commit()

    return item


@module.route('/api/v1/rb/<name>/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_rb_simple_delete(name, item_id):
    rbClass = getattr(sys.modules[__name__], name, None)
    if not rbClass:
        raise ApiException(404, u'Не найден справочник по наименованию {0}'.format(name))

    item = rbClass.query.get(item_id)
    if hasattr(item, 'deleted'):
        item.deleted = 1
        db.session.add(item)
        db.session.commit()

        return item
    else:
        raise ApiException(404, u'Физическое удаление записей не реализовано')