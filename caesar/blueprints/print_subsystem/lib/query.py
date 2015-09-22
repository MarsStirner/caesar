# -*- coding: utf-8 -*-
from flask import g

__author__ = 'viruzzz-kun'


def Query(Model):
    return g.printing_session.query(Model)
