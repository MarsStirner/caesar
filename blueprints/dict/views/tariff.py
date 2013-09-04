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


@module.route('/tariff/upload/', endpoint='tariff_upload')
def upload():
    try:
        return render_template('dict/tariff/upload.html')
    except TemplateNotFound:
        abort(404)


@module.route('/tariff/ajax_upload/', methods=['GET', 'POST'], endpoint='tariff_upload_ajax')
def ajax_upload():
    messages = list()
    errors = list()
    if request.method == 'POST':
        data_file = request.files.get('upload_file')
        file_path = os.path.join(UPLOADS_DIR, data_file.filename)
        if (data_file.content_type == 'application/x-dbf' or
                (data_file.content_type == 'application/octet-stream' and
                 os.path.splitext(data_file.filename)[1] == '.dbf')):
            with open(file_path, "wb") as f:
                f.write(data_file.stream.read())
            f.close()
            tariff = Tariff()
            try:
                data = tariff.parse(file_path)
            except Exception, e:
                errors.append(u'<b>%s</b>: ошибка обработки файла (%s)' % (data_file.filename, e))
            else:
                if data:
                    try:
                        result = tariff.send(data)
                        #TODO: сохранить выборку в БД для отчетов?
                    except SQLException, e:
                        errors.append(u'<b>%s</b>: внутренняя ошибка ядра во время обновления тарифов (%s)' %
                                      (data_file.filename, e))
                    except InvalidArgumentException, e:
                        errors.append(u'<b>%s</b>: в ядро переданы неверные аргументы (%s)' %
                                      (data_file.filename, e))
                    except TException, e:
                        errors.append(u'<b>%s</b>: внутренняя ошибка ядра во время обновления тарифов (%s)' %
                                      (data_file.filename, e))
                    except Exception, e:
                        errors.append(u'<b>%s</b>: внутренняя ошибка ядра во время обновления тарифов (%s)' %
                                      (data_file.filename, e))
                    else:
                        messages.append(u'Загрузка прошла успешно')
                        for value in result:
                            number = getattr(value, 'number', '')
                            c_tar = getattr(value, 'c_tar', '')
                            error = getattr(value, 'error', None)
                            if error is not None:
                                message = ''
                                if error:
                                    message = getattr(error, 'message', u'Сообщение об ошибке не определено')
                                errors.append(u'<b>%s %s</b>: %s' % (number, c_tar, message))
                            else:
                                messages.append(u'%s %s' % (number, c_tar))

                else:
                    errors.append(u'<b>%s</b>: нет данных для загрузки' % data_file.filename)
        else:
            errors.append(u'<b>%s</b>: не является DBF-файлом' % data_file.filename)
        return render_template('dict/tariff/upload_result.html', errors=errors, messages=messages)
