# -*- encoding: utf-8 -*-


class RegistryFactory(object):

    @staticmethod
    def create(region_code, *args, **kwargs):
        if region_code == 'pnz':
            from .pnz import XML_Registry
            obj = XML_Registry(*args, **kwargs)
        elif region_code == 'spb':
            from .spb import XML_Registry
            obj = XML_Registry(*args, **kwargs)
        else:
            raise NotImplementedError(u'XML_Registry for "{0}" is not implemented'.format(region_code))
        return obj


class ServicesFactory(object):

    @staticmethod
    def create(region_code, *args, **kwargs):
        if region_code == 'pnz':
            from .pnz import Services
            obj = Services(*args, **kwargs)
        else:
            raise NotImplementedError(u'Services for "{0}" is not implemented'.format(region_code))
        return obj


class DBF_DataFactory(object):

    @staticmethod
    def create(region_code, *args, **kwargs):
        if region_code == 'pnz':
            from .pnz import DBF_Data
            obj = DBF_Data(*args, **kwargs)
        else:
            raise NotImplementedError(u'DBF_Data for "{0}" is not implemented'.format(region_code))
        return obj


class DBF_PoliclinicFactory(object):

    @staticmethod
    def create(region_code, *args, **kwargs):
        if region_code == 'pnz':
            from .pnz import DBF_Policlinic
            obj = DBF_Policlinic(*args, **kwargs)
        else:
            raise NotImplementedError(u'DBF_Policlinic for "{0}" is not implemented'.format(region_code))
        return obj


class DBF_HospitalFactory(object):

    @staticmethod
    def create(region_code, *args, **kwargs):
        if region_code == 'pnz':
            from .pnz import DBF_Hospital
            obj = DBF_Hospital(*args, **kwargs)
        else:
            raise NotImplementedError(u'DBF_Hospital for "{0}" is not implemented'.format(region_code))
        return obj


class UploadWorkerFactory(object):

    @staticmethod
    def create(region_code, *args, **kwargs):
        if region_code == 'pnz':
            from .pnz import UploadWorker
            obj = UploadWorker()
        else:
            raise NotImplementedError(u'UploadWorker for "{0}" is not implemented'.format(region_code))
        return obj


class ContractsFactory(object):

    @staticmethod
    def create(region_code, *args, **kwargs):
        if region_code == 'pnz':
            from .pnz import Contracts
            obj = Contracts()
        else:
            raise NotImplementedError(u'Contracts for "{0}" is not implemented'.format(region_code))
        return obj


class ReportsFactory(object):

    @staticmethod
    def create(region_code, *args, **kwargs):
        if region_code == 'pnz':
            from .pnz import Reports
            obj = Reports()
        else:
            raise NotImplementedError(u'Contracts for "{0}" is not implemented'.format(region_code))
        return obj
