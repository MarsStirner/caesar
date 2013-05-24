# -*- coding: utf-8 -*-

import exceptions
import datetime
import calendar
import base64
import logging
from urlparse import urlparse

from thrift.transport import TTransport, TSocket, THttpClient
from thrift.protocol import TCompactProtocol, TProtocol

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
        transport = TTransport.TBufferedTransport(socket)
        protocol = TCompactProtocol.TCompactProtocol(transport)
        self.client = Client(protocol)
        transport.open()

    def __unicode_result(self, data):
        for element in data:
            for attr, value in element.__dict__.iteritems():
                if isinstance(value, basestring):
                    setattr(element, attr, value.strip().decode('utf8'))
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

    def get_patient_events(self, patient_id, start, end, infis_code, **kwargs):
        """Получает список событий и услуг, оказанных пациенту в указанный промежуток времени"""
        result = None
        try:
            optional = kwargs.get('optional', list())
            result = self.client.getSluchByPatient(patientId=patient_id,
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
        return self.__unicode_result(result)