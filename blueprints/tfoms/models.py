# -*- coding: utf-8 -*-
from application.database import db
from config import MODULE_NAME

TABLE_PREFIX = MODULE_NAME


class DownloadType(db.Model):
    """Тип выгрузки"""
    __tablename__ = '%s_download_type' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.Unicode(25), unique=True)

    def __repr__(self):
        return '<DownloadType %r>' % self.code

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code)


class TemplateType(db.Model):
    """Тип шаблона"""
    __tablename__ = '%s_template_type' % TABLE_PREFIX
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(45), unique=True, nullable=False)

    download_type_id = db.Column(db.Integer,
                                 db.ForeignKey('%s_download_type.id' % TABLE_PREFIX, deferrable=True),
                                 index=True)
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
    is_active = db.Column(db.Boolean, default=False)
    
    #user = db.Column(db.Integer, db.ForeignKey('.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('%s_template_type.id' % TABLE_PREFIX, deferrable=True), index=True)
    type = db.relation(TemplateType)

    tag_tree = db.relationship('TagsTree', backref='template', cascade="all, delete, delete-orphan")

    def __repr__(self):
        return '<Template %r>' % self.name

    def __unicode__(self):
        return self.name


class TagTemplateType(db.Model):
    __tablename__ = '%s_tag_template_type' % TABLE_PREFIX

    tag_id = db.Column(db.Integer,
                       db.ForeignKey('%s_tag.id' % TABLE_PREFIX, deferrable=True),
                       primary_key=True,
                       nullable=False)
    template_type_id = db.Column(db.Integer,
                                 db.ForeignKey('%s_template_type.id' % TABLE_PREFIX, deferrable=True),
                                 primary_key=True,
                                 nullable=False)

    # db.UniqueConstraint(tag_id, template_type_id)


class Tag(db.Model):
    """Теги"""
    __tablename__ = '%s_tag' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.Unicode(80))
    is_leaf = db.Column(db.Boolean, default=False)
    
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
    tag_id = db.Column(db.Integer, db.ForeignKey('%s_tag.id' % TABLE_PREFIX, deferrable=True), index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('%s_standart_tree.id' % TABLE_PREFIX, deferrable=True), index=True)
    template_type_id = db.Column(db.Integer,
                                 db.ForeignKey('%s_template_type.id' % TABLE_PREFIX, deferrable=True),
                                 index=True)
    is_necessary = db.Column(db.Boolean)
    ordernum = db.Column(db.Integer, doc=u'Поле для сортировки тегов')

    tag = db.relationship(Tag)
    parent = db.relationship('StandartTree', remote_side=[id])
    template_type = db.relationship(TemplateType)

    __table_args__ = {'order_by': ordernum}

    def __unicode__(self):
        return self.tag.code

    
class TagsTree(db.Model): 
    """Древовидная структура тегов"""
    __tablename__ = '%s_tags_tree' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.Integer,
                       db.ForeignKey('%s_tag.id' % TABLE_PREFIX, deferrable=True),
                       index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('%s.id' % __tablename__, deferrable=True), index=True)
    template_id = db.Column(db.Integer,
                            db.ForeignKey('%s_template.id' % TABLE_PREFIX, deferrable=True),
                            nullable=False,
                            index=True)
    ordernum = db.Column(db.Integer, doc=u'Поле для сортировки тегов')

    tag = db.relationship(Tag)
    parent = db.relationship('TagsTree', remote_side=[id], backref=db.backref('children', order_by=ordernum))
    # template = db.relationship(Template)

    __table_args__ = {'order_by': ordernum}

    def __unicode__(self):
        return self.tag.code


class ConfigVariables(db.Model):
    __tablename__ = '%s_config_variables' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(25), unique=True, nullable=False)
    name = db.Column(db.Unicode(50), unique=True, nullable=False)
    value = db.Column(db.Unicode(100))
    value_type = db.Column(db.String(30))

    def __unicode__(self):
        return self.code


class DownloadFiles(db.Model):
    __tablename__ = '%s_download_files' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    template_id = db.Column(db.Integer, db.ForeignKey(Template.id, deferrable=True), index=True)
    name = db.Column(db.String(50), nullable=False)
    created = db.Column(db.DateTime, default=db.text('NOW()'), nullable=False)

    db.UniqueConstraint(name, created)
    template = db.relationship(Template)


