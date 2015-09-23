# -*- coding: utf-8 -*-
import datetime
import logging
import traceback

from .query import Query
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
from sqlalchemy import func

from blueprints.print_subsystem.lib.internals import make_jinja_environment, RenderTemplateException
from blueprints.print_subsystem.models.models_utils import DateInfo
from nemesis.lib.jsonify import ScheduleVisualizer
from nemesis.lib.utils import safe_date, string_to_datetime, safe_int
from .data import current_patient_orgStructure
from .specialvars import SpecialVariable
from .utils import get_action
from ..models.models_all import Mkb, Organisation, Orgstructure, Person, Event, v_Client_Quoting, EventPayment, Action, Account, Client, \
    rbPrintTemplateMeta, rbService
from ..models.schedule import ScheduleClientTicket, Schedule

__author__ = 'viruzzz-kun'


class Print_Template(object):

    def __init__(self):
        self.today = datetime.date.today()
        self.jinja_env = make_jinja_environment()

    def print_template(self, doc):
        context_type = doc['context_type']
        template_id = doc['id']

        try:
            return self.jinja_env.get_template('db/%s' % template_id).render(self.get_context(context_type, doc))
        except TemplateNotFound, e:
            tb = traceback.format_exc()
            if isinstance(tb, str):
                tb = tb.decode('utf-8')
            raise RenderTemplateException(u'Шаблон с id=%s не найден' % template_id, {
                'type': RenderTemplateException.Type.other,
                'template_name': template_id,
                'trace': tb,
            })
        except TemplateSyntaxError, e:
            logging.error('syntax error in template id = %s', template_id, exc_info=True)
            raise RenderTemplateException(e.message, {
                'type': RenderTemplateException.Type.syntax,
                'template_name': template_id,
                'lineno': e.lineno
            })
        except Exception, e:
            print unicode(traceback.format_exc(), 'utf-8')
            logging.critical('erroneous template id = %s', template_id, exc_info=True)
            tb = traceback.format_exc()
            if isinstance(tb, str):
                tb = tb.decode('utf-8')
            raise RenderTemplateException(e.message, {
                'type': RenderTemplateException.Type.other,
                'template_name': template_id,
                'trace': tb,
            })

    def get_context(self, context_type, data):
        now = datetime.datetime.now()

        context = dict(data['context'])

        for desc in Query(rbPrintTemplateMeta).filter(rbPrintTemplateMeta.template_id == data['id']):
            name = desc.name
            if name not in context:
                continue
            value = context[name]
            typeName = desc.type
            if typeName == 'Integer':
                context[name] = int(value)
            elif typeName == 'Float':
                context[name] = float(value)
            elif typeName == 'Boolean':
                context[name] = bool(value)
            elif typeName == 'Date':
                context[name] = string_to_datetime(value).date() if value else None
            elif typeName == 'Time':
                context[name] = datetime.datetime.strptime(value, '%H:%M').time() if value else None
            elif typeName == 'Organisation':
                context[name] = Query(Organisation).get(int(value)) if value else None
            elif typeName == 'Person':
                context[name] = Query(Person).get(int(value)) if value else None
            elif typeName == 'OrgStructure':
                context[name] = Query(Orgstructure).get(int(value)) if value else None
            elif typeName == 'Service':
                context[name] = Query(rbService).get(int(value)) if value else None
            elif typeName == 'MKB':
                context[name] = Query(Mkb).get(int(value)) if value else None

        if 'special_variables' in context:
            # Я надеюсь, что нам не придётся этим пользоваться
            ext = {}
            for sp_name in context['special_variables']:
                ext[sp_name] = SpecialVariable(sp_name, **context)
            del context['special_variables']
            context.update(ext)
        currentOrganisation = Query(Organisation).get(context['currentOrganisation']) if \
            context['currentOrganisation'] else ""
        currentOrgStructure = Query(Orgstructure).get(context['currentOrgStructure']) if \
            context['currentOrgStructure'] else ""
        currentPerson = Query(Person).get(context['currentPerson']) if \
            context['currentPerson'] else ""

        context.update({
            'now': now,
            'currentDate': DateInfo(now.date()),
            'currentTime': now.time().strftime("%H:%M:%S"),
            'currentOrganisation': currentOrganisation,
            'currentOrgStructure': currentOrgStructure,
            'currentPerson': currentPerson,
        })

        context_func = getattr(self, 'context_%s' % context_type, None)
        if context_func and callable(context_func):
            context.update(context_func(context))
        return context

    def context_event(self, data):
        event = None
        quoting = None
        client = None
        patient_os = None
        if 'event_id' in data:
            event_id = data['event_id']
            event = Query(Event).get(event_id)
            client = event.client

            client.date = event.execDate.date if event.execDate else self.today
            quoting = Query(v_Client_Quoting).filter_by(
                event_id=event_id,
                clientId=event.client.id,
                deleted=0
            ).first()
            if not quoting:
                quoting = v_Client_Quoting()
            patient_os = current_patient_orgStructure(event.id)

        template_context = {
            'event': event,
            'client': client,
            'tempInvalid': None,
            'quoting': quoting,
            'patient_orgStructure': patient_os,
        }
        if 'payment_id' in data:
            template_context['payment'] = Query(EventPayment).get(data['payment_id'])
        return template_context

    def context_action(self, data):
        # ActionEditDialod, ActionInfoFrame
        action_id = data[u'action_id']
        action = Query(Action).get(action_id)
        event = action.event
        event.client.date = event.execDate.date if event.execDate.date else self.today
        quoting = Query(v_Client_Quoting).filter_by(event_id=event.id).\
            filter_by(clientId=event.client.id).filter_by(deleted=0).first()
        if not quoting:
            quoting = v_Client_Quoting()
        return {
            'event': event,
            'action': action,
            'client': event.client,
            'currentActionIndex': 0,
            'quoting': quoting,
            'patient_orgStructure': current_patient_orgStructure(event.id),
        }

    def context_account(self, data):
        # расчеты (CAccountingDialog)
        account_id = data['account_id']
        account_items_idList = data['account_items_idList']
        accountInfo = Query(Account).get(account_id)
        accountInfo.selectedItemIdList = account_items_idList
        # accountInfo.selectedItemIdList = self.modelAccountItems.idList() ???
        return {
            'account': accountInfo
        }

    def context_cashbook_list(self, data):
        operations = metrics = None

        def get_metrics():
            m = Query(EventPayment).with_entities(
                func.count(),
                func.sum(func.IF(EventPayment.sum > 0, EventPayment.sum, 0)),
                - func.sum(func.IF(EventPayment.sum < 0, EventPayment.sum, 0))
            ).filter(EventPayment.id.in_(data['payments_id_list'])).first()
            return {
                'total': m[0],
                'income': m[1],
                'expense': abs(m[2])
            }

        if 'payments_id_list' in data:
            operations = Query(EventPayment).filter(
                EventPayment.id.in_(data['payments_id_list'])
            ).order_by(EventPayment.date, EventPayment.id).all()
            metrics = get_metrics()
        return {
            'operations': operations,
            'metrics': metrics
        }

    def context_person(self, data):
        # PersonDialogcf
        person_id = data['person_id']
        person = Query(Person).get(person_id)
        return {
            'person': person
        }

    def context_registry(self, data):
        # RegistryWindow
        client_id = data['client_id']
        client = Query(Client).get(client_id)
        client.date = self.today
        return {
            'client': client
        }

    def context_preliminary_records(self, data):
        # BeforeRecord
        client_id = data['client_id']
        client_ticket_id = data['ticket_id']
        client = Query(Client).get(client_id)
        client.date = self.today
        client_ticket = Query(ScheduleClientTicket).get(client_ticket_id)
        timeRange = '--:-- - --:--'
        num = 0
        return {
            'client': client,
            'client_ticket': client_ticket
        }

    def context_risar(self, data):
        event = None
        if 'event_id' in data:
            event_id = data['event_id']
            event = Query(Event).get(event_id)
        return {
            'event': event,
            'client': event.client if event else None,
            'card_attributes': get_action(event, 'cardAttributes'),
            'mother_amamnesis': get_action(event, 'risar_mother_anamnesis'),
            'father_amamnesis': get_action(event, 'risar_father_anamnesis'),
            'transfusions': get_action(event, 'risar_anamnesis_transfusion', one=False),
            'prev_pregnancies': get_action(event, 'risar_anamnesis_pregnancy', one=False),
            'first_inspection': get_action(event, 'risarFirstInspection'),
            'second_inspections': get_action(event, 'risarSecondInspection', one=False),
            'epicrisis': get_action(event, 'epicrisis'),
        }

    def context_risar_inspection(self, data):
        event = None
        action = None
        if 'event_id' in data:
            event_id = data['event_id']
            event = Query(Event).get(event_id)
        if 'action_id' in data:
            action_id = data['action_id']
            action = Query(Action).get(action_id)
        return {
            'event': event,
            'client': event.client if event else None,
            'action': action
        }

    def context_risar_gravidograma(self, data):
        event = None
        if 'event_id' in data:
            event_id = data['event_id']
            event = Query(Event).get(event_id)
        return {
            'event': event
        }

    def context_schedule(self, data):
        today = datetime.date.today()
        person_id = safe_int(data['person_id'])
        start_date = safe_date(data.get('start_date', today))
        end_date = safe_date(data.get('end_date', today))
        sviz = ScheduleVisualizer()
        person = Query(Person).get(person_id)
        return {
            'schedule': Schedule(),
            'person': sviz.make_person(person),
            'start_date': start_date,
            'end_date': end_date
        }