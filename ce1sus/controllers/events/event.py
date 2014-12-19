# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.brokers.event.eventbroker import EventBroker
from ce1sus.db.common.broker import ValidationException, IntegrityException, BrokerException
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def get_all_attributes_from_event(event):
  attributes = list()
  for obj in event.objects:
    __get_all_attributes_from_obj(attributes, obj)
  return attributes


def __get_all_attributes_from_obj(attributes, obj):
  attributes += obj.attributes
  for child in obj.children:
    __get_all_attributes_from_obj(attributes, child)


class EventController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    BaseController.__init__(self, config)
    self.event_broker = self.broker_factory(EventBroker)

  def insert_event(self, user, event, mkrelations=True, commit=True):
    """
    inserts an event

    If it is invalid the event is returned

    :param event:
    :type event: Event

    :returns: Event, Boolean
    """
    self.logger.debug('User {0} inserts a new event'.format(user.username))
    try:
      # the the creator

      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(event, user, user.group, True)

      self.event_broker.insert(event, False)
      # generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.event_broker.do_commit(commit)
      return event
    except ValidationException:
      message = ObjectValidator.getFirstValidationError(event)
      raise ControllerException(u'Could not update object definition due to: {0}'.format(message))
    except IntegrityException as error:
      self.logger.debug(error)
      self.logger.info(u'User {0} tried to insert an event with uuid "{1}" but the uuid already exists'.format(user.username, event.identifier))
      raise ControllerException(u'An event with uuid "{0}" already exists'.format(event.identifier))
    except BrokerException as error:
      raise ControllerException(error)

  def update_event(self, user, event, mkrelations=True, commit=True):
    self.logger.debug('User {0} updates a event {1}'.format(user.username, event.identifier))
    try:
      # the the creator

      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(event, user, user.group, False)

      self.event_broker.update(event, False)
      # generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.event_broker.do_commit(commit)
      return event
    except ValidationException:
      message = ObjectValidator.getFirstValidationError(event)
      raise ControllerException(u'Could not update object definition due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def remove_event(self, user, event):
    self.logger.debug('User {0} deleted a event {1}'.format(user.username, event.identifier))
    try:
      self.event_broker.remove_by_id(event.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def get_event_by_id(self, identifier):
    try:
      event = self.event_broker.get_by_id(identifier)
      return event
    except BrokerException as error:
      raise ControllerException(error)
