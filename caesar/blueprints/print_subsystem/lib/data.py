# -*- coding: utf-8 -*-
import datetime

from caesar.blueprints.print_subsystem.models.models_utils import Query
from flask import g
from sqlalchemy import func, and_
from caesar.blueprints.print_subsystem.models.schedule import Schedule
from caesar.blueprints.print_subsystem.lib.utils import get_action

from nemesis.lib.utils import string_to_datetime, safe_date, safe_int, format_money
from nemesis.lib.jsonify import ScheduleVisualizer
from ..models.models_all import (Orgstructure, Person, Organisation, v_Client_Quoting, Event, Action, Account,
    Client, Mkb, ActionProperty, ActionProperty_OrgStructure, Actionpropertytype, Actiontype,
    ActionProperty_HospitalBed, OrgstructureHospitalbed, ActionProperty_Integer, TakenTissueJournal)
from ..models.schedule import ScheduleClientTicket
from ..models.expert_protocol import EventMeasure
from nemesis.lib.const import (STATIONARY_ORG_STRUCT_STAY_CODE, STATIONARY_HOSP_BED_CODE, STATIONARY_MOVING_CODE,
    STATIONARY_HOSP_LENGTH_CODE, STATIONARY_ORG_STRUCT_TRANSFER_CODE, STATIONARY_LEAVED_CODE)
from nemesis.models.enums import ActionStatus
from gui import applyTemplate
from specialvars import SpecialVariable
from nemesis.lib.data_ctrl.accounting.invoice import InvoiceController
from nemesis.lib.data_ctrl.accounting.service import ServiceController
from nemesis.lib.data_ctrl.accounting.utils import (calc_invoice_sum_wo_discounts, check_invoice_closed,
    check_invoice_can_add_discounts)
from caesar.blueprints.print_subsystem.lib.num_to_text_converter import NumToTextConverter
from .model_provider import PrintingModelProvider


def current_patient_orgStructure(event_id):
    return Query(Orgstructure).\
        join(ActionProperty_OrgStructure, Orgstructure.id == ActionProperty_OrgStructure.value_).\
        join(ActionProperty, ActionProperty.id == ActionProperty_OrgStructure.id).\
        join(Action).\
        join(Actionpropertytype).\
        filter(
            Actionpropertytype.code == 'orgStructStay',
            Action.event_id == event_id,
            Action.deleted == 0).\
        order_by(Action.begDate_raw.desc()).\
        first()


def get_patient_location(event, dt=None, finished_moving=False):
    if event.is_stationary:
        query = _get_stationary_location_query(event, dt, finished_moving)
        query = query.with_entities(
            Orgstructure
        )
        current_os = query.first()
    else:
        current_os = event.orgStructure
    return current_os


def _get_stationary_location_query(event, dt=None, finished_moving=False):
    query = _get_moving_query(event, dt, finished_moving)
    query = query.join(
        ActionProperty
    ).join(
        Actionpropertytype, and_(ActionProperty.type_id == Actionpropertytype.id,
                                 Actionpropertytype.actionType_id == Actiontype.id)
    ).join(
        ActionProperty_OrgStructure, ActionProperty.id == ActionProperty_OrgStructure.id
    ).join(
        Orgstructure
    ).filter(
        Actionpropertytype.code == STATIONARY_ORG_STRUCT_STAY_CODE
    )
    return query


def get_patient_hospital_bed(event, dt=None):
    query = _get_moving_query(event, dt, False)
    query = query.join(
        ActionProperty
    ).join(
        Actionpropertytype, and_(ActionProperty.type_id == Actionpropertytype.id,
                                 Actionpropertytype.actionType_id == Actiontype.id)
    ).join(
        ActionProperty_HospitalBed, ActionProperty.id == ActionProperty_HospitalBed.id
    ).join(
        OrgstructureHospitalbed
    ).filter(
        Actionpropertytype.code == STATIONARY_HOSP_BED_CODE
    ).with_entities(
        OrgstructureHospitalbed
    )
    hb = query.first()
    return hb


