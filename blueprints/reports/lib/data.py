# -*- coding: utf-8 -*-
import os
import exceptions
from datetime import date, timedelta, datetime

from ..app import module, _config
from flask.ext.sqlalchemy import SQLAlchemy
from ..utils import get_lpu_session


class Statistics(object):

    def __init__(self):
        self.db_session = get_lpu_session()
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)

    def __del__(self):
        self.db_session.close()

    def get_patients(self):
        query = '''
                    SELECT count(`Action`.`id`) as number
                           FROM `Action`
                           INNER JOIN Event
                           ON Event.id = Action.event_id
                           WHERE `Action`.`deleted` = 0 AND `Action`.`actionType_id` = 113
                           and Event.deleted = 0 and `Action`.endDate is NULL;
        '''
        return self.db_session.execute(query).first()

    def get_patients_orgStruct(self):
        query = '''
                    SELECT count(`Action`.`id`) as number, OrgStructure.id, OrgStructure.name
                    FROM `Action`
                    INNER JOIN Event
                    ON Event.id = Action.event_id
                    INNER JOIN `ActionProperty`
                    ON `Action`.`id` = `ActionProperty`.`action_id`
                    INNER  JOIN `ActionProperty_OrgStructure`
                    ON ActionProperty.id = `ActionProperty_OrgStructure`.`id` AND `ActionProperty`.`type_id` = 7021
                    INNER JOIN OrgStructure
                    ON ActionProperty_OrgStructure.value = OrgStructure.id
                    WHERE `Action`.`deleted` = 0 AND `Action`.`actionType_id` = 113
                    and Event.deleted = 0 and `Action`.endDate is NULL
                    group by OrgStructure.id
                    ORDER BY OrgStructure.name;
        '''
        return self.db_session.execute(query)

    def get_postup(self):
        query = u'''
                    SELECT
                        count(Action.id) as number
                    FROM
                        Action
                            INNER JOIN
                        ActionType ON Action.`actionType_id` = ActionType.`id`
                            INNER JOIN
                        ActionProperty ON Action.`id` = ActionProperty.`action_id`
                            INNER JOIN
                        ActionProperty_HospitalBed ON ActionProperty.`id` = ActionProperty_HospitalBed.`id`
                            INNER JOIN
                        Event ON Action.`event_id` = Event.`id`
                            INNER JOIN
                        (SELECT
                            Action.id, ActionProperty_HospitalBedProfile.value
                        FROM
                            Action
                        INNER JOIN ActionType ON Action.`actionType_id` = ActionType.`id`
                        INNER JOIN ActionProperty ON Action.`id` = ActionProperty.`action_id`
                        INNER JOIN ActionPropertyType ON ActionPropertyType.`id` = ActionProperty.`type_id`
                        INNER JOIN ActionProperty_HospitalBedProfile ON ActionProperty.`id` = ActionProperty_HospitalBedProfile.`id`
                        INNER JOIN rbHospitalBedProfile ON ActionProperty_HospitalBedProfile.`value` = rbHospitalBedProfile.`id`
                        WHERE
                            (ActionType.`flatCode` = 'moving')
                                AND (ActionPropertyType.`code` = 'hospitalBedProfile')
                                AND ((Action.`begDate` >= '{1}' - INTERVAL 1 DAY)
                                AND (Action.`begDate` <= '{1}'))) sz ON Action.id = sz.id
                    WHERE
                        ((Action.`begDate` >= '{1}' - INTERVAL 1 DAY)
                            AND (Action.`begDate` <= '{1}'))
                            AND (ActionType.`flatCode` = 'moving')
                            AND (Action.`deleted` = 0)
                            AND (Event.`deleted` = 0)
                            AND (ActionProperty.`deleted` = 0)
                            AND (Action.id IN (SELECT
                                id
                            FROM
                                (SELECT
                                    Action.id, min(Action.id)
                                FROM
                                    Action
                                JOIN ActionType ON Action.actionType_id = ActionType.id
                                WHERE
                                    ActionType.flatCode = 'moving'
                                        AND Action.begDate IS NOT NULL
                                        AND Action.deleted = 0
                                GROUP BY event_id) A))
                    '''.format(self.yesterday.strftime('%Y-%m-%d'), self.today.strftime('%Y-%m-%d'))
        return self.db_session.execute(query).first()

    def get_vypis(self):
        query = u'''
                    SELECT
                        count(Action.id) as number
                    FROM
                        Action
                            INNER JOIN
                        ActionType ON Action.`actionType_id` = ActionType.`id`
                            INNER JOIN
                        ActionProperty ON Action.`id` = ActionProperty.`action_id`
                            INNER JOIN
                        ActionProperty_HospitalBed ON ActionProperty.`id` = ActionProperty_HospitalBed.`id`
                            INNER JOIN
                        Event ON Action.`event_id` = Event.`id`
                    WHERE
                        ((Action.`endDate` >= '{1}' - INTERVAL 1 DAY)
                            AND (Action.`endDate` <= '{1}'))
                            AND (ActionType.`flatCode` = 'moving')
                            AND (Action.`deleted` = 0)
                            AND (Event.`deleted` = 0)
                            AND (ActionProperty.`deleted` = 0)
                            AND (Action.id IN (SELECT
                                id
                            FROM
                                (SELECT
                                    max(Action.id) id
                                FROM
                                    Action
                                JOIN ActionType ON Action.actionType_id = ActionType.id
                                WHERE
                                    ActionType.flatCode = 'moving'
                                        AND Action.begDate IS NOT NULL
                                        AND Action.deleted = 0
                                GROUP BY event_id) A))
                            AND (Action.event_id in (select distinct
                                Event.id
                            from
                                Action
                                    INNER JOIN
                                ActionType ON Action.actionType_id = ActionType.id
                                    INNER JOIN
                                ActionProperty ON ActionProperty.action_id = Action.id
                                    INNER JOIN
                                Event ON Event.id = Action.event_id
                                    inner join
                                ActionProperty_String aps ON ActionProperty.id = aps.id
                            where
                                ActionType.flatCode = 'leaved'))
                            AND Action.event_id NOT IN (SELECT
                                e.id
                            FROM
                                Event e
                                    INNER JOIN
                                rbResult ON rbResult.id = e.result_id
                                    AND rbResult.name = 'умер')
                    '''.format(self.yesterday.strftime('%Y-%m-%d'), self.today.strftime('%Y-%m-%d'))

        return self.db_session.execute(query).first()


