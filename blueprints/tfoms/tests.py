# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
import unittest
import logging
from lib.service_client import TFOMSClient
from lib.data import DownloadWorker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from application.app import app, db
from config import CORE_SERVICE_URL, LPU_INFIS_CODE

logging.basicConfig()
logging.getLogger('suds.client').setLevel(logging.DEBUG)

db.app = app


class TestPatients(unittest.TestCase):

    def setUp(self):
        self.client = TFOMSClient(CORE_SERVICE_URL)
        self.app = app

    def tearDown(self):
        del self.client
        del self.app

    # def testGetPatients(self):
    #     beginDate = datetime(2013, 01, 01)
    #     endDate = datetime(2013, 06, 01)
    #     patients = self.client.get_patients(LPU_INFIS_CODE, beginDate, endDate)
    #     if patients:
    #         self.assertIsInstance(patients, list)

    def testDowloadPatients(self):
        template_id = 16
        start = datetime(2013, 01, 01)
        end = datetime(2013, 06, 01)
        worker = DownloadWorker()
        file_url = worker.do_download(template_id, start, end, LPU_INFIS_CODE)
        self.assertIsNotNone(file_url)
