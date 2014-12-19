# -*- coding: utf-8 -*-
import re

from ..models.models_all import Rbspecialvariablespreference
from application.database import db

__author__ = 'mmalkov'


def SpecialVariable(name, *args, **kwargs):
    sp_variable = Rbspecialvariablespreference.query.filter(Rbspecialvariablespreference.name == name).first()
    # Проверка валидности sql-запроса
    sql_text = sp_variable.query_text
    if re.search(r"\W(delete|drop|insert|alter)\s", sql_text, re.I) or not re.match(r"^\s*SELECT", sql_text, re.I):
        raise RuntimeError(
            u"При работе со специальными переменными вы можете использовать только SELECT-запросы! "
            u"Проверьте тексты запросов.")

    # Инициализация словаря аргументов
    arg_names = sp_variable.arguments
    len_args = len(args)
    arguments = {}
    for arg_index, arg_name in enumerate(arg_names):
        if arg_index < len_args:
            arguments[arg_name] = args[arg_index]
        elif arg_name in kwargs:
            arguments[arg_name] = kwargs[arg_name]
        else:
            raise RuntimeError(u'Argument "%s" of special variable "%s" is not initialized in call' % (arg_name, name))

    sql_text = re.sub(ur'::(\w+)', ur':\1', sql_text, re.U)

    return db.session.execute(sql_text, arguments).fetchall()
