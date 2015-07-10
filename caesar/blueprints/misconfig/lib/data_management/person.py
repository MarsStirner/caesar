# -*- coding: utf-8 -*-
from .base import BaseModelManager, FieldConverter, FCType, represent_model
from nemesis.models.person import Person, PersonCurationAssoc
from nemesis.lib.utils import (get_new_uuid, safe_int, safe_unicode, safe_traverse, safe_bool,)
from nemesis.systemwide import db


class PersonModelManager(BaseModelManager):
    def __init__(self, with_curations=False):
        self._post_mng = self.get_manager('rbPost')
        self._spec_mng = self.get_manager('rbSpeciality')
        self._org_mng = self.get_manager('Organisation')
        self._os_mng = self.get_manager('OrgStructure')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'lastName', safe_unicode, 'last_name'),
            FieldConverter(FCType.basic, 'firstName', safe_unicode, 'first_name'),
            FieldConverter(FCType.basic, 'patrName', safe_unicode, 'patr_name'),
            FieldConverter(FCType.basic_repr, 'nameText', None, 'name_text'),
            FieldConverter(
                FCType.relation,
                'post', lambda val, par: self.handle_onetomany_nonedit(self._post_mng, val, par),
                'post'),
            FieldConverter(
                FCType.relation,
                'speciality', lambda val, par: self.handle_onetomany_nonedit(self._spec_mng, val, par),
                'speciality'),
            FieldConverter(
                FCType.relation,
                'organisation', lambda val, par: self.handle_onetomany_nonedit(self._org_mng, val, par),
                'organisation', lambda val: represent_model(val, self._org_mng)),
            FieldConverter(
                FCType.relation_repr,
                'org_structure', None,
                'org_structure'),
        ]
        if with_curations:
            self._curation_mng = self.get_manager('PersonCuration')
            fields.append(FieldConverter(
                FCType.relation,
                'person_curations', self.handle_person_curations,
                'person_curations', lambda val: represent_model(val, self._curation_mng)
            ))
        super(PersonModelManager, self).__init__(Person, fields)

    def create(self, data=None, parent_id=None, parent_obj=None):
        item = super(PersonModelManager, self).create(data)
        # TODO: add required fields
        item.uuid = get_new_uuid()
        return item

    def handle_person_curations(self, curation_list, parent_obj):
        if curation_list is None:
            return []
        result = []
        for item_data in curation_list:
            item_id = item_data['id']
            if item_id:
                item = self._curation_mng.update(item_id, item_data, parent_obj)
            else:
                item = self._curation_mng.create(item_data, None, parent_obj)
            result.append(item)

        # deletion
        for pers_cur in parent_obj.person_curations:
            if pers_cur not in result:
                db.session.delete(pers_cur)
        return result


class PersonCurationModelManager(BaseModelManager):
    def __init__(self):
        self._ocl_mng = self.get_manager('rbOrgCurationLevel')
        fields = [
            FieldConverter(FCType.basic, 'id', safe_int, 'id'),
            FieldConverter(FCType.basic, 'person_id', safe_int, 'person_id'),
            FieldConverter(FCType.basic, 'orgCurationLevel_id', safe_int, 'org_curation_level_id'),
            FieldConverter(
                FCType.relation,
                'org_curation_level', lambda val, par: self.handle_onetomany_nonedit(self._ocl_mng, val, par),
                'org_curation_level', lambda val: represent_model(val, self._ocl_mng)
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
