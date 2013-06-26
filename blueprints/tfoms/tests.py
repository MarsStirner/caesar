# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
import unittest
import logging
import time

from lib.service_client import TFOMSClient
#from lib.data import DownloadWorker
from .app import _config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from models import Template, TagsTree

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from application.app import app, db

logging.basicConfig()
logging.getLogger('suds.client').setLevel(logging.DEBUG)

db.app = app


class TestPatients(unittest.TestCase):

    def setUp(self):
        self.client = TFOMSClient(_config('core_service_url'))
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
        file_url = worker.do_download(template_id, start, end, _config('lpu_infis_code'))
        self.assertIsNotNone(file_url)


class SimpleTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        #self.driver = webdriver.Opera()
        self.driver.implicitly_wait(30)
        self.base_url = "http://127.0.0.1:5000/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True

    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True


class ClickTabs(SimpleTestCase):

    def test_click_tabs(self):
        driver = self.driver
        driver.get(self.base_url + "/tfoms/")
        driver.find_element_by_link_text("Выгрузка").click()
        driver.find_element_by_link_text("Выгрузка DBF").click()
        driver.find_element_by_link_text("Загрузка").click()
        driver.find_element_by_link_text("Отчёты").click()
        driver.find_element_by_id("drop1").click()
        driver.find_element_by_link_text("Шаблоны").click()
        driver.find_element_by_link_text("Сведения об оказанной мед.помощи (XML)").click()
        driver.find_element_by_link_text("Выгрузка в формате DBF").click()
        driver.find_element_by_id("drop1").click()
        driver.find_element_by_link_text("Общие настройки").click()


class EmptyTemplateName(SimpleTestCase):

    def test_empty_template_name(self):
        driver = self.driver
        driver.get(self.base_url + "/tfoms/settings_template/xml_service/")
        driver.find_element_by_link_text("Сведения об оказанной мед.помощи (XML)").click()
        driver.find_element_by_id("Save").click()
        # Warning: assertTextPresent may require manual changes
        self.assertRegexpMatches(driver.find_element_by_css_selector("BODY").text.encode('utf8'),
                                 r"^[\s\S]*Внимание! Необходимо указать наименование шаблона![\s\S]*$")
        driver.find_element_by_link_text("Сведения о персональных данных (XML)").click()
        driver.find_element_by_id("Save").click()
        # Warning: assertTextPresent may require manual changes
        self.assertRegexpMatches(driver.find_element_by_css_selector("BODY").text.encode('utf8'),
                                 r"^[\s\S]*Внимание! Необходимо указать наименование шаблона![\s\S]*$")
        driver.find_element_by_link_text("Выгрузка в формате DBF").click()
        driver.find_element_by_id("Save").click()
        # Warning: assertTextPresent may require manual changes
        self.assertRegexpMatches(driver.find_element_by_css_selector("BODY").text.encode('utf8'),
                                 r"^[\s\S]*Внимание! Необходимо указать наименование шаблона![\s\S]*$")


class SaveDeleteNewTemplate(SimpleTestCase):

    def test_save_delete_new_template(self):
        #wait = ui.WebDriverWait(self.driver, 15)
        driver = self.driver
        driver.get(self.base_url + "/tfoms/settings_template/xml_patient/")
        driver.find_element_by_id("name").clear()
        driver.find_element_by_id("name").send_keys("TestTemplate")
        driver.find_element_by_id("Save").click()
        self.assertTrue(self.is_element_present(By.LINK_TEXT, "TestTemplate"))
        driver.find_element_by_link_text("TestTemplate").click()
        driver.find_element_by_id("confirm-delete").click()
        link_yes = driver.find_element_by_xpath("//*[@id='modal-from-dom']/div[3]/a[2]")
        time.sleep(3)
        link_yes.click()
        #wait.until(lambda driver: driver.find_element_by_xpath("//*[@id='modal-from-dom'][contains(@style,'display: none')]"))
        time.sleep(10)
        deleteLinks = driver.find_elements_by_link_text("TestTemplate")
        print 'deleteLinks', deleteLinks
        self.assertTrue(not deleteLinks)

        driver.find_element_by_link_text("Сведения об оказанной мед.помощи (XML)").click()
        driver.find_element_by_id("name").clear()
        driver.find_element_by_id("name").send_keys("TestTemplate_usl")
        driver.find_element_by_id("Save").click()
        self.assertTrue(self.is_element_present(By.LINK_TEXT, "TestTemplate_usl"))
        driver.find_element_by_id("confirm-delete").click()
        time.sleep(3)
        driver.find_element_by_xpath("//*[@id='modal-from-dom']/div[3]/a[2]").click()
        #wait.until(lambda driver: driver.find_element_by_xpath("//*[@id='modal-from-dom'][contains(@style,'display: none')]"))
        time.sleep(10)
        deleteLinks = driver.find_elements_by_link_text("TestTemplate_usl")
        print 'deleteLinks2', deleteLinks
        self.assertTrue(not deleteLinks)

        driver.find_element_by_link_text("Выгрузка в формате DBF").click()
        driver.find_element_by_id("name").clear()
        driver.find_element_by_id("name").send_keys("TestTemplate_dbf")
        driver.find_element_by_id("Save").click()
        self.assertTrue(self.is_element_present(By.LINK_TEXT, "TestTemplate_dbf"))
        driver.find_element_by_id("confirm-delete").click()
        time.sleep(3)
        driver.find_element_by_xpath("//*[@id='modal-from-dom']/div[3]/a[2]").click()
        time.sleep(10)
        deleteLinks = driver.find_elements_by_link_text("TestTemplate_dbf")
        print 'deleteLinks3', deleteLinks
        self.assertTrue(not deleteLinks)


