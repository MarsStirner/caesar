# -*- coding: utf-8 -*-
import re
import datetime

from ..models.models_all import Rbspecialvariablespreference, Rbprinttemplatemeta
from application.database import db

__author__ = 'mmalkov'


def SpecialVariable(spvar, *args):
    spvar_name = spvar
    sp_variable_meta = Rbprinttemplatemeta.query.filter(Rbprinttemplatemeta.name == spvar_name).first()
    argument_names = re.findall(r"\"(\w+)\"", sp_variable_meta.arguments)
    variables_for_queue = {}
    for i in range(len(argument_names)):
        variables_for_queue.update({
            argument_names[i]: args[i]
        })
    return get_special_variable_value(spvar_name, variables_for_queue)


def get_special_variable_value(sp_variable_name, variables_for_queue):
    sp_variable = Rbspecialvariablespreference.query.filter(Rbspecialvariablespreference.name == sp_variable_name).first()
    sql_text = sp_variable.query_text

    if re.search(r"\W(delete|drop|insert|alter)\s", sql_text, re.IGNORECASE):
        message = u"При работе со специальными переменными вы можете использовать только SELECT-запросы! Проверьте тексты запросов."
        return False
    if re.match(r"^\s*SELECT", sql_text, re.IGNORECASE):
        if type(sql_text) != unicode:
            sql_text = unicode(sql_text)
        for variable_name in variables_for_queue:
            variable_value = variables_for_queue[variable_name]
            variable_type = type(variable_value)
            if (variable_type == str or variable_type == unicode or variable_type == datetime.date or
                    variable_type == datetime.time):
                variable_value = u"'" + unicode(variable_value) + u"'"
            sql_text = re.sub("::" + unicode(variable_name), unicode(variable_value), sql_text)
        # db.session.execute(sql_text, {'v1': 'Иванов'}).fetchall()
        return db.session.execute(sql_text).fetchall()
    return []