# -*- coding: utf-8 -*-
import itertools

from weakref import WeakValueDictionary, WeakKeyDictionary

from caesar.blueprints.print_subsystem.lib.html import HTMLRipper
from caesar.blueprints.print_subsystem.lib.utils import get_action, get_event, get_latest_pregnancy_event, get_fetuses, \
    get_measures_list, get_latest_measure

from caesar.blueprints.print_subsystem.models.models_all import Action
from caesar.blueprints.print_subsystem.lib.risar_config import risar_mother_anamnesis, risar_father_anamnesis, checkup_flat_codes, \
    risar_anamnesis_pregnancy, pregnancy_card_attrs, gynecological_card_attrs, risar_anamnesis_transfusion, \
    risar_gyn_general_anamnesis_flat_code, risar_gyn_checkup_flat_codes, \
    request_type_gynecological, request_type_pregnancy, risar_epicrisis, first_inspection_flat_code,\
    second_inspection_flat_code, pc_inspection_flat_code, soc_prof_codes, PregnancyResult, \
    risar_gymnastics, risar_psychological_preparation, risar_maternity_lessons
from caesar.blueprints.print_subsystem.models.models_utils import DateInfo
from nemesis.lib.mis_cache import lazy, LocalCache


def strip_html(raw_str):
    if isinstance(raw_str, basestring):
        return HTMLRipper().ultimate_rip(raw_str)


class BaseEvent(object):
    def __init__(self, event):
        self._event = event


class BaseAction(object):
    def __init__(self, action):
        self._action = action

    @property
    def action(self):
        return self._action


class PreviousPregnancy(BaseAction):
    @lazy
    def note(self):
        return self.action.get_prop_value('note')

    @lazy
    def pregnancy_result(self):
        return self.action.get_prop_value('pregnancyResult')

    @lazy
    def year(self):
        year = self.action.get_prop_value('year')
        return year and u'{} г.'.format(year)

    @lazy
    def pregnancy_week(self):
        pregnancy_week = self.action.get_prop_value('pregnancy_week')
        return pregnancy_week and u'{} нед.'.format(pregnancy_week)


class AbstractCard(object):
    cache = LocalCache()
    action_type_attrs = None

    @classmethod
    def get_for_event(cls, event):
        """
        :rtype: AbstractCard
        :param event:
        :return:
        """
        klass = classes.get(event.eventType.requestType.code, cls)
        from flask import g
        if not hasattr(g, '_card_cache'):
            g._card_cache = WeakValueDictionary()
        if event.id not in g._card_cache:
            result = g._card_cache[event.id] = klass(event)
        else:
            result = g._card_cache[event.id]
        return result

    @classmethod
    def get_by_id(cls, event_id):
        event = get_event(event_id)
        return cls.get_for_event(event) if event else None

    def __init__(self, event):
        self._cached = {}
        self.event = event
        self._card_attrs_action = None

    @lazy
    def attrs(self):
        return get_action(self.event, 'cardAttributes')

    @lazy
    def transfusions(self):
        return get_action(self.event, risar_anamnesis_transfusion, one=False)

    @lazy
    def intolerances(self):
        return list(itertools.chain(self.event.client.allergies, self.event.client.intolerances))

    @lazy
    def prev_pregs(self):
        return map(PreviousPregnancy, get_action(self.event, risar_anamnesis_pregnancy, one=False))


class BaseInspection(BaseAction):
    @lazy
    def fetuses(self):
        return get_fetuses(self._action.id)

    @lazy
    def weight(self):
        return self.action.get_prop_value('weight')

    @lazy
    def ad(self):
        get = self.action.get_prop_value
        ad_high = get('ad_right_high')
        ad_low = get('ad_right_low')
        if ad_high and ad_low:
            return '{}/{} {}'.format(ad_high, ad_low, DateInfo(self.action.begDate_raw))


class PrimaryInspection(BaseInspection):
    @lazy
    def pregnancy_week(self):
        pregnancy_week = self.action.get_prop_value('pregnancy_week')
        return pregnancy_week and u'{} нед.'.format(pregnancy_week)

    @lazy
    def height(self):
        return self.action.get_prop_value('height')


