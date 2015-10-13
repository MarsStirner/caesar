# -*- coding: utf-8 -*-
import collections
from jinja2.filters import contextfilter
from nemesis.systemwide import pspd
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

    @staticmethod
    def table_cool_group(table, group_by, key, value, other):
        result = {}
        for row in table:
            if row[group_by] not in result:
                obj = result[row[group_by]] = dict((name, row[column]) for name, column in other.iteritems())
            else:
                obj = result[row[group_by]]
            obj[row[key]] = row[value]
        return [obj for _, obj in sorted(result.items(), key=lambda x: x[0])]

    @staticmethod
    def table_compose_simple(*tables):
        result = {}
        for table, key in tables:
            for id, value in table:
                if id not in result:
                    row = result[id] = {}
                else:
                    row = result[id]
                row[key] = value
        return [obj for _, obj in sorted(result.items(), key=lambda x: x[0])]

    @staticmethod
    @contextfilter
    def dictmap(context, sequence, flt, *args, **kwargs):
        env = context.environment
        return dict(
            (key, env.call_filter(flt, value, args, kwargs, context=context))
            for key, value in sequence.iteritems()
        )

    @staticmethod
    def simple_index(sequence, attribute):
        return dict(
            (item.get(attribute) if isinstance(item, dict) else item[attribute], item)
            for item in sequence
        )

    @staticmethod
    def filter(table, conditions):
        def match(row):
            for key, cond in conditions.iteritems():
                try:
                    value = row[key]
                except KeyError:
                    return False
                try:
                    if isinstance(cond, dict):
                        for op, test in cond.iteritems():
                            if (op in ('eq', '=', '==') and value != test or
                                op in ('!eq', '!=') and value == test or
                                op == '<' and value >= test or
                                op == '<=' and value > test or
                                op == '>' and value <= test or
                                op == '>=' and value < test or
                                op == 'in' and value not in test or
                                op == '!in' and value in test
                            ):
                                return False
                    elif callable(cond):
                        return cond(value)
                    elif value != cond:
                        return False
                except TypeError:
                    return False
            return True

        return filter(match, table)


class ModelGetter(object):
    def __init__(self, model):
        self.__model = model

    def get(self, _id):
        return Query(self.__model).get(_id)

    def get_many(self, ids):
        ids = set(ids)
        result = dict(
            (item.id, item)
            for item in Query(self.__model).filter(self.__model.id.in_(ids))
        )
        if self.__model.__class__.__name__ == 'Client':
            # pre cache PSPD results
            pspd.get([item.pspd_key for item in result.itervalues()])
        return result



class ModelGetterProxy(object):
    def __getattr__(self, item):
        from ..models import models_all as module
        item_object = getattr(module, item)
        if item_object is None:
            raise AttributeError('No Proxy for %s' % item)
        getter = self.__dict__[item] = ModelGetter(item_object)
        return getter


