# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
from ce1sus.brokers.definition.attributedefinitionbroker import AttributeDefinitionBroker
from ce1sus.brokers.event.eventclasses import Attribute, Event, Object
from ce1sus.brokers.relationbroker import RelationBroker
from ce1sus.brokers.staticbroker import EventAttribtues
from ce1sus.brokers.valuebroker import ValueBroker
from dagr.db.broker import BrokerBase, BrokerException
from dagr.helpers.datumzait import DatumZait


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'



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
    # finds in addition the relations
    BrokerBase.insert(self, instance, False, validate)
    self.relation_broker.generate_attribute_relations(instance, False)

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
    except BrokerException as error:
      self.session.rollback()
      raise BrokerException(error)

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

  def look_for_attribute_value(self, attribute_definition, value, operand='=='):
    return self.relation_broker.look_for_attribute_value(attribute_definition, value, operand)

  def look_for_event_attribute_values(self, operand, attribute, needle):
    return self.relation_broker.look_for_event_attribtues(Event, operand, attribute, needle)

  def look_for_any_value(self, value, operand):
    # first look inside attributes
    found_values = self.relation_broker.look_for_attribute_value(None, value, operand)
    # the look in events
    for item in EventAttribtues.get_definitions().values():
      found_values = found_values + self.look_for_event_attribute_values(Event, operand, item, value)
    return found_values

  def look_for_uuids(self, value, operand):
    found_values = list()
    for clazz in [Object, Attribute, Event]:
      found_values = found_values + self.relation_broker.look_for_event_attribtues(clazz, operand, 'uuid', value)
    return found_values

