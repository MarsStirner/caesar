# -*- encoding: utf-8 -*-
import os
import exceptions
from datetime import date
from zipfile import ZipFile, ZIP_DEFLATED
import dbf
from flask import current_app
from jinja2 import Environment, PackageLoader
from application.database import db
from service_client import TFOMSClient as Client
from thrift_service.ttypes import InvalidArgumentException, NotFoundException, SQLException, TException
from thrift_service.ttypes import PatientOptionalFields, SluchOptionalFields, TClientPolicy
from ..app import module, _config
from ..models import Template, TagsTree, Tag, DownloadCases, DownloadBills
from reports import Reports

try:
    from lxml import etree
    print("running with lxml.etree")
except ImportError:
    import xml.etree.ElementTree as etree
    print("running with ElementTree on Python 2.5+")


DOWNLOADS_DIR = os.path.join(module.static_folder, 'downloads')
UPLOADS_DIR = os.path.join(module.static_folder, 'uploads')


def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format)


class Patients(object):

    def __init__(self, start, end, infis_code, tags):
        self.client = Client(_config('core_service_url'))
        if current_app.debug:
            try:
                self.client.prepare_tables()
            except Exception, e:
                print e
        self.start = start
        self.end = end
        self.infis_code = infis_code
        self.tags = tags

    def __filter_tags(self, tags):
        result = []
        for tag in tags:
            try:
                attr = getattr(PatientOptionalFields, tag)
            except exceptions.AttributeError:
                pass
            else:
                result.append(attr)
        return result

    def get_data(self):
        data = self.client.get_patients(infis_code=self.infis_code,
                                        start=self.start,
                                        end=self.end,
                                        optional=self.__filter_tags(self.tags))
        return data


class Services(object):

    def __init__(self, start, end, infis_code, tags):
        self.client = Client(_config('core_service_url'))
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
        data = dict(CODE=1,
                    CODE_MO=_config('lpu_infis_code'),
                    YEAR=self.start.strftime('%Y'),
                    MONTH=self.start.strftime('%m'),
                    NSCHET='%s-%s/%s' % (self.end.strftime('%Y%m'), 1, _config('old_lpu_infis_code')),
                    DSCHET=date.today().strftime('%Y-%m-%d'),
                    PLAT=_config('payer_code'),
                    SUMMAV=self.__get_ammount(services))
        return data

    def get_data(self):
        patients = Patients(self.start, self.end, self.infis_code, self.tags)
        patients_data = patients.get_data()

        patient_ids = []
        patients = dict()
        for patient in patients_data:
            patient_ids.append(patient.patientId)
            patients[patient.patientId] = patient

        data = self.client.get_patient_events(infis_code=self.infis_code,
                                              start=self.start,
                                              end=self.end,
                                              patients=patient_ids,
                                              optional=self.__filter_tags(self.tags))
        return dict(patients=patients, services=data, bill=self.__get_bill(data))


class DBF_Data(object):

    def __init__(self, start, end, infis_code):
        self.client = Client(_config('core_service_url'))
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


class DownloadWorker(object):

    def __get_template(self, id):
        return db.session.query(Template).get(id)

    def __get_template_tree(self, template_id):
        root = (db.session.query(TagsTree)
                .filter(TagsTree.template_id == template_id, TagsTree.parent_id == None)
                .first())
        # tree = TagTree(template_id=template_id, root=0)
        # return tree.load_tree(0, [])
        return [root]

    def __tags_list(self, template_id):
        tags = (db.session.query(Tag.code)
                .join(TagsTree)
                .filter(TagsTree.template_id == template_id)
                .order_by(TagsTree.ordernum).all())
        tags = [tag[0] for tag in tags]
        # tags = list()
        # for item in tree:
        #     tags.append(item.tag.code)
        return tags

    def __get_conditions(self):
        return None

    def get_data(self, template_type, **kwargs):
        if template_type == ('xml', 'patients'):
            data = Patients(**kwargs).get_data()
        elif template_type == ('xml', 'services'):
            data = Services(**kwargs).get_data()
        elif template_type == ('dbf', 'policlinic'):
            if 'tags' in kwargs:
                del kwargs['tags']
            data = DBF_Policlinic(**kwargs).get_data()
        elif template_type == ('dbf', 'hospital'):
            if 'tags' in kwargs:
                del kwargs['tags']
            data = DBF_Hospital(**kwargs).get_data()
        else:
            raise NameError
        return data

    def __get_file_object(self, template_type, end, tags):
        return File.provider(data_type=template_type[1], end=end, file_type=template_type[0], tags=tags)

    def do_download(self, template_id, start, end, infis_code):
        template = self.__get_template(template_id)
        template_type = (template.type.download_type.code, template.type.code)
        tree = self.__get_template_tree(template_id)
        if tree is None:
            return None
        conditions = self.__get_conditions()
        tags = self.__tags_list(template_id)
        data = self.get_data(template_type,
                             start=start,
                             end=end,
                             infis_code=infis_code,
                             tags=tags)
                             # conditions=conditions)
        file_obj = self.__get_file_object(template_type, end=end, tags=tags)
        file_url = file_obj.save_file(tree, data)
        if template_type == ('xml', 'services'):
            reports = Reports()
            data.update(dict(template_id=template_id, file=file_obj.head, start=start, end=end))
            try:
                reports.save_data(data)
            except Exception, e:
                print e
        elif template_type == ('xml', 'patients'):
            reports = Reports()
            try:
                reports.add_patients(data)
            except Exception, e:
                print e
        if template.archive:
            file_url = file_obj.archive_file()
        return file_url