class Patients_Process(object):

    def __init__(self):
        self.db_session = get_lpu_session()

    def __del__(self):
        self.db_session.close()

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
                    AND (Action.endDate BETWEEN '{0} 08:00:00' AND '{1} 07:59:59')
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
                    AND (VYPISKI.`Data vypiski` BETWEEN '{0} 08:00:00' AND '{1} 07:59:59')
                    '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query)

    def get_priemn_perevod(self, start, end):
        query = '''
                    SELECT
                        `Action`.`begDate` AS `Datapost`,
                        Client.lastName,
                        Client.firstName,
                        Client.patrName,
                        Event.externalId,
                        OrgStructure.Address,
                        Pac_prb.prb AS prb
                    FROM
                        `Action`
                            INNER JOIN
                        `ActionProperty` ON `Action`.`id` = `ActionProperty`.`action_id`
                            AND `Action`.`actionType_id` = 113
                            INNER JOIN
                        `ActionProperty_OrgStructure` ON ActionProperty.id = `ActionProperty_OrgStructure`.`id`
                            AND `ActionProperty`.`type_id` = 14370
                            INNER JOIN
                        OrgStructure ON ActionProperty_OrgStructure.value = OrgStructure.id
                            AND OrgStructure.id <> 28
                            INNER JOIN
                        Pac_prb ON Pac_prb.id = Action.id
                            INNER JOIN
                        Event ON Event.id = Action.event_id
                            INNER JOIN
                        Client ON Client.id = Event.client_id
                    WHERE
                        `Action`.`deleted` = 0
                            AND ((Action.begDate >= CONCAT('{0}', ' 08:00:00')
                            AND Action.begDate <= CONCAT('{1}', ' 07:59:59')))
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
                    AND (Action.endDate >= '{0} 08:00:00' AND Action.endDate <= '{1} 07:59:59')
                    '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query)


class More_Then_21(object):

    def __init__(self):
        self.db_session = get_lpu_session()

    def __del__(self):
        self.db_session.close()

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

    def __del__(self):
        self.db_session.close()

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
                    AND (`Action`.endDate BETWEEN '{0} 00:00:00' AND '{1} 23:59:59')

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

    def __del__(self):
        self.db_session.close()

    def get_list_of_operations(self, start, end):
        query = u'''
                    SELECT
                        Client.lastName,
                        Client.firstName,
                        Client.patrName,
                        Client.birthDate,
                        if(Client.sex = 1, 'М', 'Ж') AS Pol,
                        Event.setDate AS Data_otkrytiya,
                        Event.externalId,
                        Action.begDate AS Data_vremya_protokola,
                        poN.n AS Nomer_operacii,
                        poname.name AS Naimenovanie_operacii,
                        mkbd.mkb AS mkb,
                        ekstr.ekstr,
                        cel.cel AS Cel_operacii,
                        type.type AS Tip_operacii,
                        profile.profile AS Profil_operacii,
                        pobl.obl AS Oblast_operacii,
                        poblgo.poblgo AS Oblast_oper_god_ot4et,
                        zno.zno AS po_povodu_zno,
                        dsdo.ds AS ds_do_operacii,
                        mo.mo AS mo,
                        ina.ina,
                        dsafter.ds AS ds_posle_operacii,
                        morf.morf,
                        osl.osl,
                        rbFinance.name AS Isto4nik_finans
                    FROM
                        `Action`
                            INNER JOIN
                        Event ON Event.id = `Action`.event_id
                            AND `Action`.actionType_id = 127
                            AND (Action.begDate BETWEEN CONCAT('{0}', ' 08:00:00') AND CONCAT('{1}', ' 07:59:59'))
                            INNER JOIN
                        EventType ON EventType.id = Event.eventType_id
                            INNER JOIN
                        rbFinance ON rbFinance.id = EventType.finance_id
                            INNER JOIN
                        Client ON Client.id = Event.client_id
                            AND client_id <> 18
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_Integer.value AS N
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 4666
                        JOIN ActionProperty_Integer ON ActionProperty.id = ActionProperty_Integer.id) AS poN ON poN.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS cel
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 1600443
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS cel ON cel.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS type
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 1600444
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS type ON type.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS name
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 20692
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS poname ON poname.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS profile
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 3912090
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS profile ON profile.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS obl
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 10489
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS pobl ON pobl.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS poblgo
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 3912091
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS poblgo ON poblgo.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS zno
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 3912093
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS zno ON zno.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS ds
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 1600445
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS dsdo ON dsdo.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS ds
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 1748
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS dsafter ON dsafter.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, MKB.DiagID AS mkb
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 3912089
                        JOIN ActionProperty_MKB ON ActionProperty.id = ActionProperty_MKB.id
                        INNER JOIN MKB ON MKB.id = ActionProperty_MKB.value) AS mkbd ON mkbd.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS ekstr
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 1600761
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS ekstr ON ekstr.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS mo
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 6527
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS mo ON mo.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS morf
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 3913452
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS morf ON morf.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS ina
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 1600446
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS ina ON ina.id = `Action`.id
                            LEFT JOIN
                        (SELECT
                            Action.id, ActionProperty_String.value AS osl
                        FROM
                            Action
                        JOIN ActionProperty ON Action.id = ActionProperty.action_id
                            AND Action.deleted = 0
                        JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            AND ActionPropertyType.id = 1800
                        JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id) AS osl ON osl.id = `Action`.id
                    WHERE
                        `Action`.deleted = 0
                            AND Event.deleted = 0
                    ORDER BY setDate;
                '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        return self.db_session.execute(query)


