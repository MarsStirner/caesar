# -*- encoding: utf-8 -*-
from ..lib.clients.factory import ClientFactory
from ..app import _config


class Departments(object):

    def __init__(self, infis_code):
        self.client = None
        self.infis_code = infis_code

    def __get_client(self):
        if self.client is None:
            self.client = ClientFactory.create(_config('region_code'), _config('core_service_url'))

    def __get_from_core(self):
        self.__get_client()
        return self.client.get_departments(self.infis_code)

    def get_departments(self):
        data = self.__get_from_core()
        return data
