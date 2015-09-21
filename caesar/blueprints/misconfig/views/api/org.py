# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool
from blueprints.misconfig.lib.data_management.factory import get_manager
from blueprints.misconfig.app import module


@module.route('/api/v1/org/', methods=['GET'])
@module.route('/api/v1/org/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_org_get(item_id=None):
    get_new = safe_bool(request.args.get('new', False))
    with_curators = safe_bool(request.args.get('with_curators', False))
    mng = get_manager('Organisation', with_curators=with_curators)
    if get_new:
        item = mng.create()
    elif item_id:
        item = mng.get_by_id(item_id)
    else:
        raise ApiException(404, u'`item_id` required')
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/org/list/', methods=['GET'])
@api_method
def api_v1_org_list_get():
    stationary = safe_bool(request.args.get('stationary', False))
    with_curators = safe_bool(request.args.get('with_curators', False))
    mng = get_manager('Organisation', with_curators=with_curators)
    return {
        'items': map(mng.represent, mng.get_list(stationary=stationary))
    }


@module.route('/api/v1/org/', methods=['POST'])
@module.route('/api/v1/org/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_org_post(item_id=None):
    with_curators = safe_bool(request.args.get('with_curators', False))
    mng = get_manager('Organisation', with_curators=with_curators)
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