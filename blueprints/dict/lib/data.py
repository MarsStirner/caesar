# -*- coding: utf-8 -*-
import os
import exceptions
import calendar
from datetime import date, timedelta
import dbf

from ..app import module, _config
from service_client import TARIFFClient as Client

DOWNLOADS_DIR = os.path.join(module.static_folder, 'downloads')
UPLOADS_DIR = os.path.join(module.static_folder, 'uploads')


class Tariff(object):

    def __init__(self):
        self.client = Client(_config('core_service_url'))
        self.dbf_keys = ('c_tar', 'summ_tar', 'date_b', 'date_e')

    def __convert_date(self, _date):
        return calendar.timegm(_date.timetuple()) * 1000

    def __check_record(self, c_tar):
        return True

    def parse(self, file_path):
        result = list()
        if os.path.isfile(file_path):
            table = dbf.Table(file_path)
            if table:
                table.open()
                for i, record in enumerate(table):
                    value = dict()
                    if self.__check_record(record['c_tar']):
                        value['number'] = i + 1
                        for key in self.dbf_keys:
                            value[key] = record[key]
                            if isinstance(value[key], date):
                                value[key] = self.__convert_date(value[key])
                        result.append(value)
                table.close()
        return result

    def send(self, data):
        return self.client.send_tariffs(data)