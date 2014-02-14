# -*- coding: utf-8 -*-
from datetime import date

from ..app import module, _config
from ..utils import get_lpu_session
from ..models import Orgstructure, Person, Organisation, v_Client_Quoting, Event, Action
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

    def print_template(self, template_id, event_id, action_id, additional_context):
        # context = CInfoContext()
        event = self.db_session.query(Event).get(event_id)
        action = self.db_session.query(Action).get(action_id)
        quota = self.db_session.query(v_Client_Quoting).filter_by(event_id=event_id).\
            filter_by(clientId=event.client.id).first()
        currentOrganisation = self.db_session.query(Organisation).get(additional_context['currentOrganisation']) if \
            additional_context['currentOrganisation'] else ""
        currentOrgStructure = self.db_session.query(Orgstructure).get(additional_context['currentOrgStructure']) if \
            additional_context['currentOrgStructure'] else ""
        currentPerson = self.db_session.query(Person).get(additional_context['currentPerson']) if \
            additional_context['currentPerson'] else ""
        data = {'currentOrganisation': currentOrganisation,
                'currentOrgStructure': currentOrgStructure,
                'currentPerson': currentPerson,
                'event': event,
                'action': action,
                'client': event.client,
                'quota': quota,
                'currentActionIndex': 0,  # на самом деле мы ничего не знаем о текущем индексе действия
                }
        return applyTemplate(template_id, data)