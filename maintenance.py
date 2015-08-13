# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 11, 2014
"""
from ce1sus.helpers.common.config import Configuration
from ce1sus.helpers.common.objects import get_class
from ce1sus.helpers.common.strings import stringToDateTime
import json
from optparse import OptionParser
from os.path import dirname, abspath, isfile
import sys

from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController, gen_attr_chksum
from ce1sus.controllers.admin.conditions import ConditionController
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController, gen_obj_chksum
from ce1sus.controllers.admin.references import ReferencesController
from ce1sus.controllers.admin.user import UserController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.controllers.events.event import EventController
from ce1sus.controllers.events.relations import RelationController
from ce1sus.db.common.broker import BrokerException
from ce1sus.db.common.session import SessionManager
from ce1sus.handlers.base import HandlerBase


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
    self.session_manager = SessionManager(config)
    directconnection = self.session_manager.connector.get_direct_session()
    self.relation_controller = RelationController(config, directconnection)
    self.attribute_definition_controller = AttributeDefinitionController(config, directconnection)
    self.object_definition_controller = ObjectDefinitionController(config, directconnection)
    self.event_controller = EventController(config, directconnection)
    self.user_controller = UserController(config, directconnection)
    self.reference_controller = ReferencesController(config, directconnection)
    self.conditions_controller = ConditionController(config, directconnection)
    self.verbose = False

    # set maintenance user
    user_uuid = config.get('ce1sus', 'maintenaceuseruuid', None)
    if None:
      raise MaintenanceException('maintenaceuseruuid was not defined in config')
    try:
      self.user = self.user_controller.get_user_by_uuid(user_uuid)
    except ControllerNothingFoundException:
      raise MaintenanceException('Cannot find maintenance user with uuid {0}'.format(user_uuid))
    except ControllerException as error:
      raise MaintenanceException(error)

  def drop_relations(self, event_uuid=''):
    try:
      if event_uuid:
        if self.verbose:
          print 'Dropping relations for event {0}'.format(event_uuid)
        try:
          event = self.event_controller.get_event_by_uuid(event_uuid)
          self.relation_controller.remove_relations_for_event(event)
        except ControllerNothingFoundException:
          raise MaintenanceException('Event with uuid "{0}" cannot be found'.format(event_uuid))
      else:
        if self.verbose:
          print 'Dropping all relations'
        self.relation_controller.clear_relations_table()
    except ControllerException as error:
      raise MaintenanceException(error)

  def rebuild_relations(self, event_uuid='', from_date=''):
    try:
      if event_uuid:
        if self.verbose:
          print '(Re)Creation relations for event {0}'.format(event_uuid)
        try:
          event = self.event_controller.get_event_by_uuid(event_uuid)
          # drop relations for event
          self.relation_controller.remove_relations_for_event(event)
          flat_attributes = self.relation_controller.get_flat_attributes_for_event(event)
          self.relation_controller.generate_bulk_attributes_relations(event, flat_attributes, True)
        except ControllerNothingFoundException:
          raise MaintenanceException('Event with uuid "{0}" cannot be found'.format(event_uuid))
      else:

        # drop all relations
        self.relation_controller.clear_relations_table()

        if from_date:
          from_date = stringToDateTime(from_date)
          if self.verbose:
            print '(Re)Creation all relations for the events created from {0} on'.format(from_date)
          events = self.event_controller.get_all_from(from_date)
        else:
          if self.verbose:
            print '(Re)Creation all relations'
          events = self.event_controller.get_all()

        for event in events:
          if self.verbose:
            print 'Rebuild relations for event {0}'.format(event.identifier)
          flat_attributes = self.relation_controller.get_flat_attributes_for_event(event)
          self.relation_controller.generate_bulk_attributes_relations(event, flat_attributes, False)
        self.relation_controller.relation_broker.do_commit(True)
    except ControllerException as error:
      raise MaintenanceException(error)

  def fix_chksums(self):
    try:
      if self.verbose:
        print 'Checking object definitions'
      objects = self.object_definition_controller.get_all_object_definitions()
      not_matching = list()
      for obj in objects:
        if obj.chksum != gen_obj_chksum(obj):
          not_matching.append(obj)
      if self.verbose:
        print 'Found {0} not object matching object chksums'.format(len(not_matching))
      # fix checksums
      for not_matching_obj in not_matching:
        not_matching_obj.chksum = gen_obj_chksum(not_matching_obj)
        self.object_definition_controller.obj_def_broker.update(not_matching, False)

      if self.verbose:
        print 'Checking attribute definitions'
      # find attribute chksums not matching the one stored
      not_matching = list()
      objects = self.attribute_definition_controller.get_all_attribute_definitions()
      for obj in objects:
        if obj.chksum != gen_attr_chksum(obj):
          not_matching.append(obj)
      if self.verbose:
        print 'Found {0} attributes not matching object chksums'.format(len(not_matching))
      for not_matching_attr in not_matching:
        not_matching_attr.chksum = gen_attr_chksum(not_matching_attr)
        self.attribute_definition_controller.attr_def_broker.update(not_matching_attr, False)
      self.attribute_definition_controller.attr_def_broker.do_commit(True)

    except (ControllerException, BrokerException) as error:
      raise MaintenanceException(error)

  def register_handler(self, modulename, type_='attributes', classname=None):
    if not classname:
      classname = modulename.title().replace('handler', 'Handler')

    if self.verbose:
      print 'Registering handler {0}'.format(classname)

    modulename = u'{0}'.format(modulename)

    clazz = get_class(u'ce1sus.handlers.{0}.{1}'.format(type_, modulename), classname)
    instance = clazz()
    if isinstance(instance, HandlerBase):
      if self.verbose:
        print u'Adding handler {0}.{1}'.format(modulename, classname)
      uuid = instance.get_uuid()
      description = instance.get_description()
      if type_ == 'attributes':
        self.attribute_definition_controller.register_handler(uuid, u'{0}.{1}'.format(modulename, classname), description)
      elif type_ == 'references':
        self.reference_controller.register_handler(uuid, u'{0}.{1}'.format(modulename, classname), description)
      else:
        raise MaintenanceException('Type {0} for handlers is unknown'.format(type_))

      return uuid

        # TODO check if the required files are available
    else:
      raise MaintenanceException('Class {0}.{1} does not implement HandlerBase'.format(modulename, classname))

  def dump_definitions(self, dump_def, dump_dest):
    # check if file exists
    if isfile(dump_dest):
      raise MaintenanceException('File {0} is already existing'.format(dump_dest))

    dump = list()
    if dump_def == 'attributes':
      attributes = self.attribute_definition_controller.get_all_attribute_definitions()
      for attribute in attributes:
        dump.append(attribute.to_dict(True, True))
    elif dump_def == 'objects':
      obejcts = self.object_definition_controller.get_all_object_definitions()
      for obj in obejcts:
        dump.append(obj.to_dict(True, True))
    elif dump_def == 'references':
      ref_defs = self.reference_controller.get_reference_definitions_all()
      for ref_def in ref_defs:
        dump.append(ref_def.to_dict(True, True))
    elif dump_def == 'conditions':
      conditions = self.conditions_controller.get_all_conditions()
      for condition in conditions:
        dump.append(condition.to_dict(True, True))
    elif dump_def == 'types':
      types = self.attribute_definition_controller.get_all_types()
      for type_ in types:
        dump.append(type_.to_dict(True, True))
    else:
      raise MaintenanceException('No definition assigned to {0}. It can either be attributes or objects'.format(dump_def))

    # open an dump to file
    dump_file = open(dump_dest, 'w+')
    dump_file.write(json.dumps(dump))
    dump_file.close()

if __name__ == '__main__':
  basePath = dirname(abspath(__file__))

  parser = OptionParser()
  parser.add_option('--drop_rel', dest='drop_rel', action='store_true', default=False,
                    help='Removes all existing relations')
  parser.add_option('-v', dest='verbose_opt', action='store_true', default=False,
                    help='Verbose')
  parser.add_option('-e', dest='event_uuid', type='string', default='',
                    help='If set the operation applies only to this event.')
  parser.add_option('--fix_chksums', dest='check_def_opt', action='store_true', default=False,
                    help='Check and correct definition checksums')
  parser.add_option('-r', dest='rebuild_opt', action='store_true', default=False,
                    help='Rebuild relations according to the definitions')
  parser.add_option('--from', dest='from_datetime', type='string', default='',
                    help='Date for rebuilding the relations (YYYY-MM-DD)')
  parser.add_option('--reg-attr-handler', dest='attr_handler_reg_module', type='string', default='',
                    help='Function to register an installed attribute handler')
  parser.add_option('--reg-ref-handler', dest='ref_handler_reg_module', type='string', default='',
                    help='Function to register an installed references handler')
  parser.add_option('--class', dest='handler_class', type='string', default=None,
                    help='Class name of handler to register')
  parser.add_option('--dump', dest='dump_def', type='string', default=None,
                    help='[attributes|objects|references] Dumps specified definitions in json format. Must be used with --dest')
  parser.add_option('--dest', dest='dump_dest', type='string', default=None,
                    help='Destination file of the dump')
  (options, args) = parser.parse_args()

  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  try:
    maintenance = Maintenance(config)

    if options.verbose_opt:
      maintenance.verbose = True

    if options.drop_rel:
      # check if event was specified
      maintenance.drop_relations(options.event_uuid)
    elif options.check_def_opt:
      maintenance.fix_chksums()
    elif options.dump_def:
      if options.dump_dest:
        maintenance.dump_definitions(options.dump_def, options.dump_dest)
      else:
        print "No destination specified"
        parser.print_help()
        sys.exit(1)
    elif options.rebuild_opt:
      maintenance.rebuild_relations(options.event_uuid, options.from_datetime)
    elif options.attr_handler_reg_module:
      maintenance.register_handler(options.attr_handler_reg_module, 'attributes', options.handler_class)
    elif options.ref_handler_reg_module:
      maintenance.register_handler(options.ref_handler_reg_module, 'references', options.handler_class)
    else:
      parser.print_help()
      sys.exit(1)
    sys.exit(0)
  except MaintenanceException as error:
    if options.verbose_opt:
      raise MaintenanceException(error)
    else:
      print 'An error occurred: {0}'.format(error)
    print 'Exiting'
    sys.exit(1)
