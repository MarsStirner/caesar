# -*- coding: utf-8 -*-
from nemesis.models.exists import (rbPacientModel, rbTreatment, rbTreatmentType, rbFinance, MKB)
from nemesis.models.expert_protocol import rbMeasureType, rbMeasureScheduleType, Measure
from nemesis.models.actions import ActionType
from nemesis.models.person import rbPost, rbOrgCurationLevel, rbSpeciality
from nemesis.models.risar import rbPerinatalRiskRate
from nemesis.lib.settings import Settings

from .refbook import SimpleRefBookModelManager, RbTreatmentModelManager
from .organisation import (OrganisationModelManager, OrganisationBCLModelManager, Organisation_OBCLModelManager,
    OrganisationCurationModelManager)
from .expert_protocol import (MeasureModelManager, ExpertProtocolModelManager, ExpertSchemeModelManager,
      ExpertSchemeMKBModelManager, ExpertSchemeMeasureModelManager, MeasureScheduleModelManager)
from .person import PersonModelManager, PersonCurationModelManager


all_rbs = {
    'rbPacientModel': rbPacientModel,
    'rbTreatment': rbTreatment,
    'rbTreatmentType': rbTreatmentType,
    'rbFinance': rbFinance,
    'rbMeasureType': rbMeasureType,
    'rbMeasureScheduleType': rbMeasureScheduleType,
    'Measure': Measure,
    'rbPerinatalRiskRate': rbPerinatalRiskRate,
    'rbPost': rbPost,
    'rbSpeciality': rbSpeciality,
    'rbOrgCurationLevel': rbOrgCurationLevel
}

basic_rbs = [
    'rbPacientModel', 'rbTreatment', 'rbTreatmentType', 'rbFinance', 'rbMeasureType', 'rbMeasureScheduleType',
    'rbPerinatalRiskRate', 'rbOrgCurationLevel'
]

simple_rbs = [
    'rbPacientModel', 'rbTreatmentType', 'rbFinance', 'rbMeasureType', 'rbMeasureScheduleType', 'rbPerinatalRiskRate',
    'rbOrgCurationLevel',
    # next are used only for backend data manipulation, they are not presented on frontend ui
    'rbPost', 'rbSpeciality'
]

rb_groups = {
    'vmp': (u'ВМП', ['rbPacientModel', 'rbTreatment', 'rbTreatmentType']),
    'expert_protocol': (u'Протоколы лечения', ['rbMeasureType', 'rbMeasureScheduleType']),
    'risar': (u'РИСАР', ['rbPerinatalRiskRate', 'rbOrgCurationLevel']),
    'other': (u'Остальные', ['rbFinance'])
}


def make_refbook_list(rb_list):
    return sorted([
        dict(
            name=t.__tablename__,
            desc=getattr(t, '_table_description', t.__tablename__),
            is_simple=(t_name in simple_rbs)
        )
        for t_name, t in all_rbs.iteritems() if t_name in rb_list
    ], key=lambda k: k['desc'])


def get_grouped_refbooks():
    grouped = {}
    for group_code, (group_descr, rb_list) in rb_groups.iteritems():
        if group_code == 'expert_protocol' and not Settings.getBool('Expert.Protocol.Enabled', False):
            continue
        elif group_code == 'risar' and not Settings.getBool('RISAR.Enabled', False):
            continue
        grouped[group_code] = {
            'descr': group_descr,
            'rb_list': make_refbook_list(rb_list)
        }
    return grouped


def get_manager(name, **params):
    if name in simple_rbs:
        return SimpleRefBookModelManager(all_rbs[name])
    elif name == 'rbTreatment':
        return RbTreatmentModelManager()
    elif name == 'Organisation':
        return OrganisationModelManager(**params)
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
    elif name == 'MeasureSchedule':
        return MeasureScheduleModelManager()
    elif name == 'ActionType':
        return SimpleRefBookModelManager(ActionType)
    elif name == 'MKB':
        return SimpleRefBookModelManager(MKB)
    elif name == 'OrganisationBirthCareLevel':
        return OrganisationBCLModelManager(**params)
    elif name == 'Organisation_OrganisationHCL':
        return Organisation_OBCLModelManager()
    elif name == 'Person':
        return PersonModelManager(**params)
    elif name == 'PersonCuration':
        return PersonCurationModelManager()
    elif name == 'OrganisationCuration':
        return OrganisationCurationModelManager()