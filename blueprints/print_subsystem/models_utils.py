# -*- coding: utf-8 -*-
import struct


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