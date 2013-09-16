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
                    AND (Action.endDate >= '{}' AND Action.endDate <= '{}')
                    '''.format('{} 08:00:00'.format(start.strftime('%d.%m.%Y')),
                               '{} 07:59:59'.format(end.strftime('%d.%m.%Y')))

        priemn_postup = self.db_session.execute(query)
        return priemn_postup