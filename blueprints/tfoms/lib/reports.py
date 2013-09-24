# -*- encoding: utf-8 -*-
from datetime import datetime
from application.database import db
from thrift_service.ttypes import InvalidArgumentException, NotFoundException, SQLException, TException
from thrift_service.ttypes import PatientOptionalFields, SluchOptionalFields, TClientPolicy
from ..lib.service_client import TFOMSClient as Client
from ..app import module, _config


class Reports(object):

    def __init__(self):
        self.client = Client(_config('core_service_url'))

    def get_bills(self, infis_code):
        return self.client.get_bills(infis_code)

    def get_bill_cases(self, bill_id):
        return self.client.get_bill_cases(bill_id)

    def delete_bill(self, bill_id):
        return self.client.delete_bill(bill_id)