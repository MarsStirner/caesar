# -*- encoding: utf-8 -*-
from flask import render_template, abort, request, redirect, url_for, flash

from jinja2 import TemplateNotFound
from flask.ext.wtf import Form, TextField, BooleanField, IntegerField, Required

from application.app import app, db
from application.context_processors import general_menu
from models import Settings


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/settings/', methods=['GET', 'POST'])
def settings():
    try:
        class ConfigVariablesForm(Form):
            pass

        variables = db.session.query(Settings).order_by('id').all()
        for variable in variables:
            setattr(ConfigVariablesForm,
                    variable.code,
                    TextField(variable.code, validators=[Required()], default="", description=variable.name))

        form = ConfigVariablesForm()
        for variable in variables:
            form[variable.code].value = variable.value

        if form.validate_on_submit():
            for variable in variables:
                variable.value = form.data[variable.code]
            db.session.commit()
            flash(u'Настройки изменены')
            return redirect(url_for('settings'))

        return render_template('settings.html', form=form)
    except TemplateNotFound:
        abort(404)