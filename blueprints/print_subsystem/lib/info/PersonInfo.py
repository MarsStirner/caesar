# -*- coding: utf-8 -*-
# from PyQt4 import QtGui

from ..info.PrintInfo import CInfo, CRBInfo
from ..info.OrgInfo import COrgInfo, COrgStructureInfo
# from Events.Service import CServiceInfo
# from library.Utils import *


class CPersonInfo(CInfo):
    def __init__(self, context, personId):
        CInfo.__init__(self, context)
        self.personId = personId
        self._code = ''
        self._federalCode = ''
        self._regionalCode = ''
        self._lastName = ''
        self._firstName = ''
        self._patrName = ''
        self._office = ''
        self._office2 = ''
        self._post = self.getInstance(CPostInfo, None)
        self._speciality = self.getInstance(CSpecialityInfo, None)
        self._organisation = self.getInstance(COrgInfo, None)
        self._orgStructure = self.getInstance(COrgStructureInfo, None)
        self._academicDegree = self.getInstance(CAcademicDegreeInfo, None)
        self._academicTitle = self.getInstance(CAcademicTitleInfo, None)
        self._tariffCategory = self.getInstance(CTariffCategoryInfo, None)
        self._login = ''


    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('Person', '*', self.personId)
        if record:
            self._code = forceString(record.value('code'))
            self._federalCode = forceString(record.value('federalCode'))
            self._regionalCode = forceString(record.value('regionalCode'))
            self._lastName = forceString(record.value('lastName'))
            self._firstName = forceString(record.value('firstName'))
            self._patrName = forceString(record.value('patrName'))
            self._office = forceString(record.value('office'))
            self._office2 = forceString(record.value('office2'))

            self._post = self.getInstance(CPostInfo, forceRef(record.value('post_id')))
            self._speciality = self.getInstance(CSpecialityInfo, forceRef(record.value('speciality_id')))
            self._organisation = self.getInstance(COrgInfo, forceRef(record.value('org_id')))
            self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('orgStructure_id')))
            self._academicDegree = self.getInstance(CAcademicDegreeInfo, forceRef(record.value('academicdegree_id')))
            self._academicTitle = self.getInstance(CAcademicTitleInfo, forceRef(record.value('academicTitle_id')))
            self._tariffCategory = self.getInstance(CTariffCategoryInfo, forceRef(record.value('tariffCategory_id')))
            self._login = forceString(record.value('login'))
            return True
        else:
            return False


    def getShortName(self):
        self.load()
        return formatShortNameInt(self._lastName, self._firstName, self._patrName)

    def getFullName(self):
        self.load()
        return formatNameInt(self._lastName, self._firstName, self._patrName)

#    def __unicode__(self):
    def __str__(self):
        self.load()
        result = formatShortNameInt(self._lastName, self._firstName, self._patrName)
        if self._speciality:
            result += ', '+self._speciality.name

        return unicode(result)

    code           = property(lambda self: self.load()._code)
    federalCode    = property(lambda self: self.load()._federalCode)
    regionalCode   = property(lambda self: self.load()._regionalCode)
    lastName       = property(lambda self: self.load()._lastName)
    firstName      = property(lambda self: self.load()._firstName)
    patrName       = property(lambda self: self.load()._patrName)
    fullName       = property(getFullName)
    longName       = property(getFullName)
    shortName      = property(getShortName)
    name           = property(getShortName)
    office         = property(lambda self: self.load()._office)
    office2        = property(lambda self: self.load()._office2)
    post           = property(lambda self: self.load()._post)
    speciality     = property(lambda self: self.load()._speciality)
    organisation   = property(lambda self: self.load()._organisation)
    orgStructure   = property(lambda self: self.load()._orgStructure)
    academicDegree = property(lambda self: self.load()._academicDegree)
    academicTitle  = property(lambda self: self.load()._academicTitle)
    tariffCategory = property(lambda self: self.load()._tariffCategory)
    login          = property(lambda self: self.load()._login)


class CSpecialityInfo(CInfo):
    def __init__(self, context, specialityId):
        CInfo.__init__(self, context)
        self.specialityId = specialityId
        self._code = ''
        self._name = ''
        self._OKSOName = ''
        self._OKSOCode = ''
        self._service = self.getInstance(CServiceInfo, None)


    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbSpeciality', '*', self.specialityId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._OKSOName = forceString(record.value('OKSOName'))
            self._OKSOCode = forceString(record.value('OKSOCode'))
            self._service = self.getInstance(CServiceInfo, forceRef(record.value('service_id')))
            return True
        else:
            return False


    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    OKSOName = property(lambda self: self.load()._OKSOName)
    OKSOCode = property(lambda self: self.load()._OKSOCode)
    service  = property(lambda self: self.load()._service)


class CPostInfo(CInfo):
    def __init__(self, context, postId):
        CInfo.__init__(self, context)
        self.postId = postId
        self._code = ''
        self._name = ''
        self._regionalCode = ''


    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbPost', '*', self.postId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._regionalCode = forceString(record.value('regionalCode'))
            return True
        else:
            return False


    def __str__(self):
        return self.load()._name

    code     = property(lambda self: self.load()._code)
    name     = property(lambda self: self.load()._name)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CAcademicDegreeInfo(CInfo):

    def __init__(self, context, degreeId):
        CInfo.__init__(self, context)
        self.degreeId = degreeId
        self._code = ''
        self._name = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbAcademicDegree', '*', self.degreeId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code = property(lambda self: self.load()._code)
    name = property(lambda self: self.load()._name)


class CAcademicTitleInfo(CInfo):

    def __init__(self, context, titleId):
        CInfo.__init__(self, context)
        self.titleId = titleId
        self._code = ''
        self._name = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('rbAcademicTitle', '*', self.titleId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            return True
        else:
            return False

    def __str__(self):
        return self.load()._name

    code = property(lambda self: self.load()._code)
    name = property(lambda self: self.load()._name)


class CTariffCategoryInfo(CRBInfo):
    tableName = 'rbTariffCategory'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)
