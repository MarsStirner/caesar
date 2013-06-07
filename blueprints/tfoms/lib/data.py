# -*- encoding: utf-8 -*-
import os
import exceptions
from service_client import TFOMSClient as Client
from tags_tree import TagTree
from ..models import db, Template
from ..config import CORE_SERVICE_URL

DOWNLOADS_URL = os.path.join('static', 'downloads')
DOWNLOADS_DIR = os.path.abspath(DOWNLOADS_URL)
UPLOADS_URL = os.path.join('static', 'uploads')
UPLOADS_DIR = os.path.abspath(UPLOADS_URL)


class DownloadWorker(object):

    def __init__(self):
        self.client = Client(CORE_SERVICE_URL)

    def __get_template(self, id):
        return db.session.query(Template).get(id)

    def __get_template_tree(self, template_id):
        tree = TagTree(template_id=template_id, root=0)
        return tree.load_tree(0, [])

    def __tags_list(self, tree):
        tags = list()
        for item in tree:
            tags.append(item.tag.code)
        return tags

    def __get_conditions(self):
        return None

    def __get_patients(self, tags):
        data = self.client.get_patients()
        return data

    def __get_services(self, tags):
        data = self.client.get_patient_events()
        return data

    def get_data(self, template_type, tags):
        if template_type == 'xml_patients':
            data = self.__get_patients(tags)
        elif template_type == 'xml_services':
            data = self.__get_services(tags)
        else:
            raise NameError
        return data

    def __get_file_object(self, template_type):
        if template_type in ('xml_patients', 'xml_services'):
            file_type = 'xml'
        elif template_type == 'dbf':
            file_type = 'dbf'
        else:
            raise NameError
        return File.provider(file_type)

    def do_download(self, template_id):
        template = self.__get_template(template_id)
        tree = self.__get_template_tree(template_id)
        if tree is None:
            return None
        conditions = self.__get_conditions()
        tags = self.__tags_list(tree)
        data = self.get_data(template.type.name, tags)
        file_obj = self.__get_file_object(template.type.name)
        file_url = file_obj.save_file(tree, data)
        return file_url


class UploadWorker(object):

    def do_upload(self):
        pass


class File(object):

    @classmethod
    def provider(cls, file_type='xml'):
        """Вернёт объект для работы с указанным типом файла"""
        file_type = file_type.lower()
        if file_type == 'xml':
            obj = XML()
        elif file_type == 'dbf':
            obj = DBF()
        else:
            raise exceptions.NameError
        return obj


class XML(object):

    def __generate_filename(self):
        pass

    def generate_file(self, tags_tree, data):
        pass

    def save_file(self, tags_tree, data):
        content = self.generate_file(tags_tree, data)
        filename = self.__generate_filename()
        f = open(os.path.join(DOWNLOADS_DIR, '%s.xml' % filename), 'w')
        f.write(content)
        f.close()
        return os.path.join(DOWNLOADS_URL, '%s.xml' % filename)


class DBF(object):

    def generate_file(self):
        pass

    def save_file(self):
        pass


class Utility(object):

    def prepare_table(self, table_type):
        """Проверяет насколько давно было обновление таблицы с данными
        и при необходимости посылает запрос ядру на обновление таблицы

        """
        pass