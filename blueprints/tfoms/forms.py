# -*- coding: utf-8 -*-
from flask.ext.wtf import Form, TextField, BooleanField, IntegerField, Required
from models import Template

class CreateTemplateForm(Form):
    name = TextField('name', validators=[Required()], default="")
    archive = BooleanField('archive', default="true")

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        template = Template.query.filter_by(name=self.name.data).all()

        if len(template):
            self.name.errors.append('Имена шаблонов должны быть уникальны')
            return False

        return True

