# -*- encoding: utf-8 -*-
import re
from datetime import datetime

from flask import render_template, abort, request, redirect, jsonify, send_from_directory, url_for

from jinja2 import TemplateNotFound
from app import module

from lib.thrift_service.ttypes import InvalidArgumentException, NotFoundException, SQLException, TException

from forms import CreateTemplateForm
from lib.tags_tree import TagTreeNode, TagTree, StandartTagTree
from lib.data import DownloadWorker, DOWNLOADS_DIR, UPLOADS_DIR
from models import Template, TagsTree, StandartTree, TemplateType, DownloadType
from utils import template_types, save_template_tag_tree, save_new_template_tree
from application.database import db
from config import LPU_INFIS_CODE

@module.route('/')
def index():
    try:
        return render_template('index.html')
    except TemplateNotFound:
        abort(404)


@module.route('/ajax_download/', methods=['GET', 'POST'])
def ajax_download():
    result = list()
    templates = request.form.getlist('templates[]')
    start = datetime.strptime(request.form['start'], '%d.%m.%Y')
    end = datetime.strptime(request.form['end'], '%d.%m.%Y')
    #TODO: как-то покрасивее сделать
    try:
        for template_id in templates:
            worker = DownloadWorker()
            file_url = worker.do_download(template_id, start, end, LPU_INFIS_CODE)
            result.append(dict(url=file_url))
        return render_template('download/result.html', files=result)
    except NotFoundException:
        return jsonify(error=u'В заданный период данных для выгрузки не найдено')


@module.route('/download/')
@module.route('/download/<string:template_type>/')
def download(template_type='xml'):
    try:
        templates = (db.session.query(Template)
                     .filter(Template.is_active == True,
                             Template.type.has(TemplateType.download_type.has(DownloadType.code == template_type)))
                     .all())
        return render_template('download/index.html', templates=templates)
    except TemplateNotFound:
        abort(404)


@module.route('/download_file/<string:filename>')
def download_file(filename):
    """Выдаёт файлы на скачивание"""
    if filename:
        return send_from_directory(DOWNLOADS_DIR, filename, as_attachment=True)


@module.route('/upload/')
def upload():
    try:
        return render_template('upload.html')
    except TemplateNotFound:
        abort(404)


@module.route('/reports/')
def reports():
    try:
        return render_template('reports.html')
    except TemplateNotFound:
        abort(404)


@module.route('/settings/')
def settings():
    try:
        return render_template('settings.html')
    except TemplateNotFound:
        abort(404)


@module.route('/settings_template/<string:template_type>/<int:id>', methods=['GET', 'POST'])
def settings_template(template_type='xml_patient', id=0):
    try:

        template_type_id = template_types[template_type]

        templates = Template.query.filter_by(type_id=template_type_id).all()
        current_template = filter(lambda x: x.id == id, templates)

        if current_template[0].archive:
            archive = 1
        else:
            archive = 0

        form = CreateTemplateForm(name=current_template[0].name, archive=archive)

        tree_tags = [tag for tag in TagsTree.query.order_by(TagsTree.ordernum).filter_by(template_id=id)]
        tree_tags_ids = [tag.tag_id for tag in tree_tags]
        unused_tags = filter(lambda x: x.tag_id not in tree_tags_ids,
                             StandartTree.query.filter_by(template_type_id=template_type_id))
        if template_type == 'dbf':
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
                archive = 1
            else:
                archive = 0

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

        return render_template('settings_templates/%s.html' % template_type, form=form, templates=templates,
                               current_id=id, tag_tree=tag_tree, unused_tags=unused_tags)
    except TemplateNotFound:
        abort(404)    


@module.route('/settings_template/', methods=['GET', 'POST'])
@module.route('/settings_template/<string:template_type>/', methods=['GET', 'POST'])
@module.route('/settings_template/<string:template_type>/<string:action>', methods=['POST', 'GET'])
def add_new_template(template_type='xml_patient', action="add_new"):
    try:
        template_type_id = template_types[template_type]
        form = CreateTemplateForm()

        if form.is_submitted():

            if 'archive' in request.form:
                archive = 1
            else:
                archive = 0

            new_template = Template(name=request.form['name'], archive=archive, type_id=template_type_id)
            db.session.add(new_template)
            db.session.commit()
            new_id = new_template.id

            data = request.form.items()
            save_new_template_tree(new_id, data)
            return redirect(url_for('.settings_template', template_type=template_type, id=new_id))
        else:
            unused_tags = []
            if template_type == 'dbf':
                tags_tree = [TagTreeNode(tag, 0) for tag in StandartTree.query.
                filter_by(template_type_id=template_type_id).order_by(StandartTree.ordernum).
                join(StandartTree.tag).all()]
            else:
                root = TagTreeNode(StandartTree.query.filter_by(template_type_id=template_type_id).
                                   filter_by(parent_id=None).first(), 0)
                tree = StandartTagTree(root, template_type_id)
                tags_tree = tree.load_tree(root, [root])

        templates = Template.query.filter_by(type_id=template_type_id).all()

        return render_template('settings_templates/%s.html' % template_type, form=form, templates=templates,
                               current_id=0, tag_tree=tags_tree, unused_tags=unused_tags)
    except TemplateNotFound:
        abort(404)


@module.route('/settings_template/<string:template_type>/<string:action>/<int:id>', methods=['POST', 'GET'])
def delete_template(action='delete_template', template_type='xml_patient', id=id):
    try:
        current_template = Template.query.filter_by(id=id).first()
        db.session.delete(current_template)
        db.session.commit()

        return redirect(url_for('.add_new_template', template_type=template_type, action="add_new"))
    except TemplateNotFound:
        abort(404)

@module.route('/settings_template/<string:template_type>/activate/', methods=['POST'])
def activate(template_type):
    try:
        if request.form:
            if 'activate' in request.form:
                id = request.form['activate']
                template = Template.query.filter_by(id=id).first()
                type = int(template.type_id)
                if template_type != 'dbf':
                    deactivated = Template.query.filter_by(type_id=type).all()
                    for item in deactivated:
                        if item.id != id:
                            item.is_active = 0
                template.is_active = 1
                db.session.commit()
            elif 'deactivate' in request.form:
                active_template_id = request.form['deactivate']
                template = Template.query.filter_by(id=active_template_id).first()
                template.is_active = 0
                db.session.commit()

        return jsonify()

    except TemplateNotFound:
        abort(404)

@module.route('/<string:page>.html')
def show_page(page):
    try:
        return render_template('/%s.html' % page)
    except TemplateNotFound:
        abort(404)