# -*- coding: utf-8 -*-
from blueprints.misconfig.lib.data_management.base import BaseModelManager, FieldConverter, FCType, represent_model
from nemesis.lib.utils import safe_int, safe_unicode
from nemesis.models.exists import rbTreatment, MKB
from nemesis.models.risar import (rbPerinatalRiskRate, rbPerinatalRiskRateMkbAssoc, rbPregnancyPathology,
    rbPregnancyPathologyMkbAssoc)
from nemesis.systemwide import db


class SimpleRefBookModelManager(BaseModelManager):
    def __init__(self, model, additional_fields=None):
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
        ]
        if hasattr(model, 'deleted'):
            fields.append(
                FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            )
        if isinstance(additional_fields, list):
            fields.extend(additional_fields)
        super(SimpleRefBookModelManager, self).__init__(model, fields)


class RbTreatmentModelManager(SimpleRefBookModelManager):
    def __init__(self):
        self._rbtt_mng = self.get_manager('rbTreatmentType')
        super(RbTreatmentModelManager, self).__init__(rbTreatment, [
            FieldConverter(
                FCType.relation,
                'treatmentType', lambda val, par: self.handle_onetomany_nonedit(self._rbtt_mng, val, par),
                'treatment_type')
        ])


class RbPerinatalRRModelManager(BaseModelManager):
    def __init__(self):
        self._prr_mkb_mng = RbPRRMKBModelManager()
        fields = [
            FieldConverter(FCType.basic_repr, 'id', None, 'id'),
            FieldConverter(FCType.basic_repr, 'code', None, 'code'),
            FieldConverter(FCType.basic_repr, 'name', None, 'name'),
            FieldConverter(
                FCType.relation,
                'prr_mkbs', self.handle_mkbs,
                'prr_mkbs', lambda val: represent_model(val, self._prr_mkb_mng)
            )
        ]
        super(RbPerinatalRRModelManager, self).__init__(rbPerinatalRiskRate, fields)

    def handle_mkbs(self, mkb_list, parent_obj):
        if mkb_list is None:
            return []
        result = []
        for item_data in mkb_list:
            item_id = item_data['id']
            if item_id:
                item = self._prr_mkb_mng.update(item_id, item_data, parent_obj)
            else:
                item = self._prr_mkb_mng.create(item_data, None, parent_obj)
            result.append(item)

        # deletion
        for prr_mkb in parent_obj.prr_mkbs:
            if prr_mkb not in result:
                db.session.delete(prr_mkb)
        return result


class RbPRRMKBModelManager(BaseModelManager):
    def __init__(self):
        self._mkb_mng = self.get_manager('MKB')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'riskRate_id', safe_int, 'risk_rate_id'),
            FieldConverter(
                FCType.relation,
                'mkb', lambda val, par: self.handle_onetomany_nonedit(self._mkb_mng, val),
                'mkb'
            )
        ]
        super(RbPRRMKBModelManager, self).__init__(rbPerinatalRiskRateMkbAssoc, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(RbPRRMKBModelManager, self).create(data, parent_id, parent_obj)
        item.riskRate_id = data.get('risk_rate_id') if data is not None else parent_id
        return item


class RbPregnancyPathologyModelManager(BaseModelManager):
    def __init__(self):
        self._pp_mkb_mng = RbPregnancyPathologyMKBModelManager()
        fields = [
            FieldConverter(FCType.basic_repr, 'id', None, 'id'),
            FieldConverter(FCType.basic_repr, 'code', None, 'code'),
            FieldConverter(FCType.basic_repr, 'name', None, 'name'),
            FieldConverter(
                FCType.relation,
                'pp_mkbs', self.handle_mkbs,
                'pp_mkbs', lambda val: represent_model(val, self._pp_mkb_mng)
            )
        ]
        super(RbPregnancyPathologyModelManager, self).__init__(rbPregnancyPathology, fields)

    def handle_mkbs(self, mkb_list, parent_obj):
        if mkb_list is None:
            return []
        result = []
        for item_data in mkb_list:
            item_id = item_data['id']
            if item_id:
                item = self._pp_mkb_mng.update(item_id, item_data, parent_obj)
            else:
                item = self._pp_mkb_mng.create(item_data, None, parent_obj)
            result.append(item)

        # deletion
        for pp_mkb in parent_obj.pp_mkbs:
            if pp_mkb not in result:
                db.session.delete(pp_mkb)
        return result


class RbPregnancyPathologyMKBModelManager(BaseModelManager):
    def __init__(self):
        self._mkb_mng = self.get_manager('MKB')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'pathology_id', safe_int, 'pathology_id'),
            FieldConverter(
                FCType.relation,
                'mkb', lambda val, par: self.handle_onetomany_nonedit(self._mkb_mng, val),
                'mkb'
            )
        ]
        super(RbPregnancyPathologyMKBModelManager, self).__init__(rbPregnancyPathologyMkbAssoc, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(RbPregnancyPathologyMKBModelManager, self).create(data, parent_id, parent_obj)
        item.pathology_id = data.get('pathology_id') if data is not None else parent_id
        return item


class MKBModelManager(BaseModelManager):
    def __init__(self,):
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'DiagID', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'DiagName', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted')
        ]
        super(MKBModelManager, self).__init__(MKB, fields)