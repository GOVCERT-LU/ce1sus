# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Aug, 2013
"""
from ce1sus.controllers.base import BaseController, SpecialControllerException, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.definitions.attributedefinitionbroker import AttributeDefinitionBroker
from ce1sus.db.brokers.definitions.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.db.brokers.definitions.typebrokers import AttributeTypeBroker, AttributeViewTypeBroker
from ce1sus.db.classes.common import ValueTable
from ce1sus.db.classes.definitions import AttributeDefinition
from ce1sus.db.common.broker import BrokerException, ValidationException, IntegrityException, NothingFoundException
from ce1sus.helpers.common.hash import hashSHA1
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def gen_attr_chksum(attribute):
  key = '{0}{1}{2}{3}'.format(attribute.name,
                              attribute.regex,
                              attribute.table_id,
                              attribute.attributehandler_id)
  return hashSHA1(key)


class AttributeDefinitionController(BaseController):
  """Controller handling all the requests for attributes"""

  def __init__(self, config):
    BaseController.__init__(self, config)
    self.attr_def_broker = self.broker_factory(AttributeDefinitionBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)
    self.type_broker = self.broker_factory(AttributeTypeBroker)
    self.view_type_broker = self.broker_factory(AttributeViewTypeBroker)

  def get_all_attribute_definitions(self):
    """
    Returns all attribute definitions
    """
    try:
      return self.attr_def_broker.get_all(AttributeDefinition.name.asc())
    except BrokerException as error:
      raise ControllerException(error)

  def get_attribute_definitions_by_id(self, object_id):
    """
    Returns the attribute definition by the given id
    """
    try:
      return self.attr_def_broker.get_by_id(object_id)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_attribute_definition(self, attribute, user):
    try:
      attribute.chksum = gen_attr_chksum(attribute)
      # check if handler is associated
      if not attribute.attribute_handler:
        handler = self.handler_broker.get_by_id(attribute.attributehandler_id)
        attribute.attribute_handler = handler
      self.set_simple_logging(attribute, user, insert=True)
      attribute = self.attr_def_broker.insert(attribute)
      return attribute
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(attribute)
      raise ControllerException(u'Could not update object definition due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def update_attribtue_definition(self, attribute, user):
    try:
      attribute.chksum = gen_attr_chksum(attribute)
      self.set_simple_logging(attribute, user, insert=True)
      attribute = self.attr_def_broker.update(attribute)
      return attribute
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(attribute)
      raise ControllerException(u'Could not update object definition due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def remove_definition_by_id(self, uuid):
    try:
      self.attr_def_broker.remove_by_id(uuid)
    except IntegrityException as error:
      raise SpecialControllerException('Cannot delete this attribute. The attribute is still referenced.')
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_handlers(self):
    try:
      return self.handler_broker.get_all()
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_tables(self):
    values = ValueTable.get_dictionary()
    return values

  def get_all_types(self):
    try:
      return self.type_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_view_types(self):
    try:
      return self.view_type_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)