class DownloadBills(db.Model):
    __tablename__ = '%s_download_bills' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_id = db.Column(db.Integer, db.ForeignKey(DownloadFiles.id, deferrable=True))
    DSCHET = db.Column(db.DateTime, nullable=False)
    NSCHET = db.Column(db.String(50), nullable=False)
    CODE_MO = db.Column(db.String(10), nullable=False)
    YEAR = db.Column(db.Integer, nullable=False)
    MONTH = db.Column(db.Integer, nullable=False)
    PLAT = db.Column(db.Integer, nullable=False)
    SUMMAV = db.Column(db.Numeric(12, 2), nullable=False)
    start = db.Column(db.Date)
    end = db.Column(db.Date)

    download_file = db.relationship(DownloadFiles)


class DownloadPatients(db.Model):
    __tablename__ = '%s_download_patients' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True)
    VPOLIS = db.Column(db.Integer)
    SPOLIS = db.Column(db.Unicode(20))
    NPOLIS = db.Column(db.Numeric(30))
    SMO = db.Column(db.Integer)
    SMO_OGRN = db.Column(db.Numeric(30))
    SMO_OK = db.Column(db.Numeric(30))
    SMO_NAM = db.Column(db.Unicode(100))
    NOVOR = db.Column(db.Integer, default=0)
    clientDocumentId = db.Column(db.Integer)
    clientPolicyId = db.Column(db.Integer)


class DownloadRecords(db.Model):
    __tablename__ = '%s_download_records' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bill_id = db.Column(db.Integer, db.ForeignKey(DownloadBills.id, deferrable=True), index=True)
    N_ZAP = db.Column(db.Integer)
    PR_NOV = db.Column(db.Integer, default=0, nullable=False)


class DownloadCases(db.Model):
    __tablename__ = '%s_download_cases' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bill_id = db.Column(db.Integer, db.ForeignKey(DownloadBills.id, deferrable=True), index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey(DownloadPatients.id, deferrable=True), index=True)
    record_id = db.Column(db.Integer, db.ForeignKey(DownloadRecords.id, deferrable=True), index=True)
    actionId = db.Column(db.Integer)
    eventId = db.Column(db.Integer)
    rbServiceId = db.Column(db.Integer)
    USL_OK = db.Column(db.Integer)
    VIDPOM = db.Column(db.Integer)
    NPR_MO = db.Column(db.String(20))
    EXTR = db.Column(db.Integer)
    LPU = db.Column(db.String(20))
    LPU_1 = db.Column(db.String(20))
    PODR = db.Column(db.Integer)
    PROFIL = db.Column(db.Integer)
    NHISTORY = db.Column(db.String(50))
    DATE_1 = db.Column(db.Date)
    DATE_2 = db.Column(db.Date)
    DS1 = db.Column(db.Unicode(250))
    CODE_MES1 = db.Column(db.Unicode(250))
    CODE_MES2 = db.Column(db.Unicode(250))
    RSLT = db.Column(db.Integer)
    ISHOD = db.Column(db.Integer)
    PRVS = db.Column(db.BigInteger)
    IDDOKT = db.Column(db.BigInteger)
    IDSP = db.Column(db.Integer)
    ED_COL = db.Column(db.Numeric(5, 2))
    SUMV = db.Column(db.Numeric(10, 2))


class DownloadServices(db.Model):
    __tablename__ = '%s_download_services' % TABLE_PREFIX

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey(DownloadCases.id, deferrable=True), index=True)
    IDSERV = db.Column(db.Integer)
    LPU = db.Column(db.String(20))
    LPU_1 = db.Column(db.String(20))
    PODR = db.Column(db.Integer)
    PROFIL = db.Column(db.Integer)
    DATE_IN = db.Column(db.Date)
    DATE_OUT = db.Column(db.Date)
    DS = db.Column(db.Unicode(250))
    CODE_USL = db.Column(db.Unicode(50))
    KOL_USL = db.Column(db.Numeric(5, 2))
    TARIF = db.Column(db.Numeric(10, 2))
    SUMV_USL = db.Column(db.Numeric(10, 2))
    PRVS = db.Column(db.BigInteger)
    CODE_MD = db.Column(db.BigInteger)

