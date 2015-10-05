# -*- coding: utf-8 -*-
import datetime
from jinja2 import contextfilter
from blueprints.print_subsystem.lib.context import CTemplateHelpers

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


@contextfilter
def do_dictmap(context, sequence, flt, *args, **kwargs):
    env = context.environment
    return dict(
        (key, env.call_filter(flt, value, args, kwargs, context=context))
        for key, value in sequence.iteritems()
    )


def do_simple_index(sequence, attribute):
    return dict(
        (item.get(attribute) if isinstance(item, dict) else item[attribute], item)
        for item in sequence
    )


def do_filter(table, conditions):
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
                elif value != cond:
                    return False
            except TypeError:
                return False
        return True

    return [
        row
        for row in table
        if match(row)
    ]

__template_helpers = CTemplateHelpers()

do_transpose_table = __template_helpers.transpose_table
do_sum_columns = __template_helpers.sum_columns
do_table_uniform = __template_helpers.table_uniform
do_table_column = __template_helpers.table_column
do_table_group = __template_helpers.table_group
do_table_cool_group = __template_helpers.table_cool_group
