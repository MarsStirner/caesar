# -*- encoding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse


def datetimeformat_filter(value, _format='%Y-%m-%d'):
    if isinstance(value, datetime):
        return value.strftime(_format)
    else:
        return None


def strpdatetime_filter(value):
    return parse(value)