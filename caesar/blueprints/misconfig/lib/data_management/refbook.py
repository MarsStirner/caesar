# -*- coding: utf-8 -*-

from sqlalchemy.orm import joinedload
from sqlalchemy import func

from blueprints.misconfig.lib.data_management.base import BaseModelManager, FieldConverter, FCType, represent_model
from nemesis.lib.utils import safe_int, safe_unicode, safe_traverse
from nemesis.lib.apiutils import ApiException
from nemesis.models.exists import rbTreatment, MKB, rbResult
from nemesis.models.risar import (rbPerinatalRiskRate, rbPerinatalRiskRateMkbAssoc, rbPregnancyPathology,
    rbPregnancyPathologyMkbAssoc, rbRadzRiskFactor, rbRadzStage, rbRadzRiskFactor_StageAssoc)
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

    def get_list(self, **kwargs):
        options = [joinedload(rbPerinatalRiskRate.prr_mkbs).joinedload('mkb')]
        return super(RbPerinatalRRModelManager, self).get_list(options=options, **kwargs)

    def validate(self, data):
        code_by_id = {}
        mkb_rates = {}
        for x in data['prr_mkbs']:
            mkb_id = x['mkb']['id']
            mkb_rates[mkb_id] = x['risk_rate_id']
            code_by_id[mkb_id] = x['mkb']['code']

        db_data = dict(db.session.query(rbPerinatalRiskRateMkbAssoc.mkb_id,
                                        func.group_concat(
                                            rbPerinatalRiskRateMkbAssoc.riskRate_id.op('SEPARATOR')(','))
                                        ).filter(
                                            rbPerinatalRiskRateMkbAssoc.mkb_id.in_(mkb_rates.keys())
                                        ).group_by(
                                            rbPerinatalRiskRateMkbAssoc.mkb_id
                                        ).all())
        if db_data:
            for mkb_id, risk_rate_id in mkb_rates.items():
                db_risk_rate = db_data.get(mkb_id)
                if db_risk_rate is not None:
                    if db_risk_rate != unicode(risk_rate_id):
                        rates = db_risk_rate.split(',')
                        words = (u"другими", u"степенями") if len(rates) > 1 else (u"другой", u"степенью")
                        error = u"Код {} уже связан с %s %s риска: \n".format(code_by_id[mkb_id]) % words
                        risk_rates = db.session.query(
                                rbPerinatalRiskRate.name
                        ).filter(
                            rbPerinatalRiskRate.id.in_(rates)
                        ).all()
                        error += ",".join([x.name for x in risk_rates])
                        raise ApiException(500, error)


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


class RbRadzRiskFactorModelManager(SimpleRefBookModelManager):
    def __init__(self):
        self._rbfg_mng = self.get_manager('rbRadzRiskFactorGroup')
        super(RbRadzRiskFactorModelManager, self).__init__(rbRadzRiskFactor, [
            FieldConverter(
                FCType.relation,
                'group', (self.handle_onetomany_nonedit, ),
                'group',
                model_manager=self._rbfg_mng)
        ])


class RbRadzStageFactorModelManager(BaseModelManager):
    def __init__(self):
        self._sfa_mng = RbRadzStageFactorAssocModelManager()
        fields = [
            FieldConverter(FCType.basic_repr, 'id', None, 'id'),
            FieldConverter(FCType.basic_repr, 'code', None, 'code'),
            FieldConverter(FCType.basic_repr, 'name', None, 'name'),
            FieldConverter(
                FCType.relation,
                'stage_factor_assoc', (self.handle_stage_factor_assoc,),
                'stage_factor_assoc', (self.represent_model,),
                model_manager=self._sfa_mng
            )
        ]
        super(RbRadzStageFactorModelManager, self).__init__(rbRadzStage, fields)

    def handle_stage_factor_assoc(self, field, item_list, parent_obj):
        if item_list is None:
            return []
        result = []
        for item_data in item_list:
            stage_id = item_data.get('stage_id')
            if stage_id:
                factor_id = item_data['factor_id']
                item = self._sfa_mng._model.query.filter_by(stage_id=stage_id, factor_id=factor_id).first()
                item = self._sfa_mng.fill(item, item_data, parent_obj)
            else:
                stage_id = parent_obj.id
                factor_id = safe_traverse(item_data, 'factor', 'id')
                item_data['stage_id'] = stage_id
                item_data['factor_id'] = factor_id
                item = self._sfa_mng.create_new(item_data, None, parent_obj)
            result.append(item)

        # deletion
        for item in getattr(parent_obj, field.m_name):
            if item not in result:
                db.session.delete(item)
        return result


class RbRadzStageFactorAssocModelManager(BaseModelManager):
    def __init__(self):
        self._rf_mng = self.get_manager('rbRadzRiskFactor')
        fields = [
            FieldConverter(FCType.basic_repr, 'stage_id', None, 'stage_id'),
            FieldConverter(FCType.basic_repr, 'factor_id', None, 'factor_id'),
            FieldConverter(FCType.basic, 'points', safe_int, 'points', safe_int),
            FieldConverter(
                FCType.relation,
                'factor', (self.handle_onetomany_nonedit, ),
                'factor', (self.represent_model, ),
                model_manager=self._rf_mng
            )
        ]
        super(RbRadzStageFactorAssocModelManager, self).__init__(rbRadzRiskFactor_StageAssoc, fields)

    def create_new(self, data=None, parent_id=None, parent_obj=None):
        item = self._model()
        if data is not None:
            item.stage_id = data['stage_id']
            item.factor_id = data['factor_id']
            item.points = data['points']
        return item