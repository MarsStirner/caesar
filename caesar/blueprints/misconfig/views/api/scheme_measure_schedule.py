# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool, safe_int
from caesar.blueprints.misconfig.lib.data_management.factory import get_manager
from caesar.blueprints.misconfig.app import module


@module.route('/api/v1/expert/protocol/scheme_measure/', methods=['GET'])
@module.route('/api/v1/expert/protocol/scheme_measure/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_expert_scheme_measure_get(item_id=None):
    mng = get_manager('ExpertSchemeMeasure')
    get_new = safe_bool(request.args.get('new', False))
    scheme_id = safe_int(request.args.get('scheme_id'))
    if get_new:
        item = mng.create(parent_id=scheme_id)
    elif item_id:
        item = mng.get_by_id(item_id)
    else:
        raise ApiException(404, u'`item_id` required')
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/expert/protocol/scheme_measure/list/', methods=['GET'])
@api_method
def api_v1_expert_scheme_measure_list_get():
    mng = get_manager('ExpertSchemeMeasure')
    scheme_id = safe_int(request.args.get('scheme_id'))
    return {
        'items': map(mng.represent, mng.get_list(scheme_id=scheme_id))
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


@module.route('/api/v1/expert/protocol/scheme_measure/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_expert_scheme_measure_delete(item_id=None):
    mng = get_manager('ExpertSchemeMeasure')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/expert/protocol/scheme_measure/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_expert_scheme_measure_undelete(item_id=None):
    mng = get_manager('ExpertSchemeMeasure')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)