# -*- coding: utf-8 -*-
from nemesis.models.exists import (rbPacientModel, rbTreatment, rbTreatmentType, Organisation, rbFinance)

from .refbook import SimpleRefBookModelManager, RbTreatmentModelManager
from .organisation import OrganisationModelManager


all_rbs = {
    'rbPacientModel': rbPacientModel,
    'rbTreatment': rbTreatment,
    'rbTreatmentType': rbTreatmentType,
    'rbFinance': rbFinance,
    'Organisation': Organisation,
}

basic_rbs = [
    'rbPacientModel', 'rbTreatment', 'rbTreatmentType', 'rbFinance',
]

simple_rbs = [
    'rbPacientModel', 'rbTreatmentType', 'rbFinance',
]


def get_manager(name):
    if name in simple_rbs:
        return SimpleRefBookModelManager(all_rbs[name])
    elif name == 'rbTreatment':
        return RbTreatmentModelManager()
    elif name == 'Organisation':
        return OrganisationModelManager()