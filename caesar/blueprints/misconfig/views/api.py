# -*- coding: utf-8 -*-
from ..app import module
from nemesis.lib.utils import api_method
from nemesis.systemwide import db
from nemesis.models.exists import QuotaCatalog


@module.route('/api/v1/quota_catalog', methods=['GET'])
@api_method
def api_v1_quota_catalog_get():
    return [
        {'id': catalog.id,
         'finance_id': catalog.finance_id,
         'create_datetime': catalog.createDatetime,
         'create_person_id': catalog.createPerson_id,
         'beg_date': catalog.begDate,
         'end_date': catalog.endDate,
         'catalog_number': catalog.catalogNumber,
         'document_date': catalog.documentDate,
         'document_number': catalog.documentNumber,
         'document_corresp': catalog.documentCorresp,
         'comment': catalog.comment
         }
        for catalog in QuotaCatalog.query.order_by(QuotaCatalog.begDate).all()
    ]

