# -*- coding: utf-8 -*-

from nemesis.lib.utils import safe_dict, safe_traverse
from nemesis.systemwide import db


class FCType(object):
    basic = 0  # простое поле для отображения и сохранения
    basic_repr = 1  # простое поле только для отображения
    relation = 2  # поле, представляющее отношение с другими сущностями, для отображения и редактирования
    relation_repr = 3  # поле, представляющее отношение с другими сущностями, только для отображения
    parent = 4  # поле, представляющее родительскую сущность


class FieldConverter():

    def __init__(self, field_type, model_name, to_model=None, json_name=None, to_json=None):
        self.field_type = field_type
        self.m_name = model_name
        self.to_model = to_model
        if self.field_type in (FCType.basic, FCType.relation) and self.to_model is None:
            raise AttributeError('`to_model` parameter is required for valid model value conversion')
        self.j_name = json_name
        self.to_json = to_json


def represent_model(value, manager):
    if isinstance(value, list):
        return map(manager.represent, value)
    return manager.represent(value) if value else None


class BaseModelManager(object):

    @classmethod
    def get_manager(cls, name):
        from blueprints.misconfig.lib.data_management.factory import get_manager
        return get_manager(name)

    def __init__(self, model, fields):
        self._model = model
        self._fields = fields

    def get_by_id(self, item_id):
        return self._model.query.get(item_id)

    def get_list(self, **kwargs):
        query = self._model.query
        where = kwargs.get('where')
        if where:
            query = query.filter(*where)
        order = kwargs.get('order')
        if order:
            query = query.order_by(*order)
        return query.all()

    def fill(self, item, data, parent_obj=None):
        for field in self._fields:
            if field.field_type not in (FCType.basic_repr, FCType.relation_repr):
                item_field_name = field.m_name
                if field.field_type == FCType.parent:
                    value = parent_obj
                elif field.field_type == FCType.relation:
                    value = field.to_model(data.get(field.j_name), item)
                elif field.field_type == FCType.basic:
                    value = data.get(field.j_name)
                    if field.to_model:
                        value = field.to_model(value)
                else:
                    raise AttributeError('bad field type')

                if isinstance(getattr(item, item_field_name), list):
                    if isinstance(value, list):
                        getattr(item, item_field_name).extend(value)
                    else:
                        getattr(item, item_field_name).append(value)
                else:
                    setattr(item, item_field_name, value)
        return item

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = self._model()
        if data is not None:
            self.fill(item, data, parent_obj)
        return item

    def update(self, item_id, data, parent_obj=None):
        item = self.get_by_id(item_id)
        self.fill(item, data, parent_obj)
        return item

    def delete(self, item_id):
        item = self.get_by_id(item_id)
        if hasattr(item, 'deleted'):
            item.deleted = 1
        return item

    def undelete(self, item_id):
        item = self.get_by_id(item_id)
        if hasattr(item, 'deleted'):
            item.deleted = 0
        return item

    def store(self, *args):
        db.session.add_all(args)
        try:
            db.session.commit()
        except Exception, e:
            raise
        return True

    def represent(self, item):
        result = {}
        for field in self._fields:
            if field.j_name:
                j_field = field.j_name
                result[j_field] = (field.to_json or safe_dict)(getattr(item, field.m_name))
        return result

    def handle_onetomany_nonedit(self, manager, json_data, parent_obj=None):
        if json_data is None:
            return None
        item_id = json_data['id']
        item = manager.get_by_id(item_id)
        return item
