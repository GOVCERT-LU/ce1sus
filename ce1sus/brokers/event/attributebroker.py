# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, ValidationException, \
                           BrokerException
from dagr.helpers.validator.objectvalidator import ObjectValidator
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                              AttributeDefinitionBroker
from ce1sus.brokers.valuebroker import ValueBroker
from ce1sus.brokers.relationbroker import RelationBroker
from ce1sus.brokers.event.eventclasses import Attribute
from dagr.helpers.datumzait import DatumZait


class AttributeBroker(BrokerBase):
  """
  This broker handles all operations on attribute objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.value_broker = ValueBroker(session)
    self.attribute_definition_broker = AttributeDefinitionBroker(session)
    self.relation_broker = RelationBroker(session)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Attribute

  def insert(self, instance, commit=True, validate=True):
    """
    overrides BrokerBase.insert
    """
    # validation of the value of the attribute first
    # get the definition containing the definition how to validate an attribute
    definition = instance.definition
    ObjectValidator.validateRegex(instance,
                                  'plain_value',
                                  definition.regex,
                                  'The value does not match {0}'.format(
                                                            definition.regex),
                                  True)
    errors = not instance.validate()
    if errors:
      raise ValidationException(ObjectValidator.getFirstValidationError(instance))

    try:
      # insert value for value table
      BrokerBase.insert(self, instance, False, validate)
      # insert relations

      self.relation_broker.generate_attribute_relations(instance, False)

      self.value_broker.inser_by_attribute(instance, False)
      self.do_commit(True)

    except BrokerException as e:
      self.session.rollback()
      raise BrokerException(e)

  def update(self, instance, commit=True, validate=True):
    """
    overrides BrokerBase.update
    """
    # validation of the value of the attribute first
    definition = instance.definition
    ObjectValidator.validateRegex(instance,
                                  'plain_value',
                                  definition.regex,
                                  'The value does not match {0}'.format(
                                                          definition.regex),
                                  False)
    errors = not instance.validate()
    if errors:
      raise ValidationException(ObjectValidator.getFirstValidationError(instance))
    try:
      BrokerBase.update(self, instance, False, validate)
      # updates the value of the value table
      self.do_commit(False)
      self.value_broker.update_by_attribute(instance, False)
      self.do_commit(commit)
    except BrokerException as e:
      self.session.rollback()
      raise BrokerException(e)

  def remove_by_id(self, identifier, commit=True):
    try:
      attribute = self.get_by_id(identifier)
      self.value_broker.remove_by_attribute(attribute, False)
        # first remove values
      self.do_commit(False)
        # remove attribute
      BrokerBase.remove_by_id(self,
                            identifier=attribute.identifier,
                            commit=False)
      self.do_commit(commit)
    except BrokerException as e:
      self.session.rollback()
      raise BrokerException(e)

  def remove_attribute_list(self, attributes, commit=True):
    """
      Removes all the attributes of the list

      :param attributes: List of attributes
      :type attributes: List of Attributes
    """
    try:
      for attribute in attributes:
        # remove attributes
        self.remove_by_id(attribute.identifier, False)
        self.do_commit(False)
      self.do_commit(commit)
    except BrokerException as error:
      self.session.rollback()
      raise BrokerException(error)

  def look_for_attribute_value(self, attribute_definition, value, operand='=='):
    return self.relation_broker.look_for_attribute_value(attribute_definition,
                                              value,
                                              operand)

  def update_attribute(self, user, attribute, commit=True):
    """
    updates an object

    If it is invalid the event is returned

    :param event:
    :type event: Event
    """
    attribute.modifier = user
    attribute.modified = DatumZait.utcnow()
    self.update(attribute, False)
    self.do_commit(commit)
