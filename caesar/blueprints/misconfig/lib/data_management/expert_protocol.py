# -*- coding: utf-8 -*-
import uuid

from blueprints.misconfig.lib.data_management.base import BaseModelManager, FieldConverter, represent_model
from lib.utils import safe_int, safe_unicode, safe_uuid
from nemesis.models.expert_protocol import Measure, ExpertProtocol, ExpertScheme, ExpertSchemeMKB


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
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('code', 'code', safe_unicode),
            FieldConverter('name', 'name', safe_unicode),
            FieldConverter('schemes', 'schemes', None, lambda val: represent_model(val, ExpertSchemeManager())),
        ]
        super(ExpertProtocolModelManager, self).__init__(ExpertProtocol, fields)


class ExpertSchemeManager(BaseModelManager):
    def __init__(self):
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('code', 'code', safe_unicode),
            FieldConverter('name', 'name', safe_unicode),
            FieldConverter('number', 'number', safe_unicode),
            FieldConverter('protocol_id', 'protocol_id', safe_int),
            FieldConverter('mkbs', 'mkbs', None, lambda val: represent_model(val, ExpertSchemeMKBManager())),
        ]
        super(ExpertSchemeManager, self).__init__(ExpertScheme, fields)

    def create(self, data=None, parent_id=None):
        if data is None:
            if not parent_id:
                raise AttributeError('parent_id attribute requiresd')
            data = {
                'protocol_id': parent_id
            }
        return super(ExpertSchemeManager, self).create(data)


class ExpertSchemeMKBManager(BaseModelManager):
    def __init__(self):
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('scheme_id', 'scheme_id', safe_int),
            FieldConverter('mkb', 'mkb.id', safe_int),
        ]
        super(ExpertSchemeMKBManager, self).__init__(ExpertSchemeMKB, fields)
