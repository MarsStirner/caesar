# -*- coding: utf-8 -*-
from application.database import db
from .app import module

TABLE_PREFIX = module.name


class DownloadType(db.Model):
    """Тип выгрузки"""
    __tablename__ = '%s_download_type' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.Unicode(10), unique=True)

    def __init__(self, code):
        self.code = code

    def __repr__(self):
        return '<DownloadType %r>' % self.code


class TemplateType(db.Model):
    """Тип шаблона"""
    __tablename__ = '%s_template_type' % TABLE_PREFIX
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    
    download_type_id = db.Column(db.Integer, db.ForeignKey('%s_download_type.id' % TABLE_PREFIX), index=True)
    
    #templated_type = db.relationship('DownloadType', backref=backref('template_type', order_by=id))  

    def __init__(self, type_name, download_type_id):
        self.name = type_name
        self.download_type_id = download_type_id

    def __repr__(self):
        return '<TemplateType %r>' % self.name

    
class Template(db.Model):
    """Шаблоны"""
    __tablename__ = '%s_template' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    archive = db.Column(db.Boolean, default=False)
    
    #user = db.Column(db.Integer, db.ForeignKey('.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('%s_template_type.id' % TABLE_PREFIX), index=True)

    #template = db.relationship('TemplateType', backref=backref('templates', order_by=id)) 
    
    def __init__(self, code, name, archive, type_id):
        self.code = code
        self.name = name
        self.archive = archive
        self.type_id = type_id

    def __repr__(self):
        return '<Template %r>' % self.name


class TagTemplateType(db.Model):
    __tablename__ = '%s_tag_template_type' % TABLE_PREFIX

    tag_id = db.Column(db.Integer, db.ForeignKey('%s_tag.id' % TABLE_PREFIX), primary_key=True, nullable=False)
    template_type_id = db.Column(db.Integer,
                                 db.ForeignKey('%s_template_type.id' % TABLE_PREFIX),
                                 primary_key=True,
                                 nullable=False)

    # db.UniqueConstraint(tag_id, template_type_id)


class Tag(db.Model):
    """Теги"""
    __tablename__ = '%s_tag' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.Unicode(80))
    download_type_id = db.Column(db.Integer, db.ForeignKey('%s_download_type.id' % TABLE_PREFIX), index=True)
    
    # many to many TemplateType<->Tag
    template_types = db.relationship('TemplateType', secondary='TagTemplateType', backref='tags')

    def __repr__(self):
        return '<Tag %r>' % self.name

 
class StandartTree(db.Model):
    """Эталонная структура дерева для каждого из типов шаблонов, с использованием всех тегов"""
    __tablename__ = '%s_standart_tree' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('%s_tag.id' % TABLE_PREFIX), index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('%s_tags_tree.id' % TABLE_PREFIX), index=True)
    template_type_id = db.Column(db.Integer, db.ForeignKey('%s_template_type.id' % TABLE_PREFIX), index=True)
    is_necessary = db.Column(db.Boolean)
    
    
class TagsTree(db.Model): 
    """Древовидная структура тегов"""
    __tablename__ = '%s_tags_tree' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('%s_tag.id' % TABLE_PREFIX), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('%s.id' % __tablename__), index=True)
    
    template_id = db.Column(db.Integer, db.ForeignKey('%s_template.id' % TABLE_PREFIX), nullable=False, index=True)

    def __init__(self, tag_name, parent_tag, template_id):
        self.tag_id = tag_name
        self.parent_id = parent_tag
        self.template_id = template_id
