# -*- coding: utf-8 -*-

from nemesis.lib.utils import safe_dict, safe_traverse
from nemesis.systemwide import db


class FieldConverter():
    def __init__(self, model_name, json_name, to_model=None, to_json=None):
        self.m_name = model_name
        self.j_name = json_name
        self.to_model = to_model
        self.to_json = to_json


def represent_model(value, manager):
    if isinstance(value, list):
        return map(manager.represent, value)
    return manager.represent(value)


class BaseModelManager(object):
    def __init__(self, model, fields):
        self._model = model
        self._fields = fields

    def get_by_id(self, item_id):
        return self._model.query.get(item_id)

    def get_list(self):
        return self._model.query.all()

    def fill(self, item, data):
        for field in self._fields:
            value = safe_traverse(data, *field.j_name.split('.'))
            if field.to_model:
                value = field.to_model(value)
            setattr(item, field.m_name, value)
        return item

    def create(self, data=None, parent_id=None):
        item = self._model()
        if data is not None:
            self.fill(item, data)
        return item

    def update(self, item_id, data):
        item = self.get_by_id(item_id)
        self.fill(item, data)
        return item

    def delete(self, item_id):
        item = self.get_by_id(item_id)
        if hasattr(item, 'deleted'):
            item.deleted = 1
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
            j_field = field.j_name.split('.')[0]
            result[j_field] = (field.to_json or safe_dict)(getattr(item, j_field))
        return result