def _get_moving_query(event, dt=None, finished=None):
    query = Query(Action).join(
        Actiontype
    ).filter(
        Action.event_id == event.id,
        Action.deleted == 0,
        Actiontype.flatCode == STATIONARY_MOVING_CODE
    )
    if dt:
        query = query.filter(Action.begDate_raw <= dt)
    elif finished is not None:
        if finished:
            query = query.filter(Action.status == ActionStatus.finished[0])
        else:
            query = query.filter(Action.status != ActionStatus.finished[0])
    query = query.order_by(Action.begDate_raw.desc())
    return query


def get_hosp_length(event):
    def from_hosp_release():
        query = _get_hosp_release_query(event)
        query = query.join(
            ActionProperty
        ).join(
            Actionpropertytype, and_(ActionProperty.type_id == Actionpropertytype.id,
                                     Actionpropertytype.actionType_id == Actiontype.id)
        ).join(
            ActionProperty_Integer, ActionProperty.id == ActionProperty_Integer.id
        ).filter(
            Actionpropertytype.code == STATIONARY_HOSP_LENGTH_CODE
        ).with_entities(
            ActionProperty_Integer
        )
        hosp_length = query.first()
        return hosp_length.value if hosp_length else None

    def _get_start_date_from_moving():
        query = _get_moving_query(event)
        start_date = query.with_entities(
            Action.begDate_raw
        ).order_by(None).order_by(Action.begDate_raw).first()
        return safe_date(start_date[0]) if start_date else None

    def _get_finish_date_from_moving():
        last_moving_q = _get_moving_query(event, finished=True)
        final_moving_q = last_moving_q.join(
            ActionProperty
        ).join(
            Actionpropertytype, and_(ActionProperty.type_id == Actionpropertytype.id,
                                     Actionpropertytype.actionType_id == Actiontype.id)
        ).outerjoin(
            ActionProperty_Integer, ActionProperty.id == ActionProperty_Integer.id
        ).filter(
            Actionpropertytype.code == STATIONARY_ORG_STRUCT_TRANSFER_CODE,
            ActionProperty_Integer.id == None
        )
        end_date = final_moving_q.with_entities(
            Action.endDate_raw
        ).first()
        return safe_date(end_date[0]) if end_date else None

    def calculate_not_finished():
        date_start = _get_start_date_from_moving() or event.setDate_raw.date()
        date_to = _get_finish_date_from_moving()
        if not date_to:
            date_to = datetime.date.today()
        hosp_length = (date_to - date_start).days
        if event.is_day_hospital:
            hosp_length += 1
        return hosp_length

    # 1) from hospital release document
    duration = from_hosp_release()
    if duration is not None:
        hosp_length = duration
    else:
        # 2) calculate not yet finished stay length
        hosp_length = calculate_not_finished()
    return hosp_length


def _get_hosp_release_query(event):
    query = Query(Action).join(
        Actiontype
    ).filter(
        Action.event_id == event.id,
        Action.deleted == 0,
        Actiontype.flatCode == STATIONARY_LEAVED_CODE
    ).filter(
        Action.status == ActionStatus.finished[0]
    ).order_by(Action.begDate_raw.desc())
    return query


