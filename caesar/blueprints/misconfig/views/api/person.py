# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method
from blueprints.misconfig.lib.data_management.factory import get_manager
from blueprints.misconfig.app import module


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

