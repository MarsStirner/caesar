# -*- encoding: utf-8 -*-
from datetime import datetime
from application.database import db
from ..models import DownloadFiles, DownloadBills, DownloadCases, DownloadPatients, DownloadRecords, DownloadServices
from sqlalchemy import exc


class Reports(object):

    def __get_file(self, file_name, template_id):
        return (db.session.query(DownloadFiles)
                .filter(DownloadFiles.name == file_name, DownloadFiles.template_id == template_id)
                .first())

    def __add_file(self, template_id, data):
        file_obj = None
        if template_id and data:
            file_obj = self.__get_file(data['FILENAME'], template_id)
            if not file_obj:
                file_obj = DownloadFiles(template_id=template_id, name=data['FILENAME'])
                for key, value in data.iteritems():
                    if hasattr(file_obj, key):
                        setattr(file_obj, key, value)
                db.session.add(file_obj)
            file_obj.created = datetime.now()
            db.session.commit()
        return file_obj

    def __get_bill(self, file_id, bill, start, end):
        bill_obj = None
        if file_id and bill and start and end:
            bill_obj = (db.session.query(DownloadBills)
                        .filter(DownloadBills.file_id == file_id,
                                DownloadBills.start == start,
                                DownloadBills.end == end,
                                DownloadBills.NSCHET == bill.get('NSCHET'),
                                DownloadBills.DSCHET == bill.get('DSCHET'))
                        .first())
        return bill_obj

    def __add_bill(self, file_id, bill, start, end):
        bill_obj = None
        if file_id and bill and start and end:
            bill_obj = self.__get_bill(file_id, bill, start, end)
            if bill_obj:
                for key in bill_obj.__dict__.keys():
                    bill_value = bill.get(key)
                    if bill_value and bill_value != getattr(bill_obj, key):
                        setattr(bill_obj, key, bill_value)
                db.session.commit()
            else:
                bill_obj = DownloadBills(file_id=file_id, start=start, end=end)
                for key, value in bill.iteritems():
                    if value and hasattr(bill_obj, key):
                        setattr(bill_obj, key, value)
                try:
                    db.session.add(bill_obj)
                    db.session.commit()
                except exc.IntegrityError, e:
                    print e
                    db.session.rollback()
        return bill_obj

    def __get_patient(self, patient_id):
        patient = None
        if patient_id:
            patient = db.session.query(DownloadPatients).get(patient_id)
        return patient

    def __parse_default_value(self, value):
        if value == 'UNDEFINED':
            value = None
        return value

    def __add_patient(self, patient):
        patient_id = getattr(patient, 'patientId')
        patient_obj = self.__get_patient(patient_id)
        if patient_obj:
            for key in patient_obj.__dict__.keys():
                patient_value = getattr(patient, key, None)
                patient_value = self.__parse_default_value(patient_value)
                if patient_value and patient_value != getattr(patient_obj, key):
                    setattr(patient_obj, key, patient_value)
        else:
            patient_obj = DownloadPatients()
            for key in patient.__dict__.keys():
                patient_value = getattr(patient, key, None)
                patient_value = self.__parse_default_value(patient_value)
                if patient_value and hasattr(patient_obj, key):
                    setattr(patient_obj, key, getattr(patient, key))
            patient_obj.id = patient_id
            db.session.add(patient_obj)
        try:
            db.session.commit()
        except exc.OperationalError, e:
            # TODO: уведомлять пользователя
            print e
            db.session.rollback()
        except Exception, e:
            # TODO: уведомлять пользователя
            print e
            db.session.rollback()

    def add_patients(self, patients):
        if patients:
            if isinstance(patients, dict):
                patients = patients.itervalues()
            for patient in patients:
                self.__add_patient(patient)

    def __add_record(self, bill_id, N_ZAP, PR_NOV=0):
        record = DownloadRecords(bill_id=bill_id, N_ZAP=N_ZAP, PR_NOV=PR_NOV)
        db.session.add(record)
        db.session.commit()
        return record

    def __get_case(self, case_id):
        case = None
        if case_id:
            case = db.session.query(DownloadCases).get(case_id)
        return case

    def __add_case(self, bill_id, patient_id, record_id, data):
        case = self.__get_case(getattr(data, 'IDCASE'))
        if case:
            for key in case.__dict__.keys():
                case_value = getattr(data, key, None)
                if key == 'IDDOKT':
                    case_value = int(case_value)
                if hasattr(case, key) and case_value and case_value != getattr(case, key):
                    setattr(case, key, case_value)
                case.bill_id = bill_id
                case.patient_id = patient_id
                case.record_id = record_id
        else:
            case = DownloadCases()
            case.bill_id = bill_id
            case.patient_id = patient_id
            case.record_id = record_id
            for key in data.__dict__.keys():
                case_value = getattr(data, key, None)
                if key == 'IDDOKT':
                    case_value = int(case_value)
                if hasattr(case, key) and case_value:
                    setattr(case, key, case_value)
            case.id = getattr(data, 'IDCASE')
            db.session.add(case)
        try:
            db.session.commit()
        except exc.OperationalError, e:
            # TODO: уведомлять пользователя
            print e
            db.session.rollback()
        except Exception, e:
            # TODO: уведомлять пользователя
            print e
            db.session.rollback()
        return case

    def __clear_services(self, case_id):
        db.session.query(DownloadServices).filter(DownloadServices.case_id == case_id).delete()

    def __add_service(self, case_id, data):
        service = DownloadServices(case_id=case_id)
        for key in data.__dict__.keys():
            if hasattr(service, key):
                setattr(service, key, getattr(data, key))
        db.session.add(service)
        db.session.commit()

    def save_data(self, data):
        file_obj = self.__add_file(template_id=data.get('template_id'), data=data.get('file'))
        if file_obj is None:
            raise AttributeError
            # return None

        bill_obj = self.__add_bill(file_obj.id, data.get('bill'), start=data.get('start'), end=data.get('end'))
        if bill_obj is None:
            raise AttributeError
            # return None

        self.add_patients(data.get('patients'))

        services = data.get('services')
        if services:
            record_number = 0
            for patient_id, service_list in services.iteritems():
                record_number += 1
                record = self.__add_record(bill_obj.id, record_number)
                for service in service_list:
                    service_data = getattr(service, 'USL', None)

                    if hasattr(service, 'USL'):
                        del service.USL
                    case = self.__add_case(bill_obj.id, patient_id, record.id, service)

                    self.__clear_services(case.id)
                    if service_data and case:
                        for service_item in service_data:
                            self.__add_service(case.id, service_item)

    def update_patient(self, id, data):
        patient = self.__get_patient(id)
        updated = dict()
        if not patient:
            #TODO: Обработка ненайденного
            return None
        for key, value in data.iteritems():
            value = self.__parse_default_value(value)
            if getattr(patient, key) != value:
                setattr(patient, key, value)
                updated[key] = value
        if updated:
            db.session.commit()
        return updated

    def get_num_services(self, bill):
        num = 0
        if bill.cases:
            for case in bill.cases:
                if hasattr(case, 'services'):
                    num += len(case.services)
        return num

    def get_cases_sum(self, bill):
        cases_sum = dict(confirmed=0.00, unconfirmed=0.00)
        if bill.cases:
            for case in bill.cases:
                if case.REFREASON is not None:
                    if case.REFREASON == '0':
                        cases_sum['confirmed'] += float(case.SUMV)
                    else:
                        cases_sum['unconfirmed'] += float(case.SUMV)
        return cases_sum

    def get_bills(self, start=None, end=None):
        cases_sum = dict()
        num_services = dict()
        query = db.session.query(DownloadBills)
        if start and end:
            query = query.filter(DownloadBills.DSCHET.between(start, end))
        bills = query.order_by(DownloadBills.DSCHET).all()
        for bill in bills:
            cases_sum[bill.id] = self.get_cases_sum(bill)
            num_services[bill.id] = self.get_num_services(bill)
        return dict(bills=bills, cases_sum=cases_sum, num_services=num_services)

    def get_bill(self, id):
        return db.session.query(DownloadBills).get(id)

    def get_cases(self, bill_id, page, per_page):
        query = db.session.query(DownloadCases).filter(DownloadCases.bill_id == bill_id).order_by(DownloadCases.id)
        data_query = query.limit(per_page)
        if page > 1:
            data_query = data_query.offset((page-1) * per_page)
        return query, data_query.all()