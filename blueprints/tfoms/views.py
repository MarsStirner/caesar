# -*- encoding: utf-8 -*-
import re
from datetime import datetime

from flask import render_template, abort, request, jsonify, send_from_directory

from jinja2 import TemplateNotFound
from app import module

from .forms import CreateTemplateForm
from blueprints.tfoms.lib.tags_tree import TagTreeNode, TagTree, StandartTagTree
from models import Template, TagsTree, StandartTree
from utils import template_types
from application.database import db
from .lib.data import DownloadWorker, DOWNLOADS_DIR, UPLOADS_DIR
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
    data = [request.form['data']]
    for template_id in data:
        template_id = 16
        start = datetime(2013, 01, 01)
        end = datetime(2013, 06, 01)
        worker = DownloadWorker()
        file_name, file_url = worker.do_download(template_id, start, end, LPU_INFIS_CODE)
        result.append(dict(name=file_name, url=file_url))
    return render_template('download/result.html', files=result)


@module.route('/download/')
@module.route('/download/<string:template_type>/')
def download(template_type='xml'):
    try:
        # templates = db.session.query(Template).filter(Template.type.code == template_type, Template.id == 16).all()
        templates = db.session.query(Template).filter(Template.id == 16).all()
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


# @module.route('/settings_template', methods=['GET', 'POST'])
# def settings_template():
#     try:
#         template_type = "xml_patient"
#         form = CreateTemplateForm()
#         templates = Template.query.all()
#
#         root = TagTreeNode(StandartTree.query.filter_by(template_type_id=1).filter_by(parent_id=None).
#                            join(TagsTree.tag).first(), 0)
#         tree = StandartTagTree(root, 1)
#         unused_tags = []
#         if form.is_submitted():
#
#             if 'archive' in request.form:
#                 archive = 1
#             else:
#                 archive = 0
#
#             new_template = Template(name=request.form['name'], archive=archive, type_id=1)
#             db.session.add(new_template)
#             db.session.commit()
#             new_id = new_template.id
#
#             data = request.form.items()
#             existing_tags = {}
#
#             for item in data:
#                 match = re.match(r'tag\[(\d+),(\d+)\]', item[0])
#                 if match:
#                     standart_parent_id, ordernum = item[1].split(',')
#                     if standart_parent_id != 'None' and standart_parent_id not in existing_tags:
#                         new_parent = TagsTree(tag_id=1, template_id=new_id)#tag_id=None
#                         db.session.add(new_parent)
#                         db.session.commit()
#                         new_parent_id = new_parent.id
#                         existing_tags[standart_parent_id] = new_parent_id
#                     if match.group(1) not in existing_tags:
#                         if standart_parent_id == 'None':
#                             new_tag_tree_item = TagsTree(tag_id=int(match.group(2)), parent_id=None,
#                                                          template_id=new_id, ordernum=ordernum)
#                         else:
#                             new_tag_tree_item = TagsTree(tag_id=int(match.group(2)),
#                                                          parent_id=existing_tags[standart_parent_id],
#                                                          template_id=new_id, ordernum=ordernum)
#                         db.session.add(new_tag_tree_item)
#                         db.session.commit()
#                         existing_tags[match.group(1)] = new_tag_tree_item.id
#                     else:
#                         new_tag_tree_item = TagsTree.query.filter_by(id=existing_tags[match.group(1)]).first()
#                         if standart_parent_id == 'None':
#                             new_tag_tree_item.parent_id = None
#                         else:
#                             new_tag_tree_item.parent_id = existing_tags[standart_parent_id]
#                         new_tag_tree_item.tag_id = int(match.group(2))
#                         new_tag_tree_item.ordernum = ordernum
#                         db.session.commit()
#             return render_template('settings_templates/%s.html' % template_type, form=form, templates=templates,
#                                    current_id=id, tag_tree=tree.load_tree(root, [root]), unused_tags=unused_tags)
#
#         return render_template('settings_templates/%s.html' % template_type, form=form, templates=templates,
#                                tag_tree=tree.load_tree(root, [root]), unused_tags=unused_tags, test="111")
#     except TemplateNotFound:
#         abort(404)

