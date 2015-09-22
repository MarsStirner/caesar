# -*- coding: utf-8 -*-
from ..lib.query import Query

from blueprints.print_subsystem.models.models_utils import EmptyObject

from nemesis.lib.aux.data import ProxyField
from nemesis.lib.vesta import Vesta

__author__ = 'viruzzz-kun'


class DocumentTypeInfo(object):
    def __init__(self, code):
        from nemesis.systemwide import pspd
        data = pspd.metadata.doc_types.get(code)
        self.name = data.get('name')
        self.code = code


class DocumentInfoWrapper:
    def __init__(self, original=None):
        self._original = original or EmptyObject()
        self._document_type = DocumentTypeInfo(original.code)

    serial = ProxyField('_original.serial')
    number = ProxyField('_original.number')
    date = ProxyField('_original.beg_date')
    endDate = ProxyField('_original.end_date')
    origin = ProxyField('_original.origin')
    documentTypeCode = ProxyField('_original.code')
    documentTypeName = ProxyField('_document_type.name')

    def __unicode__(self):
        return (' '.join([
            self.documentTypeName if self.documentTypeCode else '',
            self.serial or '',
            self.number or ''])
        ).strip()


class PolicyInfoWrapper:
    def __init__(self, original=None):
        self._original = original or EmptyObject()
        self._document_type = DocumentTypeInfo(original.code)

    serial = ProxyField('_original.serial')
    number = ProxyField('_original.number')
    begDate = ProxyField('_original.beg_date')
    endDate = ProxyField('_original.end_date')
    insurer_id = ProxyField('_original.origin')
    policyTypeCode = ProxyField('_original.code')
    policyTypeName = ProxyField('_document_type.name')
    policyType = ProxyField('_document_type')

    @property
    def insurer(self):
        from .models_all import Organisation
        return Query(Organisation).filter(Organisation.id == self._original.origin).first()

    def __unicode__(self):
        return (' '.join([
            self.policyTypeName,
            unicode(self.insurer),
            self.serial,
            self.number
        ])).strip()


class AddressInfoWrapper:
    def __init__(self, original=None):
        self._original = original or EmptyObject()

    KLADRCode = ProxyField('_original.city_code')
    KLADRStreetCode = ProxyField('_original.street_code')
    street = ProxyField('_original.street')
    number = ProxyField('_original.house_number')
    corpus = ProxyField('_original.house_appendix')

    @property
    def city(self):

        if self._original.city:
            return self._original.city
        elif self._original.city_code:
            return Vesta.get_kladr_locality(self._original.city_code).get('fullname', u'-код региона не найден в кладр-')
        return u''

    town = city

    @property
    def street(self):
        if self._original.street:
            return self.street
        elif self._original.street_code:
            return Vesta.get_kladr_street(self.KLADRStreetCode).get('name', u'-код улицы не найден в кладр-')
        return u''

    @property
    def text(self):
        if self._original.text:
            return self._original.text

        parts = [self.city, self.street]

        if self._original.house_number:
            parts.append(u'д.' + self._original.house_number)
        if self._original.house_appendix:
            parts.append(u'к.' + self._original.house_appendix)
        if self._original.flat:
            parts.append(u'кв.' + self._original.flat)
        return (u', '.join(filter(None, parts))).strip()

    @property
    def localityType(self):
        return 0 if self._original.locality_type == 'village' else 1

    def __unicode__(self):
        return self.text


class ContactInfoWrapper:
    def __init__(self, original=None):
        self._original = original or EmptyObject()

    contact = ProxyField('_original.value')
    notes = ProxyField('_original.note')
    code = ProxyField('_original.system')

    @property
    def name(self):
        from .models_all import rbContactType
        code = self._original.system
        ct = Query(rbContactType.code == code).first()
        return ct.name if ct else ''

    def __unicode__(self):
        return u'%s: %s%s' % (
            self.name, self._original.value, ((u' (%s)' % self._original.note) if self._original.note else '')
        )