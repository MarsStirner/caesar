# -*- coding: utf-8 -*-
from flask.ext.wtf import Form, TextField, BooleanField, Required


class CreateTemplateForm(Form):
    name = TextField('name', validators = [Required()], default="" )
    archive = BooleanField('archive')