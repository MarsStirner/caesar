# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool
from blueprints.misconfig.lib.data_management.factory import get_manager
from blueprints.misconfig.app import module
from nemesis.models.person import Person
from sqlalchemy.orm import joinedload


@module.route('/api/v1/person/', methods=['GET'])
@module.route('/api/v1/person/<int:item_id>/', methods=['GET'])
@api_method
def api_v1_person_get(item_id=None):
    get_new = safe_bool(request.args.get('new', False))
    with_curations = safe_bool(request.args.get('with_curations', False))
    mng = get_manager('Person', with_curations=with_curations)
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
    with_curations = safe_bool(request.args.get('with_curations', False))
    mng = get_manager('Person', with_curations=with_curations)
    return {
        'items': map(
            mng.represent,
            mng.get_list(options=[
                joinedload(Person.user_profiles),
                joinedload(Person.organisation),
                joinedload(Person.post),
                joinedload(Person.org_structure),
            ])
        )
    }


@module.route('/api/v1/person/', methods=['POST'])
@module.route('/api/v1/person/<int:item_id>/', methods=['POST'])
@api_method
def api_v1_person_post(item_id=None):
    with_curations = safe_bool(request.args.get('with_curations', False))
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

