# -*- encoding: utf-8 -*-
from datetime import datetime
from application.database import db
from ..models import DownloadFiles, DownloadBills, DownloadCases, DownloadPatients, DownloadRecords, DownloadServices


class Reports(object):

    def __get_file(self, file_name, template_id):
        return (db.session.query(DownloadFiles)
                .filter(DownloadFiles.name == file_name, DownloadFiles.template_id == template_id)
                .first())

    def __add_file(self, template_id, file_name):
        file_obj = None
        if template_id and file_name:
            file_obj = self.__get_file(file_name, template_id)
            if not file_obj:
                file_obj = DownloadFiles(template_id=template_id, name=file_name)
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
                    bill_value = getattr(bill, key, None)
                    if bill_value and bill_value != getattr(bill_obj, key):
                        setattr(bill_obj, key, bill_value)
                db.session.commit()
            else:
                bill_obj = DownloadBills(file_id=file_id,
                                         DSCHET=bill.get('DSCHET'),
                                         NSCHET=bill.get('NSCHET'),
                                         CODE_MO=bill.get('CODE_MO'),
                                         YEAR=bill.get('YEAR'),
                                         MONTH=bill.get('MONTH'),
                                         PLAT=bill.get('PLAT'),
                                         SUMMAV=bill.get('SUMMAV'),
                                         start=start,
                                         end=end)
                db.session.add(bill_obj)
                db.session.commit()
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
                if patient_value:
                    setattr(patient_obj, key, getattr(patient, key))
            patient_obj.id = patient_id
            db.session.add(patient_obj)
        db.session.commit()

    def __add_patients(self, patients):
        if patients:
            for patient in patients.itervalues():
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
                if case_value and case_value != getattr(case, key):
                    setattr(case, key, case_value)
                case.bill_id = bill_id
                case.patient_id = patient_id
                case.record_id = record_id
            db.session.commit()
        else:
            case = DownloadCases()
            case.bill_id = bill_id
            case.patient_id = patient_id
            case.record_id = record_id
            for key in data.__dict__.keys():
                if hasattr(case, key):
                    setattr(case, key, getattr(data, key))
            case.id = getattr(data, 'IDCASE')
            db.session.add(case)
            db.session.commit()
        return case

    def __clear_services(self, case_id):
        db.session.query(DownloadServices).filter(DownloadServices.case_id == case_id).delete()

    def __add_service(self, case_id, data):
        self.__clear_services(case_id)

        service = DownloadServices(case_id=case_id)
        for key in data.__dict__.keys():
            if hasattr(service, key):
                setattr(service, key, getattr(data, key))
        db.session.add(service)
        db.session.commit()

    def save_data(self, data):
        file_obj = self.__add_file(template_id=data.get('template_id'), file_name=data.get('file'))
        if file_obj is None:
            raise AttributeError
            # return None

        bill_obj = self.__add_bill(file_obj.id, data.get('bill'), start=data.get('start'), end=data.get('end'))
        if bill_obj is None:
            raise AttributeError
            # return None

        self.__add_patients(data.get('patients'))

        services = data.get('services')
        if services:
            record_number = 0
            for patient_id, service_list in services.iteritems():
                record = self.__add_record(bill_obj.id, ++record_number)
                for service in service_list:
                    case_data = service
                    if hasattr(case_data, 'USL'):
                        del case_data.USL
                    case = self.__add_case(bill_obj.id, patient_id, record.id, case_data)

                    service_data = getattr(service, 'USL', None)
                    if service_data:
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