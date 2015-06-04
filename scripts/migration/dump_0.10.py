# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 8, 2015
"""
import json
import sys
from os import makedirs
from os.path import dirname, abspath, exists, isdir, split
from optparse import OptionParser

basePath = dirname(abspath(__file__)) + '/../../'
sys.path.insert(0, '../../')

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
      print 'Dumping {0} {1}'.format(item.__class__.__name__, item.identifier)
      dump_file.write(json.dumps(item.to_dict()))
    except TypeError as error:
      raise error

    dump_file.write('\n')
  dump_file.close()

if __name__ == '__main__':

  parser = OptionParser()
  parser.add_option('--dest', dest='dump_dest', type='string', default=None,
                    help='Destination folder of the dumps')
  parser.add_option('-c', dest='config_file', type='string', default=None,
                    help='absolute path to the configuration file')
  (options, args) = parser.parse_args()

  if options.dump_dest is None:
    print 'Destination folder not set'
    parser.print_help()
    sys.exit(1)
  if options.config_file is None:
    print 'Configuration file not set'
    parser.print_help()
    sys.exit(1)

  ce1susConfigFile = options.config_file
  config = Configuration(ce1susConfigFile)

  connector = SessionManager(config).connector
  directconnection = connector.get_direct_session()

  dest_folder = options.dump_dest
  if not exists(dest_folder):
    makedirs(dest_folder)
  else:
    if not isdir(dest_folder):
      print '{0} is not a folder'.format(dest_folder)

  # create a dump for the events
  dump_file(dest_folder + '/events.txt', OldEventBroker, directconnection)

  # create a dump for the defintions
  dump_file(dest_folder + '/attributedefinitions.txt', OldAttributeDefinitionsBroker, directconnection)
  dump_file(dest_folder + '/objectdefinitions.txt', OldObjectDefinitionsBroker, directconnection)

  # create a dump for the users
  dump_file(dest_folder + '/users.txt', OldUserBroker, directconnection)

  # create a dump for the groups
  dump_file(dest_folder + '/groups.txt', OldGroupBroker, directconnection)

  dump_file(dest_folder + '/ce1susconf.txt', OldConfigBroker, directconnection)

  dump_file(dest_folder + '/handlers.txt', OldHandlerBroker, directconnection)

  # dumps are done beginning of Migration

  directconnection.close()
