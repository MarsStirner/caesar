# -*- encoding: utf-8 -*-
from datetime import datetime
from flask import flash, session, render_template, url_for, request, redirect
from ..app import _config, module
from ..lib.data import DownloadWorker
from ..lib.thrift_service.spb.ttypes import InvalidDateIntervalException, TException


def download_view(templates):

    form_data = dict(templates=session.pop('templates', None),
                     start=session.pop('start', None),
                     end=session.pop('end', None))

    return render_template('{0}/download/spb/index.html'.format(module.name),
                           templates=templates,
                           form_data=form_data)


def download_result_view():
    result = list()
    errors = list()
    session['templates'] = template_ids = [int(_id) for _id in request.form.getlist('templates[]')]
    session['start'] = start = datetime.strptime(request.form['start'], '%d.%m.%Y')
    session['end'] = end = datetime.strptime(request.form['end'], '%d.%m.%Y')
    worker = DownloadWorker()
    try:
        result = worker.do_download(template_ids=template_ids, start=start, end=end)
    except ValueError, e:
        errors.append(u'Данных для выгрузки в заданный период не найдено (%s)' % e.message)
    except InvalidDateIntervalException, e:
        errors.append(u'Передан неверный интервал ({0}:{1})'.format(e.code, e.message))
    except TException, e:
        errors.append(u'Во время выборки данных возникла внутренняя ошибка ядра (%s)' % e)
    if errors:
        for error in errors:
            flash(error)
        return redirect(request.referrer)
    return render_template('{0}/download/result.html'.format(module.name), files=result, errors=errors)