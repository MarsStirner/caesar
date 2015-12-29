# -*- coding: utf-8 -*-

from blueprints.misconfig.lib.data_management.base import FieldConverter, FCType
from blueprints.misconfig.lib.data_management.refbook import SimpleRefBookModelManager
from nemesis.models.exists import rbService
from nemesis.lib.utils import safe_date, safe_bool, safe_int


class RbServiceModelManager(SimpleRefBookModelManager):

    def __init__(self):
        super(RbServiceModelManager, self).__init__(rbService, [
            FieldConverter(FCType.basic, 'begDate', safe_date, 'beg_date'),
            FieldConverter(FCType.basic, 'endDate', safe_date, 'end_date'),
            FieldConverter(FCType.basic, 'isComplex', safe_int, 'is_complex', safe_bool),
            FieldConverter(
                FCType.relation,
                'subservice_list',
                (self.handle_manytomany, ),
                'subservice_list',
                model_manager=self
            )
        ])
