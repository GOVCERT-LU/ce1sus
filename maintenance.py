# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 11, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from optparse import OptionParser
from dagr.db.session import SessionManager
from ce1sus.brokers.definition.attributedefinitionbroker import AttributeDefinitionBroker
from ce1sus.brokers.relationbroker import RelationBroker
from dagr.db.broker import BrokerException
import os
from dagr.helpers.config import Configuration
from ce1sus.brokers.ce1susbroker import Ce1susBroker
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.controllers.event.event import get_all_attribtues_from_event


class MaintenanceException(Exception):
  pass


class Maintenance(object):
  """
  Maintenance class
  """

  def __init__(self, config):
    self.config = config
    self.connector = SessionManager(config).connector
    directconnection = self.connector.get_direct_session()
    self.def_attr_broker = AttributeDefinitionBroker(directconnection)
    self.relation_broker = RelationBroker(directconnection)
    self.ce1sus_broker = Ce1susBroker(directconnection)
    self.event_broker = EventBroker(directconnection)

  def rebuild_relations(self, verbose=False):
    definitions = self.get_relationable_definitions(verbose)
    self.removing_obsolete_relations(definitions, verbose, False)
    self.regenerate_relations(definitions, verbose, False)
    self.relation_broker.do_commit(True)
    print 'Done.'

  def removing_obsolete_relations(self, definitions, verbose=False, commit=False):
    try:
      if verbose:
        print 'Removing obsolete relations'
      def_ids = list()
      for definition in definitions:
        def_ids.append(definition.identifier)
      # get all relations not in the definitions
      relations = self.relation_broker.get_all_rel_with_not_def_list(def_ids)
      if verbose:
        print 'Found {0} obsolete relations'.format(len(relations))
      # remove all definitions
      if relations:
        if verbose:
          print 'Removing obsolete relations'
        for relation in relations:
          self.relation_broker.remove_by_id(relation.identifier, False)
        self.relation_broker.do_commit(commit)
      else:
        if verbose:
          print 'No obsolete relation found'
    except BrokerException as error:
      raise MaintenanceException(error)

  def get_relationable_definitions(self, verbose=False):
    try:
      if verbose:
        print 'Getting relationable definitions'
      definitions = self.def_attr_broker.get_all_relationable_definitions()
      if verbose:
        print 'Found {0} relationable definitions'.format(len(definitions))
      return definitions
    except BrokerException as error:
      raise MaintenanceException(error)

  def regenerate_relations(self, definitions, verbose=False, commit=False):
    try:
      if verbose:
        print 'Regenerating definitions'
      events = self.event_broker.get_all()
      if verbose:
        print 'Found {0} events'.format(len(events))
      if events:
        for event in events:
          attributes = get_all_attribtues_from_event(event)
          self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
        self.relation_broker.do_commit(commit)
      else:
        if verbose:
          print 'No event found.'
    except BrokerException as error:
      raise MaintenanceException(error)


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('-r', dest='rebuild_opt', action='store_true', default=False,
                    help='Rebuild relations according to the definitions')
  parser.add_option('-v', dest='verbose_opt', action='store_true', default=False,
                    help='Verbose')

  (options, args) = parser.parse_args()

  basePath = os.path.dirname(os.path.abspath(__file__))
  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  maintenance = Maintenance(config)

  if options.rebuild_opt:
    maintenance.rebuild_relations(options.verbose_opt)
  else:
    parser.print_help()
