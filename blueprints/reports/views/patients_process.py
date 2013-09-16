# -*- encoding: utf-8 -*-
from datetime import datetime
from flask import render_template, abort, request, redirect, url_for
from flask.ext.wtf import Form

from jinja2 import TemplateNotFound
from flask.ext.wtf import Form, TextField, BooleanField, IntegerField, Required

from ..app import module
from ..lib.data import Patients_Process


@module.route('/patients_process/', methods=['GET', 'POST'])
def patients_process():
    try:
        errors = list()
        if request.method == 'POST':
            try:
                data_obj = Patients_Process()
            except AttributeError, e:
                errors.append(e.message)
            else:
                start = datetime.strptime(request.form['start'], '%d.%m.%Y')
                end = datetime.strptime(request.form['end'], '%d.%m.%Y')
                priemn_postup = data_obj.get_priemn_postup(start, end)
        return render_template('reports/patients_process/index.html', form=Form(), errors=errors)
    except TemplateNotFound:
        abort(404)