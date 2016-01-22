# -*- coding: utf-8 -*-

from flask import abort

from nemesis.lib.utils import safe_dict, safe_int
from nemesis.systemwide import db
from nemesis.lib.pagination import Pagination


class FCType(object):
    basic = 0  # простое поле для отображения и сохранения
    basic_repr = 1  # простое поле только для отображения
    relation = 2  # поле, представляющее отношение с другими сущностями, для отображения и редактирования
    relation_repr = 3  # поле, представляющее отношение с другими сущностями, только для отображения
    parent = 4  # поле, представляющее родительскую сущность


class FieldConverter():

    def __init__(self, field_type, model_name, to_model=None, json_name=None, to_json=None, model_manager=None):
        self.field_type = field_type
        self.m_name = model_name
        self.j_name = json_name
        self._manager = model_manager

        if self.field_type in (FCType.basic, FCType.relation) and to_model is None:
            raise AttributeError('`to_model` parameter is required for valid model value conversion')
        if isinstance(to_model, tuple):
            to_model = to_model[0]
            if model_manager is None:
                raise AttributeError('`manager` parameter is required for valid model value conversion')
            self.to_model = lambda *args: to_model(self, *args)
        else:
            self.to_model = to_model
        if isinstance(to_json, tuple):
            to_json = to_json[0]
            if model_manager is None:
                raise AttributeError('`manager` parameter is required for valid model value representation')
            self.to_json = lambda *args: to_json(self, *args)
        else:
            self.to_json = to_json

    @property
    def manager(self):
        if callable(self._manager):
            return self._manager()
        else:
            return self._manager



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
        options = kwargs.get('options')
        if options:
            query = query.options(
                *options
            )
        return query.all()

    def get_paginated_data(self, **kwargs):
        per_page = safe_int(kwargs.get('per_page')) or 20
        page = safe_int(kwargs.get('page')) or 1
        query = self._model.query
        where = kwargs.get('where')
        if where:
            query = query.filter(*where)
        order = kwargs.get('order')
        if order:
            query = query.order_by(*order)
        options = kwargs.get('options')
        if options:
            query = query.options(
                *options
            )
        paginated_data = self._paginate(query, page, per_page)
        return paginated_data

    def _paginate(self, query, page, per_page=20, error_out=False):
        """Returns `per_page` items from page `page`.  By default it will
        abort with 404 if no items were found and the page was larger than
        1.  This behavor can be disabled by setting `error_out` to `False`.

        Returns an :class:`Pagination` object.
        """
        if error_out and page < 1:
            abort(404)
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        if not items and page != 1 and error_out:
            abort(404)

        # No need to count if we're on the first page and there are fewer
        # items than we expected.
        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = query.order_by(None).count()

        return Pagination(query, page, per_page, total, items)

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

                # TODO: check
                # if isinstance(getattr(item, item_field_name), list):
                #     if isinstance(value, list):
                #         getattr(item, item_field_name).extend(value)
                #     else:
                #         getattr(item, item_field_name).append(value)
                # else:
                #     setattr(item, item_field_name, value)
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

    def handle_onetomany_nonedit(self, field, json_data, parent_obj=None):
        if json_data is None:
            return None
        item_id = json_data['id']
        item = field.manager.get_by_id(item_id)
        return item

    def handle_manytomany(self, field, item_list, parent_obj):
        if item_list is None:
            return []

        result = []
        for item_data in item_list:
            item_id = item_data['id']
            item = field.manager.get_by_id(item_id)
            result.append(item)
        return result

    def handle_manytomany_assoc_obj(self, field, item_list, parent_obj):
        if item_list is None:
            return []
        result = []
        for item_data in item_list:
            item_id = item_data['id']
            if item_id:
                item = field.manager.update(item_id, item_data, parent_obj)
            else:
                item = field.manager.create(item_data, None, parent_obj)
            result.append(item)

        # deletion
        for item in getattr(parent_obj, field.m_name):
            if item not in result:
                db.session.delete(item)
        return result

    def represent_model(self, field, value):
        if isinstance(value, list):
            return map(field.manager.represent, value)
        return field.manager.represent(value) if value else None
