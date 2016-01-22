# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool
from blueprints.misconfig.lib.data_management.factory import get_manager
from blueprints.misconfig.app import module



@module.route('/api/v1/rb_service_group_assoc/', methods=['GET'])
@api_method
def api_v1_rb_service_group_assoc_get():
    get_new = safe_bool(request.args.get('new', False))
    mng = get_manager('rbServiceGroupAssoc')
    if get_new:
        item = mng.create()
    else:
        raise ApiException(404, u'Only `new` records creation supported')
    return {
        'item': mng.represent(item)
    }
