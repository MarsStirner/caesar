# -*- encoding: utf-8 -*-
import os
import errno
import exceptions
from datetime import date, datetime, timedelta
from zipfile import ZipFile, ZIP_DEFLATED

import dbf
from jinja2 import Environment, PackageLoader

from nemesis.systemwide import db
from ..app import module, _config
from ..models import Template, TagsTree, Tag

try:
    from lxml import etree
    print("running with lxml.etree")
except ImportError:
    import xml.etree.ElementTree as etree
    print("running with ElementTree on Python 2.5+")


DOWNLOADS_DIR = os.path.join(module.static_folder, 'downloads')
UPLOADS_DIR = os.path.join(module.static_folder, 'uploads')


def __convert_date(timestamp):
    if os.name == 'nt':
        # Hack for Win (http://stackoverflow.com/questions/10588027/converting-timestamps-larger-than-maxint-into-datetime-objects)
        return date.fromtimestamp(0) + timedelta(seconds=timestamp / 1000)
    return date.fromtimestamp(timestamp / 1000)


def datetimeformat(value, _format='%Y-%m-%d'):
    if isinstance(value, datetime):
        return value.strftime(_format)
    elif isinstance(value, int) or isinstance(value, long):
        return __convert_date(value).strftime(_format)
    else:
        return None


class XML_Registry(object):

    def __new__(cls, *args, **kwargs):
        from ..lib.worker.factory import RegistryFactory
        return RegistryFactory.create(_config('region_code'), *args, **kwargs)


class Services(object):

    def __new__(cls, *args, **kwargs):
        from ..lib.worker.factory import ServicesFactory
        return ServicesFactory.create(_config('region_code'), *args, **kwargs)


class DBF_Data(object):

    def __new__(cls, *args, **kwargs):
        from ..lib.worker.factory import DBF_DataFactory
        return DBF_DataFactory.create(_config('region_code'), *args, **kwargs)


class DBF_Policlinic(object):

    def __new__(cls, *args, **kwargs):
        from ..lib.worker.factory import DBF_PoliclinicFactory
        return DBF_PoliclinicFactory.create(_config('region_code'), *args, **kwargs)


class DBF_Hospital(object):

    def __new__(cls, *args, **kwargs):
        from ..lib.worker.factory import DBF_HospitalFactory
        return DBF_HospitalFactory.create(_config('region_code'), *args, **kwargs)


class DownloadWorker(object):

    def __new__(cls, *args, **kwargs):
        from ..lib.worker.factory import UploadWorkerFactory
        return UploadWorkerFactory.create(_config('region_code'), *args, **kwargs)

    def __get_download_type(self, template_ids):
        template = db.session.query(Template).filter(Template.id.in_(template_ids)).first()
        return getattr(getattr(template.type, 'download_type', None), 'code', None)

    def __get_templates(self, template_ids):
        return db.session.query(Template).filter(Template.id.in_(template_ids)).all()

    def __get_template_tree(self, template_id):
        root = (db.session.query(TagsTree)
                .filter(TagsTree.template_id == template_id, TagsTree.parent_id == None)
                .first())
        # tree = TagTree(template_id=template_id, root=0)
        # return tree.load_tree(0, [])
        return [root]

    def __tags_list(self, template_id):
        tags = (db.session.query(Tag.code)
                .join(TagsTree)
                .filter(TagsTree.template_id == template_id)
                .order_by(TagsTree.ordernum).all())
        tags = [tag[0] for tag in tags]
        # tags = list()
        # for item in tree:
        #     tags.append(item.tag.code)
        return tags

    def __get_conditions(self):
        return None

    def get_data(self, download_type, **kwargs):
        if download_type == 'xml':
            data = XML_Registry(**kwargs).get_data()
        elif download_type == ('dbf', 'policlinic'):
            if 'tags' in kwargs:
                del kwargs['tags']
            data = DBF_Policlinic(**kwargs).get_data()
        elif download_type == ('dbf', 'hospital'):
            if 'tags' in kwargs:
                del kwargs['tags']
            data = DBF_Hospital(**kwargs).get_data()
        else:
            raise NameError
        return data

    def __get_file_object(self, template_type, end, tags):
        return File.provider(data_type=template_type[1], end=end, file_type=template_type[0], tags=tags)

    def do_download(self, template_ids, start, end, **kwargs):  #infis_code, contract_id, primary, departments=list()):
        tags, tree, files = dict(), dict(), dict()
        template, download_type = None, None
        templates = self.__get_templates(template_ids)
        for template in templates:
            tags[template.type.code] = self.__tags_list(template.id)
            tree[template.type.code] = self.__get_template_tree(template.id)

        if not tree:
            return None

        if template:
            download_type = getattr(getattr(template.type, 'download_type', None), 'code', None)

        data = self.get_data(download_type=download_type, start=start, end=end, **kwargs)

        if not getattr(data, 'registry', None):
            exception = exceptions.ValueError()
            exception.message = u'За указанный период услуг не найдено'
            raise exception

        for template in templates:
            file_obj = self.__get_file_object((download_type, template.type.code),
                                              end=end,
                                              tags=tags[template.type.code])
            files[template.type.code] = file_obj.save_file(tree[template.type.code], data)

            if template.archive:
                files[template.type.code] = file_obj.archive_file()

        return files


