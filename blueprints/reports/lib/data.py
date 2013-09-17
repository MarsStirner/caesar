# -*- coding: utf-8 -*-
import os
import exceptions
from datetime import date

from ..app import module, _config
from flask.ext.sqlalchemy import SQLAlchemy
from ..utils import get_lpu_session


class Patients_Process(object):

    def __init__(self):
        self.db_session = get_lpu_session()

    def get_priemn_postup(self, start, end):
        query = '''SELECT
                      `Action`.`begDate` AS `Datapost`,
                      Client.lastName,
                      Client.firstName,
                      Client.patrName,
                      Event.externalId,
                      OrgStructure.Address
                    FROM `Action`
                     INNER JOIN `ActionProperty`
                        ON `Action`.`id` = `ActionProperty`.`action_id` AND `ActionProperty`.`type_id` = 1608
                    INNER  JOIN `ActionProperty_OrgStructure`
                        ON ActionProperty.id = `ActionProperty_OrgStructure`.`id`
                     INNER JOIN OrgStructure
                        ON ActionProperty_OrgStructure.value = OrgStructure.id
                      INNER JOIN Event
                      ON Event.id = Action.event_id
                      INNER JOIN Client
                      ON Client.id = Event.client_id
                    WHERE `Action`.`deleted` = 0 AND `Action`.`actionType_id` = 112
                    AND (Action.endDate BETWEEN '{} 08:00:00' AND '{} 07:59:59')
                    '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query)

    def get_priemn_vypis(self, start, end):
        query = '''SELECT
                      `Action`.`begDate` AS `Datapost`,
                      Client.lastName,
                      Client.firstName,
                      Client.patrName,
                      Event.externalId,
                      OrgStructure.Address
                    FROM `Action`
                     INNER JOIN `ActionProperty`
                        ON `Action`.`id` = `ActionProperty`.`action_id` AND `Action`.`actionType_id` = 113
                    INNER  JOIN `ActionProperty_OrgStructure`
                        ON ActionProperty.id = `ActionProperty_OrgStructure`.`id` AND `ActionProperty`.`type_id` = 7021
                     INNER JOIN OrgStructure
                        ON ActionProperty_OrgStructure.value = OrgStructure.id
                      INNER JOIN VYPISKI
                      ON VYPISKI.Event_id = `Action`.event_id
                      INNER JOIN Event
                      ON Event.id = Action.event_id
                      INNER JOIN Client
                      ON Client.id = Event.client_id
                    WHERE `Action`.`deleted` = 0 AND Event.deleted=0 AND date(`Action`.endDate)=DATE(VYPISKI.`Data vypiski`)
                    AND (VYPISKI.`Data vypiski` BETWEEN '{} 08:00:00' AND '{} 07:59:59')
                    '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query)

    def get_priemn_perevod(self, start, end):
        query = '''SELECT
                      `Action`.`begDate` AS `Datapost`,
                      Client.lastName,
                      Client.firstName,
                      Client.patrName,
                      Event.externalId,
                      OrgStructure.Address,
                      Pac_prb.prb as prb

                    FROM `Action`
                     INNER JOIN `ActionProperty`
                        ON `Action`.`id` = `ActionProperty`.`action_id` AND `Action`.`actionType_id` = 113
                    INNER  JOIN `ActionProperty_OrgStructure`
                        ON ActionProperty.id = `ActionProperty_OrgStructure`.`id` AND `ActionProperty`.`type_id` = 14370
                     INNER JOIN OrgStructure
                        ON ActionProperty_OrgStructure.value = OrgStructure.id
                      INNER JOIN Pac_prb
                      ON Pac_prb.id = Action.id
                      INNER JOIN Event
                      ON Event.id = Action.event_id
                      INNER JOIN Client
                      ON Client.id = Event.client_id
                    WHERE `Action`.`deleted` = 0 AND (Action.begDate BETWEEN '{} 08:00:00' AND '{} 07:59:59')
                    '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query)

    def get_priemn_umerlo(self, start, end):
        query = '''SELECT
                      `Action`.`begDate` AS `Datapost`,
                      Client.lastName,
                      Client.firstName,
                      Client.patrName,
                      Event.externalId,
                      OrgStructure.Address,
                      rbResult.name as result
                    FROM `Action`
                     INNER JOIN `ActionProperty`
                        ON `Action`.`id` = `ActionProperty`.`action_id` AND `Action`.`actionType_id` = 118
                    INNER  JOIN `ActionProperty_OrgStructure`
                        ON ActionProperty.id = `ActionProperty_OrgStructure`.`id` AND `ActionProperty`.`type_id` = 36081
                     INNER JOIN OrgStructure
                        ON ActionProperty_OrgStructure.value = OrgStructure.id
                      INNER JOIN Event
                      ON Event.id = Action.event_id
                      INNER JOIN rbResult
                      ON rbResult.id = Event.result_id AND rbResult.id IN(18, 38, 58, 69)
                      INNER JOIN Client
                      ON Client.id = Event.client_id
                    WHERE `Action`.`deleted` = 0
                    AND (Action.endDate >= '{} 08:00:00' AND Action.endDate <= '{} 07:59:59')
                    '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query)


