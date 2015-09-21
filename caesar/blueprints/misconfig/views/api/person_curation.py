# -*- coding: utf-8 -*-

from flask import request

from nemesis.lib.apiutils import api_method, ApiException
from nemesis.lib.utils import safe_bool
from blueprints.misconfig.lib.data_management.factory import get_manager
from blueprints.misconfig.app import module


@module.route('/api/v1/person_curation_level/list/')
@api_method
def api_v1_person_curation_level_list_get():
    mng = get_manager('PersonCuration')
    items = mng.get_list()
    return {
        'items': map(mng.represent, items)
    }