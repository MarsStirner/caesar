# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method
from nemesis.models.exists import ContractTariff
from ...lib.data_management.factory import get_manager
from ...app import module


@module.route('/api/v1/price/', methods=['GET'])
@module.route('/api/v1/price/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_price_get(item_id=None):
    mng = get_manager('Price')
    if item_id:
        item = mng.get_by_id(item_id)
        return {
            'item': mng.represent(item)
        }
    return {
        'items': map(mng.represent, mng.get_list())
    }


@module.route('/api/v1/price/new/', methods=['GET'])
@api_method
def api_v1_price_get_new():
    mng = get_manager('Price')
    item = mng.create()
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/price/', methods=['POST'])
@module.route('/api/v1/price/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_price_post(item_id=None):
    with_curations = request.args.get('with_curations', False)
    mng = get_manager('Price', with_curations=with_curations)
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/price/', methods=['DELETE'])
@module.route('/api/v1/price/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_price_delete(item_id=None):
    mng = get_manager('Price')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/price/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_price_undelete(item_id):
    mng = get_manager('Price')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/tariff/', methods=['GET'])
@module.route('/api/v1/tariff/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_tariff_get(item_id=None):
    mng = get_manager('Tariff')
    if item_id:
        item = mng.get_by_id(item_id)
        return {
            'item': mng.represent(item)
        }
    return {
        'items': map(mng.represent, mng.get_list(where=[ContractTariff.priceList_id == int(request.args.get('price_id'))]))
    }


@module.route('/api/v1/tariff/new/', methods=['GET'])
@api_method
def api_v1_tariff_get_new():
    mng = get_manager('Tariff')
    item = mng.create()
    return {
        'item': mng.represent(item)
    }


@module.route('/api/v1/tariff/', methods=['POST'])
@module.route('/api/v1/tariff/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_tariff_post(item_id=None):
    with_curations = request.args.get('with_curations', False)
    mng = get_manager('Tariff', with_curations=with_curations)
    data = request.get_json()

    if item_id:
        item = mng.update(item_id, data)
    else:
        item = mng.create(data)
    mng.store(item)
    return mng.represent(item)


@module.route('/api/v1/tariff/', methods=['DELETE'])
@module.route('/api/v1/tariff/<int:item_id>/', methods=['DELETE'])
@api_method
def api_v1_tariff_delete(item_id=None):
    mng = get_manager('Tariff')
    item = mng.delete(item_id)
    mng.store()
    return mng.represent(item)


@module.route('/api/v1/tariff/<int:item_id>/undelete/', methods=['POST'])
@api_method
def api_v1_tariff_undelete(item_id):
    mng = get_manager('Tariff')
    item = mng.undelete(item_id)
    mng.store()
    return mng.represent(item)

