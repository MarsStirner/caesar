# -*- coding: utf-8 -*-
from .base import BaseModelManager
from nemesis.models.exists import rbTreatment


class SimpleRefBookModelManager(BaseModelManager):
    def __init__(self, model, additional_fields=None):
        fm = {
            'id': 'id',
            'code': 'code',
            'name': 'name'
        }
        if hasattr(model, 'deleted'):
            fm['deleted'] = 'deleted'
        if isinstance(additional_fields, dict):
            fm.update(additional_fields)
        super(SimpleRefBookModelManager, self).__init__(model, fm)


class RbTreatmentModelManager(SimpleRefBookModelManager):
    def __init__(self):
        super(RbTreatmentModelManager, self).__init__(rbTreatment, {
            'treatment_type': 'treatment_type.id'
        })