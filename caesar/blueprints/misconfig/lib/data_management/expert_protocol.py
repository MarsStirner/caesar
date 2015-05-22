# -*- coding: utf-8 -*-
import uuid

from .base import BaseModelManager
from blueprints.misconfig.lib.data_management.base import FieldConverter
from lib.utils import safe_int, safe_unicode, safe_uuid
from nemesis.models.expert_protocol import Measure, ExpertProtocol


class MeasureModelManager(BaseModelManager):
    def __init__(self):
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('measureType_id', 'measure_type.id', safe_int),
            FieldConverter('code', 'code', safe_unicode),
            FieldConverter('name', 'name', safe_unicode),
            FieldConverter('deleted', 'deleted', safe_int),
            FieldConverter('uuid', 'uuid', safe_uuid),
            FieldConverter('actionType_id', 'action_type.id', safe_int),
            FieldConverter('template_action', 'template_action', safe_int)
        ]
        super(MeasureModelManager, self).__init__(Measure, fields)

    def create(self, data):
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
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('code', 'code', safe_unicode),
            FieldConverter('name', 'name', safe_unicode),
        ]
        super(ExpertProtocolModelManager, self).__init__(ExpertProtocol, fields)