# -*- coding: utf-8 -*-
from flask import request

from nemesis.systemwide import db
from nemesis.lib.apiutils import api_method, ApiException
from nemesis.models.exists import QuotaCatalog, QuotaType, VMPQuotaDetails

from ..app import module
from ..lib.data import worker


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


@module.route('/api/v1/quota_catalog/<int:_id>', methods=['DELETE'])
@api_method
def api_v1_quota_catalog_delete(_id):
    obj = worker(QuotaCatalog)
    result = obj.delete(_id)
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
    result = obj.delete(_id)
    if result is None:
        raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    return result
