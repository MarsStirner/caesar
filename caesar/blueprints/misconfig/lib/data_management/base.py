# -*- coding: utf-8 -*-

from nemesis.lib.utils import safe_dict, safe_traverse
from nemesis.systemwide import db


def reverse_dict(d):
    return dict((v, k) for k, v in d.iteritems())


class BaseModelManager(object):
    def __init__(self, model, fields_map):
        self._model = model
        self._fields_map = fields_map
        self._reverse_fields_map = reverse_dict(fields_map)

    def get_by_id(self, item_id):
        return self._model.query.get(item_id)

    def get_list(self):
        return self._model.query.all()

    def fill(self, item, data):
        for m_field, d_field in self._fields_map.iteritems():
            setattr(item, m_field, safe_traverse(data, *d_field.split('.')))
        return item

    def create(self, data):
        item = self._model()
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
        for d_field, m_field in self._reverse_fields_map.iteritems():
            d_field = d_field.split('.')[0]
            result[d_field] = safe_dict(getattr(item, m_field))
        return result
