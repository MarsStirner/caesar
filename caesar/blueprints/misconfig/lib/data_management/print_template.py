# -*- coding: utf-8 -*-
from .base import BaseModelManager, FieldConverter, FCType
from nemesis.models.exists import rbPrintTemplate
from nemesis.lib.utils import (safe_int, safe_unicode)


class RbPrintTemplateModelManager(BaseModelManager):
    def __init__(self):
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'code', safe_unicode, 'code'),
            FieldConverter(FCType.basic, 'name', safe_unicode, 'name'),
            FieldConverter(FCType.basic, 'context', safe_unicode, 'context'),
            FieldConverter(FCType.basic, 'templateText', safe_unicode, 'template_text'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
        ]
        super(RbPrintTemplateModelManager, self).__init__(rbPrintTemplate, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(RbPrintTemplateModelManager, self).create(data)
        item.fileName = ''
        item.default = ''
        item.render = 1
        return item

    def get_list(self, **kwargs):
        where = [
            # self._model.render.__eq__(1)
        ]
        return super(RbPrintTemplateModelManager, self).get_list(where=where)