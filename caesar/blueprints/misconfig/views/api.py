# -*- coding: utf-8 -*-

from flask import request, abort

from nemesis.systemwide import db
from nemesis.lib.apiutils import api_method, ApiException
from nemesis.models.exists import QuotaCatalog, QuotaType, VMPQuotaDetails

from ..app import module
from ..lib.data import worker, WorkerException
from ..lib.data_management.factory import get_manager, all_rbs, basic_rbs, simple_rbs


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


@module.route('/api/v1/rb/list/', methods=['GET'])
@api_method
def api_v1_rb_list_get():
    return {
        'supported_rbs': sorted([
            dict(
                name=t.__tablename__,
                desc=getattr(t, '_table_description', t.__tablename__),
                is_simple=(t_name in simple_rbs)
            )
            for t_name, t in all_rbs.iteritems() if t_name in basic_rbs
        ], key=lambda k: k['desc'])
    }


@module.route('/api/v1/rb/<name>/', methods=['GET'])
@module.route('/api/v1/rb/<name>/<int:item_id>/', methods=['GET'])
@module.route('/api/v1/rb/<name>/<new>/', methods=['GET'])
@api_method
def api_v1_rb_get(name, item_id=None, new=None):
    if name not in all_rbs:
        raise ApiException(404, u'Не найден справочник по наименованию {0}'.format(name))
    mng = get_manager(name)
    if item_id or new:
        if item_id:
            item = mng.get_by_id(item_id)
        elif new == 'new':
            item = mng.create()
        else:
            raise abort(404)
        return {
            'item': mng.represent(item)
        }
    return {
        'items': map(mng.represent, mng.get_list())
    }


@module.route('/api/v1/rb/<name>/', methods=['POST'])
@module.route('/api/v1/rb/<name>/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_rb_post(name, item_id=None):
    if name not in all_rbs:
        raise ApiException(404, u'Не найден справочник по наименованию {0}'.format(name))
    mng = get_manager(name)
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/rb/<name>/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_rb_delete(name, item_id):
    if name not in all_rbs:
        raise ApiException(404, u'Не найден справочник по наименованию {0}'.format(name))

    mng = get_manager(name)
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/rb/<name>/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_rb_undelete(name, item_id):
    if name not in all_rbs:
        raise ApiException(404, u'Не найден справочник по наименованию {0}'.format(name))

    mng = get_manager(name)
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/expert/protocol/', methods=['GET'])
@module.route('/api/v1/expert/protocol/<int:item_id>/', methods=['GET'])
@module.route('/api/v1/expert/protocol/<new>/', methods=['GET'])
@api_method
def api_v1_expert_protocol_get(item_id=None, new=None):
    mng = get_manager('ExpertProtocol')
    if item_id:
        if item_id:
            item = mng.get_by_id(item_id)
        elif new == 'new':
            item = mng.create()
        else:
            raise abort(404)
        return {
            'item': mng.represent(item)
        }
    else:
        return {
            'items': map(mng.represent, mng.get_list())
        }


@module.route('/api/v1/expert/protocol/', methods=['POST'])
@module.route('/api/v1/expert/protocol/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_expert_protocol_post(item_id=None):
    mng = get_manager('ExpertProtocol')
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/expert/protocol/', methods=['DELETE'])
@api_method
def api_v1_expert_protocol_delete():
    raise NotImplementedError


@module.route('/api/v1/expert/protocol/scheme/', methods=['GET'])
@module.route('/api/v1/expert/protocol/scheme/<int:item_id>/', methods=['GET'])
@module.route('/api/v1/expert/protocol/scheme/<new>/<int:parent_id>/', methods=['GET'])
@api_method
def api_v1_expert_scheme_get(item_id=None, new=None, parent_id=None):
    mng = get_manager('ExpertScheme')
    if item_id or new:
        if item_id:
            item = mng.get_by_id(item_id)
        elif new == 'new':
            item = mng.create(parent_id=parent_id)
        else:
            raise abort(404)
        return {
            'item': mng.represent(item)
        }
    return {
        'items': map(mng.represent, mng.get_list())
    }


@module.route('/api/v1/expert/protocol/scheme/', methods=['POST'])
@module.route('/api/v1/expert/protocol/scheme/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_expert_scheme_post(item_id=None):
    mng = get_manager('ExpertScheme')
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/expert/protocol/scheme/', methods=['DELETE'])
@api_method
def api_v1_expert_scheme_delete():
    raise NotImplementedError


@module.route('/api/v1/expert/protocol/scheme_mkb/<int:item_id>/', methods=['GET'])
@module.route('/api/v1/expert/protocol/scheme_mkb/<new>/', methods=['GET'])
@module.route('/api/v1/expert/protocol/scheme_mkb/<new>/<int:parent_id>/', methods=['GET'])
@api_method
def api_v1_expert_scheme_mkb_get(item_id=None, new=None, parent_id=None):
    mng = get_manager('ExpertSchemeMKB')
    if item_id or new:
        if item_id:
            item = mng.get_by_id(item_id)
        elif new == 'new':
            item = mng.create(parent_id=parent_id)
        else:
            raise abort(404)
        return {
            'item': mng.represent(item)
        }


@module.route('/api/v1/expert/protocol/scheme_measure/<int:item_id>/', methods=['GET'])
@module.route('/api/v1/expert/protocol/scheme_measure/<specify>/', methods=['GET'])
@module.route('/api/v1/expert/protocol/scheme_measure/<specify>/<int:parent_id>/', methods=['GET'])
@api_method
def api_v1_expert_scheme_measure_get(item_id=None, specify=None, parent_id=None):
    mng = get_manager('ExpertSchemeMeasure')
    if specify == 'new':
        item = mng.create(parent_id=parent_id)
        return {
            'item': mng.represent(item)
        }
    elif specify == 'by_scheme':
        return {
            'items': map(mng.represent, mng.get_list(scheme_id=parent_id))
        }
    else:
        item = mng.get_by_id(item_id)
        return {
            'item': mng.represent(item)
        }


@module.route('/api/v1/expert/protocol/scheme_measure/', methods=['POST'])
@module.route('/api/v1/expert/protocol/scheme_measure/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_expert_scheme_measure_post(item_id=None):
    mng = get_manager('ExpertSchemeMeasure')
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/expert/protocol/scheme_measure/', methods=['DELETE'])
@api_method
def api_v1_expert_scheme_measure_delete():
    raise NotImplementedError


@module.route('/api/v1/expert/protocol/measure_schedule/<int:item_id>/', methods=['GET'])
@module.route('/api/v1/expert/protocol/measure_schedule/<specify>/', methods=['GET'])
@module.route('/api/v1/expert/protocol/measure_schedule/<specify>/<int:parent_id>/', methods=['GET'])
@api_method
def api_v1_expert_measure_schedule_get(item_id=None, specify=None, parent_id=None):
    mng = get_manager('MeasureSchedule')
    if specify == 'new':
        item = mng.create(parent_id=parent_id)
        return {
            'item': mng.represent(item)
        }
    else:
        item = mng.get_by_id(item_id)
        return {
            'item': mng.represent(item)
        }