class UploadWorker(object):

    policy_fields = dict(SPOLIS='serial', NPOLIS='number', VPOLIS='policyTypeCode', SMO='insurerInfisCode')

    def __init__(self):
        self.client = Client(_config('core_service_url'))

    def do_upload(self):
        pass

    def __patient(self, element):
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

    def __update_case(self, element, filename):
        data = dict()
        case_id = None
        case = None
        for child in element:
            if child.tag == 'IDCASE':
                case_id = int(child.text)
            elif child.tag == 'REFREASON':
                data[child.tag] = child.text
                if child.text == '0':
                    data['confirmed'] = True
            elif child.tag == 'COMENTSL':
                data[child.tag] = child.text
        if case_id:
            case = db.session.query(DownloadCases).get(case_id)
        if case and data:
            data['confirmed_date'] = date.today()
            data['uploaded_file'] = filename
            for key, value in data.iteritems():
                if hasattr(case, key):
                    setattr(case, key, value)
            db.session.commit()
        return data.get('confirmed', False)

    def __update_bill(self, element):
        data = dict()
        for child in element:
            if child.text:
                data[child.tag] = child.text
        if data:
            bill = db.session.query(DownloadBills).filter(DownloadBills.NSCHET == data.get('NSCHET')).first()
            if bill:
                for key, value in data.iteritems():
                    if hasattr(bill, key):
                        setattr(bill, key, value)
            db.session.commit()

    def parse(self, file_path):
        filename = None
        if os.path.isfile(file_path):
            tree = etree.parse(file_path)
            root = tree.getroot()
            for element in root.iter('ZGL'):
                for child in element:
                    if child.tag == 'FILENAME':
                        filename = child.text
            for element in root.iter('SCHET'):
                self.__update_bill(element)
            for element in root.iter('ZAP'):
                for child in element:
                    if child.tag == 'PACIENT':
                        self.__patient(child)
                    elif child.tag == 'SLUCH':
                        self.__update_case(child, filename)


class File(object):

    @classmethod
    def provider(cls, data_type, end, file_type='xml', tags=[]):
        """Вернёт объект для работы с указанным типом файла"""
        file_type = file_type.lower()
        if file_type == 'xml':
            obj = XML(data_type, end)
        elif file_type == 'dbf':
            obj = DBF(data_type, end, tags=tags)
        else:
            raise exceptions.NameError
        return obj


class XML(object):

    def __init__(self, data_type, end):
        self.data_type = data_type
        self.end = end

        if self.data_type == 'patients':
            self.file_name = 'L'
            self.template = 'tfoms/xml/patients.xml'
        elif self.data_type == 'services':
            self.file_name = 'H'
            self.template = 'tfoms/xml/services.xml'
        else:
            raise exceptions.NameError

    def generate_filename(self):
        self.file_name += 'M'
        self.file_name += _config('old_lpu_infis_code')
        self.file_name += 'T'
        self.file_name += _config('smo_number')
        self.file_name += '_'
        self.file_name += '%s' % self.end.strftime("%y%m")
        self.file_name += '1'

    def generate_file(self, tags_tree, data):
        env = Environment(loader=PackageLoader(module.import_name, module.template_folder))
        env.filters['datetimeformat'] = datetimeformat

        template = env.get_template(self.template)
        linked_file = XML(data_type='services', end=self.end)
        linked_file.generate_filename()
        self.head = dict(VERSION='1.0',
                         DATA=date.today().strftime('%Y-%m-%d'),
                         FILENAME=self.file_name,
                         FILENAME1=linked_file.file_name)
        return template.render(head=self.head, tags_tree=tags_tree, data=data)

    def save_file(self, tags_tree, data):
        self.generate_filename()
        content = self.generate_file(tags_tree, data)
        f = open(os.path.join(DOWNLOADS_DIR, '%s.xml' % self.file_name), 'w')
        f.write(content.encode('utf-8'))
        f.close()
        return '%s.xml' % self.file_name

    def archive_file(self):
        with ZipFile(os.path.join(DOWNLOADS_DIR, '%s.xml.zip' % self.file_name), 'w', ZIP_DEFLATED) as archive:
            archive.write(os.path.join(DOWNLOADS_DIR, '%s.xml' % self.file_name), '%s.xml' % self.file_name)
        return '%s.xml.zip' % self.file_name


