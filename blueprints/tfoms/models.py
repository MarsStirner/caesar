# -*- coding: utf-8 -*-
from application.database import db
from .config import MODULE_NAME

TABLE_PREFIX = MODULE_NAME


class DownloadType(db.Model):
    """Тип выгрузки"""
    __tablename__ = '%s_download_type' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.Unicode(10), unique=True)

    def __repr__(self):
        return '<DownloadType %r>' % self.code

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code)


class TemplateType(db.Model):
    """Тип шаблона"""
    __tablename__ = '%s_template_type' % TABLE_PREFIX
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    
    download_type_id = db.Column(db.Integer, db.ForeignKey('%s_download_type.id' % TABLE_PREFIX), index=True)
    download_type = db.relationship(DownloadType)

    def __repr__(self):
        return '<TemplateType %r>' % self.name

    def __unicode__(self):
        return self.name

    
class Template(db.Model):
    """Шаблоны"""
    __tablename__ = '%s_template' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    archive = db.Column(db.Boolean, default=False)
    
    #user = db.Column(db.Integer, db.ForeignKey('.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('%s_template_type.id' % TABLE_PREFIX), index=True)
    type = db.relation(TemplateType)

    def __repr__(self):
        return '<Template %r>' % self.name

    def __unicode__(self):
        return self.name


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
    
    # many to many TemplateType<->Tag
    template_types = db.relationship(TemplateType,
                                     secondary='%s_tag_template_type' % TABLE_PREFIX,
                                     backref='tags')

    def __repr__(self):
        return '<Tag %r>' % self.code

    def __unicode__(self):
        return self.code

 
class StandartTree(db.Model):
    """Эталонная структура дерева для каждого из типов шаблонов, с использованием всех тегов"""
    __tablename__ = '%s_standart_tree' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('%s_tag.id' % TABLE_PREFIX), index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('%s_standart_tree.id' % TABLE_PREFIX), index=True)
    template_type_id = db.Column(db.Integer, db.ForeignKey('%s_template_type.id' % TABLE_PREFIX), index=True)
    is_necessary = db.Column(db.Boolean)
    ordernum = db.Column(db.Integer, doc=u'Поле для сортировки тегов')

    tag = db.relationship(Tag)
    parent = db.relationship('StandartTree', remote_side=[id])
    template_type = db.relationship(TemplateType)

    __table_args__ = {'order_by': ordernum}

    def __unicode__(self):
        return self.name

    
class TagsTree(db.Model): 
    """Древовидная структура тегов"""
    __tablename__ = '%s_tags_tree' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('%s_tag.id' % TABLE_PREFIX), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('%s.id' % __tablename__), index=True)
    template_id = db.Column(db.Integer, db.ForeignKey('%s_template.id' % TABLE_PREFIX), nullable=False, index=True)
    ordernum = db.Column(db.Integer, doc=u'Поле для сортировки тегов')

    tag = db.relationship(Tag)
    parent = db.relationship('TagsTree', remote_side=[id])
    template = db.relationship(Template)

    __table_args__ = {'order_by': ordernum}

    def __unicode__(self):
        return self.tag.code
