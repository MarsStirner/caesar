# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool
from caesar.blueprints.misconfig.lib.data_management.factory import get_manager
from caesar.blueprints.misconfig.app import module


@module.route('/api/v1/print_template/', methods=['GET'])
@module.route('/api/v1/print_template/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_print_template_get(item_id=None):
    get_new = safe_bool(request.args.get('new', False))
    mng = get_manager('rbPrintTemplate')
    if get_new:
        item = mng.create()
    elif item_id:
        item = mng.get_by_id(item_id)
    else:
        raise ApiException(404, u'`item_id` required')
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/print_template/list/', methods=['GET'])
@api_method
def api_v1_print_template_list_get():
    mng = get_manager('rbPrintTemplate')
    return {
        'items': map(mng.represent, mng.get_list())
    }


@module.route('/api/v1/print_template/', methods=['POST'])
@module.route('/api/v1/print_template/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_print_template_post(item_id=None):
    mng = get_manager('rbPrintTemplate')
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/print_template/', methods=['DELETE'])
@module.route('/api/v1/print_template/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_print_template_delete(item_id=None):
    mng = get_manager('rbPrintTemplate')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/print_template/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_print_template_undelete(item_id):
    mng = get_manager('rbPrintTemplate')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)