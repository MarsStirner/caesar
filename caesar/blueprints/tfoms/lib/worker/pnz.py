# -*- encoding: utf-8 -*-
import exceptions
import os
from datetime import date, datetime, timedelta
from ...lib.clients.factory import ClientFactory
from ...lib.thrift_service.pnz.ttypes import PatientOptionalFields, SluchOptionalFields, \
    TClientPolicy, Payment, InvalidArgumentException, NotFoundException, SQLException, TException
from ...lib.thrift_service.pnz.ttypes import PersonOptionalFields
from ...lib.reports import Reports


from ...app import module, _config

try:
    from lxml import etree
    print("running with lxml.etree")
except ImportError:
    import xml.etree.ElementTree as etree
    print("running with ElementTree on Python 2.5+")


class XML_Registry(object):

    def __init__(self,
                 contract_id,
                 start,
                 end,
                 infis_code,
                 primary,
                 tags,
                 departments=list()):

        self.client = ClientFactory.create('pnz', _config('core_service_url'))
        self.contract_id = contract_id
        self.start = start
        self.end = end
        self.infis_code = infis_code
        self.patient_tags = tags.get('patients', list())
        self.event_tags = tags.get('services', list())
        self.primary = primary
        self.departments = departments

    def __patient_optional_tags(self):
        result = []
        patient_events_tags = self.patient_tags
        patient_events_tags.extend(self.event_tags)
        for tag in patient_events_tags:
            try:
                attr = getattr(PatientOptionalFields, tag)
            except exceptions.AttributeError:
                pass
            else:
                result.append(attr)
        return result

    def __person_optional_tags(self):
        result = []
        patient_events_tags = self.patient_tags
        patient_events_tags.extend(self.event_tags)
        for tag in patient_events_tags:
            try:
                attr = getattr(PersonOptionalFields, tag)
            except exceptions.AttributeError:
                pass
            else:
                result.append(attr)
        return result

    def __event_optional_tags(self):
        result = []
        for tag in self.event_tags:
            try:
                attr = getattr(SluchOptionalFields, tag)
            except exceptions.AttributeError:
                pass
            else:
                result.append(attr)
        return result

    def get_data(self):
        data = self.client.get_xml_registry(contract_id=self.contract_id,
                                            infis_code=self.infis_code,
                                            old_infis_code=_config('old_lpu_infis_code'),
                                            start=self.start,
                                            end=self.end,
                                            smo_number=_config('smo_number'),
                                            primary=self.primary,
                                            departments=self.departments,
                                            mo_level=_config('mo_level'),
                                            patient_optional=self.__patient_optional_tags(),
                                            person_optional=self.__person_optional_tags(),
                                            event_optional=self.__event_optional_tags())
        return data


class Services(object):

    def __init__(self, start, end, infis_code, tags):
        self.client = ClientFactory.create('pnz', _config('core_service_url'))
        self.start = start
        self.end = end
        self.infis_code = infis_code
        self.tags = tags

    def __filter_tags(self, tags):
        result = []
        for tag in tags:
            try:
                attr = getattr(SluchOptionalFields, tag)
            except exceptions.AttributeError, e:
                print e
            else:
                result.append(attr)
        return list(set(result))

    def __get_ammount(self, services):
        ammount = 0.0
        if not services:
            return ammount
        for key, event_list in services.iteritems():
            if event_list:
                for event in event_list:
                    ammount += getattr(event, 'SUMV', 0)
        return ammount

    def __get_bill(self, services):
        #TODO: инкрементировать номер пакета (01)?
        data = dict(CODE=1,
                    CODE_MO=_config('lpu_infis_code'),
                    YEAR=self.start.strftime('%Y'),
                    MONTH=self.start.strftime('%m'),
                    NSCHET='%s-%s/%s' % (self.end.strftime('%y%m'), '01', _config('old_lpu_infis_code')[0:3]),
                    DSCHET=date.today().strftime('%Y-%m-%d'),
                    PLAT=_config('payer_code'),
                    SUMMAV=self.__get_ammount(services))
        return data


