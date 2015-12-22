# -*- encoding: utf8 -*-
from pysimplelogs2 import Simplelog
from config import SIMPLELOGS_URL


class Log_Data(object):
    def __init__(self):
        self.simplelogs = Simplelog(SIMPLELOGS_URL)

    def get_owners(self):
        return self.simplelogs.get_owners()

    def get_levels(self):
        return self.simplelogs.get_levels_list()

    def get_list(self, **kwargs):
        return self.simplelogs.get_list(**kwargs)

    def get_count(self, **kwargs):
        return self.simplelogs.count(**kwargs)