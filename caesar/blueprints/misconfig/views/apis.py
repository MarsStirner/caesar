# -*- coding: utf-8 -*-

from flask import request, abort

from nemesis.systemwide import db
from nemesis.lib.apiutils import api_method, ApiException
from nemesis.models.exists import QuotaCatalog, QuotaType, VMPQuotaDetails
from nemesis.lib.utils import safe_bool, safe_int

from ..app import module
from ..lib.data import worker, WorkerException
from ..lib.data_management.factory import get_manager, all_rbs, get_grouped_refbooks


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
        order=db.desc(VMPQuotaDetails.id))


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
        'supported_rbs': get_grouped_refbooks()
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


@module.route('/api/v1/org/', methods=['GET'])
@module.route('/api/v1/org/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_org_get(item_id=None):
    with_curations = request.args.get('with_curations', False)
    mng = get_manager('Organisation', with_curations=with_curations)
    if item_id:
        item = mng.get_by_id(item_id)
        return {
            'item': mng.represent(item)
        }
    return {
        'items': map(mng.represent, mng.get_list())
    }


@module.route('/api/v1/org/new/', methods=['GET'])
@api_method
def api_v1_org_get_new():
    mng = get_manager('Organisation')
    item = mng.create()
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/org/', methods=['POST'])
@module.route('/api/v1/org/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_org_post(item_id=None):
    with_curations = request.args.get('with_curations', False)
    mng = get_manager('Organisation', with_curations=with_curations)
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/org/', methods=['DELETE'])
@module.route('/api/v1/org/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_org_delete(item_id=None):
    mng = get_manager('Organisation')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/org/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_org_undelete(item_id):
    mng = get_manager('Organisation')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/org/')
@module.route('/api/v1/org/<int:org_id>/curation/new/')
@api_method
def api_v1_org_curation_get_new(org_id=None):
    if not org_id:
        raise ApiException(404, u'`org_id` required')
    mng = get_manager('OrganisationCuration')
    item = mng.create(parent_id=org_id)
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/org_birth_care_level/', methods=['GET'])
@module.route('/api/v1/org_birth_care_level/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_org_birth_care_level_get(item_id=None):
    with_orgs = request.args.get('with_orgs', False)
    with_deleted = request.args.get('with_deleted', False)
    mng = get_manager('OrganisationBirthCareLevel', with_orgs=with_orgs)
    if item_id:
        item = mng.get_by_id(item_id)
        return {
            'item': mng.represent(item)
        }
    return {
        'items': map(mng.represent, mng.get_list(
            order={
                'idx': 'asc'
            },
            with_deleted=with_deleted
        ))
    }


@module.route('/api/v1/org_birth_care_level/new/', methods=['GET'])
@api_method
def api_v1_org_birth_care_level_get_new():
    mng = get_manager('OrganisationBirthCareLevel')
    item = mng.create()
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/org_birth_care_level/', methods=['POST'])
@module.route('/api/v1/org_birth_care_level/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_org_birth_care_level_post(item_id=None):
    with_orgs = request.args.get('with_orgs', False)
    mng = get_manager('OrganisationBirthCareLevel', with_orgs=with_orgs)
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/org_birth_care_level/', methods=['DELETE'])
@module.route('/api/v1/org_birth_care_level/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_org_birth_care_level_delete(item_id=None):
    mng = get_manager('OrganisationBirthCareLevel')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/org_birth_care_level/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_org_birth_care_level_undelete(item_id):
    mng = get_manager('OrganisationBirthCareLevel')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/org_birth_care_level/')
@module.route('/api/v1/org_birth_care_level/<int:obcl_id>/orgs/')
@api_method
def api_v1_obcl_orgs_get(obcl_id=None):
    if not obcl_id:
        raise ApiException(404, u'`obcl_id` required')
    mng = get_manager('Organisation_OrganisationHCL')
    org_obcl = mng.get_by_obcl_id(obcl_id)
    return {
        'items': map(mng.represent, org_obcl)
    }


@module.route('/api/v1/org_birth_care_level/')
@module.route('/api/v1/org_birth_care_level/<int:obcl_id>/orgs/new/')
@api_method
def api_v1_obcl_orgs_get_new(obcl_id=None):
    if not obcl_id:
        raise ApiException(404, u'`obcl_id` required')
    org_id = request.args.get('org_id')
    mng = get_manager('Organisation_OrganisationHCL')
    item = mng.create(data={
        'org_id': org_id
    }, parent_id=obcl_id)
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/person/', methods=['GET'])
@module.route('/api/v1/person/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_person_get(item_id=None):
    with_curations = request.args.get('with_curations', False)
    mng = get_manager('Person', with_curations=with_curations)
    if item_id:
        item = mng.get_by_id(item_id)
        return {
            'item': mng.represent(item)
        }
    return {
        'items': map(mng.represent, mng.get_list())
    }


@module.route('/api/v1/person/new/', methods=['GET'])
@api_method
def api_v1_person_get_new():
    raise NotImplementedError()
    mng = get_manager('Person')
    item = mng.create()
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/person/', methods=['POST'])
@module.route('/api/v1/person/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_person_post(item_id=None):
    with_curations = request.args.get('with_curations', False)
    mng = get_manager('Person', with_curations=with_curations)
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/person/', methods=['DELETE'])
@module.route('/api/v1/person/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_person_delete(item_id=None):
    raise NotImplementedError()
    mng = get_manager('Person')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/person/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_person_undelete(item_id):
    raise NotImplementedError()
    mng = get_manager('Person')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/person_curation_level/')
@api_method
def api_v1_person_curation_level_get():
    mng = get_manager('PersonCuration')
    items = mng.get_list()
    return {
        'items': map(mng.represent, items)
    }


@module.route('/api/v1/person/person_curation_level/')
@module.route('/api/v1/person/person_curation_level/<int:person_id>/new/')
@api_method
def api_v1_person_org_curation_level_get_new(person_id=None):
    if not person_id:
        raise ApiException(404, u'`person_id` required')
    mng = get_manager('PersonCuration')
    item = mng.create(parent_id=person_id)
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/rb_perinatal_risk_rate/', methods=['GET'])
@module.route('/api/v1/rb_perinatal_risk_rate/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_rb_perinatal_risk_rate_get(item_id=None):
    mng = get_manager('rbPerinatalRiskRateWithMKBs')
    if item_id:
        item = mng.get_by_id(item_id)
        return {
            'item': mng.represent(item)
        }
    return {
        'items': map(mng.represent, mng.get_list(
            order={
                'id': 'asc'
            }
        ))
    }


@module.route('/api/v1/rb_perinatal_risk_rate/', methods=['POST'])
@module.route('/api/v1/rb_perinatal_risk_rate/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_rb_perinatal_risk_rate_post(item_id=None):
    mng = get_manager('rbPerinatalRiskRateWithMKBs')
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/rb_perinatal_risk_rate/')
@module.route('/api/v1/rb_perinatal_risk_rate/<int:prr_id>/mkbs/new/')
@api_method
def api_v1_rb_perinatal_risk_rate_get_new(prr_id=None):
    if not prr_id:
        raise ApiException(404, u'`prr_id` required')
    mng = get_manager('rbPerinatalRiskRateMkb')
    item = mng.create(parent_id=prr_id)
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/rb_pregnancy_pathology/', methods=['GET'])
@module.route('/api/v1/rb_pregnancy_pathology/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_rb_pregnancy_pathology_get(item_id=None):
    mng = get_manager('rbPregnancyPathologyWithMKBs')
    if item_id:
        item = mng.get_by_id(item_id)
        return {
            'item': mng.represent(item)
        }
    return {
        'items': map(mng.represent, mng.get_list(
            order={
                'id': 'asc'
            }
        ))
    }


@module.route('/api/v1/rb_pregnancy_pathology/', methods=['POST'])
@module.route('/api/v1/rb_pregnancy_pathology/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_rb_pregnancy_pathology_post(item_id=None):
    mng = get_manager('rbPregnancyPathologyWithMKBs')
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/rb_pregnancy_pathology/')
@module.route('/api/v1/rb_pregnancy_pathology/<int:pp_id>/mkbs/new/')
@api_method
def api_v1_rb_pregnancy_pathology_get_new(pp_id=None):
    if not pp_id:
        raise ApiException(404, u'`pregnancy_pathology_id` required')
    mng = get_manager('rbPregnancyPathologyMkb')
    item = mng.create(parent_id=pp_id)
    return {
        'item': mng.represent(item)
    }