# -*- coding: utf-8 -*-
from .base import BaseModelManager
from nemesis.models.exists import Organisation
from nemesis.lib.utils import get_new_uuid


class OrganisationModelManager(BaseModelManager):
    def __init__(self):
        fm = {
            'id': 'id',
            'fullName': 'full_name',
            'shortName': 'short_name',
            'title': 'title',
            'infisCode': 'infis',
            'is_insurer': 'is_insurer',
            'is_hospital': 'is_hospital',
            'Address': 'address',
            'phone': 'phone',
            'kladr_locality': 'kladr_locality.code',
        }
        super(OrganisationModelManager, self).__init__(Organisation, fm)

    def create(self, data):
        item = super(OrganisationModelManager, self).create(data)
        item.obsoleteInfisCode = ''
        item.OKVED = ''
        item.INN = ''
        item.KPP = ''
        item.OGRN = ''
        item.OKATO = ''
        item.OKPF_code = ''
        item.OKFS_code = 0
        item.OKPO = ''
        item.FSS = ''
        item.region = ''
        item.chief = ''
        item.accountant = ''
        item.notes = ''
        item.miacCode = ''
        item.obsoleteInfisCode = ''
        item.obsoleteInfisCode = ''
        item.obsoleteInfisCode = ''
        item.obsoleteInfisCode = ''
        item.uuid = get_new_uuid()
        return item