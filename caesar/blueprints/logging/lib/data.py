# -*- encoding: utf8 -*-
from pysimplelogs.pysimplelogs import Simplelog, get_levels_list
from ..app import _config
from config import SIMPLELOGS_URL


class Log_Data(object):

    def __init__(self):
        self.simplelogs = Simplelog(SIMPLELOGS_URL)

    def get_owners(self):
        return self.simplelogs.get_owners()

    def get_levels(self):
        return get_levels_list(SIMPLELOGS_URL)

    def get_list(self, **kwargs):
        params = kwargs
        return self.simplelogs.get_list(**params)

    def get_count(self, **kwargs):
        params = kwargs
        return self.simplelogs.count(**params)