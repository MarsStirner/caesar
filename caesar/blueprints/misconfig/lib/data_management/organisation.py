# -*- coding: utf-8 -*-
from .base import BaseModelManager, FieldConverter, FCType
from nemesis.models.exists import Organisation
from nemesis.lib.utils import get_new_uuid, safe_int, safe_unicode, safe_bool


class OrganisationModelManager(BaseModelManager):
    def __init__(self):
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'fullName', safe_unicode, 'full_name'),
            FieldConverter(FCType.basic, 'shortName', safe_unicode, 'short_name'),
            FieldConverter(FCType.basic, 'title', safe_unicode, 'title'),
            FieldConverter(FCType.basic, 'infisCode', safe_unicode, 'infis'),
            FieldConverter(FCType.basic, 'isInsurer', safe_int, 'is_insurer', safe_bool),
            FieldConverter(FCType.basic, 'isHospital', safe_int, 'is_hospital', safe_bool),
            FieldConverter(FCType.basic, 'Address', safe_unicode, 'address'),
            FieldConverter(FCType.basic, 'phone', safe_unicode, 'phone'),
            FieldConverter(FCType.relation, 'kladr_locality', self.handle_kladr_locality, 'kladr_locality'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
        ]
        super(OrganisationModelManager, self).__init__(Organisation, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(OrganisationModelManager, self).create(data)
        item.isHospital = False
        item.isInsurer = False
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

    def handle_kladr_locality(self, json_data, parent_obj=None):
        return json_data.get('code', '')