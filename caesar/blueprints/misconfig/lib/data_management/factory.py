# -*- coding: utf-8 -*-
from nemesis.models.exists import (rbPacientModel, rbTreatment, rbTreatmentType, rbFinance)
from nemesis.models.expert_protocol import (rbMeasureType, rbMeasureScheduleType, rbMeasureScheduleApplyType, Measure)
from nemesis.models.exists import rbRequestType, rbEventTypePurpose, rbResult, rbService
from nemesis.models.actions import ActionType
from nemesis.models.event import EventType
from nemesis.models.person import rbPost, rbOrgCurationLevel, rbSpeciality, rbUserProfile
from nemesis.models.risar import rbPerinatalRiskRate, rbPregnancyPathology
from nemesis.models.refbooks import rbUnits
from nemesis.models.accounting import rbServiceKind
from nemesis.lib.settings import Settings

from .refbook import (SimpleRefBookModelManager, RbTreatmentModelManager, RbPerinatalRRModelManager,
    RbPRRMKBModelManager, RbPregnancyPathologyModelManager, RbPregnancyPathologyMKBModelManager, MKBModelManager,
    RbResultModelManager)
from .organisation import (OrganisationModelManager, OrganisationBCLModelManager, OrgStructureModelManager)
from .expert_protocol import (MeasureModelManager, ExpertProtocolModelManager, ExpertSchemeModelManager,
    ExpertSchemeMeasureModelManager, MeasureScheduleModelManager)
from .person import PersonModelManager, PersonCurationModelManager
from .print_template import RbPrintTemplateModelManager
from .pricelist import PriceListModelManager, PriceListItemModelManager
from .rbservice import RbServiceModelManager, RbServiceGroupAssocModelManager


all_rbs = {
    'rbPacientModel': rbPacientModel,
    'rbTreatment': rbTreatment,
    'rbTreatmentType': rbTreatmentType,
    'rbFinance': rbFinance,
    'EventType': EventType,
    'rbService': rbService,
    'rbRequestType': rbRequestType,
    'rbResult': rbResult,
    'rbMeasureType': rbMeasureType,
    'rbMeasureScheduleType': rbMeasureScheduleType,
    'rbMeasureScheduleApplyType': rbMeasureScheduleApplyType,
    'Measure': Measure,
    'rbPerinatalRiskRate': rbPerinatalRiskRate,
    'rbPost': rbPost,
    'rbSpeciality': rbSpeciality,
    'rbOrgCurationLevel': rbOrgCurationLevel,
    'rbPregnancyPathology': rbPregnancyPathology,
    'rbUnits': rbUnits,
    'rbEventTypePurpose': rbEventTypePurpose,
    'rbUserProfile': rbUserProfile,
    'rbServiceKind': rbServiceKind
}

basic_rbs = [
    'rbPacientModel', 'rbTreatment', 'rbTreatmentType', 'rbFinance', 'rbMeasureType', 'rbMeasureScheduleType',
    'rbMeasureScheduleApplyType', 'rbPerinatalRiskRate', 'rbOrgCurationLevel', 'rbPregnancyPathology', 'rbUnits',
    'rbServiceKind'
]

simple_rbs = [
    'rbPacientModel', 'rbTreatmentType', 'rbFinance', 'rbMeasureType', 'rbMeasureScheduleType',
    'rbMeasureScheduleApplyType', 'rbPerinatalRiskRate', 'rbOrgCurationLevel', 'rbPregnancyPathology',
    # next are used only for backend data manipulation, they are not presented on frontend ui
    'rbPost', 'rbSpeciality', 'rbUnits', 'rbRequestType', 'rbEventTypePurpose', 'rbUserProfile', 'EventType',
    'rbServiceKind'
]

rb_groups = {
    'vmp': (u'ВМП', ['rbPacientModel', 'rbTreatment', 'rbTreatmentType']),
    'expert_protocol': (u'Протоколы лечения', ['rbMeasureType', 'rbMeasureScheduleType', 'rbMeasureScheduleApplyType']),
    'risar': (u'РИСАР', ['rbPerinatalRiskRate', 'rbOrgCurationLevel', 'rbPregnancyPathology']),
    'other': (u'Остальные', ['rbFinance', 'rbRequestType', 'rbResult', 'rbEventTypePurpose']),
    'med_staff': (u'Мед. персонал', ['rbPost', 'rbSpeciality'])
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
    elif name == 'rbService':
        return RbServiceModelManager()
    elif name == 'Organisation':
        return OrganisationModelManager(**params)
    elif name == 'OrgStructure':
        return OrgStructureModelManager()
    elif name == 'Measure':
        return MeasureModelManager()
    elif name == 'ExpertProtocol':
        return ExpertProtocolModelManager(**params)
    elif name == 'ExpertScheme':
        return ExpertSchemeModelManager()
    elif name == 'ExpertSchemeMeasure':
        return ExpertSchemeMeasureModelManager()
    elif name == 'MeasureSchedule':
        return MeasureScheduleModelManager()
    elif name == 'ActionType':
        return SimpleRefBookModelManager(ActionType)
    elif name == 'MKB':
        return MKBModelManager()
    elif name == 'OrganisationBirthCareLevel':
        return OrganisationBCLModelManager(**params)
    elif name == 'Person':
        return PersonModelManager(**params)
    elif name == 'PersonCuration':
        return PersonCurationModelManager()
    elif name == 'rbPerinatalRiskRateWithMKBs':
        return RbPerinatalRRModelManager()
    elif name == 'rbPerinatalRiskRateMkb':
        return RbPRRMKBModelManager()
    elif name == 'rbPregnancyPathologyWithMKBs':
        return RbPregnancyPathologyModelManager()
    elif name == 'rbPregnancyPathologyMkb':
        return RbPregnancyPathologyMKBModelManager()
    elif name == 'rbResult':
        return RbResultModelManager()
    elif name == 'PriceList':
        return PriceListModelManager()
    elif name == 'PriceListItem':
        return PriceListItemModelManager()
    elif name == 'rbPrintTemplate':
        return RbPrintTemplateModelManager()
    elif name == 'rbServiceGroupAssoc':
        return RbServiceGroupAssocModelManager()