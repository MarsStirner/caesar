# -*- coding: utf-8 -*-
import datetime

from ..models.models_all import Orgstructure, Person, Organisation, v_Client_Quoting, Event, Action, Account, Rbcashoperation, \
    Client
from ..models.models_utils import formatTime
from ..models.schedule import ScheduleClientTicket
from gui import applyTemplate


def current_patient_orgStructure(event_id):
    from ..models.models_all import Actionproperty, ActionpropertyOrgstructure, Actionpropertytype
    return Orgstructure.query.\
        join(ActionpropertyOrgstructure, Orgstructure.id == ActionpropertyOrgstructure.value).\
        join(Actionproperty, Actionproperty.id == ActionpropertyOrgstructure.id).\
        join(Action).\
        join(Actionpropertytype).\
        filter(Actionpropertytype.code == 'orgStructStay', Action.event_id == event_id).\
        order_by(Action.begDate_raw.desc()).\
        first()


class Print_Template(object):

    def __init__(self):
        self.today = datetime.date.today()

    def update_context(self, template_id, context):
        from ..models.models_all import Rbprinttemplatemeta, Organisation, Orgstructure, Rbservice, Person
        for desc in Rbprinttemplatemeta.query.filter(Rbprinttemplatemeta.template_id == template_id):
            name = desc.name
            if not name in context:
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
                context[name] = datetime.datetime.strptime(value, '%d.%m.%Y').date() if value else None
            elif typeName == 'Time':
                context[name] = datetime.datetime.strptime(value, '%H:%M').time() if value else None
            elif typeName == 'Organisation':
                context[name] = Organisation.query.get(int(value)) if value else None
            elif typeName == 'Person':
                context[name] = Person.query.get(int(value)) if value else None
            elif typeName == 'OrgStructure':
                context[name] = Orgstructure.query.get(int(value)) if value else None
            elif typeName == 'Service':
                context[name] = Rbservice.query.get(int(value)) if value else None

    def print_template(self, doc):
        context_type = doc['context_type']
        template_id = doc['id']
        data = self.get_context(context_type, doc)
        return applyTemplate(template_id, data)

    def get_context(self, context_type, data):
        context = data['context']
        self.update_context(data['id'], context)

        currentOrganisation = Organisation.query.get(context['currentOrganisation']) if \
            context['currentOrganisation'] else ""
        currentOrgStructure = Orgstructure.query.get(context['currentOrgStructure']) if \
            context['currentOrgStructure'] else ""
        currentPerson = Person.query.get(context['currentPerson']) if \
            context['currentPerson'] else ""

        context.update({
            'currentOrganisation': currentOrganisation,
            'currentOrgStructure': currentOrgStructure,
            'currentPerson': currentPerson
        })

        context_func = getattr(self, 'context_%s' % context_type, None)
        if context_func and callable(context_func):
            context.update(context_func(context))
        return context

    def context_event(self, data):
        # BaseEventInfoFrame
        event = None
        quoting = None
        client = None
        if 'event_id' in data:
            event_id = data['event_id']
            event = Event.query.get(event_id)
            client = event.client

            client.date = event.execDate.date if event.execDate else self.today
            quoting = v_Client_Quoting.query.filter_by(event_id=event_id).\
                filter_by(clientId=event.client.id).first()
            if not quoting:
                quoting = v_Client_Quoting()

        return {
            'event': event,
            'client': client,
            'tempInvalid': None,
            'quoting': quoting,
            'patient_orgStructure': current_patient_orgStructure(event.id),
        }

    def context_action(self, data):
        # ActionEditDialod, ActionInfoFrame
        action_id = data[u'action_id']
        action = Action.query.get(action_id)
        event = action.event
        event.client.date = event.execDate.date if event.execDate.date else self.today
        quoting = v_Client_Quoting.query.filter_by(event_id=event.id).\
            filter_by(clientId=event.client.id).first()
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
        accountInfo = Account.query.get(account_id)
        accountInfo.selectedItemIdList = account_items_idList
        # accountInfo.selectedItemIdList = self.modelAccountItems.idList() ???
        return {
            'account': accountInfo
        }

    def context_cash_order(self, data):
        # CashBookDialog, CashDialog
        # date - datetime, Event_payments
        event = None
        client = None
        if 'event_id' in data:
            event_id = data['event_id']
            event = Event.query.get(event_id)
            client = event.client

            client.date = event.execDate.date if event.execDate else self.today
        date = data['date']
        cash_operation_id = data['cash_operation_id']
        cashBox = data['cashBox']
        cash_operation = Rbcashoperation.query.get(cash_operation_id)
        return {
            'event': event,
            'client': client,
            'date': date,
            'cashOperation': cash_operation,
            'sum': sum,
            'cashBox': cashBox,
            'tempInvalid': None
        }

    def context_person(self, data):
        # PersonDialogcf
        person_id = data['person_id']
        person = Person.query.get(person_id)
        return {
            'person': person
        }

    def context_registry(self, data):
        # RegistryWindow
        client_id = data['client_id']
        client = Client.query.get(client_id)
        client.date = self.today
        return {
            'client': client
        }

    def context_preliminary_records(self, data):
        # BeforeRecord
        client_id = data['client_id']
        client_ticket_id = data['ticket_id']
        client = Client.query.get(client_id)
        client.date = self.today
        client_ticket = ScheduleClientTicket.query.get(client_ticket_id)
        toHome = client_ticket.ticket.schedule.receptionType.code == 'home'
        if toHome:
            typeText = u'Вызов на дом'
        else:
            typeText = u'Направление на приём к врачу'
        attendance_type_code = client_ticket.ticket.attendanceType.code
        if attendance_type_code == 'planned':
            time = formatTime(client_ticket.ticket.begDateTime.time())
        elif attendance_type_code == 'CITO':
            time = "CITO"
        elif attendance_type_code == 'extra':
            time = u"сверх очереди"
        else:
            time = '--:--'
        person = client_ticket.ticket.schedule.person
        timeRange = '--:-- - --:--'
        num = 0
        return {
            'client': client,
            'person': person,
            'client_ticket': client_ticket,
            'visit': {
                'clientId': client_id,
                'type': typeText,
                'date': client_ticket.ticket.schedule.date,
                'office': client_ticket.ticket.schedule.office,
                'personId': person.id,
                'num': num,
                'time': time,
                'timeRange': timeRange,
            }
        }