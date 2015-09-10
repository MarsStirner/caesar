# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool, safe_int
from blueprints.misconfig.lib.data_management.factory import get_manager
from blueprints.misconfig.app import module


@module.route('/api/v1/expert/protocol/scheme/', methods=['GET'])
@module.route('/api/v1/expert/protocol/scheme/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_expert_scheme_get(item_id=None):
    get_new = safe_bool(request.args.get('new', False))
    protocol_id = safe_int(request.args.get('protocol_id'))
    # with_schemes = request.args.get('with_schemes', False)
    mng = get_manager('ExpertScheme')
    if get_new:
        item = mng.create(parent_id=protocol_id)
    elif item_id:
        item = mng.get_by_id(item_id)
    else:
        raise ApiException(404, u'`item_id` required')
    return {
        'item': mng.represent(item)
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


@module.route('/api/v1/expert/protocol/scheme/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_expert_scheme_delete(item_id=None):
    mng = get_manager('ExpertScheme')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/expert/protocol/scheme/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_expert_scheme_undelete(item_id=None):
    mng = get_manager('ExpertScheme')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)