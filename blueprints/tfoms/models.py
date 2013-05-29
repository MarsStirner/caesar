# -*- coding: utf-8 -*-
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class DownloadType(db.Model):
    '''
        Тип выгрузки
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True)
   
    def __init__(self, download_type_name):
        self.name = download_type_name

    def __repr__(self):
        return '<DownloadType %r>' % self.name

class TemplateType(db.Model):
    '''
        Тип шаблона
    '''
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True)
    
    download_type_id = db.Column(db.Integer, db.ForeignKey('download_type.id'))
    
    #templated_type = db.relationship('DownloadType', backref=backref('template_type', order_by=id))  

    def __init__(self, type_name, download_type_id):
        self.name = type_name
        self.download_type_id = download_type_id

    def __repr__(self):
        return '<TemplateType %r>' % self.name

    
class Template(db.Model):
    '''
        Шаблоны
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    archive = db.Column(db.Bool)
    
    #user = db.Column(db.Integer, db.ForeignKey('.id'))
    type = db.Column(db.Integer, db.ForeignKey('template_type.id'))

    #template = db.relationship('TemplateType', backref=backref('templates', order_by=id)) 
    
    def __init__(self, name, archive, type):
        self.name = name
        self.archive = archive
        self.type = type

    def __repr__(self):
        return '<Template %r>' % self.name


tags_template_types = db.Table('tags_template_types',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('template_type_id', db.Integer, db.ForeignKey('template_type.id'))
)

class Tag(db.Model):
    '''
        Теги 
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    
    download_type = db.Column(db.Integer, db.ForeignKey('download_type.id'))
    
    # many to many TemplateType<->Tag
    template_types = relationship('TemplateType', secondary=tags_template_types, backref='tags')

    def __init__(self, name, download_type, tag_group):
        self.name = name
        self.download_type = download_Type
        self.template_type = template_type

    def __repr__(self):
        return '<Tag %r>' % self.name    
 
class EtalonTree(db.Model):
    '''
        Эталонная структура дерева для каждого из типов шаблонов, с использованием
        всех тегов
    '''
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.Integer, db.ForeignKey('tag.id'))
    parent_tag =  db.Column(db.Integer, db.ForeignKey('tags_tree.id'))
    necessary = db.Column(db.Bool)
    
    template_type = db.Column(db.Integer, db.ForeignKey('template_type.id'))

    def __init__(self, tag_name, parent_tag, template):
        self.tag_name = tag_name
        self.parent_tag = parent_tag
        self.template_type = template_type   
    
    
class TagsTree(db.Model): 
    '''
        Древовидная структура тегов
    '''
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.Integer, db.ForeignKey('tag.id'))
    parent_tag =  db.Column(db.Integer, db.ForeignKey('tags_tree.id'))
    
    template = db.Column(db.Integer, db.ForeignKey('template.id'))

    def __init__(self, tag_name, parent_tag, template):
        self.tag_name = tag_name
        self.parent_tag = parent_tag
        self.template = template

    
    
    