class UniqueTemplateName(SimpleTestCase):

    def test_unique_template_name(self):
        driver = self.driver
        driver.get(self.base_url + "/tfoms/settings_template/xml_patient/")
        driver.find_element_by_id("name").clear()
        driver.find_element_by_id("name").send_keys("TestTemplate")
        driver.find_element_by_id("Save").click()
        time.sleep(5)
        driver.find_element_by_link_text("Создать").click()
        driver.find_element_by_id("name").clear()
        driver.find_element_by_id("name").send_keys("TestTemplate")
        time.sleep(2)
        driver.find_element_by_id("Save").click()
        # Warning: assertTextPresent may require manual changes
        time.sleep(10)
        self.assertRegexpMatches(driver.find_element_by_css_selector("BODY").text.encode('utf8'),
                                 r"^[\s\S]*Внимание! Наименования шаблонов должны быть уникальны![\s\S]*$")

        driver.find_element_by_link_text("Сведения об оказанной мед.помощи (XML)").click()
        time.sleep(5)
        driver.find_element_by_id("name").clear()
        driver.find_element_by_id("name").send_keys("TestTemplate_usl")
        driver.find_element_by_id("Save").click()
        time.sleep(5)
        driver.find_element_by_link_text("Создать").click()
        driver.find_element_by_id("name").clear()
        driver.find_element_by_id("name").send_keys("TestTemplate_usl")
        time.sleep(2)
        driver.find_element_by_id("Save").click()
        # Warning: assertTextPresent may require manual changes
        time.sleep(10)
        self.assertRegexpMatches(driver.find_element_by_css_selector("BODY").text.encode('utf8'),
                                 r"^[\s\S]*Внимание! Наименования шаблонов должны быть уникальны![\s\S]*$")

        driver.find_element_by_link_text("Выгрузка в формате DBF").click()
        time.sleep(5)
        driver.find_element_by_link_text("Сведения об оказанной мед.помощи (XML)").click()
        driver.find_element_by_id("name").clear()
        driver.find_element_by_id("name").send_keys("TestTemplate_dbf")
        driver.find_element_by_id("Save").click()
        time.sleep(5)
        driver.find_element_by_link_text("Создать").click()
        driver.find_element_by_id("name").clear()
        driver.find_element_by_id("name").send_keys("TestTemplate_dbf")
        time.sleep(2)
        driver.find_element_by_id("Save").click()
        time.sleep(10)
        # Warning: assertTextPresent may require manual changes
        self.assertRegexpMatches(driver.find_element_by_css_selector("BODY").text.encode('utf8'),
                                 r"^[\s\S]*Внимание! Наименования шаблонов должны быть уникальны![\s\S]*$")

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

        template = Template.query.filter_by(name="TestTemplate").first()
        template_usl = Template.query.filter_by(name="TestTemplate_usl").first()
        template_dbf = Template.query.filter_by(name="TestTemplate_dbf").first()
        db.session.delete(template)
        db.session.delete(template_usl)
        db.session.delete(template_dbf)
        db.session.commit()

if __name__ == "__main__":
    unittest.main()
