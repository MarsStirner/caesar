# -*- coding: utf-8 -*-
import datetime
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


__template_helpers = CTemplateHelpers()

do_transpose_table = __template_helpers.transpose_table
do_sum_columns = __template_helpers.sum_columns
do_table_uniform = __template_helpers.table_uniform
do_table_column = __template_helpers.table_column
do_table_group = __template_helpers.table_group
do_table_cool_group = __template_helpers.table_cool_group
do_dictmap = __template_helpers.dictmap
do_filter = __template_helpers.filter
do_simple_index = __template_helpers.simple_index
