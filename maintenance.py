# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 11, 2014
"""
from optparse import OptionParser
import os
from os.path import basename
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.definitions import AttributeDefinition, ObjectDefinition, AttributeHandler
from ce1sus.db.classes.mailtemplate import MailTemplate
from ce1sus.db.classes.object import Object
from ce1sus.db.classes.user import User
from ce1sus.db.common.session import SessionManager, Base
from ce1sus.helpers.common.config import Configuration
from apt_pkg import Group
from ce1sus.db.classes.relation import Relation
from ce1sus.db.classes.values import DateValue, StringValue, NumberValue, \
  TextValue
from ce1sus.db.classes.event import Event
from ce1sus.db.common.broker import BrokerException, NothingFoundException
from ce1sus.db.common.session import SessionManager
from ce1sus.handlers.base import HandlerBase
from ce1sus.helpers.common.config import Configuration
from ce1sus.helpers.common.objects import get_class
from ce1sus.db.classes.types import AttributeType, AttributeViewType


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


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
    # self.def_attr_broker = AttributeDefinitionBroker(directconnection)
    # self.def_obj_broker = ObjectDefinitionBroker(directconnection)
    # self.relation_broker = RelationBroker(directconnection)
    # self.ce1sus_broker = Ce1susBroker(directconnection)
    # self.event_broker = EventBroker(directconnection)

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
          attributes = None
          # attributes = get_all_attribtues_from_event(event)
          self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
        self.relation_broker.do_commit(commit)
      else:
        if verbose:
          print 'No event found.'
    except BrokerException as error:
      raise MaintenanceException(error)

  def recheck_definition_chksums(self, verbose=False):
    try:
      if verbose:
        print 'Checking definitions'
      # find all object definitions
      objects = self.def_obj_broker.get_all()
      not_matching_objs = list()
      for obj in objects:
        if obj.chksum != gen_obj_chksum(obj):
          not_matching_objs.append(obj)
      if verbose:
        print 'Found {0} not matching object chksums'.format(len(not_matching_objs))
      # fix checksums
      for not_matching_obj in not_matching_objs:
        not_matching_obj.chksum = gen_obj_chksum(not_matching_obj)
        self.def_obj_broker.update(not_matching_obj, False, True)
      self.def_obj_broker.do_commit(True)
      # find attribute chksums not matching the one stored
      attributes = self.def_attr_broker.get_all()
      not_matching_attrs = list()
      for attribute in attributes:
        if attribute.chksum != gen_attr_chksum(attribute):
          not_matching_attrs.append(attribute)
      if verbose:
        print 'Found {0} not matching object chksums'.format(len(not_matching_objs))
      # fix checksums
      for not_matching_attr in not_matching_attrs:
        not_matching_attr.chksum = gen_attr_chksum(not_matching_attr)
        self.def_attr_broker.update(not_matching_attr, False, True)
      self.def_attr_broker.do_commit(True)

    except BrokerException as error:
      raise MaintenanceException(error)

  def rebuild_event_relations(self, event_uuid, verbose):
    try:
      if verbose:
        print u'Rebuilding relations for event {0}'.format(event_uuid)
      # find event by uuid
      event = self.event_broker.get_by_uuid(event_uuid)
      attributes = None  # get_all_attribtues_from_event(event)
      self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      self.relation_broker.do_commit(True)
    except NothingFoundException as error:
      print error
    except BrokerException as error:
      raise MaintenanceException(error)

  def drop_relations(self, verbose):
    try:
      if verbose:
        print u'Truncate relations table'
      # get Table
      self.relation_broker.clear_relations_table()
      self.relation_broker.do_commit(True)
    except BrokerException as error:
      raise MaintenanceException(error)

  def add_handler(self, path):

    modulename = basename(path).replace('.py', '')
    classname = modulename.title().replace('handler', 'Handler')
    modulename = u'{0}'.format(modulename)
    # move to correct place
    print u'Adding handler {0}'.format(modulename)

    clazz = get_class(u'ce1sus.handlers.{0}'.format(modulename), classname)
    # check if class implements handler base
    instance = clazz()

    if not isinstance(instance, HandlerBase):
      # remove file

      raise Exception((u'{0} does not implement HandlerBase').format(classname))

    uuid = instance.get_uuid()
    description = instance.get_description()
    print "OK"
    attribute_handler = AttributeHandler()
    print "OK"
    attribute_handler.identifier = uuid
    attribute_handler.description = description
    attribute_handler.module_classname = u'{0}.{1}'.format(modulename, classname)
    # TODO: Use controller instead
    session = self.connector.get_direct_session().get_session()
    session.add(attribute_handler)
    session.commit()

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('-r', dest='rebuild_opt', action='store_true', default=False,
                    help='Rebuild relations according to the definitions')
  parser.add_option('-e', dest='event_uuid', type='string', default='',
                    help='Operation on a special event\nUse with option -r')
  parser.add_option('-d', dest='check_def_opt', action='store_true', default=False,
                    help='Check and correct definition checksums')
  parser.add_option('-v', dest='verbose_opt', action='store_true', default=False,
                    help='Verbose')
  parser.add_option('--drop_rel', dest='drop_rel', action='store_true', default=False,
                    help='Removes all existing relations')
  parser.add_option('--add-handler', dest='handler_file', type='string', default='',
                    help='Function to add a new handler')

  (options, args) = parser.parse_args()

  basePath = os.path.dirname(os.path.abspath(__file__))
  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  maintenance = Maintenance(config)

  if options.handler_file:
    maintenance.add_handler(options.handler_file)
  elif options.event_uuid and not options.rebuild_opt:
    print 'Option -e xxx has to be used with option -r.'
  else:
    if options.rebuild_opt:
      if options.event_uuid:
        maintenance.rebuild_event_relations(options.event_uuid, options.verbose_opt)
      else:
        maintenance.rebuild_relations(options.verbose_opt)
    elif options.check_def_opt:
      maintenance.recheck_definition_chksums(options.verbose_opt)
    elif options.drop_rel:
      maintenance.drop_relations(options.verbose_opt)
    else:
      parser.print_help()
