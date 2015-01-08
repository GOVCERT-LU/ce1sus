# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 11, 2014
"""
from optparse import OptionParser
from os import remove
from os.path import basename, dirname, abspath, isfile
from shutil import copy, move

from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController, gen_attr_chksum
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController, gen_obj_chksum
from ce1sus.controllers.base import ControllerException
from ce1sus.controllers.events.event import EventController
from ce1sus.controllers.events.relations import RelationController
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.definitions import AttributeDefinition, ObjectDefinition, AttributeHandler
from ce1sus.db.classes.event import Event
from ce1sus.db.classes.mailtemplate import MailTemplate
from ce1sus.db.classes.object import Object
from ce1sus.db.classes.relation import Relation
from ce1sus.db.classes.types import AttributeType
from ce1sus.db.classes.user import User
from ce1sus.db.classes.values import DateValue, StringValue, NumberValue, TextValue
from ce1sus.db.common.session import SessionManager
from ce1sus.handlers.base import HandlerBase
from ce1sus.helpers.common.config import Configuration
from ce1sus.helpers.common.hash import fileHashMD5
from ce1sus.helpers.common.objects import get_class
from ce1sus.controllers.admin.user import UserController


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

    # set maintenance user
    user_uuid = config.get('ce1sus', 'maintenaceuseruuid', None)
    if None:
      raise MaintenanceException('maintenaceuseruuid was not defined in config')
    self.user = self.user_controller.get_user_by_id(user_uuid)

  def rebuild_relations(self, verbose=False):
    definitions = self.get_relationable_definitions(verbose)
    self.removing_obsolete_relations(definitions, verbose, False)
    self.regenerate_relations(definitions, verbose, False)
    self.relation_controller.relation_broker.do_commit(True)
    print 'Done.'

  def removing_obsolete_relations(self, definitions, verbose=False, commit=False):
    try:
      if verbose:
        print 'Removing obsolete relations'
      def_ids = list()
      for definition in definitions:
        def_ids.append(definition.identifier)
      # get all relations not in the definitions
      removed = self.relation_controller.remove_all_relations_by_definition_ids(def_ids, commit)
      if removed:
        print 'Found and deleted {0} obsolete relations'.format(removed)
      else:
        print 'No obsolete relation found'
    except ControllerException as error:
      raise MaintenanceException(error)

  def get_relationable_definitions(self, verbose=False):
    try:
      if verbose:
        print 'Getting relationable definitions'
      definitions = self.attribute_definition_controller.get_rel.get_all_relationable_definitions()
      if verbose:
        print 'Found {0} relationable definitions'.format(len(definitions))
      return definitions
    except ControllerException as error:
      raise MaintenanceException(error)

  def regenerate_relations(self, definitions, verbose=False, commit=False):
    try:
      if verbose:
        print 'Regenerating definitions'
      events = self.event_controller.get_all()
      if verbose:
        print 'Found {0} events'.format(len(events))
      if events:
        for event in events:
          flat_attributes = self.relation_controller.get_flat_attributes_for_event(event)
          self.relation_controller.generate_bulk_attributes_relations(event, flat_attributes, False)
        self.relation_controller.relation_broker.do_commit(commit)
      else:
        if verbose:
          print 'No event found.'
    except ControllerException as error:
      raise MaintenanceException(error)

  def recheck_definition_chksums(self, verbose=False):
    try:
      if verbose:
        print 'Checking definitions'
      # find all object definitions
      objects = self.object_definition_controller.get_all_object_definitions()
      not_matching_objs = list()
      for obj in objects:
        if obj.chksum != gen_obj_chksum(obj):
          not_matching_objs.append(obj)
      if verbose:
        print 'Found {0} not matching object chksums'.format(len(not_matching_objs))
      # fix checksums
      for not_matching_obj in not_matching_objs:
        not_matching_obj.chksum = gen_obj_chksum(not_matching_obj)
        self.object_definition_controller.update_object_definition(not_matching_obj, self.user)
      self.object_definition_controller.def_obj_broker.do_commit(True)
      # find attribute chksums not matching the one stored
      attributes = self.attribute_definition_controller.get_all_attribute_definitions()
      not_matching_attrs = list()
      for attribute in attributes:
        if attribute.chksum != gen_attr_chksum(attribute):
          not_matching_attrs.append(attribute)
      if verbose:
        print 'Found {0} not matching object chksums'.format(len(not_matching_objs))
      # fix checksums
      for not_matching_attr in not_matching_attrs:
        not_matching_attr.chksum = gen_attr_chksum(not_matching_attr)
        self.attribute_definition_controller.update_attribute_definition(not_matching_attr, self.user)
      self.attribute_definition_controller.def_attr_broker.do_commit(True)

    except ControllerException as error:
      raise MaintenanceException(error)

  def rebuild_event_relations(self, event_uuid, verbose):
    try:
      if verbose:
        print u'Rebuilding relations for event {0}'.format(event_uuid)
      # find event by uuid
      event = self.event_controller.get_event_by_id(event_uuid)
      flat_attributes = self.relation_controller.get_flat_attributes_for_event(event)
      self.relation_controller.generate_bulk_attributes_relations(event, flat_attributes, True)
    except ControllerException as error:
      raise MaintenanceException(error)

  def drop_relations(self, verbose):
    try:
      if verbose:
        print u'Truncate relations table'
      # get Table
      self.relation_controller.clear_relations_table()
      self.relation_controller.relation_broker.do_commit(True)
    except ControllerException as error:
      raise MaintenanceException(error)

  def __check_templates(self, handler_base_path, classname, handler, base_templates, destination_path, type_):
    file_to_move = handler_base_path + '/' + type_ + '/' + handler.get_view_type() + '.html'
    add_file = base_templates + type_ + '/' + handler.get_view_type() + '.html'
    # check if file is supplied by the new handler
    if isfile(file_to_move):
      if isfile(add_file):
        # file exists
        if fileHashMD5(file_to_move) != fileHashMD5(add_file):
          remove(destination_path)
          raise Exception((u'{0} does supply a template (file {2}/{1}.html) wich is different from an existing one.').format(classname, handler.get_view_type(), type_))
    else:
      remove(destination_path)
      raise Exception((u'{0} does not supply a template (file {2}/{1}.html not found)').format(classname, handler.get_view_type(), type_))

  def __append_js_to_index(self, classname, base_path):
    try:
      index_file = base_path + '/htdocs/index.html'
      orig_index = base_path + '/htdocs/old_index.html'
      move(index_file, orig_index)
      old_file = open(orig_index, 'r')
      new_file = open(index_file, 'w')
      lines = old_file.readlines()
      for line in lines:
        if line == '</body>':
          # append js here
          new_file.write('<script type="text/javascript" src="/js/ce1sus/controllers/handlers/{0}controller.js"></script>'.format(classname.lower()))
          new_file.write(line)
        else:
          new_file.write(line)
      old_file.close()
      new_file.close()
      return True
    except:
      # move file back
      move(orig_index, index_file)
      return False

  def add_handler(self, path, classname):
    modulename = basename(path).replace('.py', '')
    if not classname:
      classname = modulename.title().replace('handler', 'Handler')
    modulename = u'{0}'.format(modulename)
    # move to correct place
    handler_base_path = dirname(abspath(path))
    ce1sus_base_path = dirname(abspath(__file__))
    destination_path = ce1sus_base_path + '/ce1sus/handlers/' + basename(path)

    # copy python file if nessessary
    if destination_path != path:
      if isfile(destination_path):
        raise Exception(u'Handler already exists at the given place')
      else:
        copy(path, destination_path)
        print u'Copied file {0} to {1}'.format(path, destination_path)

    clazz = get_class(u'ce1sus.handlers.{0}'.format(modulename), classname)
    # check if class implements handler base
    instance = clazz()

    print u'Adding handler {0}'.format(modulename)

    if not isinstance(instance, HandlerBase):
      # remove file
      remove(destination_path)
      raise Exception((u'{0} does not implement HandlerBase').format(classname))

    # check if input, edit and view files required exists
    base_templates = ce1sus_base_path + '/htdocs/pages/handlers/'

    # check if template files are matching
    self.__check_templates(handler_base_path, classname, instance, base_templates, destination_path, 'add')
    self.__check_templates(handler_base_path, classname, instance, base_templates, destination_path, 'edit')
    self.__check_templates(handler_base_path, classname, instance, base_templates, destination_path, 'view')

    # copy templates files
    file_to_move = handler_base_path + '/add/' + instance.get_view_type() + '.html'
    add_file = base_templates + 'add/' + instance.get_view_type() + '.html'
    copy(add_file, file_to_move)
    file_to_move = handler_base_path + '/edit/' + instance.get_view_type() + '.html'
    edit_file = base_templates + 'edit/' + instance.get_view_type() + '.html'
    copy(edit_file, file_to_move)
    file_to_move = handler_base_path + '/edit/' + instance.get_view_type() + '.html'
    view_file = base_templates + 'edit/' + instance.get_view_type() + '.html'
    copy(view_file, file_to_move)

    js_file = None
    if instance.require_js():
      # do the same checks as for the above
      file_to_move = handler_base_path + '/' + classname.lower() + 'controller.js'
      base_js = ce1sus_base_path + '/htdocs/js/ce1sus/controllers/handlers/'
      js_file = base_js + classname.lower() + 'handler.js'

      # check if file is supplied by the new handler
      if isfile(file_to_move):
        if isfile(js_file):
          if fileHashMD5(file_to_move) != fileHashMD5(js_file):
            remove(destination_path)
            remove(add_file)
            remove(edit_file)
            remove(view_file)
            raise Exception((u'{0} does supply a js (file /htdocs/js/ce1sus/controllers/handlers/{0}handler.js) which is different from an existing one.').format(classname))
          else:
            copy(file_to_move, js_file)
      else:
        remove(destination_path)
        remove(add_file)
        remove(edit_file)
        remove(view_file)
        raise Exception((u'{0} does not supply a js but states it is required (file {0}handler.js not found)').format(classname))

      # appending file to index
      worked = self.__append_js_to_index(classname, ce1sus_base_path)
      if not worked:
        remove(destination_path)
        remove(add_file)
        remove(edit_file)
        remove(view_file)
        if js_file:
          remove(js_file)

    uuid = instance.get_uuid()
    description = instance.get_description()
    try:
      self.attribute_definition_controller.register_handler(uuid, u'{0}.{1}'.format(modulename, classname), description)
    except ControllerException:
      remove(destination_path)
      remove(add_file)
      remove(edit_file)
      remove(view_file)
      if js_file:
        remove(js_file)
    print "AttributeHandler {0} added".format(classname)

  def register_handler(self, modulename, classname=None):
    if not classname:
      classname = modulename.title().replace('handler', 'Handler')
    modulename = u'{0}'.format(modulename)

    clazz = get_class(u'ce1sus.handlers.{0}'.format(modulename), classname)
    # check if class implements handler base
    instance = clazz()

    print u'Adding handler {0}'.format(modulename)

    if not isinstance(instance, HandlerBase):
      # remove file
      raise Exception((u'{0} does not implement HandlerBase').format(classname))

    uuid = instance.get_uuid()
    description = instance.get_description()
    self.attribute_definition_controller.register_handler(uuid, u'{0}.{1}'.format(modulename, classname), description)
    # TODO check if the required files are available

  def remove_handler(self, modulename, classname=None):
    if not classname:
      classname = modulename.title().replace('handler', 'Handler')
    modulename = u'{0}'.format(modulename)

    clazz = get_class(u'ce1sus.handlers.{0}'.format(modulename), classname)
    # check if class implements handler base
    instance = clazz()

    # deregister
    self.attribute_definition_controller.remove_handler_by_id(instance.get_uuid())

    ce1sus_base_path = dirname(abspath(__file__))
    handler_path = ce1sus_base_path + '/ce1sus/handlers/' + modulename + '.py'

    remove(handler_path)
    base_templates = ce1sus_base_path + '/htdocs/pages/handlers/'

    add_file = base_templates + 'add/' + instance.get_view_type() + '.html'
    remove(add_file)

    edit_file = base_templates + 'edit/' + instance.get_view_type() + '.html'
    remove(edit_file)

    view_file = base_templates + 'edit/' + instance.get_view_type() + '.html'
    remove(view_file)

    js_file = None
    if instance.require_js():
      # do the same checks as for the above
      base_js = ce1sus_base_path + '/htdocs/js/ce1sus/controllers/handlers/'
      js_file = base_js + classname.lower() + 'handler.js'
      remove(js_file)

  # TODO clean this up

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
  parser.add_option('--class', dest='handler_class', type='string', default=None,
                    help='Function to add a new handler')
  parser.add_option('--reg-handler', dest='handler_reg_module', type='string', default='',
                    help='Function to registers an installed handler')
  parser.add_option('--remove-handler', dest='handler_rem_module', type='string', default='',
                    help='Function to removes an handler')

  (options, args) = parser.parse_args()

  basePath = dirname(abspath(__file__))
  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  maintenance = Maintenance(config)

  if options.handler_file:
    maintenance.add_handler(options.handler_file, options.handler_class)
  elif options.handler_reg_module:
    maintenance.register_handler(options.handler_reg_module, options.handler_class)
  elif options.handler_rem_module:
    maintenance.register_handler(options.handler_rem_module, options.handler_class)
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
