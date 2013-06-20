# -*- coding: utf-8 -*-

from datetime import datetime
import calendar

from urlparse import urlparse

from thrift.transport import TTransport, TSocket
from thrift.protocol import TBinaryProtocol

from thrift_service.TFOMSService import Client
from thrift_service.ttypes import Patient, PatientOptionalFields, Sluch, SluchOptionalFields, Usl, Spokesman
from thrift_service.ttypes import InvalidArgumentException, NotFoundException, SQLException, TException


class TFOMSClient(object):
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
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Client(protocol)
        self.transport.open()

        self.date_tags = ['DR', 'DATE_1', 'DATE_2', 'DATE_IN', 'DATE_OUT']

    def __del__(self):
        self.transport.close()

    def __convert_date(self, timestamp):
        return datetime.fromtimestamp(timestamp / 1000)

    def __convert_dates(self, data):
        for item in data:
            for element in data[item]:
                for attr, value in element.__dict__.iteritems():
                    if attr in self.date_tags and isinstance(value, int):
                        setattr(element, attr, self.__convert_date(value))
                    elif isinstance(value, basestring):
                        setattr(element, attr, value.strip().decode('utf8'))
        return data

    def __unicode_result(self, data):
        for element in data:
            for attr, value in element.__dict__.iteritems():
                if isinstance(value, basestring):
                    setattr(element, attr, value.strip().decode('utf8'))
                elif attr in self.date_tags and isinstance(value, int):
                    setattr(element, attr, self.__convert_date(value))
        return data

    def get_patients(self, infis_code, start, end, **kwargs):
        """Получает список пациентов, которому оказаны услуги в данном ЛПУ в указанный промежуток времени"""
        result = None
        try:
            optional = kwargs.get('optional', list())
            result = self.client.getPatients(beginDate=calendar.timegm(start.timetuple()) * 1000,
                                             endDate=calendar.timegm(end.timetuple()) * 1000,
                                             infisCode=infis_code,
                                             optionalFields=optional)
        except InvalidArgumentException, e:
            print e
        except SQLException, e:
            print e
        except NotFoundException, e:
            raise e
        except TException, e:
            raise e
        return self.__unicode_result(result)

    def get_patient_events(self, patients, start, end, infis_code, **kwargs):
        """Получает список событий и услуг, оказанных пациенту в указанный промежуток времени"""
        result = None
        try:
            optional = kwargs.get('optional', list())
            result = self.client.getSluchByPatients(patientId=patients,
                                                    beginDate=calendar.timegm(start.timetuple()) * 1000,
                                                    endDate=calendar.timegm(end.timetuple()) * 1000,
                                                    infisCode=infis_code,
                                                    optionalFields=optional)
        except InvalidArgumentException, e:
            print e
        except SQLException, e:
            print e
        except NotFoundException, e:
            raise e
        except TException, e:
            raise e
        return self.__convert_dates(result)

    def prepare_tables(self):
        """Запускает процесс обновления данных во временной таблице на сервере"""
        result = None
        try:
            result = self.client.prepareTables()
        except InvalidArgumentException, e:
            print e
        except SQLException, e:
            print e
        except NotFoundException, e:
            raise e
        except TException, e:
            raise e
        return result