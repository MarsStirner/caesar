# -*- coding: utf-8 -*-
import struct
import datetime
from ..database import Base, metadata


def get_model_by_name(name):
    from blueprints.print_subsystem.models import models_all, schedule
    for mod in (models_all, schedule):
        if hasattr(mod, name):
            return getattr(mod, name)
    return None


def trim(s):
    return u' '.join(unicode(s).split())


def formatShortNameInt(lastName, firstName, patrName):
    return trim(lastName + ' ' + ((firstName[:1]+'.') if firstName else '') + ((patrName[:1]+'.') if patrName else ''))


def formatNameInt(lastName, firstName, patrName):
    return trim(lastName+' '+firstName+' '+patrName)


def code128C(barcode):
    """Make Code 128C of integer barcode (100000 - 999999)"""
    b_struct = struct.Struct(">BBBBBB")
    if not (100000 <= barcode <= 999999):
        # Этого не должно случиться.
        return None
    # Стартовый и стоповый символы в нашей таблице символов имеют иные коды (+64)
    start = 0xcd
    stop = 0xce
    c, c3 = divmod(barcode, 100)
    c, c2 = divmod(c, 100)
    c, c1 = divmod(c, 100)
    cs = reduce(lambda x, (y, c): (x + y*c) % 103, [(c1, 1), (c2, 2), (c3, 3)], 2)
    # Транслируем коды символов
    c1, c2, c3, cs = tuple(map(lambda w: w + 100 if w > 94 else w + 32, (c1, c2, c3, cs)))
    barcode_char = b_struct.pack(start, c1, c2, c3, cs, stop)
    return barcode_char


def code128C_any(string):
    number = int(string)
    result = []
    while 1:
        number, mod = divmod(number, 100)
        result.append(mod)
        if number == 0:
            break
    result.reverse()
    result.append(reduce(lambda x, (c, y): (x + y * (c + 1)) % 103, enumerate(result), 105))
    result = [0xcd] + [
        (w + 100 if w > 94 else w + 32)
        for w in result
    ] + [0xce]
    return b''.join(map(chr, result)).decode('windows-1252')


def calcAgeInDays(birthDay, today):
    if isinstance(birthDay, DateInfo):
        birthDay = birthDay.date
    return (today-birthDay).days


def calcAgeInWeeks(birthDay, today):
    return calcAgeInDays(birthDay, today)/7


def calcAgeInMonths(birthDay, today):
    if isinstance(birthDay, DateInfo):
        birthDay = birthDay.date

    bYear = birthDay.year
    bMonth = birthDay.month
    bDay = birthDay.day

    tYear = today.year
    tMonth = today.month
    tDay = today.day

    result = (tYear-bYear)*12+(tMonth-bMonth)
    if bDay > tDay:
        result -= 1
    return result


def calcAgeInYears(birthDay, today):
    if isinstance(birthDay, DateInfo):
        birthDay = birthDay.date

    bYear = birthDay.year
    bMonth = birthDay.month
    bDay = birthDay.day

    tYear = today.year
    tMonth = today.month
    tDay = today.day

    result = tYear-bYear
    if bMonth > tMonth or (bMonth == tMonth and bDay > tDay):
        result -= 1
    return result


def calcAgeTuple(birthDay, today):
    d = calcAgeInDays(birthDay, today)
    if d >= 0:
        return (
            d,
            d / 7,
            calcAgeInMonths(birthDay, today),
            calcAgeInYears(birthDay, today)
        )
    return None


def formatYears(years):
    return '%d %s' % (years, agreeNumberAndWord(years, (u'год', u'года', u'лет')))


def formatMonths(months):
    return '%d %s' % (months, agreeNumberAndWord(months, (u'месяц', u'месяца', u'месяцев')))


def formatWeeks(weeks):
    return '%d %s' % (weeks, agreeNumberAndWord(weeks, (u'неделя', u'недели', u'недель')))


def formatDays(days):
    return '%d %s' % (days, agreeNumberAndWord(days, (u'день', u'дня', u'дней')))


def formatYearsMonths(years, months):
    if years == 0:
        return formatMonths(months)
    elif months == 0:
        return formatYears(years)
    else:
        return formatYears(years) + ' ' + formatMonths(months)


def formatMonthsWeeks(months, weeks):
    if months == 0:
        return formatWeeks(weeks)
    elif weeks == 0:
        return formatMonths(months)
    else:
        return formatMonths(months) + ' ' + formatWeeks(weeks)


def agreeNumberAndWord(num, words):
    u"""
        Согласовать число и слово:
        num - число, слово = (один, два, много)
        agreeNumberAndWord(12, (u'год', u'года', u'лет'))
    """
    if num < 0:
        num = -num
    if (num/10) % 10 != 1:
        if num % 10 == 1:
            return words[0]
        elif 1 < num % 10 < 5:
            return words[1]
    return words[-1]


def formatSex(sex, full=False):
    """
    Делаем из пола строку

    sex - код пола (1 мужской, 2 женский)
    full - формат (True полный, False однобуквенный)
    """

    if sex == 1:
        return u'Мужской' if full else u'М'
    elif sex == 2:
        return u'Женский' if full else u'Ж'
    else:
        return u'Не указан' if full else u''


class DateInfo(object):
    def __init__(self, date=None):
        if date is None:
            self.date = None
        else:
            self.date = date

    def __str__(self):
        return formatDate(self.date)

    def __add__(self, x):
        return formatDate(self.date) + str(x)

    def __radd__(self, x):
        return str(x) + formatDate(self.date)


class TimeInfo(object):
    def __init__(self, time=None):
        if time is None:
            self.time = datetime.time()
        else:
            self.time = time

    def toString(self):
        return formatTime(self.time)

    def __str__(self):
        return self.toString()

    def __add__(self, x):
        return self.toString() + str(x)

    def __radd__(self, x):
        return str(x) + self.toString()


class DateTimeInfo(object):
    def __init__(self, date=None):
        if date is None:
            self.datetime = None
        else:
            self.datetime = date

    def __str__(self):
        if self.datetime:
            date = self.datetime.date() if self.datetime else None
            time = self.datetime.time() if self.datetime else None
            return formatDate(date) + ' ' + formatTime(time)
        else:
            return ''

    def __add__(self, x):
        return formatDate(self.datetime) + str(x)

    def __radd__(self, x):
        return str(x)+formatDate(self.datetime)

    date = property(lambda self: self.datetime.date() if self.datetime else None)
    time = property(lambda self: self.datetime.time() if self.datetime else None)


def formatDate(time):
    return unicode(time.strftime('%d.%m.%Y')) if time else ''


def formatTime(time):
    return unicode(time.strftime('%H:%M')) if time else ''


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


def Query(cls):
    from flask import g
    return g.printing_session.query(cls)


class ReadProxy(object):
    def __init__(self, field_name, wrapper_factory, *args, **kwargs):
        self.field_name = field_name
        self.wrapper_factory = wrapper_factory
        self.args = args
        self.kwargs = kwargs

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.wrapper_factory(
            getattr(instance, self.field_name),
            *self.args, **self.kwargs
        )


def DummyProperty(base_class, message):
    class DummyClass(base_class):
        def __unicode__(self):
            return message

    class DummyEmitter(object):
        def __get__(self, instance, owner):
            if instance is None:
                return DummyClass
            return DummyClass()

    return DummyEmitter

