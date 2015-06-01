# -*- coding: utf-8 -*-
from blueprints.misconfig.lib.data_management.base import BaseModelManager, FieldConverter
from nemesis.lib.utils import safe_int, safe_unicode
from nemesis.models.exists import rbTreatment


class SimpleRefBookModelManager(BaseModelManager):
    def __init__(self, model, additional_fields=None):
        fields = [
            FieldConverter('id', 'id', safe_int),
            FieldConverter('code', 'code', safe_unicode),
            FieldConverter('name', 'name', safe_unicode),
        ]
        if hasattr(model, 'deleted'):
            fields.append(
                FieldConverter('deleted', 'deleted', safe_int)
            )
        if isinstance(additional_fields, list):
            fields.extend(additional_fields)
        super(SimpleRefBookModelManager, self).__init__(model, fields)


class RbTreatmentModelManager(SimpleRefBookModelManager):
    def __init__(self):
        super(RbTreatmentModelManager, self).__init__(rbTreatment, {
            'treatment_type': 'treatment_type.id'
        })