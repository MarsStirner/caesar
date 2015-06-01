# -*- coding: utf-8 -*-
import uuid

from blueprints.misconfig.lib.data_management.base import BaseModelManager, FieldConverter, represent_model
from lib.utils import safe_int, safe_unicode, safe_uuid
from nemesis.models.expert_protocol import (Measure, ExpertProtocol, ExpertScheme, ExpertSchemeMKB,
    ExpertSchemeMeasureAssoc, MeasureSchedule)
from nemesis.systemwide import db


class MeasureModelManager(BaseModelManager):
    def __init__(self):
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('measure_type', 'measure_type.id', safe_int),
            FieldConverter('code', 'code', safe_unicode),
            FieldConverter('name', 'name', safe_unicode),
            FieldConverter('deleted', 'deleted', safe_int),
            FieldConverter('uuid', 'uuid', safe_uuid),
            FieldConverter('action_type', 'action_type.id', safe_int),
            FieldConverter('template_action', 'template_action', safe_int)
        ]
        super(MeasureModelManager, self).__init__(Measure, fields)

    def create(self, data=None):
        item = super(MeasureModelManager, self).create(data)
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
        self._scheme_manager = ExpertSchemeModelManager()
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('code', 'code', safe_unicode),
            FieldConverter('name', 'name', safe_unicode),
            FieldConverter('schemes', 'schemes', self.handle_schemes, lambda val: represent_model(val, self._scheme_manager)),
        ]
        super(ExpertProtocolModelManager, self).__init__(ExpertProtocol, fields)

    def handle_schemes(self, scheme_list):
        return []


class ExpertSchemeModelManager(BaseModelManager):
    def __init__(self):
        self._mkb_manager = ExpertSchemeMKBModelManager()
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('code', 'code', safe_unicode),
            FieldConverter('name', 'name', safe_unicode),
            FieldConverter('number', 'number', safe_unicode),
            FieldConverter('protocol_id', 'protocol_id', safe_int),
            FieldConverter('mkbs^', 'mkbs', self.handle_mkbs, lambda val: represent_model(val, self._mkb_manager)),
        ]
        super(ExpertSchemeModelManager, self).__init__(ExpertScheme, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        if data is None:
            # if not parent_id:
            #     raise AttributeError('parent_id attribute required')
            data = {
                'protocol_id': parent_id
            }
        return super(ExpertSchemeModelManager, self).create(data)

    def handle_mkbs(self, mkb_list, parent_obj):
        if mkb_list is None:
            return []
        result = []
        for item_data in mkb_list:
            item_id = item_data['id']
            if item_id:
                item = self._mkb_manager.update(item_id, item_data, parent_obj)
            else:
                item = self._mkb_manager.create(item_data, None, parent_obj)
            result.append(item)

        # deletion
        for scheme_mkb in parent_obj.mkbs:
            if scheme_mkb not in result:
                db.session.delete(scheme_mkb)
        db.session.add_all(result)  # or on different level? In store?
        return result


class ExpertSchemeMKBModelManager(BaseModelManager):
    def __init__(self):
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('scheme_id', 'scheme_id', safe_int),
            FieldConverter('mkb', 'mkb.id', safe_int),
            FieldConverter('^scheme', ''),
        ]
        super(ExpertSchemeMKBModelManager, self).__init__(ExpertSchemeMKB, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        if data is None:
            # if not parent_id:
            #     raise AttributeError('parent_id attribute required')
            data = {
                'scheme_id': parent_id
            }
        return super(ExpertSchemeMKBModelManager, self).create(data, parent_id, parent_obj)


class ExpertSchemeMeasureModelManager(BaseModelManager):
    def __init__(self):
        self._measure_manager = MeasureModelManager()
        self._schedule_manager = MeasureScheduleModelManager()
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('scheme_id', 'scheme_id', safe_int),
            FieldConverter('measure', 'measure.id', None, lambda val: represent_model(val, self._measure_manager)),
            FieldConverter('schedule^', 'schedule', self.handle_schedule, lambda val: represent_model(val, self._schedule_manager)),
        ]
        super(ExpertSchemeMeasureModelManager, self).__init__(ExpertSchemeMeasureAssoc, fields)

    def get_list(self, **kwargs):
        where = []
        if 'scheme_id' in kwargs:
            where.append(self._model.scheme_id.__eq__(kwargs['scheme_id']))
        return super(ExpertSchemeMeasureModelManager, self).get_list(where=where)

    def create(self, data=None, parent_id=None, parent_obj=None):
        if data is None:
            data = {
                'scheme_id': parent_id
            }
        return super(ExpertSchemeMeasureModelManager, self).create(data, parent_id, parent_obj)

    def handle_schedule(self, schedule, parent_obj):
        if schedule is None:
            return None
        item_id = schedule['id']
        if item_id:
            item = self._schedule_manager.update(item_id, schedule, parent_obj)
        else:
            item = self._schedule_manager.create(schedule, None, parent_obj)

        db.session.add(item)  # or on different level? In store?
        return item


class MeasureScheduleModelManager(BaseModelManager):
    def __init__(self):
        self._measure_manager = MeasureModelManager()
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('schedule_type', 'schedule_type.id', safe_int),
            FieldConverter('offsetStart', 'offset_start', safe_int),
            FieldConverter('offsetEnd', 'offset_end', safe_int),
            FieldConverter('repeatCount', 'repeat_count', safe_int),
        ]
        super(MeasureScheduleModelManager, self).__init__(MeasureSchedule, fields)
