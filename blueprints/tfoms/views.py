# -*- encoding: utf-8 -*-
import re
import os
from datetime import datetime

from flask import render_template, abort, request, redirect, jsonify, send_from_directory, url_for, json, current_app
from flask import flash
from wtforms import TextField, BooleanField, IntegerField, SelectField
from flask_wtf import Form
from wtforms.validators import Required
from flask.ext.sqlalchemy import Pagination

from jinja2 import TemplateNotFound, Environment, PackageLoader
from app import module, _config

from lib.thrift_service.ttypes import InvalidArgumentException, NotFoundException, SQLException, TException

from .forms import CreateTemplateForm
from .lib.tags_tree import TagTreeNode, TagTree, StandartTagTree
from .lib.data import DownloadWorker, DOWNLOADS_DIR, UPLOADS_DIR, UploadWorker, Reports, datetimeformat, UpdateWorker
from .lib.data import Contracts
from .lib.departments import Departments
from .models import Template, TagsTree, StandartTree, TemplateType, DownloadType, ConfigVariables
from .utils import save_template_tag_tree, save_new_template_tree
from application.database import db
from application.utils import admin_permission


PER_PAGE = 20
xml_encodings = ['windows-1251', 'utf-8']


@module.route('/')
def index():
    try:
        return render_template('{0}/index.html'.format(module.name))
    except TemplateNotFound:
        abort(404)


@module.route('/ajax_update_tables/', methods=['GET', 'POST'])
def ajax_update_tables():
    worker = UpdateWorker()
    error, message = None, None

    try:
        result = worker.update_tables()
    except NotFoundException, e:
        error = u'Ошибка при обновлении таблиц: %s' % e.message
    except TException, e:
        error = u'Ошибка при обновлении таблиц: %s' % e.message
    else:
        message = u'Обновление таблицы прошло успешно'
    return jsonify(message=message, error=error)


@module.route('/ajax_download/', methods=['GET', 'POST'])
def ajax_download():
    result = list()
    errors = list()
    templates = request.form.getlist('templates[]')
    start = datetime.strptime(request.form['start'], '%d.%m.%Y')
    end = datetime.strptime(request.form['end'], '%d.%m.%Y')
    #TODO: как-то покрасивее сделать?
    worker = DownloadWorker()
    for template_id in templates:
        try:
            file_url = worker.do_download(template_id, start, end, _config('lpu_infis_code'))
        except NotFoundException, e:
            template = db.session.query(Template).get(template_id)
            errors.append(u'<b>%s</b>: данных для выгрузки в заданный период не найдено (%s)' %
                          (template.name, e.message))
        except TException, e:
            template = db.session.query(Template).get(template_id)
            errors.append(u'<b>%s</b>: внутренняя ошибка ядра во время выборки данных (%s)' % (template.name, e))
        else:
            result.append(dict(url=file_url))
    return render_template('{0}/download/result.html'.format(module.name), files=result, errors=errors)


@module.route('/download/')
@module.route('/download/<string:template_type>/')
def download(template_type='xml'):
    try:
        templates = (db.session.query(Template)
                     .filter(Template.is_active == True,
                             Template.type.has(TemplateType.download_type.has(DownloadType.code == template_type)))
                     .all())
        contracts = Contracts().get_contracts(_config('lpu_infis_code'))
        return render_template('{0}/download/index.html'.format(module.name), templates=templates, contracts=contracts)
    except TemplateNotFound:
        abort(404)


@module.route('/download_file/<string:filename>')
def download_file(filename):
    """Выдаёт файлы на скачивание"""
    if filename:
        return send_from_directory(DOWNLOADS_DIR, filename, as_attachment=True, cache_timeout=0)


@module.route('/upload/')
def upload():
    try:
        return render_template('{0}/upload/index.html'.format(module.name))
    except TemplateNotFound:
        abort(404)


@module.route('/ajax_upload/', methods=['GET', 'POST'])
def ajax_upload():
    messages = list()
    errors = list()
    if request.method == 'POST':
        data_file = request.files.get('upload_file')
        file_path = os.path.join(UPLOADS_DIR, data_file.filename)
        if data_file.content_type == 'text/xml':
            with open(file_path, "wb") as f:
                f.write(data_file.stream.read())
            f.close()
            worker = UploadWorker()
            try:
                result = worker.parse(file_path)
            except TException, e:
                errors.append(u'<b>%s</b>: внутренняя ошибка ядра во время обновления данных (%s)'
                              % (data_file.filename, e))
            else:
                #TODO: добавить вывод подробной информации
                messages.append(u'Загрузка прошла успешно')
        else:
            errors.append(u'<b>%s</b>: не является XML-файлом' % data_file.filename)
        return render_template('{0}/upload/result.html'.format(module.name), errors=errors, messages=messages)


