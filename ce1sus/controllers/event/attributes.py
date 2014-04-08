# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from ce1sus.brokers.definition.attributedefinitionbroker import AttributeDefinitionBroker
from dagr.db.broker import ValidationException, BrokerException
from ce1sus.common.handlers.base import HandlerException
from ce1sus.brokers.valuebroker import ValueBroker
from ce1sus.brokers.definition.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker
from dagr.helpers.converters import ValueConverter, ConversionException
import ast


class AttributesController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.def_attributes_broker = self.broker_factory(AttributeDefinitionBroker)
    self.value_broker = self.broker_factory(ValueBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)
    self.event_broker = self.broker_factory(EventBroker)
    self.object_broker = self.broker_factory(ObjectBroker)

  def remove_by_id(self, attribute_id):
    """
    Returns an event with the given ID

    :param event_id: identifer of the event
    :type event_id: Integer

    :returns: Event
    """
    try:
      return self.attribute_broker.remove_by_id(attribute_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_cb_attr_def_by_obj(self, obj):
    """
    Returns the values for combobox displaying attributes definitions
    """
    try:
      return self.def_attributes_broker.get_cb_values(obj.def_object_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_attr_def_by_id(self, attribute_defintion_id):
    """
    Returns the attribute definition by its id
    """
    try:
      return self.def_attributes_broker.get_by_id(attribute_defintion_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_attr_def_by_chksum(self, chksum):
    """
    Returns the attribute definition by its chksum
    """
    try:
      return self.def_attributes_broker.get_defintion_by_chksum(chksum)
    except BrokerException as error:
      self._raise_exception(error)

  def get_defintion_by_chksum(self, chksum):
    """
    Alias for get_attr_def_by_chksum
    """
    return self.get_attr_def_by_chksum(chksum)

  def get_defintion_by_chksums(self, chksums):
    """
    Returns the attribute definitions matching the list of chksums
    """
    try:
      return self.def_attributes_broker.get_defintion_by_chksums(chksums)
    except BrokerException as error:
      self._raise_exception(error)

  def insert_attributes(self, user, obj, attribute, additional_attributes):
    """
    inserts the attributes to the DB
    """
    try:
      self._get_logger().debug('User {0} inserts attributes on object {1}'.format(user.username,
                                                                                  obj.identifier))
      user = self._get_user(user.username)
      valid = True
      try:
        self.attribute_broker.insert(attribute, commit=False)
      except ValidationException:
        valid = False
      if not additional_attributes is None:
        for additional_attribute in additional_attributes:
          try:
            additional_attribute.attr_parent_id = attribute.identifier
            self.attribute_broker.insert(additional_attribute, commit=False)
          except ValidationException:
            valid = False
      if valid:
        self.object_broker.update_object(user, obj, commit=False)
        event = obj.get_parent_event()
        if self.is_event_owner(event, user):
          event.published = 0
        self.event_broker.update_event(user, event, commit=False)
        self.attribute_broker.do_commit(True)
      else:
        self.attribute_broker.do_rollback()

      return attribute, additional_attributes, valid

    except BrokerException as error:
      self._raise_exception(error)

  # pylint: disable=R0913
  def __populate_attributes(self, user, obj, definition, action, params, rest=False):
    """
    Populates the attributes to be inserted
    """
    try:
      if hasattr(user, 'session'):
        user = self._get_user(user.username)
      if action == 'insert':
        definitions = dict()
        definitions[definition.chksum] = definition
        handler_instance = definition.handler
        # get additional definitions if required
        additional_definitions_chksums = handler_instance.get_additinal_attribute_chksums()
        if additional_definitions_chksums:
          additional_definitions = self.def_attributes_broker.get_defintion_by_chksums(additional_definitions_chksums)
          for additional_definition in additional_definitions:
            definitions[additional_definition.chksum] = additional_definition
        if rest:
          attribute, additional_attributes = handler_instance.process_rest_post(obj,
                                                                             definitions,
                                                                             # self._get_user(user.username),
                                                                             user,
                                                                             params)
        else:
          attribute, additional_attributes = handler_instance.process_gui_post(obj,
                                                                             definitions,
                                                                             # self._get_user(user.username),
                                                                             user,
                                                                             params)
        return attribute, additional_attributes
    except (BrokerException, HandlerException) as error:
      self._raise_exception(error)

  @staticmethod
  def __set_web_attribute(attribute):
    """
    sets the parameters for a web attribute
    """
    attribute.bit_value.is_web_insert = True
    attribute.bit_value.is_validated = True
    attribute.bit_value.is_rest_instert = False
    attribute.bit_value.is_proposal = False

  @staticmethod
  def __set_rest_attribute(attribute):
    """
    sets the parameters for a rest attribute
    """
    attribute.bit_value.is_web_insert = False
    attribute.bit_value.is_rest_instert = True
    attribute.bit_value.is_validated = False
    attribute.bit_value.is_proposal = False

  @staticmethod
  def __set_proposet_attribute(attribute):
    """
    sets the parameters for a web attribute
    """
    attribute.bit_value.is_proposal = True
    attribute.bit_value.is_validated = False

  # pylint: disable=R0913
  def populate_web_attributes(self, user, obj, definition_id, action, params, proposal):
    """
    Populates the attributes to be inserted coming from the web interface
    """
    try:
      definition = self.def_attributes_broker.get_by_id(definition_id)
      attribute, additional_attributes = self.__populate_attributes(user,
                                                                    obj,
                                                                    definition,
                                                                    action,
                                                                    params,
                                                                    False)
      # set bit values
      AttributesController.__set_web_attribute(attribute)
      if proposal:
        AttributesController.__set_proposet_attribute(attribute)
      if additional_attributes:
        for additional_attribute in additional_attributes:
          AttributesController.__set_web_attribute(additional_attribute)
          if proposal:
            AttributesController.__set_proposet_attribute(additional_attribute)
      return attribute, additional_attributes
    except BrokerException as error:
      self._raise_exception(error)

  def populate_rest_attributes(self, user, obj, dictionary, action, attr_defs=dict()):
    """
    Populates the attributes to be inserted coming from the rest api
    """
    try:
      definition_dict_obj = dictionary.get('definition', None)
      if definition_dict_obj:
        definition_dict = definition_dict_obj.get('RestAttributeDefinition', None)
        if not definition_dict:
          raise BrokerException('No definition specified')
        chksum = definition_dict.get('chksum', None)
        if chksum:
          # check if definition was not already seen
          attr_def = attr_defs.get(chksum, None)
          if attr_def:
            definition = attr_def
          else:
            # TODO: Support auto inserts of definitions
            definition = self.def_attributes_broker.get_defintion_by_chksum(chksum)
            attr_defs[chksum] = definition
        else:
          raise BrokerException('No chksum specified')
      else:
        raise BrokerException('No definition specified')

      str_value = dictionary.get('value', None)
      # convert str_value to value
      if definition.class_index in [0, 1]:
        value = str_value
      elif definition.class_index == 2:
        # date
        try:
          value = ValueConverter.set_date(str_value)
        except ConversionException:
          raise BrokerException(u'Could not convert date for attribute with type {0} and value {1}'.format(definition.name, str_value))
      elif definition.class_index == 3:
        # number
        value = ast.literal_eval(str_value)
      else:
        raise BrokerException('Could not determine type of value')
      params = dict()
      params['value'] = value
      params['ioc'] = dictionary.get('ioc', None)
      params['shared'] = dictionary.get('share', None)
      attribute, additional_attributes = self.__populate_attributes(user,
                                                                    obj,
                                                                    definition,
                                                                    action,
                                                                    params,
                                                                    True)
      # Set parent object
      attribute.object = obj
      # set bit values
      AttributesController.__set_rest_attribute(attribute)
      if additional_attributes:
        for additional_attribute in additional_attributes:
          additional_attribute.object = obj
          AttributesController.__set_rest_attribute(additional_attribute)
      return attribute, additional_attributes

    except BrokerException as error:
      self._raise_exception(error)

  def get_all_definitions(self):
    """
    Returns all the attribute definitions
    """
    try:
      return self.def_attributes_broker.get_all()
    except BrokerException as error:
      self._raise_exception(error)

  def insert_definition(self, user, attribute_definition):
    """
    Inserts an attribute definition
    """
    self._get_logger().debug('User {0} inserts an attribute definition'.format(user.username))
    try:
      self.def_attributes_broker.insert(attribute_definition, True)
      return attribute_definition, True
    except ValidationException:
      return attribute_definition, False
    except BrokerException as error:
      self._raise_exception(error)

  def get_handler_by_uuid(self, uuid):
    """
    Returns the handler by its uuid
    """
    try:
      return self.handler_broker.get_by_uuid(uuid)
    except BrokerException as error:
      self._raise_exception(error)

  def populate_rest_attr_def(self, user, dictionary, action):
    """
    Populates an attribute coming from the rest api
    """
    self._get_logger().debug('User {0} populates an attribute definition over the rest api'.format(user.username))
    try:
      handler_uuid = dictionary.get('handler_uuid', None)
      if handler_uuid:
        handler = self.handler_broker.get_by_uuid(handler_uuid)
      return self.def_attributes_broker.build_attribute_definition(identifier=None,
                                                                   name=dictionary.get('name', None),
                                                                   description=dictionary.get('description', None),
                                                                   regex=dictionary.get('regex', None),
                                                                   class_index=dictionary.get('class_index', None),
                                                                   action=action,
                                                                   handler_index=handler.identifier,
                                                                   share=dictionary.get('share', None),
                                                                   relation=dictionary.get('relation', None)
                                                                   )
    except BrokerException as error:
      self._raise_exception(error)

  def validate_attribute(self, event, attribute, user):
    try:
      attribute.bit_value.is_validated = True
      self.attribute_broker.update(attribute, commit=False)
      if event.published == 1:
        event.published = 0
        self.event_broker.update_event(user, event, commit=False)
      self.object_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)
