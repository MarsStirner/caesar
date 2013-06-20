# -*- coding: utf-8 -*-
from flask.ext.wtf import Form, TextField, BooleanField, IntegerField, Required, validators
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


class ConfigVariablesForm(Form):
    smo_number = IntegerField('smo_namber', validators=[Required()], default="")
    lpu_infis_code = IntegerField('lpu_infis_code', validators=[Required()], default="")
    old_lpu_infis_code = IntegerField('old_lpu_infis_code', validators=[Required()], default="")
    core_service_url = TextField('core_service_url', validators=[Required()], default="")