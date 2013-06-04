# -*- encoding: utf-8 -*-

from service_client import TFOMSClient as Client


class XML_Data(object):

    def generate_file(self):
        pass


class DBF_Data(object):

    def generate_file(self):
        pass


class Utility(object):

    def prepare_table(self, table_type):
        """Проверяет насколько давно было обновление таблицы с данными
        и при необходимости посылает запрос ядру на обновление таблицы

        """
        pass