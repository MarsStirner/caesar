# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool
from caesar.blueprints.misconfig.lib.data_management.factory import get_manager
from caesar.blueprints.misconfig.app import module


@module.route('/api/v1/org_birth_care_level/', methods=['GET'])
@module.route('/api/v1/org_birth_care_level/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_org_birth_care_level_get(item_id=None):
    get_new = safe_bool(request.args.get('new', False))
    with_orgs = safe_bool(request.args.get('with_orgs', False))
    mng = get_manager('OrganisationBirthCareLevel', with_orgs=with_orgs)
    if get_new:
        item = mng.create()
    elif item_id:
        item = mng.get_by_id(item_id)
    else:
        raise ApiException(404, u'необходим `item_id`')
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/org_birth_care_level/list/', methods=['GET'])
@api_method
def api_v1_org_birth_care_level_list_get():
    with_orgs = safe_bool(request.args.get('with_orgs', False))
    with_deleted = safe_bool(request.args.get('with_deleted', False))
    mng = get_manager('OrganisationBirthCareLevel', with_orgs=with_orgs)
    return {
        'items': map(mng.represent, mng.get_list(
            order={
                'idx': 'asc'
            },
            with_deleted=with_deleted
        ))
    }

@module.route('/api/v1/org_birth_care_level/', methods=['POST'])
@module.route('/api/v1/org_birth_care_level/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_org_birth_care_level_post(item_id=None):
    with_orgs = safe_bool(request.args.get('with_orgs', False))
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