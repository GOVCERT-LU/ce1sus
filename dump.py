# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 8, 2015
"""
import json
from os.path import dirname, abspath

from ce1sus.db.common.session import SessionManager
from ce1sus.depricated.brokers.oldbrokers import OldEventBroker, OldAttributeDefinitionsBroker, OldObjectDefinitionsBroker, OldUserBroker, OldGroupBroker, OldConfigBroker, OldHandlerBroker
from ce1sus.helpers.common.config import Configuration


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def dump_file(filename, brokerclass, connection):
  broker = brokerclass(connection)
  items = broker.get_all()
  dump_file = open(filename, 'w')
  for item in items:
    try:
      dump_file.write(json.dumps(item.to_dict()))
    except TypeError as error:
      raise error

    dump_file.write('\n')
  dump_file.close()

if __name__ == '__main__':

  basePath = dirname(abspath(__file__))
  # TODO change in case of need
  ce1susConfigFile = basePath + '/config/ce1sus_old.conf'
  config = Configuration(ce1susConfigFile)

  connector = SessionManager(config).connector
  directconnection = connector.get_direct_session()

  # create a dump for the events
  dump_file('events.txt', OldEventBroker, directconnection)

  # create a dump for the defintions
  # dump_file('attributedefinitions.txt', OldAttributeDefinitionsBroker, directconnection)
  # dump_file('objectdefinitions.txt', OldObjectDefinitionsBroker, directconnection)

  # create a dump for the users
  # dump_file('users.txt', OldUserBroker, directconnection)

  # create a dump for the groups
  # dump_file('groups.txt', OldGroupBroker, directconnection)

  # dump_file('ce1susconf.txt', OldConfigBroker, directconnection)

  # dump_file('handlers.txt', OldHandlerBroker, directconnection)

  # dumps are done beginning of Migration

  directconnection.close()