@module.route('/reports/', methods=['GET', 'POST'])
def reports():
    start = None
    end = None
    report = Reports()
    # if request.method == 'POST':
    #     start = datetime.strptime(request.form['start'], '%d.%m.%Y')
    #     end = datetime.strptime(request.form['end'], '%d.%m.%Y')

    data = report.get_bills(_config('lpu_infis_code'))
    try:
        current_app.jinja_env.filters['datetimeformat'] = datetimeformat
        return render_template('{0}/reports/index.html'.format(module.name), data=data, form=Form())
    except TemplateNotFound:
        abort(404)


@module.route('/reports/delete/<int:id>/', methods=['GET', 'POST'])
def delete_report(id):
    report = Reports()
    try:
        report.delete_bill(id)
    except TemplateNotFound:
        flash(u'Произошла ошибка удаления счёта')
    return redirect(url_for('.reports'))


@module.route('/reports/<int:bill_id>/', defaults={'page': 1}, methods=['GET'])
@module.route('/reports/<int:bill_id>/page/<int:page>/', methods=['GET'])
def report_cases(bill_id, page):
    report = Reports()
    data = report.get_bill_cases(bill_id)
    try:
        current_app.jinja_env.filters['datetimeformat'] = datetimeformat
        return render_template('{0}/reports/cases.html'.format(module.name), data=data)
    except TemplateNotFound:
        abort(404)


@module.route('/settings/', methods=['GET', 'POST'])
@admin_permission.require(http_exception=403)
def settings():
    try:
        class ConfigVariablesForm(Form):
            pass

        variables = ConfigVariables.query.order_by('id').all()
        for variable in variables:
            if variable.value_type == "text":
                setattr(ConfigVariablesForm, variable.code, TextField(variable.code,
                                                                      validators=[Required()], default="",
                                                                      description=variable.name))
            elif variable.value_type == "int":
                setattr(ConfigVariablesForm, variable.code, IntegerField(variable.code,
                                                                         validators=[Required()], default="",
                                                                         description=variable.name))
            elif variable.value_type == "enum" and variable.code == 'xml_encoding':
                setattr(ConfigVariablesForm,
                        variable.code,
                        SelectField(variable.code,
                                    description=variable.name,
                                    choices=[(choice, choice) for choice in xml_encodings],
                                    default=variable.value))

        form = ConfigVariablesForm()
        for variable in variables:
            form[variable.code].value = variable.value

        if form.validate_on_submit():
            for variable in variables:
                variable.value = form.data[variable.code]
            db.session.commit()
            flash(u'Настройки изменены')
            return redirect(url_for('.settings'))

        return render_template('{0}/settings.html'.format(module.name), form=form)
    except TemplateNotFound:
        abort(404)


@module.route('/settings_template/<string:template_type>/<int:id>', methods=['GET', 'POST'])
@admin_permission.require(http_exception=403)
def settings_template(template_type='patient', id=0):
    try:
        template_type_id = TemplateType.query.filter_by(code=template_type).first().id

        templates = Template.query.filter_by(type_id=template_type_id).all()
        templates_names = [template.name for template in templates]
        current_template = filter(lambda x: x.id == id, templates)

        if current_template[0].archive:
            archive = True
        else:
            archive = False

        form = CreateTemplateForm(name=current_template[0].name, archive=archive)

        tree_tags = [tag for tag in TagsTree.query.order_by(TagsTree.ordernum).filter_by(template_id=id)]
        tree_tags_ids = [tag.tag_id for tag in tree_tags]
        unused_tags = filter(lambda x: x.tag_id not in tree_tags_ids,
                             StandartTree.query.filter_by(template_type_id=template_type_id))
        if template_type in ('policlinic', 'hospital'):
            tag_tree = [TagTreeNode(tag, 0) for tag in tree_tags]
        else:
            root = TagTreeNode(TagsTree.query.filter_by(template_id=id).filter_by(parent_id=None).
                           join(TagsTree.tag).first(), 0)
            tree = TagTree(root, id)
            tag_tree = tree.load_tree(root, [root])

        if form.is_submitted():
            current_template_id = current_template[0].id
            data = request.form.items()

            if 'archive' in request.form:
                archive = True
            else:
                archive = False

            if request.form['btn'] == 'Save':
                save_template_tag_tree(data, current_template_id)
                current_template[0].name = request.form['name']
                current_template[0].archive = archive
                db.session.commit()
                return redirect(url_for('.settings_template', template_type=template_type, id=current_template_id))
            if request.form['btn'] == 'Save_as_new':
                new_template = Template(name=request.form['name'], archive=archive, type_id=template_type_id)
                db.session.add(new_template)
                db.session.commit()
                new_id = new_template.id
                save_new_template_tree(new_id, data)
                return redirect(url_for('.settings_template', template_type=template_type, id=new_id))

        return render_template('{0}/settings_templates/{1}.html'.format(module.name, template_type),
                               form=form,
                               templates=templates,
                               current_id=id,
                               tag_tree=tag_tree,
                               unused_tags=unused_tags,
                               templates_names=templates_names)
    except TemplateNotFound:
        abort(404)    