class More_Then_21(object):

    def __init__(self):
        self.db_session = get_lpu_session()

    def get_more_then_21(self):
        query = '''
                    SELECT
                       Event.externalId,
                       Client.lastName,
                       Client.firstName,
                       Client.patrName,
                       Client.birthDate,
                       Event.setDate,
                       Action.begDate,
                       datediff(curdate(), Action.begDate) AS "Days",
                       OrgStructure.name AS "OrgStructureName"
                        FROM Action
                        INNER JOIN Event
                        ON Event.id = Action.event_id

                        INNER JOIN EventType
                          ON EventType.id = Event.eventType_id AND EventType.purpose_id = 8

                        INNER JOIN Client
                        ON Client.id = Event.client_id

                        INNER JOIN ActionProperty
                        ON Action.id = ActionProperty.action_id

                        INNER JOIN ActionProperty_HospitalBed
                        ON ActionProperty.id = ActionProperty_HospitalBed.id

                        INNER JOIN OrgStructure_HospitalBed
                        ON ActionProperty_HospitalBed.value = OrgStructure_HospitalBed.id

                        INNER JOIN OrgStructure
                        ON OrgStructure_HospitalBed.master_id = OrgStructure.id

                        WHERE
                          Action.deleted = 0
                          AND Event.deleted = 0
                          AND (Action.begDate <= curdate()
                          AND Action.endDate IS NULL)
                          AND (datediff(curdate(), Action.begDate) >= 21)
                        ORDER BY
                          OrgStructure_HospitalBed.master_id
                '''
        return self.db_session.execute(query)


class AnaesthesiaAmount(object):

    def __init__(self):
        self.db_session = get_lpu_session()

    def get_anaesthesia_amount(self, start, end):
        query = '''
                    SELECT
                       Anesteziolog_zakl.value AS "zakl",
                       Anesteziolog_oper.value AS "oper",
                       Anesteziolog_status.value AS "status",
                       count(Action.id) AS "amount"
                    FROM `Action`
                    INNER JOIN Event
                    ON Event.id = `Action`.event_id AND `Action`.deleted = 0 AND Action.actionType_id = 1480
                    AND (`Action`.endDate BETWEEN '{} 00:00:00' AND '{} 23:59:59')

                    LEFT JOIN Anesteziolog_zakl
                    ON Anesteziolog_zakl.id = Action.id

                    LEFT JOIN Anesteziolog_oper
                    ON Anesteziolog_oper.id = Action.id

                    LEFT JOIN Anesteziolog_status
                    ON Anesteziolog_status.id = Action.id

                    GROUP BY

                      Anesteziolog_zakl.value
                    , Anesteziolog_oper.value
                '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        return self.db_session.execute(query)


class List_Of_Operations(object):

    def __init__(self):
        self.db_session = get_lpu_session()

    def get_list_of_operations(self, start, end):
        query = '''
                    SELECT
                          Client.lastName,
                          Client.firstName,
                          Client.patrName,
                          Event.externalId,
                          Event.setDate,
                          VYPISKI.`Data vypiski` AS "DataVypiski",
                          name_oper.name AS "operName",
                          Cel_oper.Cel AS "Cel",
                          Obl_oper.Oblast AS "Oblast",
                          Type_oper.Type AS "operType",
                          ds_before_oper.dsbo AS "dsbo",
                          Action.begDate AS "begDate"

                    FROM Action

                    INNER JOIN Event
                    ON Action.event_id = Event.id AND Action.deleted=0

                    INNER JOIN Client
                    ON Client.id= Event.client_id

                    INNER JOIN name_oper
                    ON Action.id = name_oper.ID AND Action.deleted=0 AND (Action.begDate BETWEEN '{} 00:00:00'
                    AND '{} 23:59:59')

                    LEFT JOIN Cel_oper
                    ON Action.id = Cel_oper.ID

                    LEFT JOIN Obl_oper
                    ON Action.id = Obl_oper.ID

                    LEFT JOIN Type_oper
                    ON Action.id = Type_oper.ID

                    LEFT JOIN ds_before_oper
                    ON Action.id = ds_before_oper.ID

                    LEFT JOIN VYPISKI
                    ON Action.event_id = VYPISKI.Event_id

                '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        return self.db_session.execute(query)