class UploadWorker(object):

    def __new__(cls, *args, **kwargs):
        from ..lib.worker.factory import UploadWorkerFactory
        return UploadWorkerFactory.create(_config('region_code'), *args, **kwargs)


class Contracts(object):

    def __new__(cls, *args, **kwargs):
        from ..lib.worker.factory import ContractsFactory
        return ContractsFactory.create(_config('region_code'), *args, **kwargs)


class Reports(object):

    def __new__(cls, *args, **kwargs):
        from ..lib.worker.factory import ReportsFactory
        return ReportsFactory.create(_config('region_code'), *args, **kwargs)


class DownloadHistory(object):

    def add_file(self):
        pass


class File(object):

    @classmethod
    def provider(cls, data_type, end, file_type='xml', tags=[]):
        """Вернёт объект для работы с указанным типом файла"""
        file_type = file_type.lower()
        if file_type == 'xml':
            obj = XML(data_type, end)
        elif file_type == 'dbf':
            obj = DBF(data_type, end, tags=tags)
        else:
            raise exceptions.NameError
        return obj


class XML(object):

    def __init__(self, data_type, end):
        self.data_type = data_type
        self.end = end
        self.file_name = None
        self.head = None
        self.dir_name = None

        if self.data_type == 'patients':
            self.template = 'tfoms/xml/patients.xml'
        elif self.data_type == 'services':
            self.template = 'tfoms/xml/services.xml'
        else:
            raise exceptions.NameError

    def generate_filename(self, data):
        if self.data_type == 'patients':
            self.file_name = data.patientRegistryFILENAME
        elif self.data_type == 'services':
            self.file_name = data.serviceRegistryFILENAME
        else:
            raise exceptions.NameError

    def generate_file(self, tags_tree, data):
        env = Environment(loader=PackageLoader(module.import_name,
                                               module.template_folder))
        env.filters['datetimeformat'] = datetimeformat

        template = env.get_template(self.template)
        linked_file = XML(data_type='services', end=self.end)
        linked_file.generate_filename(data)
        self.head = dict(VERSION='1.0',
                         DATA=date.today().strftime('%Y-%m-%d'),
                         FILENAME=self.file_name,
                         FILENAME1=linked_file.file_name)

        return template.render(encoding=_config('xml_encoding'), head=self.head, tags_tree=tags_tree, data=data)

    def __create_download_dir(self, account):
        self.dir_name = str(account.id)
        path = os.path.join(DOWNLOADS_DIR, self.dir_name)
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def save_file(self, tags_tree, data):
        self.generate_filename(data)
        content = self.generate_file(tags_tree, data)
        self.__create_download_dir(data.account)
        f = open(os.path.join(DOWNLOADS_DIR, self.dir_name, '%s.xml' % self.file_name), 'w')
        f.write(content.encode(_config('xml_encoding')))
        f.close()
        return self.dir_name, '{0}.xml'.format(self.file_name)

    def archive_file(self):
        with ZipFile(
                os.path.join(DOWNLOADS_DIR, self.dir_name, '{0}.xml.zip'.format(self.file_name)),
                'w',
                ZIP_DEFLATED) as archive:
            archive.write(
                os.path.join(DOWNLOADS_DIR, self.dir_name, '{0}.xml'.format(self.file_name)),
                '%s.xml' % self.file_name)
        return self.dir_name, '{0}.xml.zip'.format(self.file_name)