@module.route('/settings_template/', methods=['GET', 'POST'])
@module.route('/settings_template/<string:template_type>/', methods=['GET', 'POST'])
@module.route('/settings_template/<string:template_type>/<string:action>', methods=['POST', 'GET'])
@admin_permission.require(http_exception=403)
def add_new_template(template_type="patients", action="add_new"):
    try:
        template_type_id = TemplateType.query.filter_by(code=template_type).first().id
        form = CreateTemplateForm()

        if form.is_submitted():
            if form.validate():
                if 'archive' in request.form:
                    archive = True
                else:
                    archive = False

                new_template = Template(name=request.form['name'], archive=archive, type_id=template_type_id)
                db.session.add(new_template)
                db.session.commit()
                new_id = new_template.id

                data = request.form.items()
                save_new_template_tree(new_id, data)
                return redirect(url_for('.settings_template', template_type=template_type, id=new_id))
        else:
            unused_tags = []
            if template_type in ('policlinic', 'hospital'):
                tags_tree = [TagTreeNode(tag, 0) for tag in StandartTree.query.
                filter_by(template_type_id=template_type_id).order_by(StandartTree.ordernum).
                join(StandartTree.tag).all()]
            else:
                root = TagTreeNode(StandartTree.query.filter_by(template_type_id=template_type_id).
                                   filter_by(parent_id=None).first(), 0)
                tree = StandartTagTree(root, template_type_id)
                tags_tree = tree.load_tree(root, [root])

        templates = Template.query.filter_by(type_id=template_type_id).all()
        templates_names = [template.name for template in templates]

        return render_template('{0}/settings_templates/{1}.html'.format(module.name, template_type),
                               form=form,
                               templates=templates,
                               current_id=0,
                               tag_tree=tags_tree,
                               unused_tags=unused_tags,
                               templates_names=json.dumps(templates_names))
    except TemplateNotFound:
        abort(404)


@module.route('/settings_template/<string:template_type>/<string:action>/<int:id>', methods=['POST', 'GET'])
@admin_permission.require(http_exception=403)
def delete_template(action='delete_template', template_type='patient', id=id):
    try:
        current_template = Template.query.filter_by(id=id).first()
        db.session.delete(current_template)
        db.session.commit()

        return redirect(url_for('.add_new_template', template_type=template_type, action="add_new"))
    except TemplateNotFound:
        abort(404)


@module.route('/settings_template/<string:template_type>/activate/', methods=['POST'])
@admin_permission.require(http_exception=403)
def activate(template_type):
    try:
        if request.form:
            if 'activate' in request.form:
                id = request.form['activate']
                template = Template.query.filter_by(id=id).first()
                type = int(template.type_id)
                if template_type not in ('policlinic', 'hospital'):
                    deactivated = Template.query.filter_by(type_id=type).all()
                    for item in deactivated:
                        if item.id != id:
                            item.is_active = False
                template.is_active = True
                db.session.commit()
            elif 'deactivate' in request.form:
                active_template_id = request.form['deactivate']
                template = Template.query.filter_by(id=active_template_id).first()
                template.is_active = False
                db.session.commit()

        return jsonify()

    except TemplateNotFound:
        abort(404)


@module.route('/<string:page>.html')
def show_page(page):
    try:
        return render_template('{0}/{1}.html'.format(module.name, page))
    except TemplateNotFound:
        abort(404)


@module.route('/departments/')
@admin_permission.require(http_exception=403)
def departments():
    try:
        departments = list()
        obj = Departments(_config('lpu_infis_code'))
        departments = obj.get_departments()

        return render_template('{0}/settings_templates/departments.html'.format(module.name))

    except TemplateNotFound:
        abort(404)