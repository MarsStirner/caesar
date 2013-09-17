# -*- encoding: utf-8 -*-
from flask import render_template, abort, request, redirect, url_for, flash

from jinja2 import TemplateNotFound
from flask.ext.wtf import Form, TextField, BooleanField, IntegerField, Required

from ..app import module
from ..models import ConfigVariables
from application.database import db
from application.utils import admin_permission, public_endpoint


@module.route('/')
@public_endpoint
def index():
    try:
        return render_template('reports/index.html')
    except TemplateNotFound:
        abort(404)


@module.route('/settings/', methods=['GET', 'POST'])
@admin_permission.require(http_exception=403)
def settings():
    try:
        class ConfigVariablesForm(Form):
            pass

        variables = db.session.query(ConfigVariables).order_by('id').all()
        for variable in variables:
            if variable.value_type == "int":
                setattr(ConfigVariablesForm,
                        variable.code,
                        IntegerField(variable.code, validators=[Required()], default="", description=variable.name))
            else:
                setattr(ConfigVariablesForm,
                        variable.code,
                        TextField(variable.code, validators=[Required()], default="", description=variable.name))

        form = ConfigVariablesForm()
        for variable in variables:
            form[variable.code].value = variable.value if variable.value else ""

        if form.validate_on_submit():
            for variable in variables:
                variable.value = form.data[variable.code]
            db.session.commit()
            flash(u'Настройки изменены')
            return redirect(url_for('.settings'))

        return render_template('reports/settings.html', form=form)
    except TemplateNotFound, e:
        abort(404)