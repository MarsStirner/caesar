# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool
from blueprints.misconfig.lib.data_management.factory import get_manager
from blueprints.misconfig.app import module


@module.route('/api/v1/person/', methods=['GET'])
@module.route('/api/v1/person/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_person_get(item_id=None):
    get_new = safe_bool(request.args.get('new', False))
    with_curations = safe_bool(request.args.get('with_curations', False))
    with_profiles = safe_bool(request.args.get('with_profiles', False))
    mng = get_manager('Person', with_curations=with_curations, with_profiles=with_profiles)
    if get_new:
        item = mng.create()
    elif item_id:
        item = mng.get_by_id(item_id)
    else:
        raise ApiException(404, u'`item_id` required')
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/person/list/', methods=['GET'])
@api_method
def api_v1_person_list_get():
    args = request.args.to_dict()
    if request.json:
        args.update(request.json)
    with_curations = safe_bool(request.args.get('with_curations', False))
    with_profiles = safe_bool(request.args.get('with_profiles', False))
    paginate = safe_bool(args.get('paginate', False))
    mng = get_manager('Person', with_curations=with_curations, with_profiles=with_profiles)
    if paginate:
        data = mng.get_paginated_data(**args)
        return {
            'count': data.total,
            'total_pages': data.pages,
            'items': [
                mng.represent(item) for item in data.items
            ]
        }
    else:
        data = mng.get_list(**args)
        return {
            'items': map(mng.represent, data)
        }


@module.route('/api/v1/person/', methods=['POST'])
@module.route('/api/v1/person/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_person_post(item_id=None):
    with_curations = safe_bool(request.args.get('with_curations', False))
    with_profiles = safe_bool(request.args.get('with_profiles', False))
    mng = get_manager('Person', with_curations=with_curations, with_profiles=with_profiles)
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
    mng = get_manager('Person')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/person/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_person_undelete(item_id):
    mng = get_manager('Person')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)

