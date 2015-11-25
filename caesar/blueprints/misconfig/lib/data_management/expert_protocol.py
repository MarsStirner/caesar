# -*- coding: utf-8 -*-
import uuid

from blueprints.misconfig.lib.data_management.base import BaseModelManager, FieldConverter, FCType
from nemesis.lib.utils import safe_int, safe_unicode
from nemesis.models.expert_protocol import (Measure, ExpertProtocol, ExpertScheme, ExpertSchemeMeasureAssoc,
    MeasureSchedule)


class MeasureModelManager(BaseModelManager):
    def __init__(self):
        self._mt_mng = self.get_manager('rbMeasureType')
        self._at_mng = self.get_manager('ActionType')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(
                FCType.relation,
                'measure_type', (self.handle_onetomany_nonedit, ),
                'measure_type',
                model_manager=self._mt_mng
            ),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            FieldConverter(FCType.basic_repr, 'uuid', None, 'uuid'),
            FieldConverter(
                FCType.relation,
                'appointment_at', (self.handle_onetomany_nonedit, ),
                'appointment_at',
                model_manager=self._at_mng
            ),
            FieldConverter(
                FCType.relation,
                'result_at', (self.handle_onetomany_nonedit, ),
                'result_at',
                model_manager=self._at_mng
            ),
            FieldConverter(FCType.relation_repr, 'template_action', None, 'template_action')
        ]
        super(MeasureModelManager, self).__init__(Measure, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(MeasureModelManager, self).create(data, parent_id, parent_obj)
        item.uuid = uuid.uuid4()
        return item


class ExpertProtocolModelManager(BaseModelManager):
    def __init__(self, with_schemes=False):
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
        ]
        if with_schemes:
            self._scheme_mng = ExpertSchemeModelManager()
            fields.append(FieldConverter(
                FCType.relation_repr,
                'schemes', None,
                'schemes', (self.represent_model, ),
                self._scheme_mng
            ))
        super(ExpertProtocolModelManager, self).__init__(ExpertProtocol, fields)


class ExpertSchemeModelManager(BaseModelManager):
    def __init__(self):
        self._mkb_mng = self.get_manager('MKB')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'number', safe_unicode, 'number'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            FieldConverter(FCType.basic_repr, 'protocol_id', None, 'protocol_id'),
            FieldConverter(
                FCType.relation,
                'mkbs', (self.handle_manytomany, ),
                'mkbs', (self.represent_model, ),
                self._mkb_mng
            )
        ]
        super(ExpertSchemeModelManager, self).__init__(ExpertScheme, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(ExpertSchemeModelManager, self).create(data)
        item.protocol_id = data.get('protocol_id') if data is not None else parent_id
        return item

    def delete(self, item_id):
        item = super(ExpertSchemeModelManager, self).delete(item_id)
        for sm in item.scheme_measures:
            sm.deleted = 1
        return item


class ExpertSchemeMeasureModelManager(BaseModelManager):
    def __init__(self):
        self._measure_mng = MeasureModelManager()
        self._schedule_mng = MeasureScheduleModelManager()
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.relation_repr, 'scheme_id', None, 'scheme_id'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            FieldConverter(
                FCType.relation,
                'measure', (self.handle_onetomany_nonedit, ),
                'measure', (self.represent_model, ),
                self._measure_mng
            ),
            FieldConverter(
                FCType.relation,
                'schedule', self.handle_schedule,
                'schedule', (self.represent_model, ),
                self._schedule_mng
            ),
        ]
        super(ExpertSchemeMeasureModelManager, self).__init__(ExpertSchemeMeasureAssoc, fields)

    def get_list(self, **kwargs):
        where = []
        if 'scheme_id' in kwargs:
            where.append(self._model.scheme_id.__eq__(kwargs['scheme_id']))
        return super(ExpertSchemeMeasureModelManager, self).get_list(where=where)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(ExpertSchemeMeasureModelManager, self).create(data, parent_id, parent_obj)
        item.scheme_id = data.get('scheme_id') if data is not None else parent_id
        if not data:
            item.schedule = self._schedule_mng.create()
        return item

    def handle_schedule(self, schedule, parent_obj):
        if schedule is None:
            return None
        item_id = schedule['id']
        if item_id:
            item = self._schedule_mng.update(item_id, schedule, parent_obj)
        else:
            item = self._schedule_mng.create(schedule, None, parent_obj)
        return item


class MeasureScheduleModelManager(BaseModelManager):
    def __init__(self):
        self._measure_mng = MeasureModelManager()
        self._sched_type_mng = self.get_manager('rbMeasureScheduleType')
        self._units_mng = self.get_manager('rbUnits')
        self._apply_type_mng = self.get_manager('rbMeasureScheduleApplyType')
        self._mkb_mng = self.get_manager('MKB')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(
                FCType.relation,
                'apply_type', (self.handle_onetomany_nonedit, ),
                'apply_type',
                model_manager=self._apply_type_mng
            ),
            FieldConverter(FCType.basic, 'applyBoundRangeLow', safe_int, 'apply_bound_range_low'),
            FieldConverter(
                FCType.relation,
                'apply_bound_range_low_unit', (self.handle_onetomany_nonedit, ),
                'apply_bound_range_low_unit',
                model_manager=self._units_mng
            ),
            FieldConverter(FCType.basic, 'applyBoundRangeLowMax', safe_int, 'apply_bound_range_low_max'),
            FieldConverter(
                FCType.relation,
                'apply_bound_range_low_max_unit', (self.handle_onetomany_nonedit, ),
                'apply_bound_range_low_max_unit',
                model_manager=self._units_mng
            ),
            FieldConverter(FCType.basic, 'applyBoundRangeHigh', safe_int, 'apply_bound_range_high'),
            FieldConverter(
                FCType.relation,
                'apply_bound_range_high_unit', (self.handle_onetomany_nonedit, ),
                'apply_bound_range_high_unit',
                model_manager=self._units_mng
            ),
            FieldConverter(FCType.basic, 'period', safe_int, 'period'),
            FieldConverter(
                FCType.relation,
                'period_unit', (self.handle_onetomany_nonedit, ),
                'period_unit',
                model_manager=self._units_mng
            ),
            FieldConverter(FCType.basic, 'frequency', safe_int, 'frequency'),
            FieldConverter(FCType.basic, 'count', safe_int, 'count'),
            FieldConverter(
                FCType.relation,
                'schedule_types', (self.handle_manytomany, ),
                'schedule_types', (self.represent_model, ),
                self._sched_type_mng
            ),
            FieldConverter(FCType.basic, 'additionalText', safe_unicode, 'additional_text'),
            FieldConverter(
                FCType.relation,
                'additional_mkbs', (self.handle_manytomany, ),
                'additional_mkbs', (self.represent_model, ),
                self._mkb_mng
            ),
        ]
        super(MeasureScheduleModelManager, self).__init__(MeasureSchedule, fields)
