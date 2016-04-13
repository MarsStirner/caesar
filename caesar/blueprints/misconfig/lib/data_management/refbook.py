# -*- coding: utf-8 -*-
from blueprints.misconfig.lib.data_management.base import BaseModelManager, FieldConverter, FCType, represent_model
from nemesis.lib.utils import safe_int, safe_unicode
from nemesis.models.exists import rbTreatment, MKB, rbResult
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
                'treatmentType', (self.handle_onetomany_nonedit, ),
                'treatment_type',
                model_manager=self._rbtt_mng)
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
                'prr_mkbs', (self.handle_manytomany_assoc_obj, ),
                'prr_mkbs', (self.represent_model, ),
                model_manager=self._prr_mkb_mng
            )
        ]
        super(RbPerinatalRRModelManager, self).__init__(rbPerinatalRiskRate, fields)


class RbPRRMKBModelManager(BaseModelManager):
    def __init__(self):
        self._mkb_mng = self.get_manager('MKB')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'riskRate_id', safe_int, 'risk_rate_id'),
            FieldConverter(
                FCType.relation,
                'mkb', (self.handle_onetomany_nonedit, ),
                'mkb',
                model_manager=self._mkb_mng
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
                'pp_mkbs', (self.handle_manytomany_assoc_obj, ),
                'pp_mkbs', (self.represent_model, ),
                model_manager=self._pp_mkb_mng
            )
        ]
        super(RbPregnancyPathologyModelManager, self).__init__(rbPregnancyPathology, fields)


class RbPregnancyPathologyMKBModelManager(BaseModelManager):
    def __init__(self):
        self._mkb_mng = self.get_manager('MKB')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'pathology_id', safe_int, 'pathology_id'),
            FieldConverter(
                FCType.relation,
                'mkb', (self.handle_onetomany_nonedit, ),
                'mkb',
                model_manager=self._mkb_mng
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


class RbResultModelManager(SimpleRefBookModelManager):
    def __init__(self):
        self._rbetp_mng = self.get_manager('rbEventTypePurpose')
        super(RbResultModelManager, self).__init__(rbResult, [
            FieldConverter(
                FCType.relation,
                'eventPurpose', (self.handle_onetomany_nonedit, ),
                'event_purpose',
                model_manager=self._rbetp_mng)
        ])
