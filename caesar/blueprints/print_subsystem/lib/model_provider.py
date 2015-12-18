# -*- coding: utf-8 -*-

import types

from nemesis.lib.data_ctrl.model_provider import AbstractModelProvider
from blueprints.print_subsystem import models as printing_models


class PrintingModelProvider(AbstractModelProvider):

    @classmethod
    def get(cls, name):
        # todo: организовать сопоставление наименований из models_all с наименованиями моделей,
        # используемых в приложении, для тех случаев, где они не совпадают
        for module_attr in printing_models.__dict__.itervalues():
            if isinstance(module_attr, types.ModuleType) and hasattr(module_attr, name):
                return getattr(module_attr, name)
        raise Exception(u'Не найден класс модели по имени {0}'.format(name))

    @classmethod
    def get_query(cls, name):
        model = cls.get(name)
        return cls.session.query(model)