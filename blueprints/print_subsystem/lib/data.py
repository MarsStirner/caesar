# -*- coding: utf-8 -*-
from datetime import date

from ..models.models_all import Orgstructure, Person, Organisation, v_Client_Quoting, Event, Action, Account, Rbcashoperation, \
    Client
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
        self.today = date.today()

    def get_template_meta(self, template_id):
        return {}

    def print_template(self, context_type, template_id, data):
        data = self.get_context(context_type, data)
        return applyTemplate(template_id, data)

    def get_context(self, context_type, data):
        additional_context = data['additional_context']

        currentOrganisation = Organisation.query.get(additional_context['currentOrganisation']) if \
            additional_context['currentOrganisation'] else ""
        currentOrgStructure = Orgstructure.query.get(additional_context['currentOrgStructure']) if \
            additional_context['currentOrgStructure'] else ""
        currentPerson = Person.query.get(additional_context['currentPerson']) if \
            additional_context['currentPerson'] else ""

        context = {
            'currentOrganisation': currentOrganisation,
            'currentOrgStructure': currentOrgStructure,
            'currentPerson': currentPerson
        }

        if 'event_id' in data:
            event_id = data['event_id']
            event = Event.query.get(event_id)
            client = event.client

            client.date = event.execDate.date if event.execDate else self.today
            quoting = v_Client_Quoting.query.filter_by(event_id=event_id).\
                filter_by(clientId=event.client.id).first()
            if not quoting:
                quoting = v_Client_Quoting()

        context_func = getattr(self, 'context_%s' % context_type, None)
        if context_func and callable(context_func):
            context.update(context_func(data))
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
        person = client_ticket.ticket.schedule.person
        return {
            'client': client,
            'person': person,
            'client_ticket': client_ticket
        }