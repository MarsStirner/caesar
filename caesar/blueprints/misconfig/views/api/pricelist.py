# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool
from caesar.blueprints.misconfig.lib.data_management.factory import get_manager
from caesar.blueprints.misconfig.app import module


@module.route('/api/v1/pricelist/', methods=['GET'])
@module.route('/api/v1/pricelist/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_pricelist_get(item_id=None):
    get_new = safe_bool(request.args.get('new', False))
    mng = get_manager('PriceList')
    if get_new:
        item = mng.create()
    elif item_id:
        item = mng.get_by_id(item_id)
    else:
        raise ApiException(404, u'`item_id` required')
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/pricelist/list/', methods=['GET'])
@api_method
def api_v1_pricelist_list_get():
    mng = get_manager('PriceList')
    return {
        'items': map(mng.represent, mng.get_list())
    }


@module.route('/api/v1/pricelist/', methods=['POST'])
@module.route('/api/v1/pricelist/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_pricelist_post(item_id=None):
    mng = get_manager('PriceList')
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/pricelist/', methods=['DELETE'])
@module.route('/api/v1/pricelist/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_pricelist_delete(item_id=None):
    mng = get_manager('PriceList')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/pricelist/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_pricelist_undelete(item_id):
    mng = get_manager('PriceList')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/pricelist/<int:pricelist_id>/item/', methods=['GET'])
@module.route('/api/v1/pricelist/<int:pricelist_id>/item/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_pricelist_item_get(pricelist_id, item_id=None):
    get_new = safe_bool(request.args.get('new', False))
    mng = get_manager('PriceListItem')
    if get_new:
        item = mng.create(parent_id=pricelist_id)
    elif item_id:
        item = mng.get_by_id(item_id)
    else:
        raise ApiException(404, u'`item_id` required')
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/pricelist/<int:pricelist_id>/item/list/', methods=['GET'])
@api_method
def api_v1_pricelist_item_list_get(pricelist_id):
    args = request.args.to_dict()
    if request.json:
        args.update(request.json)
    paginate = safe_bool(args.get('paginate', True))
    mng = get_manager('PriceListItem')
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


@module.route('/api/v1/pricelist/<int:pricelist_id>/item/', methods=['POST'])
@module.route('/api/v1/pricelist/<int:pricelist_id>/item/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_pricelist_item_post(pricelist_id, item_id=None):
    mng = get_manager('PriceListItem')
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data, pricelist_id)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/pricelist/<int:pricelist_id>/item/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_pricelist_item_delete(pricelist_id, item_id=None):
    mng = get_manager('PriceListItem')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/pricelist/<int:pricelist_id>/item/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_pricelist_item_undelete(pricelist_id, item_id):
    mng = get_manager('PriceListItem')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)

