# -*- coding: utf-8 -*-
from nemesis.models.exists import (rbPacientModel, rbTreatment, rbTreatmentType, Organisation, rbFinance)
from nemesis.models.expert_protocol import rbMeasureType, rbMeasureScheduleType, Measure

from .refbook import SimpleRefBookModelManager, RbTreatmentModelManager
from .organisation import OrganisationModelManager
from .expert_protocol import (MeasureModelManager, ExpertProtocolModelManager, ExpertSchemeModelManager,
      ExpertSchemeMKBModelManager, ExpertSchemeMeasureModelManager)


all_rbs = {
    'rbPacientModel': rbPacientModel,
    'rbTreatment': rbTreatment,
    'rbTreatmentType': rbTreatmentType,
    'rbFinance': rbFinance,
    'Organisation': Organisation,
    'rbMeasureType': rbMeasureType,
    'rbMeasureScheduleType': rbMeasureScheduleType,
    'Measure': Measure
}

basic_rbs = [
    'rbPacientModel', 'rbTreatment', 'rbTreatmentType', 'rbFinance', 'rbMeasureType', 'rbMeasureScheduleType',
]

simple_rbs = [
    'rbPacientModel', 'rbTreatmentType', 'rbFinance', 'rbMeasureType', 'rbMeasureScheduleType',
]


def get_manager(name):
    if name in simple_rbs:
        return SimpleRefBookModelManager(all_rbs[name])
    elif name == 'rbTreatment':
        return RbTreatmentModelManager()
    elif name == 'Organisation':
        return OrganisationModelManager()
    elif name == 'Measure':
        return MeasureModelManager()
    elif name == 'ExpertProtocol':
        return ExpertProtocolModelManager()
    elif name == 'ExpertScheme':
        return ExpertSchemeModelManager()
    elif name == 'ExpertSchemeMKB':
        return ExpertSchemeMKBModelManager()
    elif name == 'ExpertSchemeMeasure':
        return ExpertSchemeMeasureModelManager()