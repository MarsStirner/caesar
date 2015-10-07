# -*- coding: utf-8 -*-
import calendar
from thrift.protocol import TBinaryProtocol

from .base import BaseTFOMSClient

from ...lib.thrift_service.spb.TFOMSService import Client
from ...lib.thrift_service.spb.ttypes import TException, InvalidDateIntervalException


class TFOMSClient(BaseTFOMSClient):
    """Класс клиента для взаимодействия с ядром по Thrift-протоколу"""

    class Struct:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    def __init__(self, url):
        super(TFOMSClient, self).__init__(url)

        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Client(protocol)

    def get_xml_registry(self, start, end):
        """Получает список пациентов и услуг для XML-выгрузки данном ЛПУ в указанный промежуток времени"""
        try:
            result = self.client.getRegistry(begInterval=calendar.timegm(start.timetuple()) * 1000,
                                             endInterval=calendar.timegm(end.timetuple()) * 1000)
        except InvalidDateIntervalException as e:
            raise e
        except TException, e:
            raise e
        return result

    def get_departments(self, infis_code):
        """Получает список подразделений в данном ЛПУ"""
        raise NotImplementedError

    def get_contracts(self, infis_code):
        """Получает список доступных контрактов в данном ЛПУ"""
        raise NotImplementedError

    def get_bills(self, infis_code):
        """Получает список доступных счетов в данном ЛПУ"""
        raise NotImplementedError

    def get_bill(self, bill_id):
        """Получает счет по id"""
        raise NotImplementedError

    def get_bill_cases(self, bill_id):
        """Получает список доступных счетов в данном ЛПУ"""
        raise NotImplementedError

    def change_cases_status(self, data):
        """Смена статусов для позиций счета"""
        raise NotImplementedError

    def delete_bill(self, bill_id):
        """Получает список доступных счетов в данном ЛПУ"""
        raise NotImplementedError

    def get_patients(self, infis_code, start, end, **kwargs):
        """Получает список пациентов, которому оказаны услуги в данном ЛПУ в указанный промежуток времени"""
        raise NotImplementedError

    def get_patient_events(self, patients, start, end, infis_code, **kwargs):
        """Получает список событий и услуг, оказанных пациенту в указанный промежуток времени"""
        raise NotImplementedError

    def prepare_tables(self):
        """Запускает процесс обновления данных во временной таблице на сервере"""
        raise NotImplementedError

    def get_policlinic_dbf(self, infis_code, start, end, **kwargs):
        """Получает данные для dbf по поликлинике и стационару в данном ЛПУ в указанный промежуток времени"""
        raise NotImplementedError

    def get_hospital_dbf(self, infis_code, start, end, **kwargs):
        """Получает данные для dbf по поликлинике и стационару в данном ЛПУ в указанный промежуток времени"""
        raise NotImplementedError

    def update_policy(self, patient_id, data):
        """Обновление полисов у пациентов"""
        raise NotImplementedError

    def load_tfoms_payments(self, data):
        """Отправка данных, полученных из ТФОМС"""
        raise NotImplementedError
