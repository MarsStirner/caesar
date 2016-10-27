# -*- coding: utf-8 -*-
from sqlalchemy import or_

from .base import BaseModelManager, FieldConverter, FCType, represent_model
from nemesis.models.organisation import (Organisation, OrganisationBirthCareLevel,
    Organisation_OrganisationBCLAssoc, OrganisationCurationAssoc)
from nemesis.models.exists import OrgStructure
from nemesis.lib.utils import (get_new_uuid, safe_int, safe_unicode, safe_traverse, safe_bool,
       get_max_item_attribute_value, safe_hex_color, format_hex_color)
from nemesis.systemwide import db


class OrganisationModelManager(BaseModelManager):
    def __init__(self, with_curators=False):
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'fullName', safe_unicode, 'full_name'),
            FieldConverter(FCType.basic, 'shortName', safe_unicode, 'short_name'),
            FieldConverter(FCType.basic, 'title', safe_unicode, 'title'),
            FieldConverter(FCType.basic, 'infisCode', safe_unicode, 'infis'),
            FieldConverter(FCType.basic, 'isInsurer', safe_int, 'is_insurer', safe_bool),
            FieldConverter(FCType.basic, 'isHospital', safe_int, 'is_hospital', safe_bool),
            FieldConverter(FCType.basic, 'isLPU', safe_int, 'is_lpu', safe_bool),
            FieldConverter(FCType.basic, 'isStationary', safe_int, 'is_stationary', safe_bool),
            FieldConverter(FCType.basic, 'Address', safe_unicode, 'address'),
            FieldConverter(FCType.basic, 'phone', safe_unicode, 'phone'),
            FieldConverter(FCType.relation, 'kladr_locality', self.handle_kladr_locality, 'kladr_locality'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
        ]
        if with_curators:
            self._person_cur_mng = self.get_manager('PersonCuration')
            fields.append(FieldConverter(
                FCType.relation,
                'org_curators', (self.handle_manytomany, ),
                'org_curators', (self.represent_model, ),
                self._person_cur_mng
            ))
        super(OrganisationModelManager, self).__init__(Organisation, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(OrganisationModelManager, self).create(data)
        if item.title is None:
            item.title = ''
        if item.Address is None:
            item.Address = ''
        if item.phone is None:
            item.phone = ''
        item.obsoleteInfisCode = ''
        item.OKVED = ''
        item.INN = ''
        item.KPP = ''
        item.OGRN = ''
        item.OKATO = ''
        item.OKPF_code = ''
        item.OKFS_code = 0
        item.OKPO = ''
        item.FSS = ''
        item.region = ''
        item.chief = ''
        item.accountant = ''
        item.notes = ''
        item.miacCode = ''
        item.obsoleteInfisCode = ''
        item.obsoleteInfisCode = ''
        item.obsoleteInfisCode = ''
        item.obsoleteInfisCode = ''
        item.uuid = get_new_uuid()
        return item

    def get_list(self, **kwargs):
        where = []
        if kwargs.get('is_stationary'):
            where.append(self._model.isStationary.__eq__(1))
        if kwargs.get('is_lpu'):
            where.append(self._model.isLPU.__eq__(1))
        return super(OrganisationModelManager, self).get_list(where=where)

    def handle_kladr_locality(self, json_data, parent_obj=None):
        return safe_traverse(json_data, 'code', default='')

    def filter_(self, **kwargs):
        query = self._model.query
        if 'name' in kwargs:
            query_str = u'%{0}%'.format(safe_unicode(kwargs['name']))
            query = query.filter(
                or_(Organisation.shortName.like(query_str),
                    Organisation.fullName.like(query_str))
            )
        if 'infis' in kwargs:
            query = query.filter(Organisation.infisCode == safe_unicode(kwargs['infis']))
        if 'is_lpu' in kwargs:
            query = query.filter(Organisation.isLPU == safe_int(safe_bool(kwargs['is_lpu'])))
        if 'is_stationary' in kwargs:
            query = query.filter(Organisation.isStationary == safe_int(safe_bool(kwargs['is_stationary'])))
        if 'is_insurer' in kwargs:
            query = query.filter(Organisation.isInsurer == safe_int(safe_bool(kwargs['is_insurer'])))
        return query


class OrganisationBCLModelManager(BaseModelManager):
    def __init__(self, with_orgs=False):
        self._prr_mng = self.get_manager('rbPerinatalRiskRate')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'description', safe_unicode, 'description'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            FieldConverter(FCType.basic, 'idx', safe_int, 'idx'),
            FieldConverter(
                FCType.relation,
                'perinatal_risk_rate', (self.handle_onetomany_nonedit, ),
                'perinatal_risk_rate',
                model_manager=self._prr_mng
            ),
            FieldConverter(FCType.basic, 'color', safe_hex_color, 'color', format_hex_color),
        ]
        if with_orgs:
            self._org_mng = self.get_manager('Organisation')
            fields.append(FieldConverter(
                FCType.relation,
                'orgs', (self.handle_manytomany, ),
                'orgs', (self.represent_model, ),
                self._org_mng
            ))
        super(OrganisationBCLModelManager, self).__init__(OrganisationBirthCareLevel, fields)

    def get_list(self, **kwargs):
        where = []
        order = []
        if not kwargs.get('with_deleted'):
            where.append(self._model.deleted.__eq__(0))
        if 'order' in kwargs:
            korder = kwargs['order']
            if 'idx' in korder:
                order.append(self._model.idx.desc() if korder['idx'] == 'desc' else self._model.idx)
        return super(OrganisationBCLModelManager, self).get_list(where=where, order=order)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(OrganisationBCLModelManager, self).create(data)
        max_idx = get_max_item_attribute_value(self._model, self._model.idx)
        item.idx = max_idx + 1 if max_idx is not None else 1
        return item


class OrgStructureModelManager(BaseModelManager):
    def __init__(self):
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'organisation_id', safe_int, 'organisation_id'),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
        ]
        super(OrgStructureModelManager, self).__init__(OrgStructure, fields)