class DBF(object):

    def __init__(self, data_type, end, tags):
        self.data_type = data_type
        self.end = end
        self.tags = tags

    def __get_month(self, date):
        monthes = range(13)
        monthes[10] = 'a'
        monthes[11] = 'b'
        monthes[12] = 'c'
        month = date.month
        if month > 9:
            month = monthes[month]
        return month

    def generate_filename(self):
        self.file_name = 'L'
        self.file_name += str(self.__get_org_type())
        self.file_name += _config('old_lpu_infis_code')

        self.arj_file_name = '10'
        self.arj_file_name += _config('old_lpu_infis_code')
        self.arj_file_name += '%s' % self.end.strftime('%d')
        self.arj_file_name += '%s' % self.__get_month(self.end)

    def __get_field_type(self, value, tag):
        if isinstance(value, basestring):
            _type = 'C(254)'
        elif isinstance(value, date):
            _type = 'D'
        elif isinstance(value, int):
            _type = 'N(10,0)'
        elif isinstance(value, float):
            _type = 'N(7,2)'
        else:
            _type = 'C(254)'

        if tag == 'KOD_LPU':
            _type = 'N(10,0)'
        elif tag == 'DAT_SC':
            _type = 'D'
        elif tag == 'VL':
            _type = 'N(10,0)'
        return _type

    def __generate_fields(self, tags, row):
        # NOT USED
        env = Environment(loader=PackageLoader(module.import_name, module.template_folder))
        env.filters['datetimeformat'] = datetimeformat

        template = env.get_template('dbf/fields')
        return str(template.render(tags=tags).lstrip())

    def __get_org_type(self):
        _type = None
        if self.data_type == 'hospital':
            _type = 1
        elif self.data_type == 'policlinic':
            _type = 2
        return _type

    def __generate_bill_number(self, num):
        bill_num = _config('old_lpu_infis_code')
        bill_num += str(self.__get_org_type())
        bill_num += '_'  #TODO: исправленный, то W
        bill_num += 'M'  #TODO: убедиться, что других случаев нет
        bill_num += '{0:04d}'.format(num)
        return bill_num

    def generate_file(self, tags, data):
        dbf.input_decoding = 'utf8'
        dbf.default_codepage = 'utf8'
        fields = []
        for key, item in enumerate(data):
            if key == 0:
                for tag in tags:
                    fields.append('{0} {1}'.format(tag.strip(), self.__get_field_type(getattr(item, tag, ''), tag)))
                table = dbf.Table(os.path.join(DOWNLOADS_DIR, '%s.dbf' % self.file_name), '; '.join(fields))
                table.open()

            row = []
            for tag in tags:
                value = getattr(item, tag, '')
                if tag == 'N_CH':
                    value = self.__generate_bill_number(key + 1)
                elif tag == 'KOD_LPU':
                    value = _config('lpu_infis_code')
                elif tag == 'DAT_SC':
                    value = date.today()
                elif tag == 'VL':
                    value = self.__get_org_type()
                if isinstance(value, date):
                    value = dbf.Date(value.year, value.month, value.day)
                row.append(value)
            table.append(tuple(row))
        table.close()
        return table

    def save_file(self, tags, data):
        self.generate_filename()
        dbf_file = self.generate_file(self.tags, data)
        return '%s.dbf' % self.file_name

    def archive_file(self):
        import patoolib
        patoolib.create_archive(os.path.join(DOWNLOADS_DIR, '%s.arj' % self.arj_file_name),
                                (os.path.join(DOWNLOADS_DIR, '%s.dbf' % self.file_name), ))
        return '%s.arj' % self.arj_file_name


class Utility(object):

    def prepare_table(self, table_type):
        """Проверяет насколько давно было обновление таблицы с данными
        и при необходимости посылает запрос ядру на обновление таблицы

        """
        pass