class RepeatedInspection(BaseInspection):
    pass


class Epicrisis(BaseEvent):
    @lazy
    def action(self):
        return get_action(self._event, risar_epicrisis, True)

    @property
    def exists(self):
        return self.action.id is not None


class MotherAnamnesis(BaseEvent):
    @lazy
    def action(self):
        return get_action(self._event, risar_mother_anamnesis)

    @lazy
    def finished_diseases(self):
        if not self.action:
            return []
        finished_diseases = self.action.get_prop_value('finished_diseases', default=[])
        finished_diseases_text = self.action.get_prop_value('finished_diseases_text')

        result = [i.DiagName for i in finished_diseases]
        if finished_diseases_text:
            result.append(finished_diseases_text)
        return result

    @lazy
    def menstruation_last_date(self):
        return self.action.get_prop_value('menstruation_last_date')

    @lazy
    def blood_type(self):
        blood_type = self._event.client.bloodType
        return {
            'group': blood_type and blood_type.name.split('Rh')[0],
            'rh': blood_type and u'Rh({})'.format(blood_type.name.split('Rh')[1]),
        }


class FatherAnamnesis(BaseEvent):
    @lazy
    def action(self):
        return get_action(self._event, risar_father_anamnesis)

    @lazy
    def blood_type(self):
        blood_type = self.action.get_prop_value('blood_type')
        return {
            'group': blood_type and blood_type.name.split('Rh')[0],
            'rh': blood_type and u'Rh({})'.format(blood_type.name.split('Rh')[1]),
        }


class EmResult(BaseAction):
    @lazy
    def results(self):
        return strip_html(self.action.get_prop_value('Results'))


class BaseSocial(BaseAction):
    """ Социально-профилактическая помощь беременной """
    @lazy
    def lessons_number(self):
        return self.action.get_prop_value('lessons_number')

    @lazy
    def failure_reason(self):
        return self.action.get_prop_value('failure_reason')


class CardAttrs(BaseEvent):
    @lazy
    def action(self):
        return get_action(self._event, pregnancy_card_attrs)

    @lazy
    def predicted_delivery_date(self):
        return self.action.get_prop_value('predicted_delivery_date')


