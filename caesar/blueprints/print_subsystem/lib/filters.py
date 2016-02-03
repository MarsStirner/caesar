# -*- coding: utf-8 -*-
import datetime

__author__ = 'viruzzz-kun'


def do_datetime_format(d, fmt=None):
    if isinstance(d, datetime.datetime):
        return d.strftime(fmt or '%d.%m.%Y %H:%M')
    elif isinstance(d, datetime.date):
        return d.strftime(fmt or '%d.%m.%Y')
    elif isinstance(d, datetime.time):
        return d.strftime(fmt or '%H:%M')
    return d


def do_datetime_combine(date_time_tuple):
    return datetime.datetime.combine(*date_time_tuple)


def do_datetime_add_days(dt, add):
    return dt + datetime.timedelta(days=add)


def do_transpose_table(table):
    return [[row[column_number] for row in table] for column_number in xrange(len(table[0]))] if table else [[]]


def do_sum_columns(table):
    return [sum(row[column_number] for row in table) for column_number in xrange(len(table[0]))] if table else [[]]


def do_table_uniform(list_list, null=None):
    max_len = max(len(row) for row in list_list)
    return [(row + [null] * (max_len - len(row))) for row in list_list]


def do_table_column(table, column=0):
    return [row[column] for row in table] if table and table[0] else []


def flatten_nested(item_list, attr_name):
    """Преобразует список элементов, имеющих вложенные подэлементы под названием
    атрибута `attr_name`, в плоский список элементов.

    [
        item1 (item1.attr_name = [item11, item12]),
        item2 (item2.attr_name = [])
    ] -> [item1, item11, item12, item2]
    """
    flatten = []
    cur_idx = 0
    cur_level = -1

    def traverse(ilist, level, idx, root_idx):
        level += 1
        for item in ilist:
            if not hasattr(item, 'ui_attrs'):
                setattr(item, 'ui_attrs', {})
            item.ui_attrs.update({
                'level': level,
                'idx': idx,
                'root_idx': idx if level == 0 else root_idx
            })
            flatten.append(item)
            traverse(getattr(item, attr_name, []), level, idx, idx)
            idx += 1

    traverse(item_list, cur_level, cur_idx, cur_idx)
    return flatten