class Print_Template(object):

    def __init__(self):
        self.today = datetime.date.today()

    def update_context(self, template_id, context):
        from ..models.models_all import rbPrintTemplateMeta, Organisation, Orgstructure, rbService, Person
        for desc in Query(rbPrintTemplateMeta).filter(rbPrintTemplateMeta.template_id == template_id):
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

    def print_template(self, doc):
        context_type = doc['context_type']
        template_id = doc['id']
        data = self.get_context(context_type, doc)
        return applyTemplate(template_id, data)

    def get_context(self, context_type, data):
        context = dict(data['context'])
        self.update_context(data['id'], context)
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
            'currentOrganisation': currentOrganisation,
            'currentOrgStructure': currentOrgStructure,
            'currentPerson': currentPerson,
            'SpecialVariable': SpecialVariable
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
        invoice_list = []
        if 'event_id' in data:
            event_id = data['event_id']
            event = Query(Event).get(event_id)
            client = event.client

            client.date = event.execDate.date if event.execDate else self.today
            quoting = Query(v_Client_Quoting).filter_by(event_id=event_id).\
                filter_by(clientId=event.client.id).filter_by(deleted=0).first()
            if not quoting:
                quoting = v_Client_Quoting()
            patient_os = current_patient_orgStructure(event.id)

            InvoiceController.get_selecter().set_model_provider(PrintingModelProvider.set_session(g.printing_session))
            invoice_ctrl = InvoiceController()
            invoice_list = invoice_ctrl.get_listed_data({
                'event_id': event_id
            })

        template_context = {
            'event': event,
            'client': client,
            'tempInvalid': None,
            'quoting': quoting,
            'patient_orgStructure': patient_os,
            'invoice_list': invoice_list
        }
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
        ServiceController.get_selecter().set_model_provider(PrintingModelProvider.set_session(g.printing_session))
        service_ctrl = ServiceController()
        service = service_ctrl.get_action_service(action)
        invoice_ctrl = InvoiceController()
        return {
            'event': event,
            'action': action,
            'client': event.client,
            'currentActionIndex': 0,
            'quoting': quoting,
            'patient_orgStructure': current_patient_orgStructure(event.id),
            'service': service,
            'utils': {
                'format_money': format_money,
                'get_invoice': invoice_ctrl.get_service_invoice,
                'get_service_payment_info': service_ctrl.get_service_payment_info
            }
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

    # def context_cashbook_list(self, data):
    #     operations = metrics = None
    #
    #     def get_metrics():
    #         m = Query(EventPayment).with_entities(
    #             func.count(),
    #             func.sum(func.IF(EventPayment.sum > 0, EventPayment.sum, 0)),
    #             - func.sum(func.IF(EventPayment.sum < 0, EventPayment.sum, 0))
    #         ).filter(EventPayment.id.in_(data['payments_id_list'])).first()
    #         return {
    #             'total': m[0],
    #             'income': m[1],
    #             'expense': abs(m[2])
    #         }
    #
    #     if 'payments_id_list' in data:
    #         operations = Query(EventPayment).filter(
    #             EventPayment.id.in_(data['payments_id_list'])
    #         ).order_by(EventPayment.date, EventPayment.id).all()
    #         metrics = get_metrics()
    #     return {
    #         'operations': operations,
    #         'metrics': metrics
    #     }

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

    def context_event_measure(self, data):
        em = None
        if 'event_measure_id' in data:
            em = Query(EventMeasure).get(data['event_measure_id'])
        return {
            'em': em
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

    def context_invoice(self, data):
        invoice_id = safe_int(data['invoice_id'])
        InvoiceController.get_selecter().set_model_provider(PrintingModelProvider.set_session(g.printing_session))
        invoice_ctrl = InvoiceController()
        invoice = invoice_ctrl.get_invoice(invoice_id)
        event_id = safe_int(data.get('event_id'))
        event = Query(Event).get(event_id) if event_id else None
        conv = NumToTextConverter()
        return {
            'invoice': invoice,
            'event': event,
            'utils': {
                'converter': conv,
                'get_converter': lambda: NumToTextConverter(),
                'format_money': format_money,
                'calc_invoice_sum_wo_discounts': calc_invoice_sum_wo_discounts,
                'check_invoice_closed': check_invoice_closed,
                'get_invoice_payment_info': invoice_ctrl.get_invoice_payment_info,
                'check_invoice_can_add_discounts': check_invoice_can_add_discounts
            }
        }

    def context_biomaterials(self, data):
        ttj_ids = data.get('ttj_ids')
        ttj_records = Query(TakenTissueJournal).filter(TakenTissueJournal.id.in_(ttj_ids)).all()
        return {
            'ttj_records': ttj_records
        }

    def context_event_list(self, data):
        event_ids = data.get('event_id_list')
        event_list = Query(Event).filter(Event.id.in_(event_ids)).all()
        return {
            'event_list': event_list
        }

    def context_action_list(self, data):
        action_ids = []
        action_list = []
        selected_aps = {}

        if 'action_id_dict' in data:
            action_id_dict = data.get('action_id_dict')
            selected_aps = {safe_int(k): v for k, v in action_id_dict.items()}
            action_ids = action_id_dict.keys()
        elif 'action_id_list' in data:
            action_ids = data.get('action_id_list')

        if action_ids:
            action_list = Query(Action).filter(Action.id.in_(action_ids)).all()

        return {
            'action_list': action_list,
            'selected_aps': selected_aps,
        }
