# -*- coding: utf-8 -*-
from datetime import date
from ..app import module, _config
from ..utils import get_lpu_session
from ..models.models_all import Orgstructure, Person, Organisation, v_Client_Quoting, Event, Action, Account, Rbcashoperation, \
    Client, Clientattach
from ..models.schedule import ScheduleClientTicket
from gui import applyTemplate
from info.PrintInfo import CInfoContext


class Print_Template(object):

    def __init__(self):
        self.db_session = get_lpu_session()
        self.today = date.today()

    def __del__(self):
        self.db_session.close()

    def get_template_meta(self, template_id):
        query = '''{0}'''.format(template_id)

        return self.db_session.execute(query)

    def print_template(self, context_type, template_id, data):
        data = self.get_context(context_type, data)
        return applyTemplate(template_id, data)

    def get_context(self, context_type, data):
        event = None
        quoting = None
        additional_context = data['additional_context']

        currentOrganisation = self.db_session.query(Organisation).get(additional_context['currentOrganisation']) if \
            additional_context['currentOrganisation'] else ""
        currentOrgStructure = self.db_session.query(Orgstructure).get(additional_context['currentOrgStructure']) if \
            additional_context['currentOrgStructure'] else ""
        currentPerson = self.db_session.query(Person).get(additional_context['currentPerson']) if \
            additional_context['currentPerson'] else ""

        context = {'currentOrganisation': currentOrganisation,
                   'currentOrgStructure': currentOrgStructure,
                   'currentPerson': currentPerson
                   }

        if 'event_id' in data:
            event_id = data['event_id']
            event = self.db_session.query(Event).get(event_id)
            client = event.client

            client.date = event.execDate.date() if event.execDate else self.today
            quoting = self.db_session.query(v_Client_Quoting).filter_by(event_id=event_id).\
                filter_by(clientId=event.client.id).first()

        if context_type == u'event':
            # BaseEventInfoFrame

            context.update({'event': event,
                            'client': client,
                            'tempInvalid': None,
                            'quoting': quoting
                            })
        elif context_type == u'action':
            # ActionEditDialod, ActionInfoFrame
            action_id = data[u'action_id']
            action = self.db_session.query(Action).get(action_id)
            event = action.event
            event.client.date = event.execDate.date() if event.execDate else self.today
            quoting = self.db_session.query(v_Client_Quoting).filter_by(event_id=event.id).\
                filter_by(clientId=event.client.id).first()
            context.update({'event': event,
                            'action': action,
                            'client': event.client,
                            'currentActionIndex': 0,
                            'quoting': quoting,
                            })
        elif context_type == u'acсount':
            # расчеты (CAccountingDialog)
            account_id = data['account_id']
            account_items_idList = data['account_items_idList']
            accountInfo = self.db_session.query(Account).get(account_id)
            accountInfo.selectedItemIdList = account_items_idList
            # accountInfo.selectedItemIdList = self.modelAccountItems.idList() ???
            context.update({'account': accountInfo})
        elif context_type == u'cash_order':
            # CashBookDialog, CashDialog
            # date - datetime, Event_payments
            date = data['date']
            cash_operation_id = data['cash_operation_id']
            cashBox = data['cashBox']
            cash_operation = self.db_session.query(Rbcashoperation).get(cash_operation_id)
            context.update({'event': event,
                            'client': client,
                            'date': date,
                            'cashOperation': cash_operation,
                            'sum': sum,
                            'cashBox': cashBox,
                            'tempInvalid': None
                            })
        elif context_type == u'person':
            # PersonDialogcf
            person_id = data['person_id']
            person = self.db_session.query(Person).get(person_id)
            context.update({'person': person})
        elif context_type == u'registry':
            # RegistryWindow
            client_id = data['client_id']
            client = self.db_session.query(Client).get(client_id)
            client.date = self.today
            context.update({'client': client})
        elif context_type == u'preliminary_records':
            # BeforeRecord
            client_id = data['client_id']
            client_ticket_id = data['ticket_id']
            client = self.db_session.query(Client).get(client_id)
            client.date = self.today
            client_ticket = self.db_session.query(ScheduleClientTicket).get(client_ticket_id)
            person = client_ticket.ticket.schedule.person
            context.update({'client': client,
                            'person': person,
                            'client_ticket': client_ticket})
        return context