@module.route('/settings_template/')
@module.route('/settings_template/<string:template_type>/', methods=['GET', 'POST'])
def settings_template(template_type='xml_patient', id=0):
    try:
        template_type_id = template_types[template_type]
        if not request.args.get('id'):

            form = CreateTemplateForm()
            templates = Template.query.filter_by(type_id=template_type_id).all()
            unused_tags = []

            root = TagTreeNode(StandartTree.query.filter_by(template_type_id=template_type_id).
                               filter_by(parent_id=None).join(TagsTree.tag).first(), 0)

            tree = StandartTagTree(root, template_type_id)
            tags_tree = tree.load_tree(root, [root])

            return render_template('settings_templates/%s.html' % template_type, form=form, templates=templates,
                                   tag_tree=tags_tree, unused_tags=unused_tags, test="")
        else:
            id = int(request.args.get('id'))
            templates = Template.query.filter_by(type_id=template_type_id).all()

            current_template = filter(lambda x: x.id == id, templates)

            if current_template[0].archive:
                archive = 1
            else:
                archive = 0

            form = CreateTemplateForm(name=current_template[0].name, archive=archive)

            root = TagTreeNode(TagsTree.query.filter_by(template_id=id).filter_by(parent_id=None).
                               join(TagsTree.tag).first(), 0)
            tree = TagTree(root, id)
            tree_tags = [tag.tag_id for tag in TagsTree.query.filter_by(template_id=id)]
            unused_tags = filter(lambda x: x.tag_id not in tree_tags, StandartTree.query.filter_by(template_type_id=template_type_id))

            if form.is_submitted():
                data = request.form.items()
                new_tags = {}
                for item in data:
                    match = re.match(r'tag\[(\d+),(\d+)\]', item[0])
                    if match:
                        parent_id, ordernum = item[1].split(',')
                        tag_id = match.group(1)
                        if parent_id != u'None':# корневой элемент не меняем
                            tag_tree_item = TagsTree.query.filter_by(id=int(tag_id)).first()
                            tag_tree_item.parent_id = int(parent_id)
                            tag_tree_item.ordernum = int(ordernum)

                    match = re.match(r'tag\[None,(\d+)\]', item[0])
                    if match:
                        parent_id, ordernum = item[1].split(',')
                        parent_id_t = re.match(r't(\d+)', parent_id)
                        if parent_id_t:
                            if parent_id_t.group(1) not in new_tags:
                                new_tag_tree_item = TagsTree(tag_id=int(parent_id_t.group(1)),
                                                             parent_id=1,#parent_id=None
                                                             template_id=current_template[0].id, ordernum=ordernum)
                                db.session.add(new_tag_tree_item)
                                db.session.commit()
                                new_tags[parent_id_t.group(1)] = new_tag_tree_item.id

                            if match.group(1) not in new_tags:
                                new_tag_tree_item = TagsTree(tag_id=int(match.group(1)),
                                                             parent_id=new_tags[parent_id_t.group(1)],
                                                             template_id=current_template[0].id, ordernum=ordernum)
                                db.session.add(new_tag_tree_item)
                                db.session.commit()
                                new_tags[match.group(1)] = new_tag_tree_item.id
                            else:
                                new_tag_tree_item = TagsTree.query.filter_by(id=new_tags[match.group(1)]).first()
                                new_tag_tree_item.parent_id = new_tags[parent_id_t.group(1)]
                                db.session.commit()

                        else:
                            if match.group(1) not in new_tags:
                                new_tag_tree_item = TagsTree(tag_id=int(match.group(1)), parent_id=int(parent_id),
                                                             template_id=current_template[0].id, ordernum=ordernum)
                                db.session.add(new_tag_tree_item)
                                db.session.commit()
                                new_tags[match.group(1)] = new_tag_tree_item.id
                            else:
                                new_tag_tree_item = TagsTree.query.filter_by(id=new_tags[match.group(1)]).first()
                                new_tag_tree_item.parent_id = int(parent_id)
                                db.session.commit()

                    match = re.match(r'removedtag\[(\d+),(\d+)\]', item[0])
                    if match:
                        removed_tag_tree_item = TagsTree.query.filter_by(id=match.group(1)).first()
                        db.session.delete(removed_tag_tree_item)
                        db.session.commit()


                current_template[0].name = request.form['name']

                if 'archive' in request.form:
                    current_template[0].archive = 1
                else:
                    current_template[0].archive = 0

                db.session.commit()
                return render_template('settings_templates/%s.html' % template_type, form=form, templates=templates,
                                       current_id=id, tag_tree=tree.load_tree(root, [root]), unused_tags=unused_tags)

            return render_template('settings_templates/%s.html' % template_type, form=form, templates=templates,
                                   current_id=id, tag_tree=tree.load_tree(root, [root]), unused_tags=unused_tags)
    except TemplateNotFound:
        abort(404)    


