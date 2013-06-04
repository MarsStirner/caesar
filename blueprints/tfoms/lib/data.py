# -*- encoding: utf-8 -*-

import exceptions
from service_client import TFOMSClient as Client


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

    def generate_file(self):
        pass

    def save_file(self):
        pass


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