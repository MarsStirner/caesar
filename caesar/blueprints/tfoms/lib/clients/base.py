# -*- coding: utf-8 -*-
import os
from datetime import date, timedelta
from urlparse import urlparse

from thrift.transport import TTransport, TSocket


class BaseTFOMSClient(object):
    """Класс клиента для взаимодействия с ядром по Thrift-протоколу"""

    class Struct:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    def __init__(self, url):
        self.url = url
        url_parsed = urlparse(self.url)
        host = url_parsed.hostname
        port = url_parsed.port

        socket = TSocket.TSocket(host, port)
        self.transport = TTransport.TBufferedTransport(socket)
        self.transport.open()

        self.date_tags = ['DR',
                          'DATE_1',
                          'DATE_2',
                          'DATE_IN',
                          'DATE_OUT',
                          'D_R',
                          'DAT_PR',
                          'DAT_VV',
                          'DAT_BLVN',
                          'DAT_ELVN',
                          'date',
                          'begDate',
                          'endDate',
                          'exposeDate',
                          'serviceDate', ]

    def __del__(self):
        self.transport.close()

    def __convert_date(self, timestamp):
        if os.name == 'nt':
            # Hack for Win (http://stackoverflow.com/questions/10588027/converting-timestamps-larger-than-maxint-into-datetime-objects)
            return date.fromtimestamp(0) + timedelta(seconds=timestamp / 1000)
        return date.fromtimestamp(timestamp / 1000)

    def __convert_dates(self, data):
        #TODO: унифицировать для обеих выборок, учесть вложенность
        if isinstance(data, list):
            for item in data:
                if isinstance(item, list):
                    for element in item:
                        for attr, value in element.__dict__.iteritems():
                            if attr in self.date_tags and isinstance(value, (int, long)) and value:
                                setattr(element, attr, self.__convert_date(value))
                            elif isinstance(value, basestring):
                                setattr(element, attr, value.strip().decode('utf8'))
                else:
                    for attr, value in item.__dict__.iteritems():
                        if attr in self.date_tags and isinstance(value, (int, long)) and value:
                            setattr(item, attr, self.__convert_date(value))
                        elif isinstance(value, basestring):
                            setattr(item, attr, value.strip().decode('utf8'))
        elif isinstance(data, object):
            for attr, value in data.__dict__.iteritems():
                    if attr in self.date_tags and isinstance(value, (int, long)) and value:
                        setattr(data, attr, self.__convert_date(value))
                    elif isinstance(value, basestring):
                        setattr(data, attr, value.strip().decode('utf8'))
        return data

    def __unicode_result(self, data):
        #TODO: унифицировать для обеих выборок, учесть вложенность
        for element in data:
            for attr, value in element.__dict__.iteritems():
                if isinstance(value, basestring):
                    setattr(element, attr, value.strip().decode('utf8'))
                elif attr in self.date_tags and isinstance(value, (int, long)) and value:
                    setattr(element, attr, self.__convert_date(value))
        return data