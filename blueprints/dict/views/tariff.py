# -*- encoding: utf-8 -*-
import os
from flask import render_template, abort, request, redirect, url_for

from jinja2 import TemplateNotFound, Environment, PackageLoader
from flask.ext.wtf import Form, TextField, BooleanField, IntegerField, Required

from ..lib.thrift_service.TARIFF.ttypes import InvalidArgumentException, SQLException, TException
from ..app import module, _config
from ..lib.data import Tariff, UPLOADS_DIR
from ..models import ConfigVariables
from application.database import db


@module.route('/tariff/')
def index():
    try:
        return render_template('tariff/index.html')
    except TemplateNotFound:
        abort(404)


@module.route('/tariff/upload/')
def upload():
    try:
        return render_template('tariff/upload.html')
    except TemplateNotFound:
        abort(404)


@module.route('/tariff/ajax_upload/', methods=['GET', 'POST'])
def ajax_upload():
    messages = list()
    errors = list()
    if request.method == 'POST':
        data_file = request.files.get('upload_file')
        file_path = os.path.join(UPLOADS_DIR, data_file.filename)
        if data_file.content_type == 'dbf/dbf':
            with open(file_path, "wb") as f:
                f.write(data_file.stream.read())
            f.close()
            tariff = Tariff()
            try:
                result = tariff.parse(file_path)
            except Exception, e:
                errors.append(u'<b>%s</b>: ошибка обработки файла (%s)' % (data_file.filename, e))
            else:

                #TODO: добавить вывод подробной информации
                messages.append(u'Загрузка прошла успешно')
        else:
            errors.append(u'<b>%s</b>: не является DBF-файлом' % data_file.filename)
        return render_template('tariff/upload_result.html', errors=errors, messages=messages)
