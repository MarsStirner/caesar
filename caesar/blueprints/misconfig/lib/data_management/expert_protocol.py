# -*- coding: utf-8 -*-
import uuid

from blueprints.misconfig.lib.data_management.base import BaseModelManager, FieldConverter, FCType, represent_model
from nemesis.lib.utils import safe_int, safe_unicode
from nemesis.models.expert_protocol import (Measure, ExpertProtocol, ExpertScheme, ExpertSchemeMKB,
    ExpertSchemeMeasureAssoc, MeasureSchedule)
from nemesis.systemwide import db


class MeasureModelManager(BaseModelManager):
    def __init__(self):
        self._mt_mng = self.get_manager('rbMeasureType')
        self._at_mng = self.get_manager('ActionType')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(
                FCType.relation,
                'measure_type', lambda val, par: self.handle_onetomany_nonedit(self._mt_mng, val, par),
                'measure_type'
            ),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            FieldConverter(FCType.basic_repr, 'uuid', None, 'uuid'),
            FieldConverter(
                FCType.relation,
                'action_type', lambda val, par: self.handle_onetomany_nonedit(self._at_mng, val, par),
                'action_type'
            ),
            FieldConverter(FCType.relation_repr, 'template_action', None, 'template_action')
        ]
        super(MeasureModelManager, self).__init__(Measure, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(MeasureModelManager, self).create(data, parent_id, parent_obj)
        item.uuid = uuid.uuid4()
        return item

    def represent(self, item):
        result = super(MeasureModelManager, self).represent(item)
        data_model = None
        if item.action_type:
            data_model = 'action_type'
        elif item.template_action:
            data_model = 'template_action'
        result['data_model'] = data_model
        return result


class ExpertProtocolModelManager(BaseModelManager):
    def __init__(self):
        self._scheme_mng = ExpertSchemeModelManager()
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(
                FCType.relation_repr,
                'schemes', None,
                'schemes', lambda val: represent_model(val, self._scheme_mng)
            ),
        ]
        super(ExpertProtocolModelManager, self).__init__(ExpertProtocol, fields)


class ExpertSchemeModelManager(BaseModelManager):
    def __init__(self):
        self._mkb_mng = ExpertSchemeMKBModelManager()
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'number', safe_unicode, 'number'),
            FieldConverter(FCType.basic_repr, 'protocol_id', None, 'protocol_id'),
            FieldConverter(
                FCType.relation,
                'scheme_mkbs', self.handle_mkbs,
                'scheme_mkbs', lambda val: represent_model(val, self._mkb_mng)),
        ]
        super(ExpertSchemeModelManager, self).__init__(ExpertScheme, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(ExpertSchemeModelManager, self).create(data)
        item.protocol_id = data.get('protocol_id') if data is not None else parent_id
        return item

    def handle_mkbs(self, mkb_list, parent_obj):
        if mkb_list is None:
            return []
        result = []
        for item_data in mkb_list:
            item_id = item_data['id']
            if item_id:
                item = self._mkb_mng.update(item_id, item_data, parent_obj)
            else:
                item = self._mkb_mng.create(item_data, None, parent_obj)
            result.append(item)

        # deletion
        for scheme_mkb in parent_obj.scheme_mkbs:
            if scheme_mkb not in result:
                db.session.delete(scheme_mkb)
        return result


class ExpertSchemeMKBModelManager(BaseModelManager):
    def __init__(self):
        self._mkb_mng = self.get_manager('MKB')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'scheme_id', safe_int, 'scheme_id'),
            FieldConverter(
                FCType.relation,
                'mkb', lambda val, par: self.handle_onetomany_nonedit(self._mkb_mng, val),
                'mkb'),
            FieldConverter(FCType.parent, 'scheme', None),
        ]
        super(ExpertSchemeMKBModelManager, self).__init__(ExpertSchemeMKB, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(ExpertSchemeMKBModelManager, self).create(data, parent_id, parent_obj)
        item.scheme_id = data.get('scheme_id') if data is not None else parent_id
        return item


class ExpertSchemeMeasureModelManager(BaseModelManager):
    def __init__(self):
        self._measure_mng = MeasureModelManager()
        self._schedule_mng = MeasureScheduleModelManager()
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.relation_repr, 'scheme_id', None, 'scheme_id'),
            FieldConverter(
                FCType.relation,
                'measure', lambda val, par: self.handle_onetomany_nonedit(self._measure_mng, val, par),
                'measure', lambda val: represent_model(val, self._measure_mng)),
            FieldConverter(
                FCType.relation,
                'schedule', self.handle_schedule,
                'schedule', lambda val: represent_model(val, self._schedule_mng)),
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
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(
                FCType.relation,
                'schedule_type', lambda val, par: self.handle_onetomany_nonedit(self._sched_type_mng, val, par),
                'schedule_type'),
            FieldConverter(FCType.basic, 'offsetStart', safe_int, 'offset_start'),
            FieldConverter(FCType.basic, 'offsetEnd', safe_int, 'offset_end'),
            FieldConverter(FCType.basic, 'repeatCount', safe_int, 'repeat_count'),
        ]
        super(MeasureScheduleModelManager, self).__init__(MeasureSchedule, fields)
