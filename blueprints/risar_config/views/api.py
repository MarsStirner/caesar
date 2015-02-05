# -*- coding: utf-8 -*-
from ..app import module
from ..utils import api_db_method, Session
from ..models.basic import Organisation, MKB

__author__ = 'viruzzz-kun'


@module.route('/api/routing.json')
@api_db_method()
def api_routing(session):
    return [
        {
            'org': org,
            'diagnoses': [],
        }
        for org in session.query(Organisation).filter(Organisation.isHospital == 1)
    ]