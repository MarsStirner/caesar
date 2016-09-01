# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool
from caesar.blueprints.misconfig.lib.data_management.factory import get_manager
from caesar.blueprints.misconfig.app import module


@module.route('/api/v1/expert/protocol/', methods=['GET'])
@module.route('/api/v1/expert/protocol/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_expert_protocol_get(item_id=None):
    get_new = safe_bool(request.args.get('new', False))
    with_schemes = safe_bool(request.args.get('with_schemes', False))
    mng = get_manager('ExpertProtocol', with_schemes=with_schemes)
    if get_new:
        item = mng.create()
    elif item_id:
        item = mng.get_by_id(item_id)
    else:
        raise ApiException(404, u'необходим `item_id`')
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/expert/protocol/list/', methods=['GET'])
@api_method
def api_v1_expert_protocol_list_get():
    mng = get_manager('ExpertProtocol')
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


@module.route('/api/v1/expert/protocol/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_expert_protocol_delete(item_id=None):
    mng = get_manager('ExpertProtocol')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/expert/protocol/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_expert_protocol_undelete(item_id=None):
    mng = get_manager('ExpertProtocol')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)