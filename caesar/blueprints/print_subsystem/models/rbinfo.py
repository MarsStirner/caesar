# -*- coding: utf-8 -*-
from caesar.blueprints.print_subsystem.database import Base

__author__ = 'viruzzz-kun'


class Info(Base):
    u"""Базовый класс для представления объектов при передаче в шаблоны печати"""
    __abstract__ = True

    def __cmp__(self, x):
        ss = unicode(self)
        sx = unicode(x)
        if ss > sx:
            return 1
        elif ss < sx:
            return -1
        else:
            return 0

    def __add__(self, x):
        return unicode(self) + unicode(x)

    def __radd__(self, x):
        return unicode(x) + unicode(self)


class RBInfo(Info):
    __abstract__ = True

    def __init__(self):
        self.code = ""
        self.name = ""

    def __unicode__(self):
        return self.name