class DBF(object):

    def __init__(self, data_type, end, tags):
        self.data_type = data_type
        self.end = end
        self.tags = tags

    def __get_month(self, date):
        monthes = range(13)
        monthes[10] = 'a'
        monthes[11] = 'b'
        monthes[12] = 'c'
        month = date.month
        if month > 9:
            month = monthes[month]
        return month

    def generate_filename(self):
        self.file_name = 'L'
        self.file_name += str(self.__get_org_type())
        self.file_name += _config('old_lpu_infis_code')

        self.arj_file_name = '10'
        self.arj_file_name += _config('old_lpu_infis_code')
        self.arj_file_name += '%s' % self.end.strftime('%d')
        self.arj_file_name += '%s' % self.__get_month(self.end)

    def __get_field_type(self, value, tag):
        if isinstance(value, basestring):
            _type = 'C(254)'
        elif isinstance(value, date):
            _type = 'D'
        elif isinstance(value, int):
            _type = 'N(10,0)'
        elif isinstance(value, float):
            _type = 'N(7,2)'
        else:
            _type = 'C(254)'

        if tag == 'KOD_LPU':
            _type = 'N(10,0)'
        elif tag == 'DAT_SC':
            _type = 'D'
        elif tag == 'VL':
            _type = 'N(10,0)'
        return _type

    def __generate_fields(self, tags, row):
        # NOT USED
        env = Environment(loader=PackageLoader(module.import_name, module.template_folder))
        env.filters['datetimeformat'] = datetimeformat

        template = env.get_template('dbf/fields')
        return str(template.render(tags=tags).lstrip())

    def __get_org_type(self):
        _type = None
        if self.data_type == 'hospital':
            _type = 1
        elif self.data_type == 'policlinic':
            _type = 2
        return _type

    def __generate_bill_number(self, num):
        bill_num = _config('old_lpu_infis_code')
        bill_num += str(self.__get_org_type())
        bill_num += '_'  #TODO: исправленный, то W
        bill_num += 'M'  #TODO: убедиться, что других случаев нет
        bill_num += '{0:04d}'.format(num)
        return bill_num

    def generate_file(self, tags, data):
        dbf.input_decoding = 'utf8'
        dbf.default_codepage = 'utf8'
        fields = []
        for key, item in enumerate(data):
            if key == 0:
                for tag in tags:
                    fields.append('{0} {1}'.format(tag.strip(), self.__get_field_type(getattr(item, tag, ''), tag)))
                table = dbf.Table(os.path.join(DOWNLOADS_DIR, '%s.dbf' % self.file_name), '; '.join(fields))
                table.open()

            row = []
            for tag in tags:
                value = getattr(item, tag, '')
                if tag == 'N_CH':
                    value = self.__generate_bill_number(key + 1)
                elif tag == 'KOD_LPU':
                    value = _config('lpu_infis_code')
                elif tag == 'DAT_SC':
                    value = date.today()
                elif tag == 'VL':
                    value = self.__get_org_type()
                if isinstance(value, date):
                    value = dbf.Date(value.year, value.month, value.day)
                row.append(value)
            table.append(tuple(row))
        table.close()
        return table

    def save_file(self, tags, data):
        self.generate_filename()
        dbf_file = self.generate_file(self.tags, data)
        return '%s.dbf' % self.file_name

    def archive_file(self):
        import patoolib
        patoolib.create_archive(os.path.join(DOWNLOADS_DIR, '%s.arj' % self.arj_file_name),
                                (os.path.join(DOWNLOADS_DIR, '%s.dbf' % self.file_name), ))
        return '%s.arj' % self.arj_file_name


class Utility(object):

    def prepare_table(self, table_type):
        """Проверяет насколько давно было обновление таблицы с данными
        и при необходимости посылает запрос ядру на обновление таблицы

        """
        pass
