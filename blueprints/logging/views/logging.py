# -*- encoding: utf-8 -*-
import os
from flask import render_template, abort, request, redirect, url_for, current_app

from jinja2 import TemplateNotFound, Environment, PackageLoader

from ..app import module, _config
from ..lib.data import Log_Data
from ..lib.helpers import datetimeformat_filter, strpdatetime_filter


@module.route('/')
def index():
    current_app.jinja_env.filters['datetimeformat'] = datetimeformat_filter
    current_app.jinja_env.filters['strptime'] = strpdatetime_filter
    log_obj = Log_Data()
    levels = log_obj.get_levels()
    owners = log_obj.get_owners()
    data = log_obj.get_list()
    try:
        return render_template('logging/index.html',
                               levels=levels.get('level'),
                               owners=owners.get('result'),
                               data=data.get('result'))
    except TemplateNotFound:
        abort(404)