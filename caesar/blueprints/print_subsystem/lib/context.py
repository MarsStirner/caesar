# -*- coding: utf-8 -*-
import collections
from .query import Query

__author__ = 'mmalkov'


class CTemplateHelpers(object):
    @staticmethod
    def transpose_table(table):
        return [[row[column_number] for row in table] for column_number in xrange(len(table[0]))] if table else [[]]

    @staticmethod
    def sum_columns(table):
        return [sum(row[column_number] for row in table) for column_number in xrange(len(table[0]))] if table else [[]]

    @staticmethod
    def table_uniform(list_list, null=None):
        max_len = max(len(row) for row in list_list)
        return [(row + [null] * (max_len - len(row))) for row in list_list]

    @staticmethod
    def table_column(table, column=0):
        return [row[column] for row in table] if table and table[0] else []

    @staticmethod
    def table_group(table, column=0):
        result = collections.defaultdict(list)
        for row in table:
            result[row[column]].append(row)
        return result


class ModelGetter(object):
    def __init__(self, model):
        self.__model = model

    def get(self, _id):
        return Query(self.__model).get(_id)

    def get_many(self, ids):
        return dict(
            (item.id, item)
            for item in Query(self.__model).filter(self.__model.id.in_(ids))
        )


class ModelGetterProxy(object):
    def __new__(cls, *args, **kwargs):
        from ..models import models_all as module
        bases = (module.Info, module.RBInfo)
        for item_name in dir(module):
            item = getattr(module, item_name)
            if isinstance(item, bases) and not hasattr(item, '__abstract__'):
                setattr(cls, item_name, ModelGetter(item))


