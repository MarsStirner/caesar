# -*- coding: utf-8 -*-
from .base import BaseModelManager, FieldConverter, FCType, represent_model
from nemesis.models.organisation import (Organisation, OrganisationBirthCareLevel,
    Organisation_OrganisationBCLAssoc, OrganisationCurationAssoc)
from nemesis.lib.utils import (get_new_uuid, safe_int, safe_unicode, safe_traverse, safe_bool,
       get_max_item_attribute_value)
from nemesis.systemwide import db


class OrganisationModelManager(BaseModelManager):
    def __init__(self, with_curations=False):
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'fullName', safe_unicode, 'full_name'),
            FieldConverter(FCType.basic, 'shortName', safe_unicode, 'short_name'),
            FieldConverter(FCType.basic, 'title', safe_unicode, 'title'),
            FieldConverter(FCType.basic, 'infisCode', safe_unicode, 'infis'),
            FieldConverter(FCType.basic, 'isInsurer', safe_int, 'is_insurer', safe_bool),
            FieldConverter(FCType.basic, 'isHospital', safe_int, 'is_hospital', safe_bool),
            FieldConverter(FCType.basic, 'Address', safe_unicode, 'address'),
            FieldConverter(FCType.basic, 'phone', safe_unicode, 'phone'),
            FieldConverter(FCType.relation, 'kladr_locality', self.handle_kladr_locality, 'kladr_locality'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
        ]
        if with_curations:
            self._org_cur_mng = self.get_manager('OrganisationCuration')
            fields.append(FieldConverter(
                FCType.relation,
                'org_curations', self.handle_org_curations,
                'org_curations', lambda val: represent_model(val, self._org_cur_mng)
            ))
        super(OrganisationModelManager, self).__init__(Organisation, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(OrganisationModelManager, self).create(data)
        item.isHospital = False
        item.isInsurer = False
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

    def handle_kladr_locality(self, json_data, parent_obj=None):
        return safe_traverse(json_data, 'code', default='')

    def handle_org_curations(self, curation_list, parent_obj):
        if curation_list is None:
            return []
        result = []
        for item_data in curation_list:
            item_id = item_data['id']
            if item_id:
                item = self._org_cur_mng.update(item_id, item_data, parent_obj)
            else:
                item = self._org_cur_mng.create(item_data, None, parent_obj)
            result.append(item)

        # deletion
        for org_cur in parent_obj.org_curations:
            if org_cur not in result:
                db.session.delete(org_cur)
        return result


class Organisation_OBCLModelManager(BaseModelManager):
    def __init__(self):
        self._org_mng = self.get_manager('Organisation')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'org_id', safe_int, 'org_id'),
            FieldConverter(FCType.basic, 'orgBCL_id', safe_int, 'obcl_id'),
            FieldConverter(
                FCType.relation,
                'organisation', lambda val, par: self.handle_onetomany_nonedit(self._org_mng, val, par),
                'organisation', lambda val: represent_model(val, self._org_mng)
            ),
        ]
        super(Organisation_OBCLModelManager, self).__init__(Organisation_OrganisationBCLAssoc, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(Organisation_OBCLModelManager, self).create(data, parent_id, parent_obj)
        item.organisation = db.session.query(Organisation).filter(Organisation.id == item.org_id).first()
        item.orgBCL_id = data.get('orgBCL_id') or parent_id
        return item


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
                'perinatal_risk_rate', lambda val, par: self.handle_onetomany_nonedit(self._prr_mng, val, par),
                'perinatal_risk_rate'
            ),
        ]
        if with_orgs:
            self._org_obcl_mng = self.get_manager('Organisation_OrganisationHCL')
            fields.append(FieldConverter(
                FCType.relation,
                'org_obcls', self.handle_org_obcls,
                'org_obcls', lambda val: represent_model(val, self._org_obcl_mng)
            ))
        super(OrganisationBCLModelManager, self).__init__(OrganisationBirthCareLevel, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(OrganisationBCLModelManager, self).create(data)
        max_idx = get_max_item_attribute_value(self._model, self._model.idx)
        item.idx = max_idx + 1 if max_idx is not None else 1
        return item

    def handle_org_obcls(self, org_obcl_list, parent_obj):
        if org_obcl_list is None:
            return []
        result = []
        for item_data in org_obcl_list:
            item_id = item_data['id']
            if item_id:
                item = self._org_obcl_mng.update(item_id, item_data, parent_obj)
            else:
                item = self._org_obcl_mng.create(item_data, None, parent_obj)
            result.append(item)

        # deletion
        for org_obcl in parent_obj.org_obcls:
            if org_obcl not in result:
                db.session.delete(org_obcl)
        return result


class OrganisationCurationModelManager(BaseModelManager):
    def __init__(self):
        self._pers_cur_mng = self.get_manager('PersonCuration')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'org_id', safe_int, 'org_id'),
            FieldConverter(FCType.basic, 'personCuration_id', safe_int, 'person_curation_id'),
            FieldConverter(
                FCType.relation,
                'person_curation', lambda val, par: self.handle_onetomany_nonedit(self._pers_cur_mng, val, par),
                'person_curation', lambda val: represent_model(val, self._pers_cur_mng)
            ),
        ]
        super(OrganisationCurationModelManager, self).__init__(OrganisationCurationAssoc, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(OrganisationCurationModelManager, self).create(data, parent_id, parent_obj)
        item.org_id = data.get('org_id') if data is not None else parent_id
        return item