# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.helpers.datumzait import DatumZait

from ce1sus.brokers.definition.attributedefinitionbroker import \
  AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
  ObjectDefinitionBroker
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.event.commentbroker import CommentBroker
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk
from ce1sus.controllers.base import Ce1susBaseController
from dagr.db.broker import ValidationException, BrokerException
from dagr.web.helpers.pagination import Paginator, PaginatorOptions
from ce1sus.brokers.relationbroker import RelationBroker, EventRelation


class EventController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.event_broker = self.broker_factory(EventBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.def_object_broker = self.broker_factory(ObjectDefinitionBroker)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.def_attributes_broker = self.broker_factory(AttributeDefinitionBroker)
    self.commentBroker = self.broker_factory(CommentBroker)
    self.relation_broker = self.broker_factory(RelationBroker)

  def get_by_id(self, event_id):
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

  def get_related_events(self, event, user, cache):
    """
    Returns the relations which the user can see


    :param user:
    :type user: User
    :param event:
    :type event: Event
    :param cache:
    :type cache: Dictionary

    :returns: List of Relation
    """
    result = list()
    try:
      # get for each object
      # prepare list
      #
      relations = self.relation_broker.get_relations_by_event(event, True)
      for relation in relations:
        rel_event = relation.rel_event
        if rel_event.identifier != event.identifier:
          if self._is_event_viewable_for_user(event, user, cache):
            result.append(rel_event)
    except BrokerException as error:
      self._get_logger().error(error)

    return result

  def __popultate_event(self, user, **kwargs):
    action = kwargs.get('action', None)
    identifier = kwargs.get('identifier', None)
    status = kwargs.get('status', None)
    tlp_index = kwargs.get('tlp_index', None)
    description = kwargs.get('description', None)
    name = kwargs.get('name', None)
    published = kwargs.get('published', None)
    first_seen = kwargs.get('first_seen', None)
    last_seen = kwargs.get('last_seen', None)
    risk = kwargs.get('risk', None)
    analysis = kwargs.get('analysis', None)
    # fill in the values
    return self.event_broker.build_event(identifier,
                                        action,
                                        status,
                                        tlp_index,
                                        description,
                                        name,
                                        published,
                                        first_seen,
                                        last_seen,
                                        risk,
                                        analysis,
                                        self._get_user(user.username))

  def populate_web_event(self, user, **kwargs):
    """
    populates an event object with the given arguments

    :param username:
    :type username: String

    :returns: Event
    """
    event = self.__popultate_event(user, **kwargs)
    event.bit_value.is_web_insert = True
    event.bit_value.is_validated = True
    return event

  def insert_event(self, user, event):
    """
    inserts an event

    If it is invalid the event is returned

    :param event:
    :type event: Event

    :returns: Event, Boolean
    """
    try:
      self.event_broker.insert(event)
      return event, True
    except ValidationException:
      return event, False
    except BrokerException as error:
      self._raise_exception(error)

  def remove_event(self, user, event):
    """
    removes an event

    :param event:
    :type event: Event
    """
    try:
      self.event_broker.remove_by_id(event.identifier)
    except BrokerException as error:
      self._raise_exception(error)

  def update_event(self, user, event):
    """
    updates an event

    If it is invalid the event is returned

    :param event:
    :type event: Event
    """
    try:
      user = self._get_user(user.username)
      self.event_broker.update_event(user, event, True)
      return event, True
    except ValidationException:
      return event, False
    except BrokerException as error:
      self._raise_exception(error)

  def get_full_event_relations(self, event, user, cache):
    try:
      result = list()
      relations = self.relation_broker.get_relations_by_event(event, False)
      for relation in relations:
          rel_event = relation.rel_event
          # check if is viewable for user
          if self._is_event_viewable_for_user(rel_event, user, cache):
            result.append(relation)
      return result
    except BrokerException as error:
      self._raise_exception(error)

  def get_cb_tlp_lvls(self):
    try:
      return TLPLevel.get_definitions()
    except BrokerException as error:
      self._raise_exception(error)
