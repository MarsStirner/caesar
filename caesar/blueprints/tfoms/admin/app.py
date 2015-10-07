# -*- coding: utf-8 -*-
from flask import Flask, request, session
from flask.ext.admin import Admin
from flask.ext.babelex import Babel
import views
from flask.ext.admin.contrib.sqlamodel import ModelView
from ..app import app
from ..models import *

import config

admin = Admin(app, name=u'Управление Тегами', url='/tfoms/admin')

# Initialize babel
babel = Babel(app)


@babel.localeselector
def get_locale():
    override = request.args.get('lang')

    if override:
        session['lang'] = override

    return session.get('lang', 'ru')


admin.add_view(ModelView(DownloadType, db.session, name=u'Тип выгрузки'))
admin.add_view(views.TemplateTypeView(db.session, name=u'Тип шаблона'))
admin.add_view(views.TemplateView(db.session, name=u'Шаблоны'))
admin.add_view(ModelView(Tag, db.session, name=u'Тэги'))
admin.add_view(views.StandartTreeView(db.session, name=u'StandartTree'))
admin.add_view(views.TagsTreeView(db.session, name=u'TagsTree'))

