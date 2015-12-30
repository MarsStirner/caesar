# -*- coding: utf-8 -*-
import logging
import re
import datetime
from flask import g
from sqlalchemy.exc import ProgrammingError, OperationalError

from ..models.models_all import rbSpecialVariablesPreferences

__author__ = 'mmalkov'


simple_logger = logging.getLogger('simple')


def SpecialVariable(name, *args, **kwargs):
    sp_variable = g.printing_session.query(rbSpecialVariablesPreferences).filter(rbSpecialVariablesPreferences.name == name).first()
    if not sp_variable:
        simple_logger.critical(u'Специальная переменная "%s" не найдена' % name)
        raise RuntimeError(u'Специальная переменная "%s" не найдена' % name)
    # Проверка валидности sql-запроса
    query_text = sp_variable.query_text
    if re.search(r"\W(delete|drop|insert|alter)\s", query_text, re.I) or not re.match(r"^\s*SELECT", query_text, re.I):
        simple_logger.critical(u'При работе со специальными переменными вы можете использовать только SELECT-запросы!\n' + query_text)
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

    # Эта самая страшная функция. Она должна разварачивать каждую переменную SQL-запроса в её значение
    # Самая жопа в том, что это должно быть БЕЗОПАСНО.
    # Ну и, конечно, при переходе на PgSql, стопудово придётся переписывать
    def matcher(match):
        arg_name = match.group(1)
        if arg_name not in arguments:
            return '\\' + match.group(0)
        value = arguments[arg_name]
        if isinstance(value, list):
            return u','.join(u"'%s'" % unicode(i).replace(ur"'", ur"\'") for i in value)
        elif isinstance(value, basestring):
            return u"'%s'" % value.replace(ur"'", ur"\'")
        elif value is None:
            return u'NULL'
        elif isinstance(value, datetime.datetime):
            return u"'%s'" % value.strftime('%Y-%m-%d %H:%M')
        elif isinstance(value, datetime.date):
            return u"'%s'" % value.strftime('%Y-%m-%d')
        elif isinstance(value, datetime.time):
            return u"'%s'" % value.strftime('%H:%M')
        else:
            return unicode(value).replace("'", "\'")

    exec_text = re.sub('::?@?(\w+)', matcher, query_text, flags=re.U)

    try:
        result = g.printing_session.execute(exec_text).fetchall()
    except ProgrammingError:
        simple_logger.critical(u'Ошибка в тексте запроса специальной переменной "%s"\n\n%s\n\n%s\n\n%s' % (name, query_text, (args, kwargs), exec_text))
        print "Special Variable ERROR: ", name
        raise
    except OperationalError:
        simple_logger.critical(u'Ошибка при выполнении запроса специальной переменной "%s"\n\n%s\n\n%s\n\n%s' % (name, query_text, (args, kwargs), exec_text))
        print "Special Variable execution ERROR: ", name
        raise
    except:
        simple_logger.critical(u'Неизвестная ошибка при выполнении запроса специальной переменной "%s"\n\n%s\n\n%s\n\n%s' % (name, query_text, (args, kwargs), exec_text))
        print "Special Variable execution ERROR: ", name
        raise
    else:
        simple_logger.info(u'Специальная переменная "%s" выполнена' % name)
        return result
