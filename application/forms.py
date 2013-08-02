# -*- coding: utf-8 -*-
from flask.ext.wtf import Form, TextField, BooleanField, PasswordField, Required, RadioField


class EditUserForm(Form):

    login = TextField(u'Логин', validators=[Required()], default="")
    password = PasswordField(u'Пароль', default="")
    password_reply = PasswordField(u'Повторите пароль', default="")
    role = RadioField(u'Роль', coerce=int)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.password.data and self.password_reply.data and self.password.data != self.password_reply.data:
            self.password.errors.append(u'Пароли не совпадают')
            self.password_reply.errors.append(u'Пароли не совпадают')
            return False
        return True