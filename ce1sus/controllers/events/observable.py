# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.brokers.event.observablebroker import ObservableBroker
from ce1sus.db.common.broker import ValidationException, IntegrityException, BrokerException
from ce1sus.db.brokers.event.composedobservablebroker import ComposedObservableBroker
from ce1sus.db.brokers.event.objectbroker import ObjectBroker
from ce1sus.db.brokers.event.attributebroker import AttributeBroker


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ObservableController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    BaseController.__init__(self, config)
    self.observable_broker = self.broker_factory(ObservableBroker)
    self.composed_observable_broker = self.broker_factory(ComposedObservableBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.attribute_broker = self.broker_factory(AttributeBroker)

  def insert_observable(self, observable, user, commit=True):
    """
    inserts an event

    If it is invalid the event is returned

    :param event:
    :type event: Event

    :returns: Event, Boolean
    """
    self.logger.debug(observable.identifier)
    self.logger.debug('User {0} inserts a new event'.format(user.username))
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(observable, user, user.group, True)
      self.observable_broker.insert(observable, False)
      # generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.observable_broker.do_commit(commit)
      return observable, True
    except ValidationException:
      return observable, False
    except IntegrityException as error:
      self.logger.debug(error)
      self.logger.info(u'User {0} tried to insert an event with uuid "{1}" but the uuid already exists'.format(user.username, observable.identifier))
      raise ControllerException(u'An event with uuid "{0}" already exists'.format(observable.identifier))
    except BrokerException as error:
      raise ControllerException(error)

  def get_observable_by_id(self, identifier):
    try:
      observable = self.observable_broker.get_by_id(identifier)
      return observable
    except BrokerException as error:
      raise ControllerException(error)

  def get_composed_observable_by_id(self, identifier):
    try:
      composed_observable = self.composed_observable_broker.get_by_id(identifier)
      return composed_observable
    except BrokerException as error:
      raise ControllerException(error)

  def get_attribute_by_id(self, identifier):
    try:
      obj = self.attribute_broker.get_by_id(identifier)
      return obj
    except BrokerException as error:
      raise ControllerException(error)

  def get_object_by_id(self, identifier):
    try:
      obj = self.object_broker.get_by_id(identifier)
      return obj
    except BrokerException as error:
      raise ControllerException(error)

  def update_observable(self, observable, user, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(observable, user, user.group, True)
      self.observable_broker.update(observable, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_observable(self, observable, user, commit=True):
    try:
      self.observable_broker.remove_by_id(observable.identifier)
    except BrokerException as error:
      raise ControllerException(error)