class PregnancyCard(AbstractCard):
    """
    @type event: nemesis.models.event.Event
    """
    cache = LocalCache()
    action_type_attrs = pregnancy_card_attrs

    def __init__(self, event):
        super(PregnancyCard, self).__init__(event)
        self._anamnesis = MotherAnamnesis(event)
        self._father_anamnesis = FatherAnamnesis(event)
        self._epicrisis = Epicrisis(event)
        self._card_attrs = CardAttrs(event)

    @property
    def anamnesis(self):
        return self._anamnesis

    @property
    def father_anamnesis(self):
        return self._father_anamnesis

    @property
    def card_attrs(self):
        return self._card_attrs

    @lazy
    def checkups(self):
        return get_action(self.event, checkup_flat_codes, one=None).order_by(Action.begDate_raw).all()

    @lazy
    def all_inspections(self):
        return map(BaseInspection, self.checkups)

    @lazy
    def gymnastics_list(self):
        return map(BaseSocial, get_action(self.event, risar_gymnastics, one=False))

    @lazy
    def gymnastics_lessons_number(self):
        return sum(g.lessons_number for g in self.gymnastics_list if not g.failure_reason)

    @lazy
    def psychological_preparation_list(self):
        return map(BaseSocial, get_action(self.event, risar_psychological_preparation, one=False))

    @lazy
    def psychological_preparation_lessons_number(self):
        return sum(pp.lessons_number for pp in self.psychological_preparation_list if not pp.failure_reason)

    @lazy
    def maternity_lessons_list(self):
        return map(BaseSocial, get_action(self.event, risar_maternity_lessons, one=False))

    @lazy
    def maternity_lessons_number(self):
        return sum(ml.lessons_number for ml in self.maternity_lessons_list if not ml.failure_reason)

    @lazy
    def primary_inspection(self):
        for checkup in self.checkups:
            if checkup.actionType.flatCode in (first_inspection_flat_code, pc_inspection_flat_code):
                return PrimaryInspection(checkup)

    @lazy
    def latest_inspection(self):
        if self.checkups:
            checkup = self.checkups[-1]
            if checkup.actionType.flatCode in (first_inspection_flat_code, pc_inspection_flat_code):
                return PrimaryInspection(checkup)
            elif checkup.actionType.flatCode == second_inspection_flat_code:
                return RepeatedInspection(checkup)

    @lazy
    def latest_rep_inspection(self):
        for checkup in reversed(self.checkups):
            if checkup.actionType.flatCode == second_inspection_flat_code:
                return RepeatedInspection(checkup)

    @lazy
    def prev_pregnancies_features(self):
        return [strip_html(p.note) for p in self.prev_pregs if p.note]

    @lazy
    def abortion_pregnancies(self):
        return filter(lambda p: p.pregnancy_result.get('code') in PregnancyResult.abortion, self.prev_pregs)

    @lazy
    def birth_pregnancies(self):
        return filter(lambda p: p.pregnancy_result.get('code') in PregnancyResult.birth, self.prev_pregs)

    @lazy
    def early_birth_pregnancies(self):
        return filter(lambda p: p.pregnancy_result.get('code') in PregnancyResult.early_birth, self.prev_pregs)

    @lazy
    def pelvic_measurements(self):
        get = self.primary_inspection.action.get_prop_value
        return {
            'CDiag': get('CDiag'),
            'CExt': get('CExt'),
            'CVera': get('CVera'),
            'DsCr': get('DsCr'),
            'DsSP': get('DsSP'),
            'DsTr': get('DsTr'),
        }

    @cache.cached_call
    def get_em_result(self, code):
        em = get_latest_measure(self.event.id, code, with_result=True)
        if em:
            return EmResult(em.result_action)

    @lazy
    def rw_em_result_list(self):
        return map(lambda m: EmResult(m.result_action), get_measures_list(self.event.id, '0019', with_result=True))

    @lazy
    def rw1_em_result(self):
        rw_list = self.rw_em_result_list
        if len(rw_list) == 1:
            return rw_list[0]
        elif len(rw_list) > 1:
            return rw_list[-2]

    @lazy
    def rw2_em_result(self):
        rw_list = self.rw_em_result_list
        return rw_list[-1] if len(rw_list) > 1 else None

    @lazy
    def weight_gain(self):
        start_weight = self.primary_inspection.weight
        current_weight = self.latest_inspection.weight
        if start_weight and current_weight:
            return current_weight - start_weight

    @lazy
    def ad(self):
        """Артериальное давление"""
        return (i.ad for i in self.all_inspections if i.ad)

    @lazy
    def epicrisis(self):
        return self._epicrisis

    @lazy
    def soc_prof_help(self):
        return {code: get_action(self.event, code, one=False)
                for code in soc_prof_codes}


class GynecologicCard(AbstractCard):
    cache = LocalCache()
    action_type_attrs = gynecological_card_attrs

    def __init__(self, event):
        super(GynecologicCard, self).__init__(event)

    @lazy
    def anamnesis(self):
        return get_action(self.event, risar_gyn_general_anamnesis_flat_code, True)

    @lazy
    def checkups(self):
        return get_action(self.event, risar_gyn_checkup_flat_codes, one=False)

    @lazy
    def latest_pregnancy_event(self):
        return get_latest_pregnancy_event(self.event.client_id) if self.event else None


classes = {
    request_type_pregnancy: PregnancyCard,
    request_type_gynecological: GynecologicCard,
}


def _clear_caches():
    from flask import g
    if hasattr(g, '_card_cache'):
        del g._card_cache

    AbstractCard.cache = LocalCache()
    PregnancyCard.cache = LocalCache()
    GynecologicCard.cache = LocalCache()

    lazy.cache = WeakKeyDictionary()
