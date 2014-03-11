# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Nov 13, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from dagr.db.broker import BrokerException
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.definition.attributedefinitionbroker import \
                  AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
                  ObjectDefinitionBroker
from dagr.helpers.datumzait import DatumZait
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.relationbroker import RelationBroker
from ce1sus.common.mailhandler import MailHandler, MailHandlerException


class ValidationController(Ce1susBaseController):

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.send_mails = config.get('ce1sus', 'sendmail', False)
    self.event_broker = self.broker_factory(EventBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.def_attributes_broker = self.broker_factory(AttributeDefinitionBroker)
    self.def_object_broker = self.broker_factory(ObjectDefinitionBroker)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.relation_broker = self.broker_factory(RelationBroker)
    self.mail_handler = MailHandler(config)

  def get_all_unvalidated_events(self, limit=200, offset=0):
    try:
      return self.event_broker.get_all_unvalidated(limit, offset)
    except BrokerException as error:
      self._raise_exception(error)

  def get_event_by_id(self, event_id):
    """
    Returns an event with the given ID

    :param event_id: identifer of the event
    :type event_id: Integer

    :returns: Event
    """
    try:
      return self.event_broker.get_by_id(event_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_related_events(self, event):
    try:
      result = list()
      relations = self.relation_broker.get_relations_by_event(event, True)
      for relation in relations:
        rel_event = relation.rel_event
        if rel_event.identifier != event.identifier:
          result.append(rel_event)
      return result
    except BrokerException as error:
      self._raise_exception(error)

  def get_attr_def_by_obj_def(self, object_definition):
    """
    Returns a list of attribute definitions with the given object definition

    :param object_definition:
    :type object_definition: ObjectDefinition

    :returns: List of AttributeDefinitions
    """
    try:
      return self.def_attributes_broker.get_cb_values(object_definition.identifier)
    except BrokerException as error:
      self._raise_exception(error)

  def __validate_objects(self, objects):
    for obj in objects:
      obj.bit_value.is_validated = True
      # perfom validation of object attribtues
      for attribtue in obj.attributes:
        attribtue.bit_value.is_validated = True
      self.__validate_objects(obj.children)

  def validate_event(self, event, user):
    try:
      user = self._get_user(user.username)
      # perfom validation of event
      event.bit_value.is_validated = True
      # update modifier
      event.modifier = user
      event.modifier_id = event.modifier.identifier
      event.modified = DatumZait.utcnow()
      # check if the event has a group
      if event.creator_group is None:
        # if not add the default group of the validating user
        event.creator_group = user.default_group

      # perform validation of objects
      self.__validate_objects(event.objects)
      self.event_broker.update(event)
      if self.send_mails:
        if event.published == 1 and event.bit_value.is_validated_and_shared:
          self.mail_handler.send_event_mail(event)
    except (BrokerException, MailHandlerException) as error:
      self._raise_exception(error)

  def remove_unvalidated_event(self, event):
    try:
      self.event_broker.remove_by_id(event.identifier)
    except BrokerException as error:
      self._raise_exception(error)

  def get_flat_objects(self, event):
    result = list()
    objects = self.object_broker.get_all_event_objects(event.identifier)
    for obj in objects:
      for attribute in obj.attributes:
          result.append((obj, attribute))
    return result
