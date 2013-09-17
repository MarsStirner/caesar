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