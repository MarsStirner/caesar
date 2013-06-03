# -*- encoding: utf-8 -*-
from flask import render_template, abort
from jinja2 import TemplateNotFound
from app import module

from .forms  import CreateTemplateForm
from .utils  import get_tree
from models import Template, TagsTree, Tag 


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


@module.route('/settings_template/')
@module.route('/settings_template/<string:template_type>/')
def settings_template(template_type='xml_patient'):
    try:
        form = CreateTemplateForm()
        templates = Template.query.all()
        templates_ids = [template.id for template in templates]
        templates_names = [template.name for template in templates]        
        
        root = TagsTree.query.filter_by(template_id=1).filter_by(parent_id=None).join(TagsTree.tag).first()
        tree = get_tree(1, root, 0, [[root, 0]]) 
        
        tree_tags = [tag.tag_id for tag in TagsTree.query.filter_by(template_id=1)]

        unused_tags = filter(lambda x:x.id not in tree_tags, Tag.query.all())
                
        return render_template('settings_templates/%s.html' % template_type, templates_ids = templates_ids, 
                               templates_names = templates_names, tag_tree = tree, unused_tags = unused_tags)
    except TemplateNotFound:
        abort(404)

@module.route('/settings_template/<string:template_type>/<int:id>/', methods = ['GET', 'POST'])        
def save_template(id='1', template_type='xml_patient'):
    try:
        form = CreateTemplateForm()
        templates = Template.query.all()
        templates_ids = [template.id for template in templates]
        templates_names = [template.name for template in templates]        
        
        root = TagsTree.query.filter_by(template_id=1).filter_by(parent_id=None).first()

        tree = get_tree(1, root, 0, [[root, 0]]) 
                
        return render_template('settings_templates/%s.html' % template_type, current_id = id, templates_ids = templates_ids, 
                               templates_names = templates_names, tag_tree = tree)
    except TemplateNotFound:
        abort(404)    

@module.route('/<string:page>.html')
def show_page(page):
    try:
        return render_template('/%s.html' % page)
    except TemplateNotFound:
        abort(404)