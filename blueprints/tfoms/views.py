# -*- encoding: utf-8 -*-
import re

from flask import render_template, abort, request, jsonify
from flask.ext.wtf import Form, TextField, Required, IntegerField

from jinja2 import TemplateNotFound
from app import module

from .forms import CreateTemplateForm
from blueprints.tfoms.lib.tags_tree import TagTreeNode, TagTree, StandartTagTree
from models import Template, TagsTree, StandartTree, Tag
from application.database import db

@module.route('/')
def index():
    try:
        return render_template('index.html')
    except TemplateNotFound:
        abort(404)


@module.route('/download/')
def download():
    try:
        return render_template('download.html')
    except TemplateNotFound:
        abort(404)


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


@module.route('/settings_template/', methods=['GET', 'POST'])
@module.route('/settings_template/<string:template_type>/', methods=['GET', 'POST'])
def settings_template(template_type='xml_patient'):
    try:
        form = CreateTemplateForm()

        templates = Template.query.all()
        templates_ids = [template.id for template in templates]
        templates_names = [template.name for template in templates]        

        root = TagTreeNode(StandartTree.query.filter_by(template_type_id=1).filter_by(parent_id=None).
                           join(TagsTree.tag).first(), 0)
        tree = StandartTagTree(root, 1)
        unused_tags = []

        return render_template('settings_templates/%s.html' % template_type, form=form, templates_ids=templates_ids,
                               templates_names=templates_names, tag_tree=tree.load_tree(root, [root]),
                               unused_tags=unused_tags)
    except TemplateNotFound:
        abort(404)

@module.route('/settings_template/<string:template_type>/<int:id>', methods=['GET', 'POST'])
def save_template(id=1, template_type='xml_patient'):
    try:

        templates = Template.query.all()
        templates_ids = [template.id for template in templates]
        templates_names = [template.name for template in templates]

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
        unused_tags = filter(lambda x: x.tag_id not in tree_tags, StandartTree.query.filter_by(template_type_id=1))

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
            return render_template('settings_templates/%s.html' % template_type, form=form, current_id=id,
                                   templates_ids=templates_ids, templates_names=templates_names,
                                   tag_tree=tree.load_tree(root, [root]), unused_tags=unused_tags, test="456", data=data)

        return render_template('settings_templates/%s.html' % template_type, form=form, current_id=id,
                               templates_ids=templates_ids, templates_names=templates_names,
                               tag_tree=tree.load_tree(root, [root]), unused_tags=unused_tags, test=id)
    except TemplateNotFound:
        abort(404)    
        
@module.route('/settings_template/<string:template_type>/<string:action>', methods=['POST', 'GET'])
def add_new_template(action='add_new', template_type='xml_patient'):
    try:
        form = CreateTemplateForm()

        templates = Template.query.all()
        templates_ids = [template.id for template in templates]
        templates_names = [template.name for template in templates]        

        root = TagTreeNode(StandartTree.query.filter_by(template_type_id=1).filter_by(parent_id=None).
                           join(TagsTree.tag).first(), 0)
        tree = StandartTagTree(root, 1)
        unused_tags = []
        data = []
        if form.is_submitted():

            if 'archive' in request.form:
                archive = 1
            else:
                archive = 0

            new_template = Template(name=request.form['name'], archive=archive, type_id=1)
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
            return render_template('settings_templates/%s.html' % template_type, form=form, current_id=id,
                                   templates_ids=templates_ids, templates_names=templates_names,
                                   tag_tree=tree.load_tree(root, [root]), unused_tags=unused_tags, test=existing_tags)
        return render_template('settings_templates/%s.html' % template_type, form=form, current_id=id,
                               templates_ids=templates_ids, templates_names=templates_names,
                               tag_tree=tree.load_tree(root, [root]), unused_tags=unused_tags)
    except TemplateNotFound:
        abort(404)


@module.route('/<string:page>.html')
def show_page(page):
    try:
        return render_template('/%s.html' % page)
    except TemplateNotFound:
        abort(404)