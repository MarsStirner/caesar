# -*- coding: utf-8 -*-

from blueprints.misconfig.lib.data_management.base import FieldConverter, FCType, BaseModelManager
from blueprints.misconfig.lib.data_management.refbook import SimpleRefBookModelManager
from nemesis.models.exists import rbService, rbServiceGroupAssoc
from nemesis.lib.utils import safe_date, safe_bool, safe_int


class RbServiceModelManager(SimpleRefBookModelManager):

    def __init__(self):
        self._service_gr_mng = RbServiceGroupAssocModelManager()
        super(RbServiceModelManager, self).__init__(rbService, [
            FieldConverter(FCType.basic, 'begDate', safe_date, 'beg_date'),
            FieldConverter(FCType.basic, 'endDate', safe_date, 'end_date'),
            FieldConverter(FCType.basic, 'isComplex', safe_int, 'is_complex', safe_bool),
            FieldConverter(
                FCType.relation,
                'subservice_assoc', (self.handle_manytomany_assoc_obj, ),
                'subservice_assoc', (self.represent_model, ),
                model_manager=self._service_gr_mng
            )
        ])


class RbServiceGroupAssocModelManager(BaseModelManager):

    def __init__(self):
        self._service_kind_mng = self.get_manager('rbServiceKind')
        self._service_mng = lambda: RbServiceModelManager()
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'group_id', safe_int, 'group_id'),
            FieldConverter(FCType.basic, 'service_id', safe_int, 'service_id'),
            FieldConverter(
                FCType.relation,
                'service_kind', (self.handle_onetomany_nonedit, ),
                'service_kind',
                model_manager=self._service_kind_mng
            ),
            FieldConverter(
                FCType.relation,
                'subservice', (self.handle_onetomany_nonedit, ),
                'subservice',
                model_manager=self._service_mng
            )
        ]
        super(RbServiceGroupAssocModelManager, self).__init__(rbServiceGroupAssoc, fields)
