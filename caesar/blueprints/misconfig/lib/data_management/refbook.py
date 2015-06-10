# -*- coding: utf-8 -*-
from blueprints.misconfig.lib.data_management.base import BaseModelManager, FieldConverter, FCType
from nemesis.lib.utils import safe_int, safe_unicode
from nemesis.models.exists import rbTreatment


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