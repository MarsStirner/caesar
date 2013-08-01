# -*- coding: utf-8 -*-
from flask.ext.wtf import Form, TextField, BooleanField, PasswordField, Required


class EditUserForm(Form):

    login = TextField('login', validators=[Required()], default="")
    password = PasswordField('password', validators=[Required()], default="")
    password_reply = PasswordField('password', validators=[Required()], default="")

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.password != self.password_reply:
            self.password.errors.append('Пароли не совпадают')
            self.password_reply.errors.append('Пароли не совпадают')
            return False
        return True