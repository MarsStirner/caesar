# -*- encoding: utf-8 -*-
from datetime import datetime
from flask import flash, session, render_template, url_for, request, redirect
from ..app import _config, module
from ..lib.data import DownloadWorker, Contracts
from ..lib.departments import Departments
from ..lib.thrift_service.pnz.ttypes import InvalidArgumentException, NotFoundException, TException


def download_view(templates):
    contracts = Contracts().get_contracts(_config('lpu_infis_code'))
    obj = Departments(_config('lpu_infis_code'))
    departments = obj.get_departments()

    form_data = dict(templates=session.pop('templates', None),
                     departments=session.pop('departments', None),
                     start=session.pop('start', None),
                     end=session.pop('end', None),
                     contract_id=session.pop('contract_id', None),
                     primary=session.pop('primary', None))

    if not _config('mo_level'):
        flash(u'В <a href="{0}" class="text-error"><u>настройках</u></a> не задан уровень МО'.format(url_for('.settings')))

    return render_template('{0}/download/pnz/index.html'.format(module.name),
                           templates=templates,
                           contracts=contracts,
                           departments=departments,
                           mo_level=_config('mo_level'),
                           form_data=form_data)


def download_result_view():
    result = list()
    errors = list()
    session['templates'] = template_ids = [int(_id) for _id in request.form.getlist('templates[]')]
    department_ids = [int(_id) for _id in request.form.getlist('departments[]') if int(_id)]
    session['departments'] = [int(_id) for _id in request.form.getlist('departments[]')]
    session['start'] = start = datetime.strptime(request.form['start'], '%d.%m.%Y')
    session['end'] = end = datetime.strptime(request.form['end'], '%d.%m.%Y')
    session['contract_id'] = contract_id = int(request.form.get('contract_id'))
    primary = bool(int(request.form.get('primary')))
    session['primary'] = request.form.get('primary')
    #TODO: как-то покрасивее сделать?
    worker = DownloadWorker()
    try:
        result = worker.do_download(template_ids=template_ids,
                                    infis_code=_config('lpu_infis_code'),
                                    contract_id=contract_id,
                                    start=start,
                                    end=end,
                                    primary=primary,
                                    departments=department_ids)
    except ValueError, e:
        errors.append(u'Данных для выгрузки в заданный период не найдено (%s)' % e.message)
    except InvalidArgumentException, e:
        errors.append(u'Переданы некорректные данные ({0}:{1})'.format(e.code, e.message))
    except NotFoundException, e:
        errors.append(u'Данных для выгрузки в заданный период не найдено ({0}:{1})'.format(e.code, e.message))
    except TException, e:
        errors.append(u'Во время выборки данных возникла внутренняя ошибка ядра (%s)' % e)
    if errors:
        for error in errors:
            flash(error)
        return redirect(request.referrer)
    return render_template('{0}/download/result.html'.format(module.name), files=result, errors=errors)