@module.route('/settings_template/<string:template_type>/<string:action>', methods=['POST', 'GET'])
def add_new_template(action='add_new', template_type='xml_patient'):
    try:
        template_type_id = template_types[template_type]
        form = CreateTemplateForm()

        templates = Template.query.filter_by(type_id=template_type_id).all()
        unused_tags = []

        root = TagTreeNode(StandartTree.query.filter_by(template_type_id=template_type_id).
                           filter_by(parent_id=None).join(TagsTree.tag).first(), 0)

        tree = StandartTagTree(root, template_type_id)
        tags_tree = tree.load_tree(root, [root])
        test = ""
        if form.is_submitted():

            if 'archive' in request.form:
                archive = 1
            else:
                archive = 0
            test = "save"
            new_template = Template(name=request.form['name'], archive=archive, type_id=template_type_id)
            db.session.add(new_template)
            db.session.commit()
            new_id = new_template.id

            data = request.form.items()
            existing_tags = {}

            for item in data:
                match = re.match(r'tag\[(\d+),(\d+)\]', item[0])
                if match:
                    standart_parent_id, ordernum = item[1].split(',')
                    if standart_parent_id != 'None' and standart_parent_id not in existing_tags:
                        new_parent = TagsTree(tag_id=1, template_id=new_id)#tag_id=None
                        db.session.add(new_parent)
                        db.session.commit()
                        new_parent_id = new_parent.id
                        existing_tags[standart_parent_id] = new_parent_id
                    if match.group(1) not in existing_tags:
                        if standart_parent_id == 'None':
                            new_tag_tree_item = TagsTree(tag_id=int(match.group(2)), parent_id=None,
                                                         template_id=new_id, ordernum=ordernum)
                        else:
                            new_tag_tree_item = TagsTree(tag_id=int(match.group(2)),
                                                         parent_id=existing_tags[standart_parent_id],
                                                         template_id=new_id, ordernum=ordernum)
                        db.session.add(new_tag_tree_item)
                        db.session.commit()
                        existing_tags[match.group(1)] = new_tag_tree_item.id
                    else:
                        new_tag_tree_item = TagsTree.query.filter_by(id=existing_tags[match.group(1)]).first()
                        if standart_parent_id == 'None':
                            new_tag_tree_item.parent_id = None
                        else:
                            new_tag_tree_item.parent_id = existing_tags[standart_parent_id]
                        new_tag_tree_item.tag_id = int(match.group(2))
                        new_tag_tree_item.ordernum = ordernum
                        db.session.commit()
            return render_template('settings_templates/%s.html' % template_type, form=form, templates=templates,
                                   current_id=id, tag_tree=tags_tree, unused_tags=unused_tags, test=test)
        return render_template('settings_templates/%s.html' % template_type, form=form, templates=templates,
                               current_id=id, tag_tree=tags_tree, unused_tags=unused_tags, test=test)
    except TemplateNotFound:
        abort(404)


@module.route('/<string:page>.html')
def show_page(page):
    try:
        return render_template('/%s.html' % page)
    except TemplateNotFound:
        abort(404)