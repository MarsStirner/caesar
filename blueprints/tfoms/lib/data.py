# -*- encoding: utf-8 -*-
import os
import exceptions
from datetime import date
from zipfile import ZipFile
import dbf
import patoolib
from jinja2 import Environment, PackageLoader
from application.database import db
from service_client import TFOMSClient as Client
from thrift_service.ttypes import PatientOptionalFields, SluchOptionalFields
from ..app import module, _config
from ..models import Template, TagsTree, Tag


DOWNLOADS_DIR = os.path.join(module.static_folder, 'downloads')
UPLOADS_DIR = os.path.join(module.static_folder, 'uploads')


def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format)


class Patients(object):

    def __init__(self, start, end, infis_code, tags):
        self.client = Client(_config('core_service_url'))
        self.start = start
        self.end = end
        self.infis_code = infis_code
        self.tags = tags

    def __filter_tags(self, tags):
        result = []
        for tag in tags:
            try:
                attr = getattr(PatientOptionalFields, tag)
            except exceptions.AttributeError:
                pass
            else:
                result.append(attr)
        return result

    def get_data(self):
        data = self.client.get_patients(infis_code=self.infis_code,
                                        start=self.start,
                                        end=self.end,
                                        optional=self.__filter_tags(self.tags))
        return data


class Services(object):

    def __init__(self, start, end, infis_code, tags):
        self.client = Client(_config('core_service_url'))
        self.start = start
        self.end = end
        self.infis_code = infis_code
        self.tags = tags

    def __filter_tags(self, tags):
        result = []
        for tag in tags:
            try:
                attr = getattr(SluchOptionalFields, tag)
            except exceptions.AttributeError, e:
                print e
            else:
                result.append(attr)
        return result

    def __get_ammount(self, services):
        ammount = 0.0
        if not services:
            return ammount
        for key, event_list in services.iteritems():
            if event_list:
                for event in event_list:
                    ammount += getattr(event, 'SUMV', 0)
        return ammount

    def __get_bill(self, services):
        data = dict(CODE=1,
                    CODE_MO=_config('lpu_infis_code'),
                    YEAR=self.end.strftime('%Y'),
                    MONTH=self.end.strftime('%m'),
                    NSCHET='%s-%s/%s' % (self.end.strftime('%Y%m'), 1, _config('old_lpu_infis_code')),
                    DSCHET=date.today().strftime('%Y-%m-%d'),
                    PLAT=_config('payer_code'),
                    SUMMAV=self.__get_ammount(services))
        return data

    def get_data(self):
        patients = Patients(self.start, self.end, self.infis_code, self.tags)
        patients_data = patients.get_data()

        patient_ids = []
        patients = dict()
        for patient in patients_data:
            patient_ids.append(patient.patientId)
            patients[patient.patientId] = patient

        data = self.client.get_patient_events(infis_code=self.infis_code,
                                              start=self.start,
                                              end=self.end,
                                              patients=patient_ids,
                                              optional=self.__filter_tags(self.tags))
        return dict(patients=patients, services=data, bill=self.__get_bill(data))


class DBF_Data(object):

    def __init__(self, start, end, infis_code):
        self.client = Client(_config('core_service_url'))
        self.start = start
        self.end = end
        self.infis_code = infis_code

    def get_data(self):
        data = self.client.get_policlinic_dbf(infis_code=self.infis_code,
                                              start=self.start,
                                              end=self.end)
        return data


class DownloadWorker(object):

    def __get_template(self, id):
        return db.session.query(Template).get(id)

    def __get_template_tree(self, template_id):
        root = (db.session.query(TagsTree)
                .filter(TagsTree.template_id == template_id, TagsTree.parent_id == None)
                .first())
        # tree = TagTree(template_id=template_id, root=0)
        # return tree.load_tree(0, [])
        return [root]

    def __tags_list(self, template_id):
        tags = db.session.query(Tag.code).join(TagsTree).filter(TagsTree.template_id == template_id).all()
        tags = [r[0] for r in tags]
        # tags = list()
        # for item in tree:
        #     tags.append(item.tag.code)
        return tags

    def __get_conditions(self):
        return None

    def get_data(self, template_type, **kwargs):
        if template_type == ('xml', 'patients'):
            data = Patients(**kwargs).get_data()
        elif template_type == ('xml', 'services'):
            data = Services(**kwargs).get_data()
        elif template_type[0] == 'dbf':
            if 'tags' in kwargs:
                del kwargs['tags']
            data = DBF_Data(**kwargs).get_data()
        else:
            raise NameError
        return data

    def __get_file_object(self, template_type, end, tags):
        return File.provider(data_type=template_type[1], end=end, file_type=template_type[0], tags=tags)

    def do_download(self, template_id, start, end, infis_code):
        template = self.__get_template(template_id)
        template_type = (template.type.download_type.code, template.type.code)
        tree = self.__get_template_tree(template_id)
        if tree is None:
            return None
        conditions = self.__get_conditions()
        tags = self.__tags_list(template_id)
        data = self.get_data(template_type,
                             start=start,
                             end=end,
                             infis_code=infis_code,
                             tags=tags)
                             # conditions=conditions)
        file_obj = self.__get_file_object(template_type, end=end, tags=tags)
        file_url = file_obj.save_file(tree, data)
        if template.archive:
            file_url = file_obj.archive_file()
        return file_url


