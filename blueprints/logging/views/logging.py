# -*- encoding: utf-8 -*-
from ast import literal_eval
from flask import render_template, abort, request, redirect, url_for, current_app

from jinja2 import TemplateNotFound, Environment, PackageLoader

from ..app import module, _config
from ..lib.data import Log_Data
from ..lib.helpers import datetimeformat_filter, strpdatetime_filter, nl2br_filter
from datetime import datetime


@module.route('/', methods=['GET', 'POST'])
def index():
    current_app.jinja_env.filters['datetimeformat'] = datetimeformat_filter
    current_app.jinja_env.filters['strptime'] = strpdatetime_filter
    current_app.jinja_env.filters['nl2br'] = nl2br_filter
    log_obj = Log_Data()
    levels = log_obj.get_levels()
    owners = log_obj.get_owners()
    find = dict()
    if request.form:
        owner = request.form.get('owner')
        if owner:
            try:
                owner = literal_eval(owner)
            except Exception, e:
                print e
            else:
                find['owner'] = owner
        level = request.form.get('level')
        if level:
            find['level'] = level
        start = request.form.get('start')
        end = request.form.get('end')
        if start:
            find['start'] = datetime.strptime(start, '%d.%m.%Y').date()
        if end:
            find['end'] = datetime.strptime(end, '%d.%m.%Y').date()

    data = log_obj.get_list(find=find)
    try:
        return render_template('logging/index.html',
                               levels=levels.get('level') if levels else None,
                               owners=owners.get('result') if owners else None,
                               data=data.get('result') if data else None)
    except TemplateNotFound:
        abort(404)