class Policlinic(object):

    def __init__(self):
        self.db_session = get_lpu_session()
        self.db_session2 = get_lpu_session()

    def __del__(self):
        self.db_session.close()
        self.db_session2.close()

    def __get_t21005oms(self, id, start, end):
        query = '''SELECT count(*) AS `number`
                         , `rbSpeciality`.`name` AS `speciality`
                         , `Event`.`execPerson_id` AS `execPerson_id`
                    FROM
                      ((((`Event`
                    JOIN `Client`
                    ON (((`Client`.`id` = `Event`.`client_id`)
                    AND (((year(`Event`.`setDate`) - year(`Client`.`birthDate`)) - (date_format(curdate(), '%%m%%d') < date_format(`Client`.`birthDate`, '%%m%%d'))) < 18))))
                    JOIN `Person`
                    ON ((`Person`.`id` = `Event`.`execPerson_id`)))
                    JOIN `EventType`
                    ON ((`Event`.`eventType_id` = `EventType`.`id`)))
                    JOIN `rbSpeciality`
                    ON ((`Person`.`speciality_id` = `rbSpeciality`.`id`)))
                    WHERE
                      `Event`.`eventType_id` = 109
                    AND Person.id = {0}
                      AND (`Event`.`setDate` BETWEEN '{1} 00:00:00' AND '{2} 23:59:59') AND `Event`.`deleted` = 0
                    GROUP BY
                      `rbSpeciality`.`name`
                    , `Person`.`lastName`
                    ORDER BY
                      `rbSpeciality`.`name`
                    '''.format(id, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query).first()

    def __get_polip(self, id, start, end):
        query = '''SELECT count(*) AS `number`
                         , `rbSpeciality`.`name` AS `speciality`
                         , `Event`.`execPerson_id` AS `execPerson_id`
                    FROM
                      ((((`Event`
                    JOIN `Client`
                    ON ((`Client`.`id` = `Event`.`client_id`)))
                    JOIN `Person`
                    ON ((`Person`.`id` = `Event`.`execPerson_id`)))
                    JOIN `EventType`
                    ON ((`Event`.`eventType_id` = `EventType`.`id`)))
                    JOIN `rbSpeciality`
                    ON ((`Person`.`speciality_id` = `rbSpeciality`.`id`)))
                    WHERE
                      `Event`.`eventType_id` = 70
                    AND Person.id = {0}
                      AND (`Event`.`setDate` BETWEEN '{1} 00:00:00' AND '{2} 23:59:59') AND `Event`.`deleted` = 0
                    GROUP BY
                      `rbSpeciality`.`name`
                    , `Person`.`lastName`
                    ORDER BY
                      `rbSpeciality`.`name`
                    '''.format(id, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query).first()

    def __get_polib(self, id, start, end):
        query = '''SELECT count(*) AS `number`
                         , `rbSpeciality`.`name` AS `speciality`
                         , `Event`.`execPerson_id` AS `execPerson_id`
                    FROM
                      ((((`Event`
                    JOIN `Client`
                    ON ((`Client`.`id` = `Event`.`client_id`)))
                    JOIN `Person`
                    ON ((`Person`.`id` = `Event`.`execPerson_id`)))
                    JOIN `EventType`
                    ON ((`Event`.`eventType_id` = `EventType`.`id`)))
                    JOIN `rbSpeciality`
                    ON ((`Person`.`speciality_id` = `rbSpeciality`.`id`)))
                    WHERE
                      `Event`.`eventType_id` = 61
                    AND Person.id = {0}
                      AND (`Event`.`setDate` BETWEEN '{1} 00:00:00' AND '{2} 23:59:59') AND `Event`.`deleted` = 0
                    GROUP BY
                      `rbSpeciality`.`name`
                    , `Person`.`lastName`
                    ORDER BY
                      `rbSpeciality`.`name`
                    '''.format(id, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query).first()

    def __get_poliz(self, id, start, end):
        query = '''SELECT count(*) AS `number`
                         , `rbSpeciality`.`name` AS `speciality`
                         , `Event`.`execPerson_id` AS `execPerson_id`
                    FROM
                      ((((`Event`
                    JOIN `Client`
                    ON ((`Client`.`id` = `Event`.`client_id`)))
                    JOIN `Person`
                    ON ((`Person`.`id` = `Event`.`execPerson_id`)))
                    JOIN `EventType`
                    ON ((`Event`.`eventType_id` = `EventType`.`id`)))
                    JOIN `rbSpeciality`
                    ON ((`Person`.`speciality_id` = `rbSpeciality`.`id`)))
                    WHERE
                      `Event`.`eventType_id` = 65
                    AND Person.id = {0}
                      AND (`Event`.`setDate` BETWEEN '{1} 00:00:00' AND '{2} 23:59:59') AND `Event`.`deleted` = 0
                    GROUP BY
                      `rbSpeciality`.`name`
                    , `Person`.`lastName`
                    ORDER BY
                      `rbSpeciality`.`name`
                    '''.format(id, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query).first()

    def __get_zaochb(self, id, start, end):
        query = '''SELECT count(*) AS `number`
                         , `rbSpeciality`.`name` AS `speciality`
                         , `Event`.`execPerson_id` AS `execPerson_id`
                    FROM
                      ((((`Event`
                    JOIN `Client`
                    ON ((`Client`.`id` = `Event`.`client_id`)))
                    JOIN `Person`
                    ON ((`Person`.`id` = `Event`.`execPerson_id`)))
                    JOIN `EventType`
                    ON ((`Event`.`eventType_id` = `EventType`.`id`)))
                    JOIN `rbSpeciality`
                    ON ((`Person`.`speciality_id` = `rbSpeciality`.`id`)))
                    WHERE
                      `Event`.`eventType_id` = 66
                    AND Person.id = {0}
                      AND (`Event`.`setDate` BETWEEN '{1} 00:00:00' AND '{2} 23:59:59') AND `Event`.`deleted` = 0
                    GROUP BY
                      `rbSpeciality`.`name`
                    , `Person`.`lastName`
                    ORDER BY
                      `rbSpeciality`.`name`
                    '''.format(id, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        return self.db_session.execute(query).first()

    def __get_kskons(self, id, start, end):
        query = '''SELECT count(*) AS `number`
                         , `rbSpeciality`.`name` AS `speciality`
                         , `Action`.`person_id` AS `person_id`
                    FROM
                      ((((((`Event`
                    JOIN `EventType`
                    ON ((`Event`.`eventType_id` = `EventType`.`id`)))
                    JOIN `Action`
                    ON ((`Event`.`id` = `Action`.`event_id`)))
                    JOIN `ActionType`
                    ON ((`Action`.`actionType_id` = `ActionType`.`id`)))
                    JOIN `Client`
                    ON ((`Client`.`id` = `Event`.`client_id`)))
                    LEFT JOIN `Person`
                    ON ((`Person`.`id` = `Action`.`person_id`)))
                    JOIN `rbSpeciality`
                    ON ((`rbSpeciality`.`id` = `Person`.`speciality_id`)))
                    WHERE
                      `EventType`.`purpose_id` = 8
                    AND Person.id = {0}
                    AND `ActionType`.`group_id` = 101
                    AND (`Event`.`setDate` BETWEEN '{1} 00:00:00' AND '{2} 23:59:59') AND `Action`.`deleted` = 0
                    GROUP BY
                      `rbSpeciality`.`name`
                    , `Person`.`lastName`
                    '''.format(id, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        return self.db_session.execute(query).first()

    def get_personpoly(self, start, end):
        query = '''SELECT
                          Person.id,
                          Person.lastName,
                          Person.firstName,
                          rbSpeciality.name as speciality

                    FROM
                      Person

                    INNER JOIN rbSpeciality
                    ON rbSpeciality.id = Person.speciality_id
                    AND (Person.orgStructure_id = 42 OR Person.orgStructure_id = 45 OR Person.id IN (216,457))

                    WHERE Person.speciality_id NOT IN (1,29,30,31,32,66,67,83)

                    ORDER BY Person.lastName'''
        result = self.db_session2.execute(query)
        data = list()
        for person in result:
            data.append(dict(person=person,
                             oms=self.__get_t21005oms(person.id, start, end),
                             polip=self.__get_polip(person.id, start, end),
                             polib=self.__get_polib(person.id, start, end),
                             poliz=self.__get_poliz(person.id, start, end),
                             zaochb=self.__get_zaochb(person.id, start, end),
                             kskons=self.__get_kskons(person.id, start, end),))
        return data


class Discharged_Patients(object):

    def __init__(self):
        self.db_session = get_lpu_session()

    def __del__(self):
        self.db_session.close()

    def get_vypis(self, start, end):
        query = '''SELECT Action.begDate
                     , ActionType.name AS document
                     , Event.externalId
                     , Event.setDate
                     , Client.lastName
                     , Client.firstName
                     , Client.patrName
                     , Client.birthDate
                     , otd_postup_from_dvizh.otd as otd
                     , DS_osnk_zak_epic.value AS primary_kd
                     , DS_zak_epic.DiagID
                     , DS_zak_epic.DiagName
                     , kladr_obl.NAME AS obl
                     , kladr_rai.NAME AS rai
                     , kladr.KLADR.SOCR
                     , kladr.infisREGION.NAME AS infisREGION
                     , kladr.KLADR.NAME AS city
                     , kladr.STREET.NAME AS street
                     , AddressHouse.number AS house
                     , Address.flat
                     , Adr.freeInput

                FROM
                  Action

                INNER JOIN ActionType
                ON ActionType.id = Action.actionType_id AND Action.actionType_id = 118 AND `Action`.deleted = 0
                AND Action.endDate BETWEEN '{0}' AND '{1}'

                INNER JOIN Event
                ON Event.id = Action.event_id

                INNER JOIN Client
                ON Client.id = Event.client_id

                LEFT JOIN otd_postup_from_dvizh
                  ON otd_postup_from_dvizh.EventID = Event.id AND date(otd_postup_from_dvizh.begDate) = date(Event.setDate)

                LEFT JOIN DS_osnk_zak_epic
                ON Event.id = DS_osnk_zak_epic.event_id

                LEFT JOIN DS_zak_epic
                ON Event.id = DS_zak_epic.event_id

                INNER JOIN ClientAddress AS Adr
                ON (Adr.client_id = Client.id AND Adr.id IN (SELECT max(Tmp.id)
                                                                      FROM
                                                                        ClientAddress AS Tmp
                                                                      WHERE
                                                                        Tmp.deleted = 0
                                                                        AND type = '0'
                                                                      GROUP BY
                                                                        client_id))
                LEFT JOIN Address
                ON Address.id = Adr.address_id
                LEFT JOIN AddressHouse
                ON AddressHouse.id = Address.house_id
                LEFT JOIN kladr.KLADR
                ON kladr.KLADR.Code = AddressHouse.KLADRCode
                LEFT JOIN kladr.infisREGION
                ON kladr.infisREGION.KLADR = kladr.KLADR.CODE

                LEFT JOIN kladr_obl
                ON kladr_obl.id = AddressHouse.id

                LEFT JOIN kladr_rai
                ON kladr_rai.id = AddressHouse.id

                LEFT JOIN kladr.infisAREA
                ON kladr.infisAREA.CODE = kladr.infisREGION.AREA
                LEFT JOIN kladr.STREET
                ON AddressHouse.KLADRStreetCode = kladr.STREET.code
                    '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        return self.db_session.execute(query)


class Sickness_Rate_Blocks(object):

    def __init__(self):
        self.db_session = get_lpu_session()

    def __del__(self):
        self.db_session.close()

    def get_sickness_rate_blocks(self, start, end):
        query = '''
                    SELECT
                          MKB.BlockName,
                          MKB.BlockID,
                          count(MKB) AS amount
                    FROM
                      Event

                    INNER JOIN Client
                    ON Client.id = Event.client_id

                    INNER JOIN EventType
                    ON EventType.id = Event.eventType_id AND EventType.purpose_id = 8

                    INNER JOIN Person
                    ON Person.id = Event.execPerson_id

                    INNER JOIN rbSpeciality
                    ON rbSpeciality.id = Person.speciality_id

                    INNER JOIN Diagnostic
                    ON Diagnostic.event_id = Event.id

                    INNER JOIN Diagnosis
                    ON Diagnostic.diagnosis_id = Diagnosis.id

                    INNER JOIN MKB
                    ON MKB.DiagID = Diagnosis.MKB

                    WHERE
                      Event.deleted = 0
                      AND Event.execDate BETWEEN ('{0} 00:00:00' AND '{1} 23:59:59')
                      AND Diagnosis.deleted = 0
                      AND Diagnostic.deleted = 0
                      AND Person.deleted = 0

                    GROUP BY

                      MKB.BlockName

                    ORDER BY
                      MKB.BlockName
                '''.format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        return self.db_session.execute(query)


class Paid_Patients(object):

    def __init__(self):
        self.db_session = get_lpu_session()

    def __del__(self):
        self.db_session.close()

    def get_platn_ks(self):
        query = '''SELECT
                      Client.lastName,
                      Client.firstName,
                      Client.patrName,
                      Event.externalId,
                      Event.setDate,
                      Pac_prb.name AS otd,
                     rbFinance.name AS finance_source,
                      EventType.name AS event_type

                      FROM Event

                    INNER JOIN Client
                    ON Client.id = Event.client_id AND Event.deleted =0

                     INNER JOIN Pac_prb
                     ON Pac_prb.Evid = Event.id

                       INNER JOIN EventType
                      ON EventType.id = Event.eventType_id AND EventType.finance_id IN (4,9)

                      LEFT
                      JOIN rbFinance
                      ON rbFinance.id = EventType.finance_id

                      WHERE Event.execDate IS NULL

                      ORDER
                       BY Pac_prb.Prb,Client.lastName,rbFinance.name'''
        return self.db_session.execute(query)


class Sickness_Rate_Diagnosis(object):

    def __init__(self):
        self.db_session = get_lpu_session()

    def __del__(self):
        self.db_session.close()

    def get_vypds(self, diagnosis, start, end):
        query = u'''SELECT Client.lastName
                               , Client.firstName
                              ,  Client.patrName
                              , DS_zak_epic.DiagID
                         , otd_vypis_from_dvizh.NAME as otd_vypis
                         , Event.externalid
                         , date(Event.setDate) as setDate
                         , date(otd_vypis_from_dvizh.endDate) as endDate

                    FROM
                      DS_zak_epic

                    INNER JOIN Event
                    ON Event.id = DS_zak_epic.event_id AND DS_zak_epic.DiagID = '{0}'

                    INNER JOIN otd_vypis_from_dvizh
                    ON otd_vypis_from_dvizh.EventID = DS_zak_epic.event_id
                    AND (otd_vypis_from_dvizh.endDate BETWEEN '{1} 00:00:00' AND '{2} 23:59:59')

                    INNER JOIN Client
                    ON Client.id = Event.client_id
                '''.format(diagnosis, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        return self.db_session.execute(query)