class UploadWorker(object):

    def do_upload(self):
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

        if self.data_type == 'patients':
            self.file_name = 'L'
            self.template = 'xml/patients.xml'
        elif self.data_type == 'services':
            self.file_name = 'H'
            self.template = 'xml/services.xml'
        else:
            raise exceptions.NameError

    def generate_filename(self):
        self.file_name += 'M'
        self.file_name += _config('old_lpu_infis_code')
        self.file_name += 'T'
        self.file_name += _config('smo_number')
        self.file_name += '_'
        self.file_name += '%s' % self.end.strftime("%y%m")
        self.file_name += '1'

    def generate_file(self, tags_tree, data):
        env = Environment(loader=PackageLoader(module.import_name, module.template_folder))
        env.filters['datetimeformat'] = datetimeformat

        template = env.get_template(self.template)
        linked_file = XML(data_type='services', end=self.end)
        linked_file.generate_filename()
        head = dict(VERSION='1.0',
                    DATA=date.today().strftime('%Y-%m-%d'),
                    FILENAME=self.file_name,
                    FILENAME1=linked_file.file_name)
        return template.render(head=head, tags_tree=tags_tree, data=data)

    def save_file(self, tags_tree, data):
        self.generate_filename()
        content = self.generate_file(tags_tree, data)
        f = open(os.path.join(DOWNLOADS_DIR, '%s.xml' % self.file_name), 'w')
        f.write(content.encode('utf-8'))
        f.close()
        return '%s.xml' % self.file_name

    def archive_file(self):
        with ZipFile(os.path.join(DOWNLOADS_DIR, '%s.xml.zip' % self.file_name), 'w') as archive:
            archive.write(os.path.join(DOWNLOADS_DIR, '%s.xml' % self.file_name), '%s.xml' % self.file_name)
        return '%s.xml.zip' % self.file_name


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
        self.file_name += _config('lpu_type')
        self.file_name += _config('old_lpu_infis_code')

        self.arj_file_name = '10'
        self.arj_file_name += _config('old_lpu_infis_code')
        self.arj_file_name += '%s' % self.end.strftime('%d')
        self.arj_file_name += '%s' % self.__get_month(self.end)

    def __generate_fields(self, tags):
        env = Environment(loader=PackageLoader(module.import_name, module.template_folder))
        env.filters['datetimeformat'] = datetimeformat

        template = env.get_template('dbf/fields')
        return str(template.render(tags=tags).lstrip())

    def generate_file(self, tags_tree, data):
        dbf.input_decoding = 'utf8'
        dbf.default_codepage = 'utf8'
        table = dbf.Table(os.path.join(DOWNLOADS_DIR, '%s.dbf' % self.file_name), self.__generate_fields(self.tags))
        table.open()
        for item in data:
            row = []
            for tag_item in tags_tree:
                row.append(getattr(item, tag_item.tag.code, ''))
            table.append(tuple(row))
        table.close()
        return table

    def save_file(self, tags_tree, data):
        self.generate_filename()
        dbf_file = self.generate_file(tags_tree, data)
        return '%s.dbf' % self.file_name

    def archive_file(self):
        patoolib.create_archive(os.path.join(DOWNLOADS_DIR, '%s.arj' % self.arj_file_name),
                                os.path.join(DOWNLOADS_DIR, '%s.dbf' % self.file_name))
        return '%s.arj' % self.arj_file_name


class Utility(object):

    def prepare_table(self, table_type):
        """Проверяет насколько давно было обновление таблицы с данными
        и при необходимости посылает запрос ядру на обновление таблицы

        """
        pass