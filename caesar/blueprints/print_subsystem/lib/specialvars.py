# -*- coding: utf-8 -*-
import re
import datetime
from flask import g
from .query import Query

from sqlalchemy.exc import ProgrammingError, OperationalError

from ..models.models_all import rbSpecialVariablesPreferences

__author__ = 'mmalkov'


class ExecutableSql(object):
    _cache = {}
    _timeout = 60

    def __init__(self, name):
        self.name = name
        self.sql_text = ''
        self.arg_names = []

    def _check_valid_sql(self):
        # Проверка валидности sql-запроса
        if re.search(r"\W(delete|drop|insert|alter)\s", self.sql_text, re.I) or not re.match(r"^\s*SELECT", self.sql_text, re.I):
            raise RuntimeError(
                u"При работе со специальными переменными вы можете использовать только SELECT-запросы! "
                u"Проверьте тексты запросов.")

    def __call__(self, *args, **kwargs):
        self._check_valid_sql()
        # Инициализация словаря аргументов
        len_args = len(args)
        arguments = {}
        for arg_index, arg_name in enumerate(self.arg_names):
            if arg_index < len_args:
                arguments[arg_name] = args[arg_index]
            elif arg_name in kwargs:
                arguments[arg_name] = kwargs[arg_name]
            else:
                raise RuntimeError(u'Argument "%s" of special variable "%s" is not initialized in call' % (arg_name, self.name))

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
                return unicode(value)

        sql_text = re.sub('::?@?(\w+)', matcher, self.sql_text, flags=re.U)

        try:
            result = g.printing_session.execute(sql_text).fetchall()
        except ProgrammingError:
            print "Special Variable ERROR: ", self.name
            raise
        except OperationalError:
            print "Special Variable execution ERROR: ", self.name
            raise
        else:
            return result

    @classmethod
    def get(cls, name):
        if name in cls._cache:
            obj, deadline = cls._cache[name]
            if datetime.datetime.utcnow() < deadline:
                return obj
        obj = cls(name)
        cls._cache[name] = (obj, datetime.datetime.utcnow() + datetime.timedelta(seconds=cls._timeout))
        return obj


class StoredSql(ExecutableSql):
    def __init__(self, name):
        ExecutableSql.__init__(self, name)
        sp_variable = Query(rbSpecialVariablesPreferences).filter(rbSpecialVariablesPreferences.name == name).first()
        if not sp_variable:
            raise RuntimeError(u"Специальная переменная %s не определена" % name)
        self.sql_text = sp_variable.query_text
        self.arg_names = sp_variable.arguments


class InlineSql(ExecutableSql):
    def __init__(self, name, args, text):
        ExecutableSql.__init__(self, name)
        self.arg_names = args
        self.sql_text = text


class SP(object):
    def __init__(self):
        self._cache = {}

    def __getattr__(self, item):
        cache = self.__dict__['_cache']
        if item in cache:
            if cache[item] is None:
                raise AttributeError(item)
            return cache[item]
        cache[item] = data = StoredSql(item)
        return data


def SpecialVariable(name, *args, **kwargs):
    return StoredSql.get(name)(*args, **kwargs)
