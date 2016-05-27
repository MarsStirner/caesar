# -*- coding: utf-8 -*-
from hashlib import md5
from sqlalchemy import func

from .base import BaseModelManager, FieldConverter, FCType, represent_model
from nemesis.models.person import Person, PersonCurationAssoc, PersonContact
from nemesis.lib.utils import (get_new_uuid, safe_int, safe_unicode, safe_traverse, safe_bool, safe_date)


class PersonModelManager(BaseModelManager):
    def __init__(self, with_curations=False, with_profiles=False):
        self._post_mng = self.get_manager('rbPost')
        self._spec_mng = self.get_manager('rbSpeciality')
        self._org_mng = self.get_manager('Organisation')
        self._os_mng = self.get_manager('OrgStructure')
        self._person_contact = self.get_manager('PersonContact')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'lastName', safe_unicode, 'last_name'),
            FieldConverter(FCType.basic, 'firstName', safe_unicode, 'first_name'),
            FieldConverter(FCType.basic, 'patrName', safe_unicode, 'patr_name'),
            FieldConverter(FCType.basic, 'login', safe_unicode, 'login'),
            FieldConverter(FCType.basic, 'SNILS', safe_unicode, 'snils'),
            FieldConverter(FCType.basic, 'INN', safe_unicode, 'inn'),
            FieldConverter(FCType.basic, 'sex', safe_int, 'sex'),
            FieldConverter(FCType.basic, 'birthDate', safe_date, 'birth_date'),
            FieldConverter(FCType.basic_repr, 'nameText', None, 'name_text'),
            FieldConverter(FCType.basic, 'deleted', safe_int, 'deleted'),
            FieldConverter(
                FCType.relation,
                'post', (self.handle_onetomany_nonedit, ),
                'post',
                model_manager=self._post_mng),
            FieldConverter(
                FCType.relation,
                'contacts', (self.handle_manytomany_assoc_obj, ),
                'contacts', (self.represent_model,),
                model_manager=self._person_contact),
            FieldConverter(
                FCType.relation,
                'speciality', (self.handle_onetomany_nonedit, ),
                'speciality',
                model_manager=self._spec_mng),
            FieldConverter(
                FCType.relation,
                'organisation', (self.handle_onetomany_nonedit, ),
                'organisation',
                model_manager=self._org_mng),
            FieldConverter(
                FCType.relation,
                'org_structure', (self.handle_onetomany_nonedit, ),
                'org_structure',
                model_manager=self._os_mng),
        ]
        if with_profiles:
            self._profile_mng = self.get_manager('rbUserProfile')
            fields.append(FieldConverter(
                FCType.relation,
                'user_profiles', (self.handle_manytomany, ),
                'user_profiles', (self.represent_model, ),
                self._profile_mng
            ))
        if with_curations:
            self._curation_mng = self.get_manager('rbOrgCurationLevel')
            fields.append(FieldConverter(
                FCType.relation,
                'curation_levels', (self.handle_manytomany, ),
                'curation_levels', (self.represent_model, ),
                self._curation_mng
            ))

        super(PersonModelManager, self).__init__(Person, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(PersonModelManager, self).create(data)
        # TODO: add required fields
        item.uuid = get_new_uuid()
        if item.patrName is None:
            item.patrName = ''
        if item.SNILS is None:
            item.SNILS = ''
        item.INN = ''
        item.code = ''
        item.federalCode = ''
        item.regionalCode = ''
        item.office = ''
        item.office2 = ''
        item.ambPlan = 0
        item.ambPlan2 = 0
        item.ambNorm = 0
        item.homPlan = 0
        item.homPlan2 = 0
        item.homNorm = 0
        item.expPlan = 0
        item.expNorm = 0
        item.password = ''
        item.retired = 0
        item.birthPlace = ''
        item.typeTimeLinePerson = 0
        if data is not None and 'new_password' in data and data['new_password']:
            m = md5()
            m.update(data['new_password'])
            item.password = m.hexdigest()
        return item

    def update(self, item_id, data, parent_obj=None):
        item = super(PersonModelManager, self).update(item_id, data)
        if 'new_password' in data and data['new_password']:
            m = md5()
            m.update(data['new_password'])
            item.password = m.hexdigest()
        return item

    def filter_(self, **kwargs):
        query = self._model.query
        if 'fio' in kwargs:
            query_str = u'%{0}%'.format(safe_unicode(kwargs['fio']))
            query = query.filter(
                func.concat_ws(' ', Person.lastName, Person.firstName, Person.patrName).like(query_str)
            )
        if 'speciality_id' in kwargs:
            query = query.filter(Person.speciality_id == safe_int(kwargs['speciality_id']))
        if 'post_id' in kwargs:
            query = query.filter(Person.post_id == safe_int(kwargs['post_id']))
        if 'org_id' in kwargs:
            query = query.filter(Person.org_id == safe_int(kwargs['org_id']))
        return query


class PersonCurationModelManager(BaseModelManager):
    def __init__(self):
        self._ocl_mng = self.get_manager('rbOrgCurationLevel')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'person_id', safe_int, 'person_id'),
            FieldConverter(FCType.basic, 'orgCurationLevel_id', safe_int, 'org_curation_level_id'),
            FieldConverter(
                FCType.relation,
                'org_curation_level', (self.handle_onetomany_nonedit, ),
                'org_curation_level', (self.represent_model, ),
                model_manager=self._ocl_mng
            ),
            FieldConverter(
                FCType.relation_repr,
                'person', None,
                'person'
            ),
        ]
        super(PersonCurationModelManager, self).__init__(PersonCurationAssoc, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(PersonCurationModelManager, self).create(data, parent_id, parent_obj)
        item.person_id = data.get('person_id') if data is not None else parent_id
        return item


class PersonContactManager(BaseModelManager):
    def __init__(self):
        self._ocl_mng = self.get_manager('rbContactType')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'value', safe_unicode, 'value'),
            FieldConverter(FCType.basic, 'person_id', safe_int, 'person_id'),
            FieldConverter(FCType.basic, 'contactType_id', safe_int, 'org_curation_level_id'),
            FieldConverter(
                FCType.relation,
                'contactType', (self.handle_onetomany_nonedit, ),
                'contact_type',
                model_manager=self._ocl_mng
            ),
            FieldConverter(
                FCType.relation_repr,
                'person', None,
                'person'
            ),
        ]
        super(PersonContactManager, self).__init__(PersonContact, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(PersonContactManager, self).create(data, parent_id, parent_obj)
        item.person_id = data.get('person_id') if data is not None else parent_id
        return item