class Contracts(object):

    def get_contracts(self, infis_code):
        client = ClientFactory.create('pnz', _config('core_service_url'))
        return client.get_contracts(infis_code)


class UploadWorker(object):

    policy_fields = dict(SPOLIS='serial', NPOLIS='number', VPOLIS='policyTypeCode', SMO='insurerInfisCode')

    def __init__(self):
        self.client = ClientFactory.create('pnz', _config('core_service_url'))

    def do_upload(self, file_path):
        data = self.__parse(file_path)
        return self.client.load_tfoms_payments(data)

    def __patient(self, element):
        # TODO: legagy, clean
        data = dict()
        patient_id = None
        for child in element:
            if child.tag == 'ID_PAC':
                patient_id = int(child.text)
            elif child.tag == 'VPOLIS':
                data[child.tag] = int(child.text)
            else:
                data[child.tag] = child.text
        report = Reports()
        result = report.update_patient(patient_id, data)
        if result:
            policy_data = dict()
            for key, value in data.iteritems():
                if key in self.policy_fields:
                    policy_data[self.policy_fields[key]] = value

            policy_data = TClientPolicy(**policy_data)
            try:
                client_result = self.client.update_policy(patient_id, policy_data)
            except NotFoundException, e:
                print e
            except TException, e:
                print e
            else:
                pass

    def __get_filename(self, root):
        for element in root.iter('ZGLV'):
            for child in element:
                if child.tag.lower() == 'filename':
                    filename = child.text
                    return filename

    def __get_nschet(self, root):
        for element in root.iter('SCHET'):
            for child in element:
                if child.tag.lower() == 'nschet':
                    nschet = child.text
                    return nschet

    def __get_case(self, element):
        # TODO: переделать перебор тегов на find?
        payment = Payment()
        confirmed = False
        sumv = 0.0
        for child in element:
            if child.tag.lower() == 'idcase':
                payment.accountItemId = int(child.text)
            elif child.tag.lower() == 'refreason':
                payment.refuseTypeCode = child.text
                if child.text == '0':
                    confirmed = True
                else:
                    confirmed = False
            elif child.tag.lower() == 'comentsl':
                payment.comment = child.text
            elif child.tag.lower() == 'sumv':
                sumv = float(child.text)
        return payment, confirmed, sumv

    def __parse(self, file_path):
        data = dict(payments=list(), refusedAmount=0, payedAmount=0, payedSum=0.0, refusedSum=0.0, comment='')

        if os.path.isfile(file_path):
            try:
                tree = etree.parse(file_path)
            except etree.XMLSyntaxError, e:
                raise AttributeError(u'Некорректная структура XML: {0}'.format(e))
            root = tree.getroot()
            filename = self.__get_filename(root)
            if filename:
                #data['fileName'] = '{0}.xml'.format(filename)
                data['fileName'] = filename
            else:
                raise AttributeError(u'Не заполнен тег FILENAME')
            nschet = self.__get_nschet(root)
            if nschet:
                data['accountNumber'] = nschet
            else:
                raise AttributeError(u'Не заполнен тег NSCHET')
            for element in root.iter('ZAP'):
                for child in element:
                    if child.tag.lower() == 'sluch':
                        payment, confirmed, sumv = self.__get_case(child)
                        data['payments'].append(payment)
                        if confirmed is True:
                            data['payedAmount'] += 1
                            data['payedSum'] += sumv
                        else:
                            data['refusedAmount'] += 1
                            data['refusedSum'] += sumv
        return data


class DBF_Data(object):

    def __init__(self, start, end, infis_code):
        self.client = ClientFactory.create('pnz', _config('core_service_url'))
        self.start = start
        self.end = end
        self.infis_code = infis_code

    def get_data(self):
        pass


class DBF_Policlinic(DBF_Data):

    def get_data(self):
        data = self.client.get_policlinic_dbf(infis_code=self.infis_code,
                                              start=self.start,
                                              end=self.end)
        return data


class DBF_Hospital(DBF_Data):

    def get_data(self):
        data = self.client.get_hospital_dbf(infis_code=self.infis_code,
                                            start=self.start,
                                            end=self.end)
        return data

