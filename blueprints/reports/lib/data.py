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
                    AND Person.id = {}
                      AND (`Event`.`setDate` BETWEEN '{} 00:00:00' AND '{} 23:59:59') AND `Event`.`deleted` = 0
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
                    AND Person.id = {}
                      AND (`Event`.`setDate` BETWEEN '{} 00:00:00' AND '{} 23:59:59') AND `Event`.`deleted` = 0
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
                    AND Person.id = {}
                      AND (`Event`.`setDate` BETWEEN '{} 00:00:00' AND '{} 23:59:59') AND `Event`.`deleted` = 0
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
                    AND Person.id = {}
                      AND (`Event`.`setDate` BETWEEN '{} 00:00:00' AND '{} 23:59:59') AND `Event`.`deleted` = 0
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
                    AND Person.id = {}
                      AND (`Event`.`setDate` BETWEEN '{} 00:00:00' AND '{} 23:59:59') AND `Event`.`deleted` = 0
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
                    AND Person.id = {}
                    AND `ActionType`.`group_id` = 101
                    AND (`Event`.`setDate` BETWEEN '{} 00:00:00' AND '{} 23:59:59') AND `Action`.`deleted` = 0
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