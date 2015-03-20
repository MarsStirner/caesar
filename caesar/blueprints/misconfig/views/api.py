# -*- coding: utf-8 -*-
from flask import request

from nemesis.systemwide import db
from nemesis.lib.apiutils import api_method, ApiException
from nemesis.models.exists import QuotaCatalog, QuotaType

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


@module.route('/api/v1/quota_type/<int:catalog_id>', methods=['GET'])
@module.route('/api/v1/quota_type/<int:catalog_id>/<int:_id>', methods=['GET'])
@api_method
def api_v1_quota_type_get(catalog_id, _id=None):
    obj = worker(QuotaType)
    if _id is not None:
        data = obj.get_by_id(_id)
        if not data:
            raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
        return data
    return obj.get_list(where=db.and_(QuotaType.catalog_id == catalog_id, QuotaType.deleted == 0),
                        order=QuotaType.group_code)


@module.route('/api/v1/quota_type/<int:catalog_id>', methods=['POST'])
@module.route('/api/v1/quota_type/<int:catalog_id>/<int:_id>', methods=['POST'])
@api_method
def api_v1_quota_type_post(catalog_id, _id=None):
    obj = worker(QuotaType)
    data = request.get_json()
    if 'catalog_id' not in data:
        data.update({'catalog_id': catalog_id})
    if _id is not None:
        result = obj.update(_id, data)
        if result is None:
            raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    else:
        result = obj.add(data)
    return result


@module.route('/api/v1/quota_type/<int:catalog_id>/<int:_id>', methods=['DELETE'])
@api_method
def api_v1_quota_type_delete(catalog_id, _id):
    obj = worker(QuotaType)
    result = obj.delete(_id)
    if result is None:
        raise ApiException(404, u'Значение с id={0} не найдено'.format(_id))
    return result

