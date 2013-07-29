# -*- coding: utf-8 -*-
import os
import exceptions
from datetime import date
import dbf

from ..app import module, _config
from service_client import TARIFFClient as Client

DOWNLOADS_DIR = os.path.join(module.static_folder, 'downloads')
UPLOADS_DIR = os.path.join(module.static_folder, 'uploads')


class Tariff(object):

    def __init__(self):
        self.client = Client(_config('core_service_url'))

    def __check_record(self, record):
        pass

    def parse(self, file_path):
        if os.path.isfile(file_path):
            table = dbf.Table(file_path)
            if table:
                for record in table:
                    print record